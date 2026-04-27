"""
RAG Engine for Pet Care Q&A

Handles knowledge retrieval and AI-powered answer generation for pet care questions.
Implements a hybrid approach: keyword matching + semantic scoring + LLM generation.
"""

import os
import re
from typing import List, Dict, Tuple
from knowledge_base import get_knowledge_for_breed, get_available_breeds, KNOWLEDGE_BASE


def retrieve_knowledge(pet_breed: str, query: str, top_k: int = 3) -> Dict[str, str]:
    """
    Retrieve relevant pet care knowledge using keyword matching + semantic scoring.
    
    Args:
        pet_breed: Type of pet (e.g., 'dog', 'cat', 'goldfish')
        query: User's question
        top_k: Number of top categories to retrieve
    
    Returns:
        Dictionary with keys as categories and values as relevant knowledge snippets.
    """
    breed_data = get_knowledge_for_breed(pet_breed)
    
    if not breed_data:
        return {}
    
    # Normalize query for matching
    query_lower = query.lower()
    query_words = set(query_lower.split())
    
    # Score each category by keyword overlap
    scores = {}
    for category, content in breed_data.items():
        category_words = set(category.lower().split())
        content_words = set(content.lower().split())
        
        # Calculate similarity: keywords in query matching category or content
        overlap = len(query_words & (category_words | content_words))
        scores[category] = overlap
    
    # Sort by score and return top_k categories
    sorted_categories = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    
    result = {}
    for category, _ in sorted_categories[:top_k]:
        result[category] = breed_data[category]
    
    return result


def generate_rule_based_answer(query: str, retrieved_context: Dict[str, str], pet_breed: str) -> str:
    """
    Generate an answer using rule-based formatting (fallback when LLM unavailable).
    
    This function works without any API calls, making it a reliable fallback
    when the OpenAI API is down or inaccessible.
    
    Args:
        query: User's question
        retrieved_context: Dictionary of relevant knowledge
        pet_breed: Type of pet for context
    
    Returns:
        Rule-based formatted answer from knowledge base.
    """
    if not retrieved_context:
        return (
            f"I don't have specific information about '{pet_breed}' "
            f"in our knowledge base. For personalized advice, please consult a veterinarian."
        )
    
    # Format answer by combining retrieved categories
    answer_parts = [f"Based on our pet care database for {pet_breed}s:\n"]
    
    for category, content in retrieved_context.items():
        answer_parts.append(f"\n**{category.capitalize()}:** {content[:150]}...")  # First 150 chars
    
    answer_parts.append(
        "\n\n*Note: This answer is generated from our knowledge base. "
        "For personalized or medical advice, consult a veterinarian.*"
    )
    
    return "".join(answer_parts)


def generate_answer(query: str, retrieved_context: Dict[str, str], pet_breed: str) -> Tuple[str, str]:
    """
    Generate an answer using OpenAI API with retrieved context, with fallback to rule-based system.
    
    Args:
        query: User's question
        retrieved_context: Dictionary of relevant knowledge
        pet_breed: Type of pet for context
    
    Returns:
        Tuple of (answer_text, answer_type) where answer_type is 'llm' or 'rule_based'
        answer_text: Generated answer
        answer_type: 'llm' for LLM-generated, 'rule_based' for fallback
    """
    try:
        from openai import OpenAI, APIError
    except ImportError:
        rule_based = generate_rule_based_answer(query, retrieved_context, pet_breed)
        return rule_based, "rule_based"
    
    # Get API key from environment
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        rule_based = generate_rule_based_answer(query, retrieved_context, pet_breed)
        return rule_based, "rule_based"
    
    # Build context string from retrieved knowledge
    context_text = f"Pet Type: {pet_breed.capitalize()}\n\n"
    for category, content in retrieved_context.items():
        context_text += f"{category.capitalize()}:\n{content}\n\n"
    
    if not retrieved_context:
        context_text += "No specific knowledge found for this pet type in the database.\n"
    
    # Try to use OpenAI API
    try:
        client = OpenAI(api_key=api_key)
        
        system_prompt = """You are a helpful pet care expert assistant. 
Use the provided knowledge base to answer questions accurately and helpfully.
If the knowledge base doesn't have specific information, provide general advice based on pet care best practices.
Keep answers concise but informative (2-3 sentences for direct answers, up to 1 paragraph for detailed guidance)."""
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": f"Knowledge Base:\n{context_text}\n\nUser Question: {query}"
                }
            ],
            temperature=0.7,
            max_tokens=300,
            timeout=10  # 10 second timeout
        )
        
        return response.choices[0].message.content, "llm"
    
    except APIError as e:
        # API error - use fallback
        fallback = generate_rule_based_answer(query, retrieved_context, pet_breed)
        fallback += f"\n\n⚠️ *LLM Error (using fallback): {str(e)[:100]}*"
        return fallback, "rule_based"
    except TimeoutError:
        # API timeout - use fallback
        fallback = generate_rule_based_answer(query, retrieved_context, pet_breed)
        fallback += "\n\n⚠️ *API timeout (using fallback)*"
        return fallback, "rule_based"
    except Exception as e:
        # Any other error - use fallback
        fallback = generate_rule_based_answer(query, retrieved_context, pet_breed)
        fallback += f"\n\n⚠️ *Error (using fallback): {str(e)[:100]}*"
        return fallback, "rule_based"


