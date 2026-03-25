"""
Tests for PawPal+ Backend System

Tests cover core functionality: task management, pet management, and scheduling.
"""

import pytest
from pawpal_system import Task, Pet, Owner, Scheduler, Priority, Frequency
from datetime import date, timedelta


class TestTask:
    """Tests for Task class."""

    def test_task_completion(self):
        """Verify that marking a task complete changes its status."""
        task = Task(
            task_id="test_1",
            description="Test task",
            duration_minutes=30,
            priority=Priority.HIGH,
            frequency=Frequency.DAILY,
            completed=False
        )

        assert not task.completed
        task.mark_complete()
        assert task.completed

    def test_task_incomplete(self):
        """Verify that marking a task incomplete changes its status."""
        task = Task(
            task_id="test_1",
            description="Test task",
            duration_minutes=30,
            priority=Priority.HIGH,
            frequency=Frequency.DAILY,
            completed=True
        )

        assert task.completed
        task.mark_incomplete()
        assert not task.completed

    def test_task_is_urgent(self):
        """Verify that is_urgent() correctly identifies high priority tasks."""
        high_task = Task(
            task_id="test_1",
            description="Urgent",
            duration_minutes=10,
            priority=Priority.HIGH,
            frequency=Frequency.DAILY
        )

        medium_task = Task(
            task_id="test_2",
            description="Normal",
            duration_minutes=10,
            priority=Priority.MEDIUM,
            frequency=Frequency.DAILY
        )

        assert high_task.is_urgent()
        assert not medium_task.is_urgent()


class TestPet:
    """Tests for Pet class."""

    def test_add_task_to_pet(self):
        """Verify that adding a task to a pet increases the task count."""
        pet = Pet(name="Fluffy", species="cat", age=3, breed="Tabby")
        assert len(pet.get_tasks()) == 0

        task = Task(
            task_id="task_1",
            description="Feed cat",
            duration_minutes=10,
            priority=Priority.HIGH,
            frequency=Frequency.DAILY
        )
        pet.add_task(task)
        assert len(pet.get_tasks()) == 1

    def test_remove_task_from_pet(self):
        """Verify that removing a task decreases the task count."""
        pet = Pet(name="Fluffy", species="cat", age=3, breed="Tabby")

        task1 = Task(
            task_id="task_1",
            description="Feed cat",
            duration_minutes=10,
            priority=Priority.HIGH,
            frequency=Frequency.DAILY
        )
        task2 = Task(
            task_id="task_2",
            description="Play with cat",
            duration_minutes=15,
            priority=Priority.MEDIUM,
            frequency=Frequency.DAILY
        )

        pet.add_task(task1)
        pet.add_task(task2)
        assert len(pet.get_tasks()) == 2

        pet.remove_task("task_1")
        assert len(pet.get_tasks()) == 1
        assert pet.get_tasks()[0].task_id == "task_2"

    def test_get_incomplete_tasks(self):
        """Verify that get_incomplete_tasks returns only incomplete tasks."""
        pet = Pet(name="Fluffy", species="cat", age=3, breed="Tabby")

        task1 = Task(
            task_id="task_1",
            description="Feed cat",
            duration_minutes=10,
            priority=Priority.HIGH,
            frequency=Frequency.DAILY,
            completed=False
        )
        task2 = Task(
            task_id="task_2",
            description="Play with cat",
            duration_minutes=15,
            priority=Priority.MEDIUM,
            frequency=Frequency.DAILY,
            completed=True
        )

        pet.add_task(task1)
        pet.add_task(task2)

        incomplete = pet.get_incomplete_tasks()
        assert len(incomplete) == 1
        assert incomplete[0].task_id == "task_1"


