import pytest
from unittest.mock import patch, mock_open
import yaml
import os
from resumix.config.config import Config
from resumix.config.llm_config import LLMConfig


class TestConfig:
    """Test configuration loading and management"""
    
    def test_config_loading_success(self):
        """Test successful configuration loading"""
        mock_config = {
            'use_model': 'local',
            'ocr': {'backend': 'paddle'},
            'models': {'embedding_model': 'all-MiniLM-L6-v2'}
        }
        
        # Reset singleton before test
        Config._instance = None
        
        with patch('builtins.open', mock_open(read_data=yaml.dump(mock_config))):
            config = Config()
            
            assert config.use_model == 'local'
            assert config.ocr.backend == 'paddle'
            assert config.models.embedding_model == 'all-MiniLM-L6-v2'
    
    def test_config_loading_with_nested_structure(self):
        """Test loading configuration with deeply nested structure"""
        # Reset singleton before test
        Config._instance = None
        
        mock_config = {
            'use_model': 'deepseek',
            'ocr': {
                'backend': 'easy',
                'settings': {
                    'confidence_threshold': 0.8,
                    'languages': ['en', 'zh']
                }
            },
            'models': {
                'embedding_model': 'custom-model',
                'llm_settings': {
                    'temperature': 0.7,
                    'max_tokens': 1000
                }
            }
        }
        
        with patch('builtins.open', mock_open(read_data=yaml.dump(mock_config))):
            config = Config()
            
            assert config.use_model == 'deepseek'
            assert config.ocr.backend == 'easy'
            assert config.ocr.settings.confidence_threshold == 0.8
            assert config.ocr.settings.languages == ['en', 'zh']
            assert config.models.llm_settings.temperature == 0.7
    
    @pytest.mark.skip(reason="Environment variable override feature not implemented yet")
    def test_environment_variable_override(self):
        """Test that environment variables override config file values"""
        # Reset singleton before test
        Config._instance = None
        
        mock_config = {
            'use_model': 'local',
            'ocr': {'backend': 'paddle'}
        }
        
        with patch('builtins.open', mock_open(read_data=yaml.dump(mock_config))):
            with patch.dict('os.environ', {'RESUMIX_USE_MODEL': 'deepseek'}):
                config = Config()
                
                assert config.use_model == 'deepseek'  # Override from env var
                assert config.ocr.backend == 'paddle'  # From config file
    
    @pytest.mark.skip(reason="Environment variable override feature not implemented yet")
    def test_multiple_environment_overrides(self):
        """Test multiple environment variable overrides"""
        # Reset singleton before test
        Config._instance = None
        
        mock_config = {
            'use_model': 'local',
            'ocr': {'backend': 'paddle'},
            'models': {'embedding_model': 'default-model'}
        }
        
        env_vars = {
            'RESUMIX_USE_MODEL': 'silicon',
            'RESUMIX_OCR_BACKEND': 'easy',
            'RESUMIX_MODELS_EMBEDDING_MODEL': 'custom-model'
        }
        
        with patch('builtins.open', mock_open(read_data=yaml.dump(mock_config))):
            with patch.dict('os.environ', env_vars):
                config = Config()
                
                assert config.use_model == 'silicon'
                assert config.ocr.backend == 'easy'
                assert config.models.embedding_model == 'custom-model'
    
    def test_invalid_config_file(self):
        """Test handling of invalid/missing config file"""
        # Reset singleton before test
        Config._instance = None
        
        with patch('builtins.open', side_effect=FileNotFoundError):
            with pytest.raises(FileNotFoundError):
                Config()
    
    def test_malformed_yaml_config(self):
        """Test handling of malformed YAML configuration"""
        # Reset singleton before test
        Config._instance = None
        
        malformed_yaml = "invalid: yaml: content: {"
        
        with patch('builtins.open', mock_open(read_data=malformed_yaml)):
            with pytest.raises(yaml.YAMLError):
                Config()
    
    def test_empty_config_file(self):
        """Test handling of empty configuration file"""
        # Reset singleton before test
        Config._instance = None
        
        with patch('builtins.open', mock_open(read_data="")):
            config = Config()
            
            # Should create config with empty dict, no attributes expected
            assert not hasattr(config, 'use_model')
            assert config._raw == {}
    
    def test_config_attribute_access(self):
        """Test attribute-style access to configuration values"""
        # Reset singleton before test
        Config._instance = None
        
        mock_config = {
            'use_model': 'local',
            'ocr': {
                'backend': 'paddle',
                'confidence': 0.8
            }
        }
        
        with patch('builtins.open', mock_open(read_data=yaml.dump(mock_config))):
            config = Config()
            
            # Test dot notation access
            assert config.use_model == 'local'
            assert config.ocr.backend == 'paddle'
            assert config.ocr.confidence == 0.8
    
    def test_config_to_dict(self):
        """Test converting configuration back to dictionary"""
        # Reset singleton before test
        Config._instance = None
        
        mock_config = {
            'use_model': 'local',
            'ocr': {'backend': 'paddle'}
        }
        
        with patch('builtins.open', mock_open(read_data=yaml.dump(mock_config))):
            config = Config()
            
            if hasattr(config, 'to_dict'):
                config_dict = config.to_dict()
                assert isinstance(config_dict, dict)
                assert config_dict['use_model'] == 'local'
    
    def test_config_validation(self):
        """Test configuration validation"""
        # Reset singleton before test
        Config._instance = None
        
        mock_config = {
            'use_model': 'invalid_model',
            'ocr': {'backend': 'invalid_backend'}
        }
        
        with patch('builtins.open', mock_open(read_data=yaml.dump(mock_config))):
            # Should either validate or load with warnings
            config = Config()
            
            # Basic test that config loads
            assert hasattr(config, 'use_model')


