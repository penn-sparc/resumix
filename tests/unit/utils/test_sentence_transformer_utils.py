import pytest
from unittest.mock import Mock, patch
import numpy as np
from resumix.utils.sentence_transformer_utils import SentenceTransformerUtils


class TestSentenceTransformerUtils:
    """Test sentence transformer utility functions"""
    
    @pytest.fixture
    def mock_sentence_transformer(self):
        """Mock SentenceTransformer model"""
        with patch('resumix.utils.sentence_transformer_utils.SentenceTransformer') as mock_st:
            with patch('resumix.utils.sentence_transformer_utils.CONFIG') as mock_config:
                # Mock config values
                mock_config.SENTENCE_TRANSFORMER.USE_MODEL = "all-MiniLM-L6-v2"
                mock_config.SENTENCE_TRANSFORMER.DIRECTORY = "/tmp/models"
                
                mock_model = Mock()
                # Mock embeddings dynamically based on input length
                def mock_encode(sentences):
                    if isinstance(sentences, str):
                        sentences = [sentences]
                    n_sentences = len(sentences)
                    return np.random.rand(n_sentences, 4)  # Return embeddings matching input size
                
                mock_model.encode.side_effect = mock_encode
                mock_st.return_value = mock_model
                yield mock_model
    
    def test_initialization(self, mock_sentence_transformer):
        """Test SentenceTransformerUtils initialization"""
        utils = SentenceTransformerUtils()
        
        assert utils.model is not None
        # Should use default model name
        assert hasattr(utils, 'model_name')
    
    def test_initialization_with_custom_model(self, mock_sentence_transformer):
        """Test initialization with custom model name"""
        custom_model = "custom-model-name"
        utils = SentenceTransformerUtils(model_name=custom_model)
        
        assert utils.model_name == custom_model
    
    def test_get_embeddings_single_sentence(self, mock_sentence_transformer):
        """Test getting embeddings for a single sentence"""
        utils = SentenceTransformerUtils()
        
        sentence = "This is a test sentence"
        embeddings = utils.get_embeddings([sentence])
        
        assert isinstance(embeddings, np.ndarray)
        assert embeddings.shape == (1, 4)  # 1 sentence, 4 dimensions
        mock_sentence_transformer.encode.assert_called_once_with([sentence])
    
    def test_get_embeddings_multiple_sentences(self, mock_sentence_transformer):
        """Test getting embeddings for multiple sentences"""
        utils = SentenceTransformerUtils()
        
        sentences = ["First sentence", "Second sentence"]
        embeddings = utils.get_embeddings(sentences)
        
        assert isinstance(embeddings, np.ndarray)
        assert embeddings.shape == (2, 4)  # 2 sentences, 4 dimensions
        mock_sentence_transformer.encode.assert_called_once_with(sentences)
    
    def test_get_embeddings_empty_list(self, mock_sentence_transformer):
        """Test getting embeddings for empty sentence list"""
        mock_sentence_transformer.encode.return_value = np.array([])
        utils = SentenceTransformerUtils()
        
        embeddings = utils.get_embeddings([])
        
        assert isinstance(embeddings, np.ndarray)
        assert embeddings.size == 0
    
    def test_calculate_similarity_basic(self, mock_sentence_transformer):
        """Test basic similarity calculation between two sentences"""
        utils = SentenceTransformerUtils()
        
        with patch('resumix.utils.sentence_transformer_utils.cosine_similarity') as mock_cosine:
            mock_cosine.return_value = np.array([[0.85]])
            
            similarity = utils.calculate_similarity("text1", "text2")
            
            assert similarity == 0.85
            mock_cosine.assert_called_once()
            
            # Verify encode was called once with both texts (more efficient)
            assert mock_sentence_transformer.encode.call_count == 1
    
    def test_calculate_similarity_identical_texts(self, mock_sentence_transformer):
        """Test similarity calculation for identical texts"""
        utils = SentenceTransformerUtils()
        
        with patch('resumix.utils.sentence_transformer_utils.cosine_similarity') as mock_cosine:
            mock_cosine.return_value = np.array([[1.0]])
            
            similarity = utils.calculate_similarity("same text", "same text")
            
            assert similarity == 1.0
    
    def test_calculate_similarity_completely_different(self, mock_sentence_transformer):
        """Test similarity calculation for completely different texts"""
        utils = SentenceTransformerUtils()
        
        with patch('resumix.utils.sentence_transformer_utils.cosine_similarity') as mock_cosine:
            mock_cosine.return_value = np.array([[0.0]])
            
            similarity = utils.calculate_similarity("text1", "completely different")
            
            assert similarity == 0.0
    
    def test_calculate_batch_similarities(self, mock_sentence_transformer):
        """Test calculating similarities between multiple sentence pairs"""
        utils = SentenceTransformerUtils()
        
        sentences1 = ["First sentence", "Second sentence"]
        sentences2 = ["Third sentence", "Fourth sentence"]
        
        with patch('resumix.utils.sentence_transformer_utils.cosine_similarity') as mock_cosine:
            mock_cosine.return_value = np.array([
                [0.8, 0.3],
                [0.2, 0.9]
            ])
            
            similarities = utils.calculate_batch_similarities(sentences1, sentences2)
            
            assert isinstance(similarities, np.ndarray)
            assert similarities.shape == (2, 2)
            assert similarities[0, 0] == 0.8
            assert similarities[1, 1] == 0.9
    
    def test_find_most_similar(self, mock_sentence_transformer):
        """Test finding most similar sentence from a list"""
        utils = SentenceTransformerUtils()
        
        query = "Python programming"
        candidates = [
            "Java development",
            "Python software engineering", 
            "JavaScript coding",
            "Python programming language"
        ]
        
        with patch('resumix.utils.sentence_transformer_utils.cosine_similarity') as mock_cosine:
            # Mock similarities: highest for Python programming language
            mock_cosine.return_value = np.array([[0.3, 0.7, 0.2, 0.95]])
            
            most_similar_idx, similarity_score = utils.find_most_similar(query, candidates)
            
            assert most_similar_idx == 3  # "Python programming language"
            assert similarity_score == 0.95
    
    def test_find_most_similar_empty_candidates(self, mock_sentence_transformer):
        """Test finding most similar with empty candidates list"""
        utils = SentenceTransformerUtils()
        
        query = "Test query"
        candidates = []
        
        result = utils.find_most_similar(query, candidates)
        
        assert result == (None, 0.0)
    
    def test_normalize_embeddings(self, mock_sentence_transformer):
        """Test embedding normalization"""
        # Create non-normalized embeddings
        mock_sentence_transformer.encode.return_value = np.array([
            [3.0, 4.0, 0.0],  # Length = 5
            [1.0, 1.0, 1.0]   # Length = sqrt(3)
        ])
        
        utils = SentenceTransformerUtils()
        embeddings = utils.get_embeddings(["test1", "test2"])
        
        # Check if embeddings can be normalized
        norms = np.linalg.norm(embeddings, axis=1)
        assert len(norms) == 2
    
    def test_error_handling_invalid_model(self):
        """Test error handling for invalid model name"""
        with patch('resumix.utils.sentence_transformer_utils.SentenceTransformer') as mock_st:
            with patch('resumix.utils.sentence_transformer_utils.CONFIG') as mock_config:
                mock_config.SENTENCE_TRANSFORMER.USE_MODEL = "all-MiniLM-L6-v2"
                mock_config.SENTENCE_TRANSFORMER.DIRECTORY = "/tmp/models"
                mock_st.side_effect = Exception("Model not found")
                
                with pytest.raises(Exception, match="Model not found"):
                    SentenceTransformerUtils(model_name="invalid-model")
    
    def test_similarity_bounds(self, mock_sentence_transformer):
        """Test that similarity scores are within expected bounds"""
        utils = SentenceTransformerUtils()
        
        with patch('resumix.utils.sentence_transformer_utils.cosine_similarity') as mock_cosine:
            # Test boundary values
            test_cases = [
                (np.array([[1.0]]), 1.0),    # Maximum similarity
                (np.array([[0.0]]), 0.0),    # No similarity
                (np.array([[-1.0]]), -1.0),  # Opposite vectors
                (np.array([[0.5]]), 0.5)     # Moderate similarity
            ]
            
            for cosine_result, expected in test_cases:
                mock_cosine.return_value = cosine_result
                similarity = utils.calculate_similarity("text1", "text2")
                assert similarity == expected
                assert -1.0 <= similarity <= 1.0  # Cosine similarity bounds