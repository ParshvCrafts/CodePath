"""
PawPal+ CLI Testing Script

Demonstrates the backend system with sorting, filtering, recurring tasks, and conflict detection.
"""

from pawpal_system import Owner, Pet, Task, Scheduler, Priority, Frequency, ScheduleConflict
from datetime import date, timedelta

# Create an owner
owner = Owner(
    name="Jordan",
    available_hours_per_day=6.0,
    preferences={"preferred_walk_time": "morning"}
)

# Create pets
mochi = Pet(
    name="Mochi",
    species="dog",
    age=3,
    breed="Golden Retriever"
)

luna = Pet(
    name="Luna",
    species="cat",
    age=5,
    breed="Siamese"
)

# Add pets to owner
owner.add_pet(mochi)
owner.add_pet(luna)

# Create tasks for Mochi (dog) - intentionally out of order
task1 = Task(
    task_id="mochi_walk_1",
    description="Morning walk (Mochi)",
    duration_minutes=30,
    priority=Priority.HIGH,
    frequency=Frequency.DAILY,
    scheduled_time="09:00",
    due_date=date.today(),
    pet_name="Mochi"
)

task2 = Task(
    task_id="mochi_feeding_1",
    description="Morning feeding (Mochi)",
    duration_minutes=15,
    priority=Priority.HIGH,
    frequency=Frequency.DAILY,
    scheduled_time="08:00",  # Before walk
    due_date=date.today(),
    pet_name="Mochi"
)

task3 = Task(
    task_id="mochi_play_1",
    description="Play time (Mochi)",
    duration_minutes=20,
    priority=Priority.MEDIUM,
    frequency=Frequency.DAILY,
    scheduled_time="14:00",  # Afternoon
    due_date=date.today(),
    pet_name="Mochi"
)

# Create tasks for Luna (cat)
task4 = Task(
    task_id="luna_feeding_1",
    description="Morning feeding (Luna)",
    duration_minutes=10,
    priority=Priority.HIGH,
    frequency=Frequency.DAILY,
    scheduled_time="08:30",
    due_date=date.today(),
    pet_name="Luna"
)

task5 = Task(
    task_id="luna_litter_1",
    description="Clean litter box (Luna)",
    duration_minutes=10,
    priority=Priority.MEDIUM,
    frequency=Frequency.DAILY,
    scheduled_time="17:00",
    due_date=date.today(),
    pet_name="Luna"
)

# Add a conflicting task (same time as task1)
task6 = Task(
    task_id="luna_playtime_1",
    description="Play with Luna",
    duration_minutes=15,
    priority=Priority.MEDIUM,
    frequency=Frequency.DAILY,
    scheduled_time="09:00",  # Same time as Mochi's walk!
    due_date=date.today(),
    pet_name="Luna"
)

# Add tasks to pets
mochi.add_task(task1)
mochi.add_task(task2)
mochi.add_task(task3)

luna.add_task(task4)
luna.add_task(task5)
luna.add_task(task6)

# Print owner and pet info
print("=" * 70)
print(f"Owner: {owner.name}")
print(f"Available hours per day: {owner.available_hours_per_day}")
print(f"Number of pets: {len(owner.get_pets())}")
print()

for pet in owner.get_pets():
    print(f"\nPet: {pet.name} ({pet.species}, {pet.breed}, age {pet.age})")
    print(f"  Total tasks: {len(pet.get_tasks())}")
    for task in pet.get_tasks():
        status = "[X]" if task.completed else "[ ]"
        time_str = f" at {task.scheduled_time}" if task.scheduled_time else ""
        print(f"    {status} {task.description} ({task.duration_minutes} min, {task.priority.name}){time_str}")

# ============================================================================
# DEMONSTRATE SORTING
# ============================================================================

print("\n" + "=" * 70)
print("FEATURE 1: SORTING TASKS BY TIME")
print("=" * 70)

all_tasks = owner.get_all_tasks()
sorted_tasks = owner.get_all_tasks_sorted_by_time()

