from sentence_transformers import SentenceTransformer, models, util, SimilarityFunction
from app.backend.dtos.create_request import CreateDataPointDTO, CreateDataPointEvaluationDTO
from app.backend.dtos.response import DataPointDTO, DataPointEvaluationDTO
import torch

""" GENERAL INFO - https://www.sbert.net/

1. If a Sentence Transformer instance ends with a Normalize module, then it is sensible to choose the “dot” metric instead of “cosine”.

    Dot product on normalized embeddings is equivalent to cosine similarity, but “cosine” will re-normalize the embeddings again. As a result, the “dot” metric will be faster than “cosine”.

2. Encode sentences to vector embeddings:

    # The sentences to encode
    sentences = [
        "The weather is lovely today.",
        "It's so sunny outside!",
        "He drove to the stadium.",
    ]

    # Calculate embeddings by calling model.encode()
    embeddings = model.encode(sentences)
    print(embeddings.shape)
    # [3, 384]

3. Calculate sentence embedding similarities:
    similarities = model.similarity(embeddings, embeddings)
    print(similarities)
    # tensor([[ -0.0000, -12.6269, -20.2167],
    #         [-12.6269,  -0.0000, -20.1288],
    #         [-20.2167, -20.1288,  -0.0000]])

    -> SentenceTransformer.similarity: Calculates the similarity between all pairs of embeddings.

    -> SentenceTransformer.pairwise_similarity: Calculates the similarity between embeddings in a pairwise fashion.

4. Some models require specific prompt templates: https://sbert.net/examples/applications/computing-embeddings/README.html

5. How to get and set the models max input sequence length and why smaller inputs are faster: Also look here: https://stackoverflow.com/questions/75901231/max-seq-length-for-transformer-sentence-bert

    For transformer models like BERT, RoBERTa, DistilBERT etc., the runtime and memory requirement grows quadratic with the input length. This limits transformers to inputs of certain lengths. A common value for BERT-based models are 512 tokens, which corresponds to about 300-400 words (for English).

    Each model has a maximum sequence length under model.max_seq_length, which is the maximal number of tokens that can be processed. Longer texts will be truncated to the first model.max_seq_length tokens:

    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer("all-MiniLM-L6-v2")
    print("Max Sequence Length:", model.max_seq_length)
    # => Max Sequence Length: 256

    # Change the length to 200
    model.max_seq_length = 200

    print("Max Sequence Length:", model.max_seq_length)
    # => Max Sequence Length: 200

6. Cross Encoders COULD be used for small datasets to achieve higher semantic similarity accuracy.

7. Pooling Methods - models use default pooling methods if non specified:

    pooling_mode – Either “cls”, “lasttoken”, “max”, “mean”, “mean_sqrt_len_tokens”, or “weightedmean”. If set, overwrites the other pooling_mode_* settings

    pooling_mode_cls_token – Use the first token (CLS token) as text representations

    pooling_mode_max_tokens – Use max in each dimension over all tokens.

    pooling_mode_mean_tokens – Perform mean-pooling

    pooling_mode_mean_sqrt_len_tokens – Perform mean-pooling, but divide by sqrt(input_length).

    pooling_mode_weightedmean_tokens – Perform (position) weighted mean pooling. See SGPT: GPT Sentence Embeddings for Semantic Search.

    pooling_mode_lasttoken –

    Perform last token pooling. See SGPT: GPT Sentence Embeddings for Semantic Search and Text and Code Embeddings by Contrastive Pre-Training.
    
8. Available vector similarity functions:
    
    # SimilarityFunction.COSINE (a.k.a “cosine”): Cosine Similarity (default)
    # SimilarityFunction.DOT_PRODUCT (a.k.a “dot”): Dot Product
    # SimilarityFunction.EUCLIDEAN (a.k.a “euclidean”): Negative Euclidean Distance
    # SimilarityFunction.MANHATTAN (a.k.a. “manhattan”): Negative Manhattan Distance
    
"""

# TODO: Add support for manhattan, dot, euclidean similarity calculations


class SemanticSimilarityCalculator:

    def __init__(self):
        pass

    # TODO: Also pass CreateDataPOintEvaluations, add semantic similarity score, save them afterwards. Eventually implement some optimization method beyond truncation to increase the semantic similarity score accuracy (1. such as sliding windows with stride and overlapping sequences 2. Splitting long texts into sentences or at commas -> but might not be ideal since EDA removes special characters like dots and commas.)

    @staticmethod
    def initialize_model(semantic_similarity_model: dict):
        # The model automatically uses its max_seq_length if not changed and truncates the rest.
        # Only models with cosine similarity calculation are allowed at the moment to correctly scale the value to 0-100.
        # Pooling is automatically set to the models preffered pooling mode.
        model = SentenceTransformer(
            semantic_similarity_model["model_name"], similarity_fn_name=SimilarityFunction.COSINE)
        return model

    @classmethod
    def calculate_datapoints_semantic_similarity_score(cls,
                                                       datapoints: list[CreateDataPointDTO],
                                                       augmented_datapoints: list[CreateDataPointDTO], datapoint_evaluations: list[CreateDataPointEvaluationDTO],
                                                       semantic_similarity_model: dict
                                                       ) -> tuple[list[CreateDataPointDTO], list[CreateDataPointEvaluationDTO]]:

        model: SentenceTransformer = cls.initialize_model(
            semantic_similarity_model)

        # Create a dictionary for efficient lookup of original datapoints
        original_datapoints_dict: dict[int, DataPointDTO] = {
            dp.id: dp for dp in datapoints}

        for augmented_dp, evaluation_dto in zip(augmented_datapoints, datapoint_evaluations):
            original_dp = original_datapoints_dict.get(
                augmented_dp.initial_datapoint_id)

            if not original_dp:
                raise ValueError(
                    "An augmented datapoint references an original datapoint that does not exist in the passed datapoints list.")

            # Extract messages from both original and augmented datapoints
            original_messages = original_dp.messages['messages']
            augmented_messages = augmented_dp.messages['messages']

            similarities = []

            for original_message, augmented_message in zip(original_messages, augmented_messages):
                original_content = original_message['content']
                augmented_content = augmented_message['content']

                # Compute embeddings using the model
                # Uses numpy arrays by default
                original_embedding = model.encode(
                    original_content)
                augmented_embedding = model.encode(
                    augmented_content)

                # Calculate cosine similarity
                # Uses PyTorch or NumPy depending on if a tensor or numpy array is passed. PyTorch could theoretically be used to laverage CPU AND GPU.
                similarity = model.similarity(
                    original_embedding, augmented_embedding)
                similarities.append(similarity.item())

            # Calculate average similarity and convert to float
            avg_similarity = torch.tensor(similarities).mean().item()
            # Scale from -1 to 1 to 0 to 100
            scaled_similarity = (avg_similarity + 1) * 50
            # Assign similarity score to datapoint evaluation dto
            evaluation_dto.semantic_similarity_score = scaled_similarity

        return augmented_datapoints, datapoint_evaluations
