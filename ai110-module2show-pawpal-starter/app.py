"""
PawPal+ Streamlit Application

Interactive UI for pet care task scheduling.
"""

import streamlit as st
from datetime import date
from pawpal_system import Owner, Pet, Task, Scheduler, Priority, Frequency

# Page configuration
st.set_page_config(page_title="PawPal+", page_icon="[paw]", layout="wide")

st.title("PawPal+ - Pet Care Scheduler")

st.markdown(
    """
Welcome to **PawPal+**, your intelligent pet care planning assistant.

This app helps you organize and schedule pet care tasks based on priorities and available time.
"""
)

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

def initialize_session_state():
    """Initialize session state with Owner object if it doesn't exist."""
    if "owner" not in st.session_state:
        # Create a default owner
        st.session_state.owner = Owner(
            name="Pet Owner",
            available_hours_per_day=8.0,
            preferences={"preferred_walk_time": "morning"}
        )
    if "current_pet" not in st.session_state:
        st.session_state.current_pet = None

initialize_session_state()

# ============================================================================
# OWNER SETUP
# ============================================================================

st.divider()
st.header("Owner Profile")

col1, col2 = st.columns(2)
with col1:
    owner_name = st.text_input(
        "Owner name",
        value=st.session_state.owner.name,
        key="owner_name_input"
    )
    if owner_name != st.session_state.owner.name:
        st.session_state.owner.name = owner_name

with col2:
    available_hours = st.number_input(
        "Available hours per day for pet care",
        min_value=1.0,
        max_value=24.0,
        value=st.session_state.owner.available_hours_per_day,
        step=0.5,
        key="hours_input"
    )
    if available_hours != st.session_state.owner.available_hours_per_day:
        st.session_state.owner.available_hours_per_day = available_hours

# ============================================================================
# PET MANAGEMENT
# ============================================================================

st.divider()
st.header("Pet Management")

# Add new pet section
st.subheader("Add a New Pet")
col1, col2, col3 = st.columns(3)

with col1:
    pet_name = st.text_input("Pet name", value="Mochi")
with col2:
    species = st.selectbox("Species", ["dog", "cat", "bird", "rabbit", "other"])
with col3:
    pet_age = st.number_input("Age (years)", min_value=0, max_value=30, value=3)

breed = st.text_input("Breed", value="Mixed")

if st.button("Add Pet"):
    if pet_name and pet_name.strip():
        new_pet = Pet(name=pet_name, species=species, age=pet_age, breed=breed)
        st.session_state.owner.add_pet(new_pet)
        st.session_state.current_pet = new_pet
        st.success(f"Added {pet_name} the {species}!")
        st.rerun()
    else:
        st.error("Please enter a pet name.")

# Display current pets
st.subheader("Your Pets")
pets = st.session_state.owner.get_pets()

if pets:
    # Pet selector
    pet_names = [p.name for p in pets]
    selected_pet_name = st.selectbox("Select a pet", pet_names)
    st.session_state.current_pet = next(p for p in pets if p.name == selected_pet_name)

    # Display selected pet info
    current_pet = st.session_state.current_pet
    st.write(f"**{current_pet.name}** - {current_pet.breed} {current_pet.species}, age {current_pet.age}")
else:
    st.info("No pets yet. Add one above.")
    st.session_state.current_pet = None

# ============================================================================
# TASK MANAGEMENT
# ============================================================================

st.divider()
st.header("Task Management")