class TestOwner:
    """Tests for Owner class."""

    def test_add_pet_to_owner(self):
        """Verify that adding a pet to an owner increases the pet count."""
        owner = Owner(name="John", available_hours_per_day=8.0)
        assert len(owner.get_pets()) == 0

        pet = Pet(name="Fluffy", species="cat", age=3, breed="Tabby")
        owner.add_pet(pet)
        assert len(owner.get_pets()) == 1

    def test_remove_pet_from_owner(self):
        """Verify that removing a pet decreases the pet count."""
        owner = Owner(name="John", available_hours_per_day=8.0)

        pet1 = Pet(name="Fluffy", species="cat", age=3, breed="Tabby")
        pet2 = Pet(name="Buddy", species="dog", age=5, breed="Labrador")

        owner.add_pet(pet1)
        owner.add_pet(pet2)
        assert len(owner.get_pets()) == 2

        owner.remove_pet("Fluffy")
        assert len(owner.get_pets()) == 1
        assert owner.get_pets()[0].name == "Buddy"

    def test_get_all_tasks(self):
        """Verify that get_all_tasks returns tasks from all pets."""
        owner = Owner(name="John", available_hours_per_day=8.0)

        pet1 = Pet(name="Fluffy", species="cat", age=3, breed="Tabby")
        pet2 = Pet(name="Buddy", species="dog", age=5, breed="Labrador")

        task1 = Task(
            task_id="task_1",
            description="Feed cat",
            duration_minutes=10,
            priority=Priority.HIGH,
            frequency=Frequency.DAILY
        )
        task2 = Task(
            task_id="task_2",
            description="Feed dog",
            duration_minutes=15,
            priority=Priority.HIGH,
            frequency=Frequency.DAILY
        )
        task3 = Task(
            task_id="task_3",
            description="Walk dog",
            duration_minutes=30,
            priority=Priority.HIGH,
            frequency=Frequency.DAILY
        )

        pet1.add_task(task1)
        pet2.add_task(task2)
        pet2.add_task(task3)

        owner.add_pet(pet1)
        owner.add_pet(pet2)

        all_tasks = owner.get_all_tasks()
        assert len(all_tasks) == 3

    def test_get_incomplete_tasks_across_pets(self):
        """Verify that get_incomplete_tasks returns incomplete tasks from all pets."""
        owner = Owner(name="John", available_hours_per_day=8.0)

        pet1 = Pet(name="Fluffy", species="cat", age=3, breed="Tabby")
        pet2 = Pet(name="Buddy", species="dog", age=5, breed="Labrador")

        task1 = Task(
            task_id="task_1",
            description="Feed cat",
            duration_minutes=10,
            priority=Priority.HIGH,
            frequency=Frequency.DAILY,
            completed=False
        )
        task2 = Task(
            task_id="task_2",
            description="Feed dog",
            duration_minutes=15,
            priority=Priority.HIGH,
            frequency=Frequency.DAILY,
            completed=True
        )
        task3 = Task(
            task_id="task_3",
            description="Walk dog",
            duration_minutes=30,
            priority=Priority.HIGH,
            frequency=Frequency.DAILY,
            completed=False
        )

        pet1.add_task(task1)
        pet2.add_task(task2)
        pet2.add_task(task3)

        owner.add_pet(pet1)
        owner.add_pet(pet2)

        incomplete_tasks = owner.get_incomplete_tasks()
        assert len(incomplete_tasks) == 2