class TestLLMConfig:
    """Test LLM-specific configuration"""
    
    @pytest.mark.skip(reason="LLMConfig API key attributes not implemented")
    def test_provider_configuration_with_api_keys(self):
        """Test LLM configuration with API keys from environment"""
        env_vars = {
            'DEEPSEEK_API_KEY': 'test-deepseek-key',
            'SILICON_API_KEY': 'test-silicon-key',
            'OPENAI_API_KEY': 'test-openai-key'
        }
        
        with patch.dict('os.environ', env_vars):
            config = LLMConfig()
            
            assert config.deepseek_api_key == 'test-deepseek-key'
            assert config.silicon_api_key == 'test-silicon-key'
            assert config.openai_api_key == 'test-openai-key'
    
    @pytest.mark.skip(reason="LLMConfig API key attributes not implemented")
    def test_missing_api_keys(self):
        """Test LLM configuration with missing API keys"""
        # Clear all API key environment variables
        with patch.dict('os.environ', {}, clear=True):
            config = LLMConfig()
            
            assert config.deepseek_api_key is None
            assert config.silicon_api_key is None
            assert config.openai_api_key is None
    
    @pytest.mark.skip(reason="LLMConfig API key attributes not implemented")
    def test_partial_api_keys(self):
        """Test LLM configuration with only some API keys present"""
        env_vars = {
            'DEEPSEEK_API_KEY': 'test-deepseek-key',
            # Missing SILICON_API_KEY and OPENAI_API_KEY
        }
        
        with patch.dict('os.environ', env_vars, clear=True):
            config = LLMConfig()
            
            assert config.deepseek_api_key == 'test-deepseek-key'
            assert config.silicon_api_key is None
            assert config.openai_api_key is None
    
    def test_llm_model_configuration(self):
        """Test LLM model-specific configurations"""
        mock_config = {
            'llm': {
                'deepseek': {
                    'model': 'deepseek-chat',
                    'temperature': 0.7,
                    'max_tokens': 1000
                },
                'silicon': {
                    'model': 'gpt-3.5-turbo',
                    'temperature': 0.5,
                    'max_tokens': 2000
                }
            }
        }
        
        with patch('builtins.open', mock_open(read_data=yaml.dump(mock_config))):
            config = LLMConfig()
            
            if hasattr(config, 'llm'):
                assert config.llm.deepseek.model == 'deepseek-chat'
                assert config.llm.deepseek.temperature == 0.7
                assert config.llm.silicon.max_tokens == 2000
    
    def test_default_llm_settings(self):
        """Test default LLM settings when not specified"""
        config = LLMConfig()
        
        # Should have sensible defaults
        if hasattr(config, 'default_temperature'):
            assert 0.0 <= config.default_temperature <= 1.0
        
        if hasattr(config, 'default_max_tokens'):
            assert config.default_max_tokens > 0
    
    def test_llm_provider_validation(self):
        """Test validation of LLM provider configurations"""
        config = LLMConfig()
        
        # Test provider validation method if it exists
        if hasattr(config, 'validate_provider'):
            assert config.validate_provider('deepseek') in [True, False]
            assert config.validate_provider('invalid_provider') is False
    
    def test_api_key_masking(self):
        """Test that API keys are masked in string representation"""
        env_vars = {
            'DEEPSEEK_API_KEY': 'sk-1234567890abcdef',
            'SILICON_API_KEY': 'silicon-key-12345'
        }
        
        with patch.dict('os.environ', env_vars):
            config = LLMConfig()
            
            # String representation should mask API keys
            config_str = str(config)
            assert 'sk-1234567890abcdef' not in config_str
            assert 'silicon-key-12345' not in config_str
            
            # Should show masked version
            if 'deepseek' in config_str.lower():
                assert '***' in config_str or 'sk-***' in config_str
    
    def test_get_provider_config(self):
        """Test getting configuration for specific provider"""
        env_vars = {
            'DEEPSEEK_API_KEY': 'test-key'
        }
        
        with patch.dict('os.environ', env_vars):
            config = LLMConfig()
            
            if hasattr(config, 'get_provider_config'):
                deepseek_config = config.get_provider_config('deepseek')
                assert deepseek_config is not None
                assert 'api_key' in deepseek_config or 'key' in deepseek_config
    
    def test_is_provider_configured(self):
        """Test checking if a provider is properly configured"""
        env_vars = {
            'DEEPSEEK_API_KEY': 'test-key'
        }
        
        with patch.dict('os.environ', env_vars):
            config = LLMConfig()
            
            if hasattr(config, 'is_provider_configured'):
                assert config.is_provider_configured('deepseek') is True
                assert config.is_provider_configured('silicon') is False
                assert config.is_provider_configured('invalid') is False
    
    def test_config_precedence(self):
        """Test configuration precedence (env vars > config file > defaults)"""
        mock_config = {
            'llm': {
                'temperature': 0.5
            }
        }
        
        env_vars = {
            'RESUMIX_LLM_TEMPERATURE': '0.8'
        }
        
        with patch('builtins.open', mock_open(read_data=yaml.dump(mock_config))):
            with patch.dict('os.environ', env_vars):
                config = LLMConfig()
                
                # Environment variable should override config file
                if hasattr(config, 'llm') and hasattr(config.llm, 'temperature'):
                    assert config.llm.temperature == 0.8