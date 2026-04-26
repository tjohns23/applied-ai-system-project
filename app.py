import streamlit as st
from datetime import time
from pawpal_system import Task, Pet, Owner, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

# Initialize session state
if "owner" not in st.session_state:
    st.session_state.owner = None
if "scheduler" not in st.session_state:
    st.session_state.scheduler = None

# Owner Setup
st.subheader("Owner Setup")
owner_name = st.text_input("Owner name", value="Jordan")

if st.button("Create Owner"):
    st.session_state.owner = Owner(name=owner_name, owner_id=1)
    st.session_state.scheduler = Scheduler(owner=st.session_state.owner)
    st.success(f"✓ Owner '{owner_name}' created!")

# Pet Management
if st.session_state.owner:
    st.subheader("Pet Management")
    col1, col2 = st.columns(2)
    with col1:
        pet_name = st.text_input("Pet name", value="Mochi")
    with col2:
        species = st.selectbox("Species", ["dog", "cat", "other"])
    
    if st.button("Add Pet"):
        new_pet = Pet(name=pet_name, breed=species, owner_id=st.session_state.owner.owner_id)
        st.session_state.owner.add_pet(new_pet)
        st.success(f"✓ Pet '{pet_name}' ({species}) added!")
    
    # Display current pets
    if st.session_state.owner.get_pets():
        st.write("**Current Pets:**")
        for pet in st.session_state.owner.get_pets():
            st.write(f"  • {pet.name} ({pet.breed}) - {len(pet.get_tasks())} tasks")
    
    # Task Management
    st.markdown("### Add Tasks")
    st.caption("Select a pet and add a task to their schedule.")
    
    pet_options = {pet.name: pet for pet in st.session_state.owner.get_pets()}
    selected_pet_name = st.selectbox("Select pet", list(pet_options.keys()))
    selected_pet = pet_options[selected_pet_name]
    
    col1, col2, col3 = st.columns(3)
    with col1:
        task_description = st.text_input("Task description", value="Walk")
    with col2:
        task_hour = st.number_input("Hour (0-23)", min_value=0, max_value=23, value=9)
        task_minute = st.number_input("Minute (0-59)", min_value=0, max_value=59, value=0)
    with col3:
        task_frequency = st.selectbox("Frequency", ["daily", "weekly", "monthly"])
    
    if st.button("Add Task"):
        task_time = time(hour=int(task_hour), minute=int(task_minute))
        new_task = Task(description=task_description, time=task_time, frequency=task_frequency)
        selected_pet.add_task(new_task)
        st.success(f"✓ Task '{task_description}' added to {selected_pet.name} at {task_time.strftime('%H:%M')}")
    
    # Display Schedule Overview
    st.markdown("---")
    st.subheader("📅 Schedule Overview")
    
    all_tasks = st.session_state.scheduler.get_pending_tasks()
    if all_tasks:
        # Show conflict warnings
        if st.session_state.scheduler.has_conflicts():
            st.warning(st.session_state.scheduler.get_conflict_summary())
        
        # Organize and display tasks by time
        organized_tasks = st.session_state.scheduler.organize_tasks()
        
        if organized_tasks:
            st.markdown("#### Tasks (sorted by time)")
            task_display = []
            for task in organized_tasks:
                status = "✓ DONE" if task.is_completed() else "○ PENDING"
                task_display.append({
                    "Time": task.get_time().strftime("%H:%M"),
                    "Task": task.get_description(),
                    "Frequency": task.get_frequency(),
                    "Status": status
                })
            
            # Display as a nice table
            import pandas as pd
            df = pd.DataFrame(task_display)
            st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No tasks scheduled yet. Add a task to get started!")
    
    # Display all tasks
    all_tasks = st.session_state.owner.get_all_tasks()
    if all_tasks:
        st.write("**All Tasks:**")
        for task in all_tasks:
            status = "✓ DONE" if task.is_completed() else "⏳ PENDING"
            st.write(f"  • {task.get_time().strftime('%H:%M')} - {task.get_description()} [{status}] ({task.get_frequency()})")
    else:
        st.info("No tasks yet. Add one above.")

    st.divider()
    
    st.subheader("📅 Generate Schedule")
    st.caption("Organize all tasks by time and view your daily schedule.")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Organize by Time"):
            organized = st.session_state.scheduler.organize_tasks()
            if organized:
                st.write("**Today's Schedule (sorted by time):**")
                for task in organized:
                    status = "✓" if task.is_completed() else "⏳"
                    st.write(f"{status} {task.get_time().strftime('%H:%M')} - {task.get_description()} ({task.get_frequency()})")
            else:
                st.info("No tasks to organize yet.")
    
    with col2:
        if st.button("View Pending Tasks"):
            pending = st.session_state.scheduler.get_pending_tasks()
            if pending:
                st.write("**Pending Tasks:**")
                for task in pending:
                    st.write(f"  • {task.get_time().strftime('%H:%M')} - {task.get_description()}")
            else:
                st.success("✓ All tasks completed!")
    
    with col3:
        frequency_filter = st.selectbox("Filter by frequency", ["daily", "weekly", "monthly"])
        if st.button("Apply Filter"):
            filtered = st.session_state.scheduler.get_tasks_by_frequency(frequency_filter)
            if filtered:
                st.write(f"**{frequency_filter.capitalize()} Tasks:**")
                for task in filtered:
                    st.write(f"  • {task.get_description()}")
            else:
                st.info(f"No {frequency_filter} tasks found.")
else:
    st.warning("Create an owner first to get started!")