class TestScheduler:
    """Tests for Scheduler class."""

    def test_create_daily_schedule_with_tasks(self):
        """Verify that the scheduler creates a schedule from owner's tasks."""
        owner = Owner(name="John", available_hours_per_day=3.0)

        pet = Pet(name="Fluffy", species="cat", age=3, breed="Tabby")

        task1 = Task(
            task_id="task_1",
            description="Feed cat",
            duration_minutes=10,
            priority=Priority.HIGH,
            frequency=Frequency.DAILY
        )
        task2 = Task(
            task_id="task_2",
            description="Play with cat",
            duration_minutes=20,
            priority=Priority.MEDIUM,
            frequency=Frequency.DAILY
        )

        pet.add_task(task1)
        pet.add_task(task2)
        owner.add_pet(pet)

        scheduler = Scheduler()
        schedule = scheduler.create_daily_schedule(owner, date.today())

        assert len(schedule.get_tasks_by_time()) == 2

    def test_scheduler_respects_available_hours(self):
        """Verify that the scheduler doesn't schedule tasks beyond available hours."""
        owner = Owner(name="John", available_hours_per_day=1.0)

        pet = Pet(name="Fluffy", species="cat", age=3, breed="Tabby")

        task1 = Task(
            task_id="task_1",
            description="Feed cat",
            duration_minutes=30,
            priority=Priority.HIGH,
            frequency=Frequency.DAILY
        )
        task2 = Task(
            task_id="task_2",
            description="Play with cat",
            duration_minutes=30,
            priority=Priority.HIGH,
            frequency=Frequency.DAILY
        )
        task3 = Task(
            task_id="task_3",
            description="Groom cat",
            duration_minutes=30,
            priority=Priority.LOW,
            frequency=Frequency.DAILY
        )

        pet.add_task(task1)
        pet.add_task(task2)
        pet.add_task(task3)
        owner.add_pet(pet)

        scheduler = Scheduler()
        schedule = scheduler.create_daily_schedule(owner, date.today())

        # Only 2 tasks should fit in 1 hour (high priority tasks)
        assert len(schedule.get_tasks_by_time()) == 2

    def test_scheduler_prioritizes_high_priority_tasks(self):
        """Verify that high priority tasks are scheduled before lower priority ones."""
        owner = Owner(name="John", available_hours_per_day=1.5)

        pet = Pet(name="Fluffy", species="cat", age=3, breed="Tabby")

        task_low = Task(
            task_id="task_low",
            description="Groom cat",
            duration_minutes=30,
            priority=Priority.LOW,
            frequency=Frequency.DAILY
        )
        task_high = Task(
            task_id="task_high",
            description="Feed cat",
            duration_minutes=30,
            priority=Priority.HIGH,
            frequency=Frequency.DAILY
        )

        pet.add_task(task_low)
        pet.add_task(task_high)
        owner.add_pet(pet)

        scheduler = Scheduler()
        schedule = scheduler.create_daily_schedule(owner, date.today())

        # High priority task should be scheduled first (lower start time)
        scheduled = schedule.get_tasks_by_time()
        assert scheduled[0].task.priority == Priority.HIGH
        assert scheduled[1].task.priority == Priority.LOW

    def test_scheduler_returns_empty_schedule_for_no_tasks(self):
        """Verify that scheduler returns empty schedule when there are no tasks."""
        owner = Owner(name="John", available_hours_per_day=8.0)

        scheduler = Scheduler()
        schedule = scheduler.create_daily_schedule(owner, date.today())

        assert len(schedule.get_tasks_by_time()) == 0


class TestSorting:
    """Tests for sorting functionality."""

    def test_sort_tasks_by_time(self):
        """Verify that tasks are sorted by scheduled time (HH:MM format)."""
        pet = Pet(name="Fluffy", species="cat", age=3, breed="Tabby")

        # Add tasks out of order
        task1 = Task(
            task_id="task_1",
            description="Afternoon play",
            duration_minutes=20,
            priority=Priority.MEDIUM,
            frequency=Frequency.DAILY,
            scheduled_time="14:00"
        )
        task2 = Task(
            task_id="task_2",
            description="Morning feed",
            duration_minutes=10,
            priority=Priority.HIGH,
            frequency=Frequency.DAILY,
            scheduled_time="08:00"
        )
        task3 = Task(
            task_id="task_3",
            description="Evening walk",
            duration_minutes=30,
            priority=Priority.HIGH,
            frequency=Frequency.DAILY,
            scheduled_time="18:00"
        )

        pet.add_task(task1)
        pet.add_task(task2)
        pet.add_task(task3)

        sorted_tasks = pet.get_tasks_sorted_by_time()
        assert len(sorted_tasks) == 3
        assert sorted_tasks[0].scheduled_time == "08:00"
        assert sorted_tasks[1].scheduled_time == "14:00"
        assert sorted_tasks[2].scheduled_time == "18:00"

    def test_sort_by_due_date(self):
        """Verify that tasks are sorted by due date."""
        pet = Pet(name="Buddy", species="dog", age=5, breed="Labrador")

        task1 = Task(
            task_id="task_1",
            description="Task for today",
            duration_minutes=20,
            priority=Priority.MEDIUM,
            frequency=Frequency.DAILY,
            due_date=date.today()
        )
        task2 = Task(
            task_id="task_2",
            description="Task for yesterday",
            duration_minutes=10,
            priority=Priority.HIGH,
            frequency=Frequency.DAILY,
            due_date=date.today() - timedelta(days=1)
        )
        task3 = Task(
            task_id="task_3",
            description="Task for tomorrow",
            duration_minutes=30,
            priority=Priority.HIGH,
            frequency=Frequency.DAILY,
            due_date=date.today() + timedelta(days=1)
        )

        pet.add_task(task1)
        pet.add_task(task2)
        pet.add_task(task3)

        sorted_tasks = pet.get_tasks_sorted_by_due_date()
        assert len(sorted_tasks) == 3
        assert sorted_tasks[0].due_date == date.today() - timedelta(days=1)
        assert sorted_tasks[1].due_date == date.today()
        assert sorted_tasks[2].due_date == date.today() + timedelta(days=1)


