"""
This module contains functions for evaluating the performance of the fine-tuned model.
It includes implementations for metrics like confusion matrix, F1 score, Chi-Square test and comparing different models.

Classes:
    ModelEvaluator: Statistically evaluates and compares models performances.
"""


import re
from typing import Any, Counter

from sklearn.metrics import confusion_matrix
from app.backend.database.schema import EvaluationType
from app.backend.dtos.get_request import GetDataPointEvaluationsDTO, GetModelEvalautionsDTO, GetModelsDTO
from app.backend.dtos.response import ComplexModelDTO, ModelDTO, TrainingRunDTO
from app.backend.service.implementations.service_manager_facade import ServiceManagerFacade
import plotly as pl
import numpy as np
from sklearn.metrics import precision_score, recall_score, f1_score, accuracy_score, confusion_matrix
from scipy.stats import chi2_contingency
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import streamlit as st
import matplotlib.colors as mc
import colorsys
from decimal import Decimal, getcontext
import plotly.express as px


class ModelMetricsEvaluator:
    """
    Provides functionalities to evaluate the performance of the fine-tuned language model,
    including calculating metrics like confusion matrix, F1 score, Chi-Saquare test and comparing different models.
    """

    def __init__(self, service: ServiceManagerFacade, model_id: int):
        self._service: ServiceManagerFacade = service
        self._model: ComplexModelDTO = service.get_model_by_id(model_id)[0]

        # The non-checkpoint model the checkpoint model has been created with
        original_model: ModelDTO = None
        if self._model.is_checkpoint_model:
            original_model: ModelDTO = service.filter_models(GetModelsDTO(
                fine_tuning_job_id=self._model.fine_tuning_job_id, is_checkpoint_model=False))[0]

        # Model evaluations data
        # Get the model/datapoint evaluations from the non_checkpoint model since this is the only model that stores this data
        self._helpfulness_score_data, self._honesty_score_data, self._harmlessness_score_data, self._model_evaluation_scemantic_similarity_score_data, self._evaluation_types, self._total_model_evaluations_count = service.calculate_model_evaluation_scores(
            GetModelEvalautionsDTO(model_id=original_model.id if original_model else model_id))
        # Datapoint evaluations data
        self._coherence_score_data, self._relevance_score_data, self._datapoints_semantic_similarity_score_data, self._total_datapoint_evaluations_count = service.calculate_datapoint_evaluation_scores(
            GetDataPointEvaluationsDTO(model_id=original_model.id if original_model else model_id))
        self._fine_tuning_job_metrics: dict[str,
                                            Any] = service.get_fine_tuning_job_metrics(self._model.fine_tuning_job_id, self._model.checkpoint_step)

    def generate_datapoint_evaluations_statistic(self):
        self._service.calculate_datapoint_evaluation_scores(
            GetDataPointEvaluationsDTO(model_id=self._model.id))
        # TODO: Implement to properly display return values as statistic

    def generate_model_evalaution_statistic(self):
        self._service.calculate_model_evaluation_scores(
            GetDataPointEvaluationsDTO(model_id=self._model.id))
        # TODO: Implement to properly display return values as statistic

    def get_fine_tuning_job_metrics(self):
        return self._fine_tuning_job_metrics

    def get_model(self):
        return self._model

    def lighten_color(self, rgba_color: str, amount: float = 0.3):
        """Lightens the given RGBA color by a specified amount."""
        # Extract the RGBA components
        match = re.match(r'rgba\((\d+), (\d+), (\d+), ([\d\.]+)\)', rgba_color)
        if not match:
            raise ValueError("Invalid RGBA color format")

        r, g, b, a = map(float, match.groups())
        r /= 255
        g /= 255
        b /= 255

        # Convert RGB to HLS
        h, l, s = colorsys.rgb_to_hls(r, g, b)

        # Lighten the color
        l = min(1, l + amount * (1 - l))

        # Convert back to RGB
        r, g, b = colorsys.hls_to_rgb(h, l, s)

        # Return the lightened color as an RGBA string
        return f"rgba({int(r * 255)}, {int(g * 255)}, {int(b * 255)}, {a})"

    def create_model_evaluation_chart(self):
        data = [
            self._helpfulness_score_data,
            self._honesty_score_data,
            self._harmlessness_score_data,
            self._model_evaluation_scemantic_similarity_score_data
        ]
        labels = ["Helpfulness", "Honesty",
                  "Harmlessness", "Semantic Similarity"]
        colors = {
            "Helpfulness": "rgba(40, 64, 52, 0.8)",  # light green
            "Honesty": "rgba(4, 78, 148, 0.8)",  # light blue
            "Harmlessness": "rgba(183, 35, 37, 0.8)",  # light red
            "Semantic Similarity": "rgba(77, 81, 87, 0.8)"  # light gray
        }

        chart_title = "Model Evaluation Metrics"

        self.create_combined_evaluation_chart(
            data, labels, colors, self._total_model_evaluations_count, chart_title)

    def create_datapoint_evaluation_chart(self):
        data = [
            self._coherence_score_data,
            self._relevance_score_data,
            self._datapoints_semantic_similarity_score_data
        ]
        labels = ["Coherence", "Relevance", "Semantic Similarity"]
        colors = {
            "Coherence": "rgba(40, 64, 52, 0.8)",  # light green
            "Relevance": "rgba(4, 78, 148, 0.8)",  # light blue
            "Semantic Similarity": "rgba(77, 81, 87, 0.8)"  # light gray
        }

        chart_title = "Datapoint Evaluation Metrics"

        self.create_combined_evaluation_chart(
            data, labels, colors, self._total_datapoint_evaluations_count, chart_title)

    def create_combined_evaluation_chart(self, data, labels, colors, total_count, chart_title):
        """
        Create a combined evaluation chart.

        :param data: List of tuples containing (average, percentage, count) for each evaluation type.
        :param labels: List of labels for each evaluation type.
        :param colors: Dictionary containing colors for each evaluation type.
        :param total_count: Total count for scaling the count plot.
        :param chart_title: Title of the chart.
        """

        # Set precision for Decimal operations
        getcontext().prec = 6  # Enough precision to handle division and maintain 4 decimal places

        # Adjust semantic similarity average to accomodate other stats which only scale from 0-10
        for i, (avg, pct, count) in enumerate(data):
            if "Semantic Similarity" in labels[i]:
                avg = Decimal(avg) / Decimal(10)
                avg = round(avg, 4)
                data[i] = (avg, pct, count)

        # Create lighter colors for hover text
        hover_colors = {
            key: self.lighten_color(value, 0.5)
            for key, value in colors.items()
        }

        # Create subplots for averages, percentages, and counts
        fig = make_subplots(
            rows=1, cols=3,
            subplot_titles=(
                "<span style='color:white'>Average Scores</span>",
                "<span style='color:white'>Evaluations Percentage</span>",
                "<span style='color:white'>Evaluation Counts</span>"
            )
        )

        # Add traces for averages
        for i, (avg, _, _) in enumerate(data):
            label = labels[i]
            color = colors[label]
            hover_color = hover_colors[label]

            fig.add_trace(go.Bar(
                x=[label],
                y=[avg],
                name=f"{label} Avg.",
                marker_color=color,
                hovertemplate=f"<span style='color:{hover_color}'>{
                    label} Avg.</span>: {avg}<extra></extra>"
            ), row=1, col=1)

        # Add traces for percentages
        for i, (_, pct, _) in enumerate(data):
            label = labels[i]
            color = colors[label]
            hover_color = hover_colors[label]

            fig.add_trace(go.Bar(
                x=[label],
                y=[pct],
                name=f"{label} %",
                marker_color=color,
                hovertemplate=f"<span style='color:{hover_color}'>{
                    label} %</span>: {pct}<extra></extra>"
            ), row=1, col=2)

        # Add traces for counts
        for i, (_, _, count) in enumerate(data):
            label = labels[i]
            color = colors[label]
            hover_color = hover_colors[label]

            fig.add_trace(go.Bar(
                x=[label],
                y=[count],
                name=f"{label} Total",
                marker_color=color,
                hovertemplate=f"<span style='color:{hover_color}'>{
                    label} Total</span>: {count}<extra></extra>"
            ), row=1, col=3)

        # Customize layout and scaling
        fig.update_layout(
            title={
                'text': chart_title,
                'x': 0.5,
                'xanchor': 'center'
            },
            height=350,
            showlegend=False
        )

        # Set y-axis ranges for each subplot
        fig.update_yaxes(title_text="Average Score (0-10.0)",
                         range=[0, 10], row=1, col=1)
        fig.update_yaxes(title_text="Percentage (%)",
                         range=[0, 100], row=1, col=2)
        fig.update_yaxes(
            title_text=f"Count (0-{total_count})", range=[0, total_count], row=1, col=3)

        # Update annotations (titles) to have custom colors
        annotations = fig['layout']['annotations']
        for i, label in enumerate(labels):
            annotations[0]['font']['color'] = "white"
            annotations[1]['font']['color'] = "white"
            annotations[2]['font']['color'] = "white"

        # Display the combined chart in Streamlit
        st.plotly_chart(fig, use_container_width=True)

    def create_fine_tuning_result_charts(self):
        result_files_contents = self._fine_tuning_job_metrics["result_files_contents"]

        headers = ["step", "train_loss", "train_accuracy",
                   "valid_loss", "valid_mean_token_accuracy"]
        custom_names = {
            "train_loss": "Training Loss",
            "train_accuracy": "Training Accuracy",
            "valid_loss": "Validation Loss",
            "valid_mean_token_accuracy": "Valid Mean Token Accuracy"
        }

        # Check if result_files_contents is empty
        if not result_files_contents:
            # Create an empty figure with labels and legends
            fig = make_subplots(
                rows=1, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.05,
            )

            for header in headers[1:]:  # Skip 'step'
                fig.add_trace(
                    go.Scatter(x=[], y=[],
                               mode='lines+markers', name=custom_names.get(header, header))
                )

            fig.update_layout(
                title={
                    'text': "Fine Tuning Job Metrics",
                    'x': 0.5,
                    'xanchor': 'center'
                },
                height=400,  # Adjust height to accommodate the legend
                showlegend=True,  # Show legend
                legend=dict(
                    orientation="h",  # Horizontal orientation
                    x=0.5,  # Center horizontally
                    y=-0.2,  # Position below the chart
                    xanchor='center',  # Horizontal center alignment
                    yanchor='top'  # Vertical top alignment
                )
            )

            # Update x and y axes titles
            fig.update_xaxes(title_text="Steps")
            fig.update_yaxes(title_text="Value")

            # Display the empty chart
            st.plotly_chart(fig, use_container_width=True)
            return

        data = result_files_contents["data"]

        # Transpose data to get columns
        transposed_data = list(zip(*data))

        # Convert 'step' column to integers for plotting
        step_index = headers.index("step")
        steps = list(map(int, transposed_data[step_index]))

        # Create a single subplot figure
        fig = make_subplots(
            rows=1, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
        )

        # Initialize min and max values for y-axis range
        y_min = float('inf')
        y_max = float('-inf')

        # Add a plot for each column (excluding 'step')
        for header in headers:
            if header == "step":
                continue

            # Get the column data and filter out empty strings
            column_index = headers.index(header)
            filtered_data = [(step, float(val)) for step, val in zip(
                steps, transposed_data[column_index]) if val != '']

            # Separate steps and values
            if filtered_data:
                filtered_steps, column_data = zip(*filtered_data)

                # Update min and max values for y-axis range
                y_min = min(y_min, min(column_data))
                y_max = max(y_max, max(column_data))

                # Add the trace
                fig.add_trace(
                    go.Scatter(x=filtered_steps, y=column_data,
                               mode='lines+markers', name=custom_names.get(header, header))
                )

        # Add vertical lines for checkpoint metrics if they exist
        checkpoint_metrics = self._fine_tuning_job_metrics.get(
            "checkpoint_metrics", [])
        for checkpoint in checkpoint_metrics:
            step = checkpoint.get('step', None)
            if step is not None:
                hover_text = f"Step: {step}<br>"
                if 'train_loss' in checkpoint:
                    hover_text += f"Training Loss: {
                        checkpoint['train_loss']}<br>"
                if 'train_mean_token_accuracy' in checkpoint:
                    hover_text += f"Training Mean Token Accuracy: {
                        checkpoint['train_mean_token_accuracy']}<br>"
                if 'valid_loss' in checkpoint:
                    hover_text += f"Validation Loss: {
                        checkpoint['valid_loss']}<br>"
                if 'valid_mean_token_accuracy' in checkpoint:
                    hover_text += f"Validation Mean Token Accuracy: {
                        checkpoint['valid_mean_token_accuracy']}<br>"

                fig.add_trace(go.Scatter(
                    x=[step, step],
                    y=[y_min, y_max],
                    mode="lines",
                    line=dict(color="rgba(91, 172, 120, 1)",
                              width=2, dash="dash"),
                    hoverinfo="text",
                    text=hover_text,
                    name=f"Checkpoint {step}"
                ))

        # Customize layout
        fig.update_layout(
            title={
                'text': "Fine Tuning Job Metrics",
                'x': 0.5,
                'xanchor': 'center'
            },
            height=400,  # Adjust height to accommodate the legend
            showlegend=True,  # Show legend
            legend=dict(
                orientation="h",  # Horizontal orientation
                x=0.5,  # Center horizontally
                y=-0.2,  # Position below the chart
                xanchor='center',  # Horizontal center alignment
                yanchor='top'  # Vertical top alignment
            )
        )

        # Update x and y axes titles
        fig.update_xaxes(title_text="Steps")
        fig.update_yaxes(title_text="Value")

        # Display the combined chart in Streamlit
        st.plotly_chart(fig, use_container_width=True)

    def create_confusion_matrix(self):
        evaluation_types = self._evaluation_types

        # Extract ground_truth and predicted_label from evaluation_types
        ground_truth_labels = [
            et["ground_truth"].value for et in evaluation_types]
        predicted_labels = [
            et["predicted_label"].value for et in evaluation_types]

        # Count the occurrences of each predicted label type for display purposes
        predicted_counts = Counter(predicted_labels)
        total_count = len(evaluation_types)

        # Generate confusion matrix
        labels = [et.name for et in EvaluationType]
        cm = confusion_matrix(ground_truth_labels,
                              predicted_labels, labels=labels)

        # Display confusion matrix
        fig = px.imshow(cm, text_auto=True, x=labels, y=labels,
                        color_continuous_scale='Blues',
                        labels=dict(x="Predicted Label",
                                    y="True Label", color="Count"),
                        )

        fig.update_layout(
            title={
                'text': "Confusion Matrix",
                'x': 0.5,
                'xanchor': 'center'
            },
            height=400,
            # Adjust bottom margin for space
            margin=dict(l=20, r=20, t=60, b=60),
            coloraxis_colorbar=dict(
                title="Count",
                thicknessmode="pixels",
                thickness=10,
                lenmode="fraction",
                len=0.7,
                yanchor="top",
                y=1,
                xanchor="right",
                x=1.05
            ),
            legend=dict(
                x=0.5,
                y=-0.2,  # Adjust y position to move the legend closer
                xanchor='center',
                orientation='h'  # Horizontal legend
            )
        )

        st.plotly_chart(fig, use_container_width=True)

        # Create a custom legend for the evaluation types
        labels = [et.name for et in EvaluationType]
        # Adding one for the total count
        custom_legend_columns = st.columns(len(labels) + 1)
        for i, label in enumerate(labels):
            count_value = predicted_counts.get(label, 0)
            with custom_legend_columns[i]:
                st.markdown(f"{label}: {count_value}")

        # Add total count in the last column
        with custom_legend_columns[-1]:
            st.markdown(f"Total: {total_count}")

    def calculate_metrics(self):
        ground_truth_labels = [
            eval['ground_truth'].name for eval in self._evaluation_types]
        predicted_labels = [
            eval['predicted_label'].name for eval in self._evaluation_types]

        # Calculate Precision, Recall, F1 Score, and Accuracy
        precision = precision_score(
            ground_truth_labels, predicted_labels, average='weighted', labels=["TP", "TN", "FP", "FN"])
        recall = recall_score(ground_truth_labels, predicted_labels,
                              average='weighted', labels=["TP", "TN", "FP", "FN"])
        f1 = f1_score(ground_truth_labels, predicted_labels,
                      average='weighted', labels=["TP", "TN", "FP", "FN"])
        accuracy = accuracy_score(ground_truth_labels, predicted_labels)

        # Create a confusion matrix
        labels = ["TP", "TN", "FP", "FN"]
        cm = confusion_matrix(ground_truth_labels,
                              predicted_labels, labels=labels)

        # Add a small constant to avoid zero elements - TODO: Read this up and mention it in the bachelor work.
        cm_with_constant = cm + 1e-6
        # Perform Chi-Square test using Monte Carlo simulation due to the likelyhood of zero values in the confusion matrix
        chi2, p, dof, ex = chi2_contingency(cm_with_constant)

        return {
            "precision": precision,
            "recall": recall,
            "f1_score": f1,
            "accuracy": accuracy,
            "chi2": chi2,
            "p_value": p,
            "degrees_of_freedom": dof,
            "expected_frequencies": ex
        }

    def display_metrics(self):
        metrics: dict[str, Any] = self.calculate_metrics()

        # Analysis based on metric values
        self.display_analysis(metrics)

    def display_analysis(self, metrics):

        interpretations = {
            "precision": {
                "high": f"**Precision Analysis: ({metrics['precision']:.2f})**\nHigh precision indicates that most of the predicted positive instances are correct.",
                "moderate": f"**Precision Analysis: ({metrics['precision']:.2f})**\nModerate precision indicates a reasonable number of correct positive predictions, but there is room for improvement.",
                "low": f"**Precision Analysis: ({metrics['precision']:.2f})**\nLow precision indicates a high number of false positives, suggesting that the model needs improvement."
            },
            "recall": {
                "high": f"**Recall Analysis: ({metrics['recall']:.2f})**\nHigh recall indicates that most of the actual positive instances are correctly identified.",
                "moderate": f"**Recall Analysis: ({metrics['recall']:.2f})**\nModerate recall indicates that the model is missing a significant number of positive instances.",
                "low": f"**Recall Analysis: ({metrics['recall']:.2f})**\nLow recall indicates that the model is missing most of the positive instances, which is concerning."
            },
            "f1_score": {
                "high": f"**F1 Score Analysis: ({metrics['f1_score']:.2f})**\nHigh F1 score indicates a good balance between precision and recall.",
                "moderate": f"**F1 Score Analysis: ({metrics['f1_score']:.2f})**\nModerate F1 score indicates a trade-off between precision and recall.",
                "low": f"**F1 Score Analysis: ({metrics['f1_score']:.2f})**\nLow F1 score indicates poor performance in both precision and recall."
            },
            "accuracy": {
                "high": f"**Accuracy Analysis: ({metrics['accuracy']:.2f})**\nHigh accuracy indicates that the model performs well on both positive and negative instances.",
                "moderate": f"**Accuracy Analysis: ({metrics['accuracy']:.2f})**\nModerate accuracy indicates that the model has a reasonable performance but still has a significant error rate.",
                "low": f"**Accuracy Analysis: ({metrics['accuracy']:.2f})**\nLow accuracy indicates poor performance, and the model needs substantial improvements."
            },
            "chi2": {
                "high": f"**Chi-Square Analysis: ({metrics['chi2']:.2f})**\nA high chi-square value indicates a significant discrepancy between the observed and expected frequencies, suggesting a strong association between the variables. This means the model's predictions differ significantly from what would be expected by chance, indicating a meaningful pattern or relationship.",
                "moderate": f"**Chi-Square Analysis: ({metrics['chi2']:.2f})**\nA moderate chi-square value suggests a reasonable association between the observed and expected frequencies. There is some discrepancy, but it may not be strong enough to indicate a highly significant pattern.",
                "low": f"**Chi-Square Analysis: ({metrics['chi2']:.2f})**\nA low chi-square value indicates that the observed frequencies are close to the expected frequencies, suggesting a weaker association between the variables. This means the model's predictions align more closely with what would be expected by chance."
            },
            "p_value": {
                "high": f"**P-Value Analysis: ({metrics['p_value']:.2f})**\nThe p-value is greater than 0.05, suggesting that there is no statistically significant relationship between the observed and expected frequencies. This implies that the differences are likely due to random variation.",
                "low": f"**P-Value Analysis: ({metrics['p_value']:.2f})**\nThe p-value is less than or equal to 0.05, suggesting a statistically significant relationship between the observed and expected frequencies. This indicates that the differences are unlikely to be due to random variation and there is a significant association."
            },
            "degrees_of_freedom": {
                "interpretation": f"**Degrees of Freedom Analysis: ({metrics['degrees_of_freedom']})**\nThe degrees of freedom for the chi-square test indicates the number of independent values in the calculation."
            },
            "expected_frequencies": {
                "interpretation": f"**Expected Frequencies Analysis: ({metrics['expected_frequencies']})**\nThe expected frequencies matrix shows the expected counts under the null hypothesis (no association). Comparing these with the observed frequencies can provide insights into specific areas where the model's predictions diverge from expectations."
            }
        }

        def get_interpretation(metric, value):
            if metric in ["precision", "recall", "f1_score", "accuracy"]:
                if value > 0.8:
                    return interpretations[metric]["high"]
                elif value > 0.5:
                    return interpretations[metric]["moderate"]
                else:
                    return interpretations[metric]["low"]
            elif metric == "p_value":
                if value > 0.05:
                    return interpretations[metric]["high"]
                else:
                    return interpretations[metric]["low"]
            elif metric == "chi2":
                if value > 10:
                    return interpretations[metric]["high"]
                elif value > 5:
                    return interpretations[metric]["moderate"]
                else:
                    return interpretations[metric]["low"]
            else:
                return interpretations[metric]["interpretation"]

        with st.expander(label="Analysis", expanded=False):
            # Display interpretations
            for metric, value in metrics.items():
                st.code(get_interpretation(metric, value))