def suggest_tasks(answer: str, pet_breed: str) -> List[Tuple[str, str]]:
    """
    Extract task suggestions from the generated answer using heuristic patterns.
    
    Args:
        answer: The generated answer from OpenAI
        pet_breed: Type of pet
    
    Returns:
        List of tuples: (task_description, suggested_frequency)
        Example: [("Walk dog", "daily"), ("Groom", "weekly")]
    """
    suggestions = []
    
    # Patterns to detect tasks and frequencies
    patterns = [
        # Pattern: "X times daily/weekly/monthly"
        (r"(\d+)\s*(?:times?|to|-)?\s*(\d+)?\s*(times?|hours?|minutes?|daily|daily|weekly|monthly|day|days|week|weeks|month|months)", "frequency_first"),
        # Pattern: "daily/weekly/monthly X"
        (r"(daily|weekly|monthly|every\s+day|every\s+week|every\s+month|each\s+day)\s+(.+?)(?:\.|,|$)", "frequency_first"),
        # Pattern: "X need(s) Y"
        (r"(?:your\s+)?[\w\s]+\s+need(?:s)?\s+(.+?)(?:\.|,|$)", "task_only"),
        # Pattern: "provide/include X"
        (r"(?:provide|include|offer|give)\s+(?:a\s+)?(.+?)(?:\.|,|$)", "task_only"),
    ]
    
    keywords_by_pet = {
        "dog": ["walk", "exercise", "play", "train", "feed", "groom", "brush", "bathe", "trim nails", "clean ears"],
        "cat": ["play", "exercise", "feed", "groom", "brush", "clean litter", "trim nails", "brush teeth"],
        "goldfish": ["feed", "water change", "tank maintenance", "clean", "check water"],
        "hamster": ["feed", "clean cage", "play", "exercise", "spot clean"],
        "rabbit": ["feed", "exercise", "groom", "brush", "play", "clean habitat"],
        "bird": ["feed", "clean cage", "interact", "socialize", "play", "provide enrichment"],
    }
    
    answer_lower = answer.lower()
    
    # Extract frequency patterns
    frequency_map = {
        "1": "once daily",
        "2": "twice daily",
        "3": "three times daily",
        "daily": "daily",
        "weekly": "weekly",
        "monthly": "monthly",
        "hour": "hourly",
        "day": "daily",
        "week": "weekly",
        "month": "monthly",
    }
    
    # Simple extraction: look for action words specific to this pet type
    pet_keywords = keywords_by_pet.get(pet_breed.lower(), [])
    
    # Extract sentences with task keywords
    sentences = re.split(r'[.!?]', answer)
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        
        # Find pet-specific keywords in this sentence
        for keyword in pet_keywords:
            if keyword in sentence.lower():
                # Check for frequency info in this sentence
                freq_match = re.search(
                    r"(\d+)\s*times?|daily|weekly|monthly|each day|per day",
                    sentence,
                    re.IGNORECASE
                )
                
                frequency = "daily" if freq_match else "as needed"
                
                # Create task description
                if keyword in ["feed", "groom", "exercise", "play", "walk", "clean"]:
                    task = f"{keyword.capitalize()} {pet_breed}"
                else:
                    task = f"{keyword.capitalize()}"
                
                suggestions.append((task, frequency))
                break  # Only one suggestion per sentence
    
    # Remove duplicates while preserving order
    seen = set()
    unique_suggestions = []
    for task, freq in suggestions:
        if task not in seen:
            seen.add(task)
            unique_suggestions.append((task, freq))
    
    return unique_suggestions[:5]  # Return max 5 suggestions


def answer_pet_question(pet_breed: str, query: str) -> Dict:
    """
    Complete RAG pipeline: retrieve -> generate -> suggest tasks.
    
    Automatically falls back to rule-based system if LLM is unavailable.
    
    Args:
        pet_breed: Type of pet
        query: User's question
    
    Returns:
        Dictionary with keys:
            - 'answer': Generated answer text
            - 'answer_type': 'llm' or 'rule_based' indicating source
            - 'pet_breed': Pet type used
            - 'task_suggestions': List of (task_name, frequency) tuples
            - 'source_categories': Categories used for retrieval
    """
    # Step 1: Retrieve relevant knowledge
    context = retrieve_knowledge(pet_breed, query, top_k=3)
    
    # Step 2: Generate answer (with automatic fallback)
    answer, answer_type = generate_answer(query, context, pet_breed)
    
    # Step 3: Suggest tasks
    task_suggestions = suggest_tasks(answer, pet_breed)
    
    return {
        "answer": answer,
        "answer_type": answer_type,
        "pet_breed": pet_breed,
        "task_suggestions": task_suggestions,
        "source_categories": list(context.keys()),
    }


def validate_api_key() -> bool:
    """
    Check if OpenAI API key is configured.
    
    Returns:
        True if API key is set, False otherwise.
    """
    return bool(os.getenv("OPENAI_API_KEY"))