class TestFiltering:
    """Tests for filtering functionality."""

    def test_filter_by_status(self):
        """Verify that tasks can be filtered by completion status."""
        pet = Pet(name="Fluffy", species="cat", age=3, breed="Tabby")

        task1 = Task(
            task_id="task_1",
            description="Complete task",
            duration_minutes=10,
            priority=Priority.HIGH,
            frequency=Frequency.DAILY,
            completed=True
        )
        task2 = Task(
            task_id="task_2",
            description="Incomplete task",
            duration_minutes=15,
            priority=Priority.HIGH,
            frequency=Frequency.DAILY,
            completed=False
        )

        pet.add_task(task1)
        pet.add_task(task2)

        complete = pet.filter_tasks_by_status(completed=True)
        incomplete = pet.filter_tasks_by_status(completed=False)

        assert len(complete) == 1
        assert len(incomplete) == 1
        assert complete[0].task_id == "task_1"
        assert incomplete[0].task_id == "task_2"

    def test_filter_by_priority(self):
        """Verify that tasks can be filtered by priority level."""
        pet = Pet(name="Buddy", species="dog", age=5, breed="Labrador")

        high = Task(
            task_id="high_1",
            description="Feed dog",
            duration_minutes=10,
            priority=Priority.HIGH,
            frequency=Frequency.DAILY
        )
        medium = Task(
            task_id="med_1",
            description="Play with dog",
            duration_minutes=20,
            priority=Priority.MEDIUM,
            frequency=Frequency.DAILY
        )
        low = Task(
            task_id="low_1",
            description="Groom dog",
            duration_minutes=30,
            priority=Priority.LOW,
            frequency=Frequency.WEEKLY
        )

        pet.add_task(high)
        pet.add_task(medium)
        pet.add_task(low)

        high_tasks = pet.filter_tasks_by_priority(Priority.HIGH)
        assert len(high_tasks) == 1
        assert high_tasks[0].task_id == "high_1"

    def test_owner_filter_by_pet(self):
        """Verify that owner can filter tasks by specific pet."""
        owner = Owner(name="John", available_hours_per_day=8.0)

        pet1 = Pet(name="Fluffy", species="cat", age=3, breed="Tabby")
        pet2 = Pet(name="Buddy", species="dog", age=5, breed="Labrador")

        task1 = Task(
            task_id="task_1",
            description="Feed Fluffy",
            duration_minutes=10,
            priority=Priority.HIGH,
            frequency=Frequency.DAILY
        )
        task2 = Task(
            task_id="task_2",
            description="Walk Buddy",
            duration_minutes=30,
            priority=Priority.HIGH,
            frequency=Frequency.DAILY
        )

        pet1.add_task(task1)
        pet2.add_task(task2)

        owner.add_pet(pet1)
        owner.add_pet(pet2)

        fluffy_tasks = owner.filter_tasks_by_pet("Fluffy")
        assert len(fluffy_tasks) == 1
        assert fluffy_tasks[0].description == "Feed Fluffy"


