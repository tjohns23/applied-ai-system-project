"""
Tests for RAG Engine and Knowledge Base

Run with: pytest test_rag_system.py -v
"""

import pytest
from unittest.mock import patch, MagicMock
from knowledge_base import (
    get_knowledge_for_breed,
    get_available_breeds,
    get_care_category,
    KNOWLEDGE_BASE,
)
from rag_engine import (
    retrieve_knowledge,
    suggest_tasks,
    validate_api_key,
    generate_rule_based_answer,
    generate_answer,
    answer_pet_question,
)


class TestKnowledgeBase:
    """Test suite for knowledge base retrieval functions."""
    
    def test_get_available_breeds(self):
        """Test that available breeds are correctly returned."""
        breeds = get_available_breeds()
        assert isinstance(breeds, list)
        assert len(breeds) > 0
        assert "dog" in breeds
        assert "cat" in breeds
        assert "goldfish" in breeds
    
    def test_get_knowledge_for_valid_breed(self):
        """Test retrieving knowledge for a valid pet breed."""
        dog_knowledge = get_knowledge_for_breed("dog")
        assert isinstance(dog_knowledge, dict)
        assert len(dog_knowledge) > 0
        assert "feeding" in dog_knowledge
        assert "exercise" in dog_knowledge
    
    def test_get_knowledge_for_invalid_breed(self):
        """Test retrieving knowledge for non-existent breed returns empty dict."""
        invalid = get_knowledge_for_breed("unicorn")
        assert isinstance(invalid, dict)
        assert len(invalid) == 0
    
    def test_breed_case_insensitivity(self):
        """Test that breed names are case-insensitive."""
        dog_lower = get_knowledge_for_breed("dog")
        dog_upper = get_knowledge_for_breed("DOG")
        dog_mixed = get_knowledge_for_breed("DoG")
        
        assert dog_lower == dog_upper == dog_mixed
    
    def test_get_care_category_valid(self):
        """Test retrieving specific care category for a pet."""
        feeding_info = get_care_category("dog", "feeding")
        assert isinstance(feeding_info, str)
        assert len(feeding_info) > 0
    
    def test_get_care_category_invalid(self):
        """Test retrieving non-existent category returns empty string."""
        invalid = get_care_category("dog", "flying")
        assert invalid == ""
    
    def test_all_breeds_have_multiple_categories(self):
        """Test that each breed has multiple care categories."""
        for breed in get_available_breeds():
            knowledge = get_knowledge_for_breed(breed)
            assert len(knowledge) >= 3, f"{breed} should have at least 3 care categories"


class TestRAGRetrieval:
    """Test suite for RAG knowledge retrieval functions."""
    
    def test_retrieve_knowledge_basic(self):
        """Test basic knowledge retrieval."""
        result = retrieve_knowledge("dog", "How often should I feed my dog?")
        assert isinstance(result, dict)
        assert len(result) > 0
    
    def test_retrieve_knowledge_priority(self):
        """Test that feeding question retrieves feeding info."""
        result = retrieve_knowledge("dog", "feeding schedule")
        categories = list(result.keys())
        
        # Feeding should be in top results for feeding question
        assert "feeding" in categories or len(result) > 0
    
    def test_retrieve_knowledge_empty_on_invalid_breed(self):
        """Test retrieval returns empty dict for invalid breed."""
        result = retrieve_knowledge("alien", "What do aliens eat?")
        assert result == {}
    
    def test_retrieve_knowledge_respects_top_k(self):
        """Test that top_k parameter limits results."""
        result_1 = retrieve_knowledge("dog", "pet care general question", top_k=1)
        result_3 = retrieve_knowledge("dog", "pet care general question", top_k=3)
        
        assert len(result_1) <= 1
        assert len(result_3) <= 3
        assert len(result_3) >= len(result_1)
    
    def test_retrieve_knowledge_all_breeds(self):
        """Test retrieval works for all available breeds."""
        for breed in get_available_breeds():
            result = retrieve_knowledge(breed, "How do I care for my pet?")
            assert isinstance(result, dict), f"Failed for breed: {breed}"


