"""Unit tests for LLM cache utility."""
import pytest
from app.utils.llm_cache import LLMCache


class TestLLMCache:
    """Test cases for LLM cache."""

    def test_cache_initialization(self):
        """Test cache initializes with correct parameters."""
        cache = LLMCache(max_size=100, default_ttl=3600)
        assert cache.max_size == 100
        assert cache.default_ttl == 3600
        stats = cache.get_stats()
        assert stats["size"] == 0

    def test_cache_set_and_get(self):
        """Test basic cache set and get operations."""
        cache = LLMCache()
        key = cache.generate_key("test prompt", "gpt-4", 0.7, "test_agent")
        
        cache.set(key, "test response")
        result = cache.get(key)
        
        assert result == "test response"
        stats = cache.get_stats()
        assert stats["size"] == 1

    def test_cache_miss(self):
        """Test cache returns None on miss."""
        cache = LLMCache()
        result = cache.get("nonexistent_key")
        assert result is None

    def test_cache_statistics(self):
        """Test cache statistics tracking."""
        cache = LLMCache()
        key = cache.generate_key("test", "gpt-4", 0.7, "agent")
        
        # First access - miss
        cache.get(key)
        stats = cache.get_stats()
        assert stats["misses"] == 1
        assert stats["hits"] == 0
        
        # Set value
        cache.set(key, "response")
        
        # Second access - hit
        cache.get(key)
        stats = cache.get_stats()
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert stats["hit_rate"] == 50.0

    def test_cache_eviction(self):
        """Test cache evicts oldest entries when max size reached."""
        cache = LLMCache(max_size=2)
        
        key1 = cache.generate_key("prompt1", "gpt-4", 0.7, "agent")
        key2 = cache.generate_key("prompt2", "gpt-4", 0.7, "agent")
        key3 = cache.generate_key("prompt3", "gpt-4", 0.7, "agent")
        
        cache.set(key1, "response1")
        cache.set(key2, "response2")
        cache.set(key3, "response3")  # Should evict key1
        
        stats = cache.get_stats()
        assert stats["size"] == 2
        assert cache.get(key1) is None  # Evicted
        assert cache.get(key2) == "response2"
        assert cache.get(key3) == "response3"

    def test_key_generation_consistency(self):
        """Test that same inputs generate same key."""
        cache = LLMCache()
        
        key1 = cache.generate_key("prompt", "gpt-4", 0.7, "agent")
        key2 = cache.generate_key("prompt", "gpt-4", 0.7, "agent")
        
        assert key1 == key2

    def test_key_generation_uniqueness(self):
        """Test that different inputs generate different keys."""
        cache = LLMCache()
        
        key1 = cache.generate_key("prompt1", "gpt-4", 0.7, "agent")
        key2 = cache.generate_key("prompt2", "gpt-4", 0.7, "agent")
        key3 = cache.generate_key("prompt1", "gpt-3.5", 0.7, "agent")
        
        assert key1 != key2
        assert key1 != key3
        assert key2 != key3

    def test_cache_clear(self):
        """Test cache can be cleared."""
        cache = LLMCache()
        key = cache.generate_key("test", "gpt-4", 0.7, "agent")
        
        cache.set(key, "response")
        stats = cache.get_stats()
        assert stats["size"] == 1
        
        cache.clear()
        stats = cache.get_stats()
        assert stats["size"] == 0
        assert cache.get(key) is None