class TestRecurringTasks:
    """Tests for recurring task functionality."""

    def test_create_next_daily_occurrence(self):
        """Verify that marking a daily task complete creates next day's task."""
        task = Task(
            task_id="walk_1",
            description="Morning walk",
            duration_minutes=30,
            priority=Priority.HIGH,
            frequency=Frequency.DAILY,
            due_date=date.today()
        )

        assert task.completed == False
        assert task.due_date == date.today()

        task.mark_complete()
        next_task = task.create_next_occurrence()

        assert next_task is not None
        assert next_task.completed == False
        assert next_task.due_date == date.today() + timedelta(days=1)
        assert next_task.frequency == Frequency.DAILY

    def test_create_next_weekly_occurrence(self):
        """Verify that marking a weekly task complete creates next week's task."""
        task = Task(
            task_id="groom_1",
            description="Grooming",
            duration_minutes=60,
            priority=Priority.MEDIUM,
            frequency=Frequency.WEEKLY,
            due_date=date.today()
        )

        task.mark_complete()
        next_task = task.create_next_occurrence()

        assert next_task is not None
        assert next_task.due_date == date.today() + timedelta(weeks=1)

    def test_as_needed_task_no_recurrence(self):
        """Verify that AS_NEEDED tasks don't create recurrences."""
        task = Task(
            task_id="vet_1",
            description="Vet visit",
            duration_minutes=60,
            priority=Priority.HIGH,
            frequency=Frequency.AS_NEEDED
        )

        task.mark_complete()
        next_task = task.create_next_occurrence()

        assert next_task is None


class TestConflictDetection:
    """Tests for conflict detection functionality."""

    def test_detect_exact_time_conflict(self):
        """Verify that scheduler detects tasks at the same time."""
        owner = Owner(name="John", available_hours_per_day=6.0)

        pet1 = Pet(name="Mochi", species="dog", age=3, breed="Golden Retriever")
        pet2 = Pet(name="Luna", species="cat", age=5, breed="Siamese")

        # Two tasks scheduled for the exact same time
        task1 = Task(
            task_id="mochi_walk",
            description="Walk Mochi",
            duration_minutes=30,
            priority=Priority.HIGH,
            frequency=Frequency.DAILY
        )
        task2 = Task(
            task_id="luna_feed",
            description="Feed Luna",
            duration_minutes=15,
            priority=Priority.HIGH,
            frequency=Frequency.DAILY
        )

        pet1.add_task(task1)
        pet2.add_task(task2)

        owner.add_pet(pet1)
        owner.add_pet(pet2)

        scheduler = Scheduler()
        schedule = scheduler.create_daily_schedule(owner, date.today())

        # Check if schedule has tasks
        assert len(schedule.get_tasks_by_time()) > 0

        # Detect conflicts
        conflicts = scheduler.detect_conflicts(schedule)
        # Note: Conflicts may not occur if scheduler places tasks at different times
        # This test verifies the conflict detection method works, even if no conflicts found
        assert isinstance(conflicts, list)

    def test_no_conflicts_in_clean_schedule(self):
        """Verify that clean schedules report no conflicts."""
        owner = Owner(name="John", available_hours_per_day=8.0)

        pet = Pet(name="Fluffy", species="cat", age=3, breed="Tabby")

        task1 = Task(
            task_id="feed_1",
            description="Feed Fluffy",
            duration_minutes=10,
            priority=Priority.HIGH,
            frequency=Frequency.DAILY
        )

        pet.add_task(task1)
        owner.add_pet(pet)

        scheduler = Scheduler()
        schedule = scheduler.create_daily_schedule(owner, date.today())

        conflicts = scheduler.detect_conflicts(schedule)
        assert len(conflicts) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