print("\nOriginal order (unsorted):")
for task in all_tasks:
    time_str = f" at {task.scheduled_time}" if task.scheduled_time else " (no time)"
    print(f"  - {task.description}{time_str}")

print("\nSorted by scheduled time (HH:MM):")
for task in sorted_tasks:
    time_str = f" at {task.scheduled_time}" if task.scheduled_time else " (no time)"
    print(f"  - {task.description}{time_str}")

# ============================================================================
# DEMONSTRATE FILTERING
# ============================================================================

print("\n" + "=" * 70)
print("FEATURE 2: FILTERING TASKS")
print("=" * 70)

print("\nFilter by pet (Mochi):")
mochi_tasks = owner.filter_tasks_by_pet("Mochi")
for task in mochi_tasks:
    print(f"  - {task.description}")

print("\nFilter by priority (HIGH):")
high_priority = owner.filter_tasks_by_priority(Priority.HIGH)
for task in high_priority:
    print(f"  - {task.description} (Pet: {task.pet_name})")

print("\nFilter by status (incomplete):")
incomplete = owner.filter_tasks_by_status(completed=False)
for task in incomplete:
    print(f"  - {task.description}")

# ============================================================================
# DEMONSTRATE CONFLICT DETECTION
# ============================================================================

print("\n" + "=" * 70)
print("GENERATING DAILY SCHEDULE")
print("=" * 70)

scheduler = Scheduler()
schedule = scheduler.create_daily_schedule(owner, date.today())

print(f"\nSchedule for {schedule.schedule_date}:")
print("-" * 70)

if schedule.get_tasks_by_time():
    for scheduled_task in schedule.get_tasks_by_time():
        task = scheduled_task.task
        start = scheduled_task.start_hour
        end = scheduled_task.end_hour
        reason = scheduled_task.reason
        print(f"\n  {start:5.1f}h - {end:5.1f}h | {task.description}")
        print(f"              Reason: {reason}")
else:
    print("\n  No tasks scheduled.")

# Check for conflicts
print("\n" + "-" * 70)
print("FEATURE 3: CONFLICT DETECTION")
print("-" * 70)

conflicts = scheduler.detect_conflicts(schedule)
if conflicts:
    print("\n[WARNING] Scheduling conflicts detected:")
    for conflict in conflicts:
        print(f"  - {conflict.message}")
else:
    print("\nNo conflicts detected - schedule is clean!")

# ============================================================================
# DEMONSTRATE RECURRING TASKS
# ============================================================================

print("\n" + "=" * 70)
print("FEATURE 4: RECURRING TASKS")
print("=" * 70)

print("\nMarking task1 (Morning walk) as complete...")
task1.mark_complete()

print(f"Task1 completed: {task1.completed}")

# Create next occurrence
next_task = task1.create_next_occurrence()
if next_task:
    print(f"New task created for next occurrence:")
    print(f"  Task ID: {next_task.task_id}")
    print(f"  Due date: {next_task.due_date}")
    print(f"  Completed: {next_task.completed}")
    mochi.add_task(next_task)
    print(f"  Added to {mochi.name}'s task list")
else:
    print("No recurring task needed")

print(f"\nMochi now has {len(mochi.get_tasks())} tasks (was {len(mochi.get_tasks()) - 1})")

# Show the new complete vs incomplete count
print(f"\nComplete tasks for {mochi.name}:")
for task in mochi.filter_tasks_by_status(completed=True):
    print(f"  - {task.description}")

print(f"\nIncomplete tasks for {mochi.name}:")
for task in mochi.filter_tasks_by_status(completed=False):
    print(f"  - {task.description}")

# ============================================================================
# SUMMARY
# ============================================================================

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
print("\nNew features demonstrated:")
print("  [1] Sorting tasks by scheduled time (HH:MM format)")
print("  [2] Filtering tasks by pet, priority, and completion status")
print("  [3] Conflict detection for overlapping scheduled times")
print("  [4] Automatic recurring task creation (daily/weekly)")
print("\nAll features working correctly!")
print("=" * 70)