if st.session_state.current_pet:
    current_pet = st.session_state.current_pet

    st.subheader(f"Tasks for {current_pet.name}")

    # Add new task section
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        task_desc = st.text_input("Task description", value="Morning walk")
    with col2:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=30)
    with col3:
        priority_str = st.selectbox("Priority", ["low", "medium", "high"], index=2)
        priority = {"low": Priority.LOW, "medium": Priority.MEDIUM, "high": Priority.HIGH}[priority_str]
    with col4:
        frequency_str = st.selectbox("Frequency", ["daily", "weekly", "as_needed"], index=0)
        frequency = {"daily": Frequency.DAILY, "weekly": Frequency.WEEKLY, "as_needed": Frequency.AS_NEEDED}[frequency_str]

    if st.button("Add Task"):
        if task_desc and task_desc.strip():
            # Generate task ID
            task_id = f"{current_pet.name.lower()}_{len(current_pet.get_tasks())}"
            new_task = Task(
                task_id=task_id,
                description=task_desc,
                duration_minutes=int(duration),
                priority=priority,
                frequency=frequency,
                completed=False
            )
            current_pet.add_task(new_task)
            st.success(f"Added task: {task_desc}")
            st.rerun()
        else:
            st.error("Please enter a task description.")

    # Display tasks for current pet
    tasks = current_pet.get_tasks()
    if tasks:
        st.subheader("Current Tasks")

        # Add filtering and sorting options
        col1, col2, col3 = st.columns(3)
        with col1:
            filter_status = st.selectbox(
                "Filter by status",
                ["All", "Complete", "Incomplete"],
                key="filter_status"
            )
        with col2:
            sort_by = st.selectbox(
                "Sort by",
                ["Added", "Time", "Priority", "Due Date"],
                key="sort_by"
            )
        with col3:
            filter_priority = st.selectbox(
                "Filter by priority",
                ["All", "HIGH", "MEDIUM", "LOW"],
                key="filter_priority"
            )

        # Apply filters
        filtered_tasks = tasks
        if filter_status == "Complete":
            filtered_tasks = current_pet.filter_tasks_by_status(completed=True)
        elif filter_status == "Incomplete":
            filtered_tasks = current_pet.filter_tasks_by_status(completed=False)

        if filter_priority != "All":
            priority_map = {"HIGH": Priority.HIGH, "MEDIUM": Priority.MEDIUM, "LOW": Priority.LOW}
            filtered_tasks = [t for t in filtered_tasks if t.priority == priority_map[filter_priority]]

        # Apply sorting
        if sort_by == "Time":
            filtered_tasks = sorted(filtered_tasks, key=lambda t: t.scheduled_time or "99:99")
        elif sort_by == "Priority":
            filtered_tasks = sorted(filtered_tasks, key=lambda t: t.priority.value, reverse=True)
        elif sort_by == "Due Date":
            filtered_tasks = sorted(filtered_tasks, key=lambda t: t.due_date)

        # Create a display table
        task_data = []
        for task in filtered_tasks:
            time_str = f"{task.scheduled_time}" if task.scheduled_time else "No time"
            task_data.append({
                "Description": task.description,
                "Duration (min)": task.duration_minutes,
                "Priority": task.priority.name,
                "Frequency": task.frequency.value,
                "Time": time_str,
                "Completed": "[X]" if task.completed else "[ ]"
            })

        if task_data:
            st.dataframe(task_data, use_container_width=True)
        else:
            st.info("No tasks match the selected filters.")

        # Mark task complete/incomplete
        st.subheader("Update Task Status")
        task_desc_list = [t.description for t in tasks]
        selected_task_desc = st.selectbox("Select a task to update", task_desc_list)

        selected_task = next(t for t in tasks if t.description == selected_task_desc)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Mark Complete"):
                selected_task.mark_complete()
                st.success("Task marked complete!")
                st.rerun()
        with col2:
            if st.button("Mark Incomplete"):
                selected_task.mark_incomplete()
                st.success("Task marked incomplete!")
                st.rerun()
    else:
        st.info(f"No tasks yet for {current_pet.name}. Add one above.")

else:
    st.info("Select or add a pet to manage its tasks.")

# ============================================================================
# SCHEDULE GENERATION
# ============================================================================

st.divider()
st.header("Generate Daily Schedule")

if st.session_state.owner.get_pets():
    if st.button("Generate Today's Schedule", type="primary"):
        scheduler = Scheduler()
        schedule = scheduler.create_daily_schedule(st.session_state.owner, date.today())

        if schedule.get_tasks_by_time():
            st.success("Schedule generated!")

            # Check for conflicts
            conflicts = scheduler.detect_conflicts(schedule)
            if conflicts:
                st.warning("⚠️ **Scheduling Conflicts Detected**")
                for conflict in conflicts:
                    st.warning(conflict.message)

            # Display schedule
            st.subheader(f"Daily Schedule - {schedule.schedule_date}")

            for scheduled_task in schedule.get_tasks_by_time():
                with st.container(border=True):
                    task = scheduled_task.task
                    start = scheduled_task.start_hour
                    end = scheduled_task.end_hour

                    col1, col2 = st.columns([1, 3])
                    with col1:
                        st.write(f"**{start:.1f} - {end:.1f}h**")
                    with col2:
                        st.write(f"**{task.description}**")
                        st.caption(f"Duration: {task.duration_minutes} min | Priority: {task.priority.name} | Reason: {scheduled_task.reason}")

            # Show explanation
            st.subheader("Schedule Explanation")
            st.info(schedule.get_explanation())

            # Summary
            total_minutes = sum(s.task.duration_minutes for s in schedule.get_tasks_by_time())
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(
                    "Total Time Scheduled",
                    f"{total_minutes / 60:.1f} hours",
                    f"out of {st.session_state.owner.available_hours_per_day} available"
                )
            with col2:
                st.metric(
                    "Tasks Scheduled",
                    len(schedule.get_tasks_by_time()),
                    f"out of {len(st.session_state.owner.get_incomplete_tasks())} total"
                )
            with col3:
                time_used_pct = (total_minutes / 60) / st.session_state.owner.available_hours_per_day * 100
                st.metric("Time Utilization", f"{time_used_pct:.0f}%")

        else:
            st.warning("No tasks available to schedule. Add tasks to your pets.")

else:
    st.warning("Please add at least one pet and tasks before generating a schedule.")