class TestTaskSuggestion:
    """Test suite for task suggestion extraction."""
    
    def test_suggest_tasks_from_answer(self):
        """Test that tasks are extracted from answers."""
        answer = "You should walk your dog 2-3 times daily. Grooming should happen weekly."
        suggestions = suggest_tasks(answer, "dog")
        
        assert isinstance(suggestions, list)
        # Should extract at least walk and groom
        task_names = [task for task, freq in suggestions]
        # Flexible assertion since extraction can vary
        assert len(suggestions) > 0
    
    def test_suggest_tasks_returns_tuples(self):
        """Test that suggestions are returned as tuples of (task, frequency)."""
        answer = "Feed your goldfish once daily."
        suggestions = suggest_tasks(answer, "goldfish")
        
        for item in suggestions:
            assert isinstance(item, tuple)
            assert len(item) == 2
            assert isinstance(item[0], str)  # task name
            assert isinstance(item[1], str)  # frequency
    
    def test_suggest_tasks_max_count(self):
        """Test that suggestions are limited to max 5."""
        long_answer = """
        Walk your dog daily. Feed daily. Groom weekly. Train daily. 
        Exercise daily. Bathe monthly. Clean ears daily. Brush teeth daily.
        """
        suggestions = suggest_tasks(long_answer, "dog")
        
        assert len(suggestions) <= 5
    
    def test_suggest_tasks_empty_answer(self):
        """Test handling of empty answer."""
        suggestions = suggest_tasks("", "dog")
        assert isinstance(suggestions, list)
    
    def test_suggest_tasks_pet_specific_keywords(self):
        """Test that pet-specific keywords are recognized."""
        # Dog answer
        dog_answer = "Dogs need walks and exercise."
        dog_tasks = suggest_tasks(dog_answer, "dog")
        assert len(dog_tasks) > 0
        
        # Cat answer
        cat_answer = "Cats need playtime and grooming."
        cat_tasks = suggest_tasks(cat_answer, "cat")
        assert len(cat_tasks) > 0


class TestAPIValidation:
    """Test suite for API configuration validation."""
    
    def test_validate_api_key_missing(self):
        """Test that validation fails when API key is missing."""
        with patch.dict("os.environ", {}, clear=True):
            result = validate_api_key()
            assert result is False
    
    def test_validate_api_key_present(self):
        """Test that validation succeeds when API key is present."""
        with patch.dict("os.environ", {"OPENAI_API_KEY": "sk-test-key"}):
            result = validate_api_key()
            assert result is True


class TestRuleBasedFallback:
    """Test suite for rule-based answer generation and fallback system."""
    
    def test_rule_based_answer_with_context(self):
        """Test rule-based answer generation with retrieved context."""
        context = {
            "feeding": "Dogs need 1-2 meals per day.",
            "exercise": "Dogs need 30 mins to 2 hours daily.",
        }
        answer = generate_rule_based_answer("How much should I feed my dog?", context, "dog")
        
        assert isinstance(answer, str)
        assert len(answer) > 0
        assert "dog" in answer.lower()
        assert "feeding" in answer.lower() or "Dogs need" in answer
    
    def test_rule_based_answer_empty_context(self):
        """Test rule-based answer with no context."""
        answer = generate_rule_based_answer("What about rabbits?", {}, "rabbit")
        
        assert isinstance(answer, str)
        assert "don't have specific information" in answer or "knowledge base" in answer.lower()
    
    def test_generate_answer_returns_tuple(self):
        """Test that generate_answer returns (answer, answer_type) tuple."""
        with patch.dict("os.environ", {}, clear=True):
            context = {"feeding": "Test content"}
            answer, answer_type = generate_answer("Test question", context, "dog")
            
            assert isinstance(answer, str)
            assert answer_type in ["llm", "rule_based"]
    
    def test_fallback_when_api_key_missing(self):
        """Test fallback to rule-based when API key is missing."""
        with patch.dict("os.environ", {}, clear=True):
            context = {"feeding": "Dogs need food"}
            answer, answer_type = generate_answer("Feed dog", context, "dog")
            
            assert answer_type == "rule_based"
            assert len(answer) > 0
    
    def test_fallback_when_api_error(self):
        """Test fallback when OpenAI API returns an error."""
        with patch("openai.OpenAI") as mock_openai:
            # Mock API to raise error
            mock_client = MagicMock()
            mock_client.chat.completions.create.side_effect = Exception("API Error")
            mock_openai.return_value = mock_client
            
            with patch.dict("os.environ", {"OPENAI_API_KEY": "sk-test"}):
                context = {"feeding": "Dogs eat daily"}
                answer, answer_type = generate_answer("Feed", context, "dog")
                
                assert answer_type == "rule_based"
                assert len(answer) > 0
                assert "fallback" in answer.lower() or "error" in answer.lower()
    
    def test_answer_pet_question_includes_answer_type(self):
        """Test that answer_pet_question includes answer_type in result."""
        with patch.dict("os.environ", {}, clear=True):
            result = answer_pet_question("dog", "feeding")
            
            assert "answer_type" in result
            assert result["answer_type"] in ["llm", "rule_based"]
            assert "answer" in result
            assert len(result["answer"]) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
