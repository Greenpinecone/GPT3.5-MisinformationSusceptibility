"""
This module contains functions for evaluating the performance of the fine-tuned model.
It includes implementations for metrics like confusion matrix, F1 score, Chi-Square test and comparing different models.

Classes:
    ModelEvaluator: Statistically evaluates and compares models performances.
"""


import re
import streamlit as st
import numpy as np
import colorsys
import plotly.graph_objs as go
import plotly.express as px
from typing import Any, Counter
from sklearn.metrics import precision_score, recall_score, f1_score, accuracy_score, confusion_matrix
from scipy.stats import chi2_contingency
from plotly.subplots import make_subplots
from decimal import Decimal, getcontext
from sklearn.metrics import balanced_accuracy_score, confusion_matrix, matthews_corrcoef
from app.frontend.classes.dataframe_widget_provider import DataFrameWidgetProvider
from app.backend.database.schema import EvaluationType
from app.backend.dtos.get_request import GetDataPointEvaluationsDTO, GetModelEvalautionsDTO, GetModelsDTO
from app.backend.dtos.response import ComplexModelDTO, ModelDTO
from app.backend.service.implementations.service_manager_facade import ServiceManagerFacade


class ModelMetricsEvaluator:
    """
    Provides functionalities to evaluate the performance of the fine-tuned language model,
    including calculating metrics like confusion matrix, F1 score, Chi-Square test, and comparing different models.

    Attributes:
        _service (ServiceManagerFacade): Service manager facade for handling service operations.
        _model (ComplexModelDTO): The model being evaluated.
        _helpfulness_score_data (list[tuple]): Helpfulness score data for model evaluations.
        _honesty_score_data (list[tuple]): Honesty score data for model evaluations.
        _harmlessness_score_data (list[tuple]): Harmlessness score data for model evaluations.
        _model_evaluation_scemantic_similarity_score_data (list[tuple]): Semantic similarity score data for model evaluations.
        _evaluation_types (list[EvaluationType]): Types of evaluations.
        _total_model_evaluations_count (int): Total count of model evaluations.
        _coherence_score_data (list[tuple]): Coherence score data for datapoint evaluations.
        _relevance_score_data (list[tuple]): Relevance score data for datapoint evaluations.
        _datapoints_semantic_similarity_score_data (list[tuple]): Semantic similarity score data for datapoint evaluations.
        _total_datapoint_evaluations_count (int): Total count of datapoint evaluations.
        _fine_tuning_job_metrics (dict[str, Any]): Metrics from the fine-tuning job.
    """

    def __init__(self, service: ServiceManagerFacade, model_id: int):
        self._service: ServiceManagerFacade = service
        self._model: ComplexModelDTO = service.get_model_by_id(model_id)[0]
        self.expand_all: bool = True

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
        # TODO: Can be removed

    def generate_model_evalaution_statistic(self):
        self._service.calculate_model_evaluation_scores(
            GetDataPointEvaluationsDTO(model_id=self._model.id))
        # TODO: Can be removed

    def set_expand_all_button(self):
        self.expand_all = not self.expand_all

    def get_fine_tuning_job_metrics(self):
        """
        Retrieves the metrics from the fine-tuning job.

        Returns:
            dict[str, Any]: Fine-tuning job metrics.
        """

        return self._fine_tuning_job_metrics

    def get_model(self):
        """
        Retrieves the model being evaluated.

        Returns:
            ComplexModelDTO: The model being evaluated.
        """
        return self._model

    def lighten_color(self, rgba_color: str, amount: float = 0.3):
        """
        Lightens the given RGBA color by a specified amount.

        Args:
            rgba_color (str): The original RGBA color.
            amount (float): The amount to lighten the color.

        Returns:
            str: The lightened RGBA color.
        """

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
        with st.expander("Model Evaluation Metrics", self.expand_all):
            """
            Creates and displays a combined evaluation chart for model evaluations.
            """

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

            self.create_combined_evaluation_chart(
                data, labels, colors, self._total_model_evaluations_count, "")

    def create_datapoint_evaluation_chart(self):
        """
        Creates and displays a combined evaluation chart for datapoint evaluations.
        """
        with st.expander("Datapoint Evaluation Metrics", self.expand_all):
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

            self.create_combined_evaluation_chart(
                data, labels, colors, self._total_datapoint_evaluations_count, "")

    def create_combined_evaluation_chart(self, data, labels, colors, total_count, chart_title=""):
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
            # title={
            #     'text': chart_title,
            #     'x': 0.5,
            #     'xanchor': 'center'
            # },
            height=390,
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
        with st.expander("Fine Tuning Job Metrics", self.expand_all):
            """
            Creates and displays charts for fine-tuning job metrics.
            """

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
                    # title={
                    #     'text': "Fine Tuning Job Metrics",
                    #     'x': 0.5,
                    #     'xanchor': 'center'
                    # },
                    height=390,  # Adjust height to accommodate the legend
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
                # title={
                #     'text': "Fine Tuning Job Metrics",
                #     'x': 0.5,
                #     'xanchor': 'center'
                # },
                height=390,  # Adjust height to accommodate the legend
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
        with st.expander("Confusion Matrix", self.expand_all):
            """
            Creates and displays a confusion matrix based on the evaluation types.
            """

            evaluation_types = self._evaluation_types

            # Extract ground_truth and predicted_label from evaluation_types as strings
            ground_truth_labels = [
                et["ground_truth"].value for et in evaluation_types]
            predicted_labels = [
                et["predicted_label"].value for et in evaluation_types]

            # Count the occurrences of each predicted label type for display purposes
            predicted_counts = Counter(predicted_labels)
            total_count = len(evaluation_types)

            # Generate confusion matrix
            labels = EvaluationType.values()
            cm = confusion_matrix(ground_truth_labels,
                                  predicted_labels, labels=labels)

            # Display confusion matrix
            fig = px.imshow(cm, text_auto=True, x=labels, y=labels,
                            color_continuous_scale='Blues',
                            labels=dict(x="Predicted Label", y="True Label", color="Count"))

            fig.update_layout(
                # title={'text': "Confusion Matrix",
                #        'x': 0.5, 'xanchor': 'center'},
                height=390,
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
                    y=-0.2,
                    xanchor='center',
                    orientation='h'
                )
            )

            st.plotly_chart(fig, use_container_width=True)

            # Create a custom legend for the evaluation types
            custom_legend_columns = st.columns(len(labels) + 1)
            for i, label in enumerate(labels):
                count_value = predicted_counts.get(label, 0)
                with custom_legend_columns[i]:
                    st.markdown(f"{label}: {count_value}")

            # Add total count in the last column
            with custom_legend_columns[-1]:
                st.markdown(f"Total: {total_count}")

    def calculate_metrics(self) -> dict:
        """
        Calculates various evaluation metrics for the model.

        Returns:
            dict: Dictionary containing calculated metrics.
        """

        ground_truth_labels: list[str] = [
            eval['ground_truth'].value for eval in self._evaluation_types]
        predicted_labels: list[str] = [
            eval['predicted_label'].value for eval in self._evaluation_types]

        # Filter out pairs where either ground truth or predicted label is missing
        filtered_pairs = [(gt, pred) for gt, pred in zip(
            ground_truth_labels, predicted_labels) if gt is not None and pred is not None]

        # Minimum sample size for stable metrics calculation (39 would be better)
        min_samples_for_metrics = 15

        # Check if data is sufficient
        if len(filtered_pairs) < min_samples_for_metrics or len(predicted_labels) < min_samples_for_metrics:
            # If there is too little data, set all metrics to None
            accuracy = precision = recall = f1 = specificity = fpr = balanced_acc = mcc = chi2 = p = dof = expected_freq = None
        else:
            # Calculate metrics
            accuracy: float = accuracy_score(
                ground_truth_labels, predicted_labels)
            precision: float = precision_score(
                ground_truth_labels, predicted_labels, pos_label='T')
            recall: float = recall_score(
                ground_truth_labels, predicted_labels, pos_label='T')
            f1: float = f1_score(ground_truth_labels,
                                 predicted_labels, pos_label='T')
            specificity: float = recall_score(
                ground_truth_labels, predicted_labels, pos_label='F')
            fpr: float = 1 - specificity
            balanced_acc: float = balanced_accuracy_score(
                ground_truth_labels, predicted_labels)
            mcc: float = matthews_corrcoef(
                ground_truth_labels, predicted_labels)

            # Create a confusion matrix
            labels: list[str] = EvaluationType.values()
            cm: np.ndarray = confusion_matrix(
                ground_truth_labels, predicted_labels, labels=labels)

            # MINIMUM REQUIREMENT Chi2Test: You can safely use the chi-square test with critical values from the chi-square distribution when no more than 20% of the expected counts are less than 5 and all individual expected counts are 1 or greater. In particular, all four expected counts in a 2 × 2 table should be 5 or greater.
            # Calculate chi-square and expected frequencies

            """ 
                        Observed Frequencies:
                            Predicted Positive  Predicted Negative
            Actual Positive          40                10
            Actual Negative          5                 45

            Expected Frequencies:
                            Predicted Positive  Predicted Negative
            Actual Positive          22.5              27.5
            Actual Negative          22.5              27.5
            
            """
            chi2, p, dof, expected_freq = chi2_contingency(cm + 1e-6)

            # Conditions for valid chi-square test
            total_cells = expected_freq.size
            cells_less_than_5 = np.sum(expected_freq < 5)
            cells_greater_than_1 = np.all(expected_freq >= 1)
            valid_2x2 = cm.shape == (2, 2)

            if valid_2x2:
                valid_chi_square = np.all(expected_freq >= 5)
            else:
                valid_chi_square = (
                    cells_less_than_5 / total_cells <= 0.2) and cells_greater_than_1

            if not valid_chi_square:
                chi2 = p = dof = expected_freq = None

        return {
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "f1_score": f1,
            "specificity": specificity,
            "fpr": fpr,
            "balanced_accuracy": balanced_acc,
            "mcc": mcc,
            "chi2": chi2,
            "p_value": p,
            "degrees_of_freedom": dof,
            "expected_frequencies": expected_freq,
            "amount_of_valid_pairs": filtered_pairs
        }

    def display_metrics(self):
        """
        Calculates and displays the metrics and their analysis.
        """

        metrics: dict[str, Any] = self.calculate_metrics()
        self.display_analysis(metrics)

    def display_analysis(self, metrics: dict[str, Any]) -> None:
        """
        Displays the analysis of metrics with interpretations.

        Args:
            metrics (dict[str, Any]): Dictionary containing calculated metrics.
        """

        def format_metric(metric, precision=3, default_value="N/A"):
            """
            Formats a metric to a specified precision. Returns a default value if the metric is None.

            Args:
            - metric (float or None): The metric to format.
            - precision (int): The number of decimal places to format the metric to.
            - default_value (str): The value to return if the metric is None.

            Returns:
            - str: The formatted metric or the default value if the metric is None.
            """
            return f"{metric:.{precision}f}" if metric is not None else default_value

        interpretations: dict[str, dict[str, str]] = {
            "precision": {
                "description": "Precision measures how many of the predicted 'Truth' instances were correct.",
                "high": f"**Precision Analysis: ({format_metric(metrics['precision'])})**\nHigh precision indicates that most of the predicted positive instances are correct.",
                "moderate": f"**Precision Analysis: ({format_metric(metrics['precision'])})**\nModerate precision indicates a reasonable number of correct positive predictions, but there is room for improvement.",
                "low": f"**Precision Analysis: ({format_metric(metrics['precision'])})**\nLow precision indicates a high number of false positives, suggesting that the model needs improvement."
            },
            "recall": {
                "description": "Recall (Sensitivity) measures how many of the actual 'Truth' instances were correctly predicted.",
                "high": f"**Recall Analysis: ({format_metric(metrics['recall'])})**\nHigh recall indicates that most of the actual positive instances are correctly identified.",
                "moderate": f"**Recall Analysis: ({format_metric(metrics['recall'])})**\nModerate recall indicates that the model is missing a significant number of positive instances.",
                "low": f"**Recall Analysis: ({format_metric(metrics['recall'])})**\nLow recall indicates that the model is missing most of the positive instances, which is concerning."
            },
            "f1_score": {
                "description": "F1 Score provides a single metric that balances precision and recall.",
                "high": f"**F1 Score Analysis: ({format_metric(metrics['f1_score'])})**\nHigh F1 score indicates a good balance between precision and recall.",
                "moderate": f"**F1 Score Analysis: ({format_metric(metrics['f1_score'])})**\nModerate F1 score indicates a trade-off between precision and recall.",
                "low": f"**F1 Score Analysis: ({format_metric(metrics['f1_score'])})**\nLow F1 score indicates poor performance in both precision and recall."
            },
            "accuracy": {
                "description": "Accuracy measures the proportion of correctly identified instances (both 'Truth' and 'Falsehood').",
                "high": f"**Accuracy Analysis: ({format_metric(metrics['accuracy'])})**\nHigh accuracy indicates that the model performs well on both positive and negative instances.",
                "moderate": f"**Accuracy Analysis: ({format_metric(metrics['accuracy'])})**\nModerate accuracy indicates that the model has a reasonable performance but still has a significant error rate.",
                "low": f"**Accuracy Analysis: ({format_metric(metrics['accuracy'])})**\nLow accuracy indicates poor performance, and the model needs substantial improvements."
            },
            "specificity": {
                "description": "Specificity (True Negative Rate) measures how many of the actual 'Falsehood' instances were correctly predicted.",
                "high": f"**Specificity Analysis: ({format_metric(metrics['specificity'])})**\nHigh specificity indicates that most of the actual negative instances are correctly identified.",
                "moderate": f"**Specificity Analysis: ({format_metric(metrics['specificity'])})**\nModerate specificity indicates that the model misses some negative instances, leading to false positives.",
                "low": f"**Specificity Analysis: ({format_metric(metrics['specificity'])})**\nLow specificity indicates poor performance in identifying negative instances, leading to many false positives."
            },
            "fpr": {
                "description": "False Positive Rate (FPR) measures the proportion of 'Falsehood' instances incorrectly classified as 'Truth'.",
                "high": f"**False Positive Rate Analysis: ({format_metric(metrics['fpr'])})**\nHigh FPR indicates a large number of false positives, meaning the model often incorrectly identifies negative instances as positive.",
                "moderate": f"**False Positive Rate Analysis: ({format_metric(metrics['fpr'])})**\nModerate FPR indicates a balance but still some false positives, which need attention.",
                "low": f"**False Positive Rate Analysis: ({format_metric(metrics['fpr'])})**\nLow FPR indicates the model rarely makes false positive errors."
            },
            "balanced_accuracy": {
                "description": "Balanced Accuracy gives a better indication of performance across both 'Truth' and 'Falsehood' classes, especially if your dataset is imbalanced.",
                "high": f"**Balanced Accuracy Analysis: ({format_metric(metrics['balanced_accuracy'])})**\nHigh balanced accuracy indicates good performance across both positive and negative instances.",
                "moderate": f"**Balanced Accuracy Analysis: ({format_metric(metrics['balanced_accuracy'])})**\nModerate balanced accuracy suggests the model performs reasonably well but has significant room for improvement.",
                "low": f"**Balanced Accuracy Analysis: ({format_metric(metrics['balanced_accuracy'])})**\nLow balanced accuracy indicates poor performance across both classes, suggesting substantial improvements are needed."
            },
            "mcc": {
                "description": "Matthews Correlation Coefficient (MCC) provides a more nuanced measure that considers all elements of the confusion matrix.",
                "high": f"**MCC Analysis: ({format_metric(metrics['mcc'])})**\nHigh MCC indicates strong correlation between the observed and predicted labels.",
                "moderate": f"**MCC Analysis: ({format_metric(metrics['mcc'])})**\nModerate MCC suggests some correlation but room for improvement.",
                "low": f"**MCC Analysis: ({format_metric(metrics['mcc'])})**\nLow MCC indicates weak correlation, suggesting the model's predictions are not reliable."
            },
            "chi2": {
                "description": "Chi-Square measures the discrepancy between observed and expected frequencies.",
                "high": f"**Chi-Square Analysis: ({format_metric(metrics['chi2'])})**\nA high chi-square value indicates a significant discrepancy between the observed and expected frequencies, suggesting a strong association between the variables. This means the model's predictions differ significantly from what would be expected by chance, indicating a meaningful pattern or relationship.",
                "moderate": f"**Chi-Square Analysis: ({format_metric(metrics['chi2'])})**\nA moderate chi-square value suggests a reasonable association between the observed and expected frequencies. There is some discrepancy, but it may not be strong enough to indicate a highly significant pattern.",
                "low": f"**Chi-Square Analysis: ({format_metric(metrics['chi2'])})**\nA low chi-square value indicates that the observed frequencies are close to the expected frequencies, suggesting a weaker association between the variables. This means the model's predictions align more closely with what would be expected by chance."
            },
            "p_value": {
                "description": "P-Value indicates the statistical significance of the observed frequencies.",
                "high": f"**P-Value Analysis: ({format_metric(metrics['p_value'])})**\nThe p-value is greater than 0.05, suggesting that there is no statistically significant relationship between the observed and expected frequencies. This implies that the differences are likely due to random variation.",
                "low": f"**P-Value Analysis: ({format_metric(metrics['p_value'])})**\nThe p-value is less than or equal to 0.05, suggesting a statistically significant relationship between the observed and expected frequencies. This indicates that the differences are unlikely to be due to random variation and there is a significant association."
            },
            "degrees_of_freedom": {
                "description": "Degrees of Freedom indicates the number of independent values in the calculation.",
                "interpretation": f"**Degrees of Freedom Analysis: ({metrics['degrees_of_freedom']})**\nThe degrees of freedom for the chi-square test indicates the number of independent values in the calculation."
            },
            "expected_frequencies": {
                "description": "Expected Frequencies matrix shows the expected counts under the null hypothesis (no association).",
                "interpretation": f"**Expected Frequencies Analysis: ({metrics['expected_frequencies']})**\nThe expected frequencies matrix shows the expected counts under the null hypothesis (no association). Comparing these with the observed frequencies can provide insights into specific areas where the model's predictions diverge from expectations."
            }
        }

        def get_interpretation(metric: str, value: float | None) -> str:
            if value is None:
                return "Value could not be calculated or interpreted due too little available data."

            if metric in ["precision", "recall", "f1_score", "accuracy", "specificity", "fpr", "balanced_accuracy", "mcc"]:
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

        with st.expander(label="Statistical Analysis", expanded=False):
            # Display metric descriptions
            descriptions = [interpretation.get(
                'description', '') for interpretation in interpretations.values()]

            st.write(f"""{len(metrics["amount_of_valid_pairs"])
                          } valid labelled pairs (ground truth and evaluation label set) have been considered""")
            # Display interpretations
            for i, (metric, value) in enumerate(metrics.items()):
                if metric == "amount_of_valid_pairs":
                    continue
                st.caption(descriptions[i])
                st.code(f"{get_interpretation(metric, value)}")

    @classmethod
    def show_current_fine_tuning_event_progress(cls, events: list[object]):
        """
        Shows the current progress of fine-tuning events.

        Args:
            events (list[object]): List of fine-tuning events.
        """

        # Filter out events with no data
        events_with_data = [event for event in events if event.model_extra.get(
            'data') and event.model_extra.get('data').get('step')]

        if not events_with_data:
            st.write("No data available for the fine-tuning job events.")
            return

        # Extract metrics from events
        steps = []
        train_losses = []
        valid_losses = []
        train_accuracies = []
        valid_accuracies = []
        total_steps = events_with_data[0].data['total_steps']

        for event in events_with_data:
            data = event.model_extra.get('data')
            steps.append(data['step'])
            train_losses.append(data.get('train_loss'))
            valid_losses.append(data.get('valid_loss'))
            train_accuracies.append(data.get('train_mean_token_accuracy'))
            valid_accuracies.append(data.get('valid_mean_token_accuracy'))

        # TODO: Fetch trainings job validation file to check if validation is available and adjust graph accoringly
        # Determine if validation data is available
        # validation_data_available = any(valid_losses) or any(valid_accuracies)

        # Create a single subplot figure
        fig = make_subplots(
            rows=1, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
        )

        # Add traces for each metric if available
        # if any(train_losses):
        fig.add_trace(
            go.Scatter(x=steps, y=train_losses,
                       mode='lines+markers', name='Training Loss')
        )

    # if any(valid_losses):
        fig.add_trace(
            go.Scatter(x=steps, y=valid_losses,
                       mode='lines+markers', name='Validation Loss')
        )

    # if any(train_accuracies):
        fig.add_trace(
            go.Scatter(x=steps, y=train_accuracies,
                       mode='lines+markers', name='Valid Mean Training Accuracy')
        )

    # if any(valid_accuracies):
        fig.add_trace(
            go.Scatter(x=steps, y=valid_accuracies,
                       mode='lines+markers', name='Valid Mean Validation Accuracy')
        )

        # Customize layout
        fig.update_layout(
            title={
                'text': "Fine Tuning Job Metrics",
                'x': 0.5,
                'xanchor': 'center'
            },
            height=425,  # Adjust height to accommodate the legend
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

        # Create a DataFrame to display the event data in tabular form
        data = {
            'Step': steps,
            'Training Loss': train_losses,
            'Validation Loss': valid_losses,
            'Valid Mean Training Accuracy': train_accuracies,
            'Valid Mean Validation Accuracy': valid_accuracies
        }

        DataFrameWidgetProvider.general_dataframe(data)
