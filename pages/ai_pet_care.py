"""
PawPal+ Pet Care Q&A Page

AI-powered pet care assistant using RAG. Users ask questions about pet care,
and the system retrieves knowledge from the knowledge base, generates answers
with OpenAI, and suggests related tasks to add to their schedule.
"""

import streamlit as st
from datetime import time
from rag_engine import (
    answer_pet_question,
    get_available_breeds,
    validate_api_key,
)
from pawpal_system import Task, Scheduler, Owner, Pet
from knowledge_base import get_available_breeds

st.set_page_config(page_title="Pet Care Q&A", page_icon="🤖", layout="wide")

st.title("🤖 Pet Care Q&A Assistant")
st.markdown(
    """
Ask questions about pet care and get answers powered by our knowledge base and AI.
Get personalized suggestions to add tasks to your schedule!
"""
)

# Check if API key is configured
if not validate_api_key():
    st.error(
        """
        ⚠️ **OpenAI API Key Not Configured**
        
        To use the Pet Care Q&A feature, you need to set up your OpenAI API key:
        1. Create a `.env` file in the project root (copy from `.env.example`)
        2. Add your OpenAI API key: `OPENAI_API_KEY=sk-...`
        3. Restart the Streamlit app
        
        Get a free API key at: https://platform.openai.com/api_keys
        """
    )
    st.stop()

# Initialize session state for Q&A
if "qa_history" not in st.session_state:
    st.session_state.qa_history = []

st.divider()

# Pet selection
st.subheader("🐾 Select Your Pet Type")
available_breeds = get_available_breeds()
selected_breed = st.selectbox(
    "What type of pet do you have?",
    options=available_breeds,
    format_func=lambda x: x.capitalize(),
)

st.divider()

# Question input
st.subheader("❓ Ask a Question")
st.markdown(f"**About your {selected_breed}:**")

question = st.text_area(
    "What would you like to know?",
    placeholder=f"e.g., How often should I feed my {selected_breed}?",
    height=80,
    label_visibility="collapsed",
)

col1, col2 = st.columns([1, 4])
with col1:
    ask_button = st.button("🔍 Ask Question", use_container_width=True)
with col2:
    st.write("")  # Spacer

# Process question
if ask_button and question:
    with st.spinner("🤔 Thinking..."):
        result = answer_pet_question(selected_breed, question)
    
    # Store in history
    st.session_state.qa_history.append({
        "breed": selected_breed,
        "question": question,
        "result": result,
    })
    
    st.success("✓ Answer generated!")

# Display latest answer
if st.session_state.qa_history:
    latest = st.session_state.qa_history[-1]
    result = latest["result"]
    
    st.divider()
    st.subheader(f"📚 Answer for {latest['breed'].capitalize()}")
    
    # Display the generated answer
    st.markdown(f"**Q: {latest['question']}**")
    st.info(result["answer"])
    
    # Display source categories and answer type
    col1, col2 = st.columns([3, 1])
    with col1:
        if result["source_categories"]:
            st.caption(f"📖 Source categories: {', '.join(result['source_categories'])}")
    with col2:
        if result.get("answer_type") == "rule_based":
            st.caption("🔄 Using fallback (LLM unavailable)")
        elif result.get("answer_type") == "llm":
            st.caption("✨ AI-generated answer")
    
    st.divider()
    
    # Display task suggestions
    if result["task_suggestions"]:
        st.subheader("💡 Suggested Tasks")
        st.markdown(
            "Based on the answer above, here are tasks you might want to add to your schedule:"
        )
        
        # Create task suggestion cards
        for idx, (task_name, frequency) in enumerate(result["task_suggestions"]):
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.write(f"**{task_name}**")
            with col2:
                st.caption(f"Freq: {frequency}")
            with col3:
                if st.button("➕ Add Task", key=f"add_task_{idx}"):
                    # Try to add task to existing owner's schedule
                    if "owner" in st.session_state and st.session_state.owner:
                        owner = st.session_state.owner
                        
                        # Let user select which pet to assign task to
                        pets = owner.get_pets()
                        if pets:
                            # Use a modal or expander to select pet and details
                            with st.expander(f"Configure task: {task_name}", expanded=True):
                                # Select pet
                                pet_options = {pet.name: pet for pet in pets}
                                selected_pet_name = st.selectbox(
                                    "Assign to pet:",
                                    options=list(pet_options.keys()),
                                    key=f"pet_select_{idx}",
                                )
                                selected_pet = pet_options[selected_pet_name]
                                
                                # Select time
                                col_hour, col_min = st.columns(2)
                                with col_hour:
                                    task_hour = st.number_input(
                                        "Hour (0-23)",
                                        min_value=0,
                                        max_value=23,
                                        value=9,
                                        key=f"hour_{idx}",
                                    )
                                with col_min:
                                    task_minute = st.number_input(
                                        "Minute (0-59)",
                                        min_value=0,
                                        max_value=59,
                                        value=0,
                                        key=f"min_{idx}",
                                    )
                                
                                # Map frequency string to formal frequency
                                freq_mapping = {
                                    "once daily": "daily",
                                    "twice daily": "daily",
                                    "daily": "daily",
                                    "weekly": "weekly",
                                    "monthly": "monthly",
                                    "as needed": "once",
                                }
                                task_frequency = freq_mapping.get(frequency.lower(), "daily")
                                
                                if st.button("✓ Create Task", key=f"confirm_{idx}"):
                                    # Create and add task
                                    task_time = time(hour=int(task_hour), minute=int(task_minute))
                                    new_task = Task(
                                        description=task_name,
                                        time=task_time,
                                        frequency=task_frequency,
                                    )
                                    selected_pet.add_task(new_task)
                                    st.success(
                                        f"✓ Task '{task_name}' added to {selected_pet.name}'s schedule!"
                                    )
                        else:
                            st.warning("No pets in your profile yet. Add a pet first on the main page!")
                    else:
                        st.warning("Please create an owner and pet on the main page first!")
    else:
        st.info("No specific tasks suggested for this answer.")

st.divider()

# Display Q&A History
if len(st.session_state.qa_history) > 1:
    st.subheader("📜 Q&A History")
    
    for idx, entry in enumerate(reversed(st.session_state.qa_history[:-1])):  # Exclude the latest
        with st.expander(
            f"{entry['breed'].capitalize()}: {entry['question'][:60]}..."
        ):
            st.write(f"**Answer:** {entry['result']['answer'][:200]}...")
            if st.button("View Full", key=f"view_full_{idx}"):
                st.write(entry["result"]["answer"])

st.divider()

# Footer with tips
st.markdown(
    """
    ---
    
    ### 💡 Tips for Best Results
    - Be specific in your questions (e.g., "How often should I bathe my goldfish?" vs "Goldfish care")
    - The system works best for: feeding, exercise, grooming, health, training, and environment
    - Task suggestions are generated based on the AI response
    - You can manually adjust suggested tasks before adding them to your schedule
    
    ### 🔗 Integration
    Tasks added here automatically appear in your main PawPal+ schedule!
    """
)
