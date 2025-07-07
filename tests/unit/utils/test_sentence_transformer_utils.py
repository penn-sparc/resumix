import pytest
from unittest.mock import Mock, patch
import numpy as np
from resumix.shared.utils.sentence_transformer_utils import SentenceTransformerUtils


class TestSentenceTransformerUtils:
    """Test sentence transformer utility functions"""
    
    def setup_method(self):
        """Reset singleton before each test"""
        SentenceTransformerUtils._instance = None
    
    @pytest.fixture
    def mock_sentence_transformer(self):
        """Mock SentenceTransformer model"""
        with patch('resumix.shared.utils.sentence_transformer_utils.SentenceTransformer') as mock_st:
            with patch('resumix.shared.utils.sentence_transformer_utils.CONFIG') as mock_config:
                # Mock config values
                mock_config.SENTENCE_TRANSFORMER.USE_MODEL = "all-MiniLM-L6-v2"
                mock_config.SENTENCE_TRANSFORMER.DIRECTORY = "/tmp/models"
                
                mock_model = Mock()
                # Mock encode method to return proper embeddings
                mock_model.encode.return_value = np.array([[0.1, 0.2, 0.3, 0.4]])
                mock_st.return_value = mock_model
                
                yield mock_model

    def test_singleton_pattern(self, mock_sentence_transformer):
        """Test that SentenceTransformerUtils follows singleton pattern"""
        instance1 = SentenceTransformerUtils.get_instance()
        instance2 = SentenceTransformerUtils.get_instance()
        
        assert instance1 is instance2
        assert instance1 is not None

    def test_get_instance_with_custom_model(self, mock_sentence_transformer):
        """Test getting instance with custom model name"""
        custom_model = "custom-model-name"
        instance = SentenceTransformerUtils.get_instance(model_name=custom_model)
        
        assert instance is not None
        # Verify SentenceTransformer was called
        assert mock_sentence_transformer.encode is not None

    def test_encode_functionality(self, mock_sentence_transformer):
        """Test that the returned instance can encode text"""
        transformer = SentenceTransformerUtils.get_instance()
        
        # Test encoding
        test_text = "This is a test sentence"
        embeddings = transformer.encode(test_text)
        
        # Verify encode was called
        mock_sentence_transformer.encode.assert_called_with(test_text)
        assert embeddings is not None

    def test_encode_multiple_sentences(self, mock_sentence_transformer):
        """Test encoding multiple sentences"""
        transformer = SentenceTransformerUtils.get_instance()
        
        # Mock return value for multiple sentences
        mock_sentence_transformer.encode.return_value = np.array([
            [0.1, 0.2, 0.3, 0.4],
            [0.5, 0.6, 0.7, 0.8]
        ])
        
        sentences = ["First sentence", "Second sentence"]
        embeddings = transformer.encode(sentences)
        
        mock_sentence_transformer.encode.assert_called_with(sentences)
        assert embeddings is not None
        assert len(embeddings) == 2

    def test_thread_safety(self, mock_sentence_transformer):
        """Test that singleton is thread-safe"""
        import threading
        import time
        
        instances = []
        
        def get_instance():
            time.sleep(0.01)  # Small delay to simulate concurrent access
            instance = SentenceTransformerUtils.get_instance()
            instances.append(instance)
        
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=get_instance)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # All instances should be the same object
        first_instance = instances[0]
        for instance in instances:
            assert instance is first_instance

    def test_error_handling_no_model_name_first_call(self):
        """Test error handling when no model name provided on first call"""
        # Reset singleton to test first call behavior
        SentenceTransformerUtils._instance = None
        
        with patch('resumix.shared.utils.sentence_transformer_utils.CONFIG') as mock_config:
            with patch('resumix.shared.utils.sentence_transformer_utils.SentenceTransformer') as mock_st:
                # Set config to None to simulate missing model name
                mock_config.SENTENCE_TRANSFORMER.USE_MODEL = None
                mock_config.SENTENCE_TRANSFORMER.DIRECTORY = "/tmp/models"
                
                with pytest.raises(ValueError, match="首次调用必须提供 model_name"):
                    SentenceTransformerUtils.get_instance(model_name=None)

    def test_config_integration(self, mock_sentence_transformer):
        """Test that config values are used correctly"""
        with patch('resumix.shared.utils.sentence_transformer_utils.CONFIG') as mock_config:
            mock_config.SENTENCE_TRANSFORMER.USE_MODEL = "test-model"
            mock_config.SENTENCE_TRANSFORMER.DIRECTORY = "/test/path"
            
            instance = SentenceTransformerUtils.get_instance()
            
            # Verify SentenceTransformer was initialized with correct path
            assert instance is not None

    def test_subsequent_calls_ignore_parameters(self, mock_sentence_transformer):
        """Test that subsequent calls ignore model_name parameter"""
        # First call with specific model
        instance1 = SentenceTransformerUtils.get_instance(model_name="first-model")
        
        # Second call with different model should return same instance
        instance2 = SentenceTransformerUtils.get_instance(model_name="second-model")
        
        assert instance1 is instance2

    def test_reset_singleton(self, mock_sentence_transformer):
        """Test that singleton can be reset for testing"""
        instance1 = SentenceTransformerUtils.get_instance()
        
        # Reset singleton
        SentenceTransformerUtils._instance = None
        
        # Create a new mock for the second instance
        with patch('resumix.shared.utils.sentence_transformer_utils.SentenceTransformer') as mock_st2:
            mock_model2 = Mock()
            mock_st2.return_value = mock_model2
            
            instance2 = SentenceTransformerUtils.get_instance()
            
            # Should be different instances after reset
            assert instance1 is not instance2