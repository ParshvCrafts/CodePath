"""
PawPal+ Backend System

Core classes for pet care task scheduling.
"""

from dataclasses import dataclass, field
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional
from enum import Enum
import copy


class Priority(Enum):
    """Task priority levels."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3


class Frequency(Enum):
    """Task recurrence patterns."""
    DAILY = "daily"
    WEEKLY = "weekly"
    AS_NEEDED = "as_needed"


@dataclass
class Task:
    """Represents a single pet care task."""
    task_id: str
    description: str
    duration_minutes: int
    priority: Priority
    frequency: Frequency
    completed: bool = False
    scheduled_time: Optional[str] = None  # Format: "HH:MM" (e.g., "09:30")
    due_date: date = field(default_factory=date.today)
    pet_name: Optional[str] = None  # Name of the pet this task belongs to

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def mark_incomplete(self) -> None:
        """Mark this task as incomplete."""
        self.completed = False

    def is_urgent(self) -> bool:
        """Check if task is high priority."""
        return self.priority == Priority.HIGH

    def create_next_occurrence(self) -> Optional["Task"]:
        """Create a new task for the next occurrence if this is recurring."""
        if self.frequency == Frequency.AS_NEEDED:
            return None

        # Calculate next occurrence date
        if self.frequency == Frequency.DAILY:
            next_date = self.due_date + timedelta(days=1)
        elif self.frequency == Frequency.WEEKLY:
            next_date = self.due_date + timedelta(weeks=1)
        else:
            return None

        # Create a new task instance for next occurrence
        new_task = copy.deepcopy(self)
        new_task.task_id = f"{self.task_id}_next"
        new_task.due_date = next_date
        new_task.completed = False
        return new_task


@dataclass
class Pet:
    """Represents a pet that needs care tasks."""
    name: str
    species: str
    age: int
    breed: str
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task for this pet."""
        self.tasks.append(task)

    def remove_task(self, task_id: str) -> None:
        """Remove a task by ID."""
        self.tasks = [t for t in self.tasks if t.task_id != task_id]

    def get_tasks(self) -> List[Task]:
        """Get all tasks for this pet."""
        return self.tasks

    def get_incomplete_tasks(self) -> List[Task]:
        """Get incomplete tasks for this pet."""
        return [t for t in self.tasks if not t.completed]

    def get_tasks_sorted_by_time(self) -> List[Task]:
        """Get tasks sorted by scheduled time (HH:MM format)."""
        def time_to_minutes(time_str: Optional[str]) -> int:
            if not time_str:
                return 0
            try:
                hours, minutes = map(int, time_str.split(":"))
                return hours * 60 + minutes
            except (ValueError, AttributeError):
                return 0

        return sorted(self.tasks, key=lambda t: time_to_minutes(t.scheduled_time))

    def get_tasks_sorted_by_due_date(self) -> List[Task]:
        """Get tasks sorted by due date."""
        return sorted(self.tasks, key=lambda t: t.due_date)

    def filter_tasks_by_status(self, completed: bool) -> List[Task]:
        """Filter tasks by completion status."""
        return [t for t in self.tasks if t.completed == completed]

    def filter_tasks_by_priority(self, priority: Priority) -> List[Task]:
        """Filter tasks by priority level."""
        return [t for t in self.tasks if t.priority == priority]


@dataclass
class Owner:
    """Represents a pet owner who manages multiple pets."""
    name: str
    available_hours_per_day: float
    preferences: Dict[str, any] = field(default_factory=dict)
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's collection."""
        self.pets.append(pet)

    def remove_pet(self, pet_name: str) -> None:
        """Remove a pet by name."""
        self.pets = [p for p in self.pets if p.name != pet_name]

    def get_pets(self) -> List[Pet]:
        """Get all pets owned by this owner."""
        return self.pets

    def get_all_tasks(self) -> List[Task]:
        """Get all tasks across all pets."""
        all_tasks = []
        for pet in self.pets:
            all_tasks.extend(pet.get_tasks())
        return all_tasks

    def get_incomplete_tasks(self) -> List[Task]:
        """Get all incomplete tasks across all pets."""
        return [t for t in self.get_all_tasks() if not t.completed]

    def filter_tasks_by_pet(self, pet_name: str) -> List[Task]:
        """Get all tasks for a specific pet."""
        pet = next((p for p in self.pets if p.name == pet_name), None)
        return pet.get_tasks() if pet else []

    def filter_tasks_by_status(self, completed: bool) -> List[Task]:
        """Filter all tasks by completion status."""
        return [t for t in self.get_all_tasks() if t.completed == completed]

    def filter_tasks_by_priority(self, priority: Priority) -> List[Task]:
        """Filter all tasks by priority level."""
        return [t for t in self.get_all_tasks() if t.priority == priority]

    def get_all_tasks_sorted_by_time(self) -> List[Task]:
        """Get all tasks across all pets sorted by scheduled time."""
        def time_to_minutes(time_str: Optional[str]) -> int:
            if not time_str:
                return 0
            try:
                hours, minutes = map(int, time_str.split(":"))
                return hours * 60 + minutes
            except (ValueError, AttributeError):
                return 0

        return sorted(self.get_all_tasks(), key=lambda t: time_to_minutes(t.scheduled_time))

    def get_all_tasks_sorted_by_due_date(self) -> List[Task]:
        """Get all tasks across all pets sorted by due date."""
        return sorted(self.get_all_tasks(), key=lambda t: t.due_date)


@dataclass
class ScheduledTask:
    """Represents a task placed into a schedule with timing and reasoning."""
    task: Task
    start_hour: float
    end_hour: float
    reason: str = ""

    def duration(self) -> float:
        """Get the duration in hours."""
        return self.end_hour - self.start_hour


@dataclass
class Schedule:
    """Represents a daily schedule of tasks."""
    scheduled_tasks: List[ScheduledTask] = field(default_factory=list)
    total_duration_minutes: int = 0
    schedule_date: date = field(default_factory=date.today)

    def add_scheduled_task(self, scheduled_task: ScheduledTask) -> None:
        """Add a scheduled task to the schedule."""
        self.scheduled_tasks.append(scheduled_task)

    def get_tasks_by_time(self) -> List[ScheduledTask]:
        """Get all scheduled tasks ordered by start time."""
        return sorted(self.scheduled_tasks, key=lambda st: st.start_hour)

    def get_explanation(self) -> str:
        """Get a text explanation of the schedule."""
        if not self.scheduled_tasks:
            return "No tasks scheduled for this day."

        explanation = f"Daily schedule for {self.schedule_date}:\n"
        for st in self.get_tasks_by_time():
            explanation += f"  {st.start_hour:.1f} - {st.end_hour:.1f} hours: {st.task.description} ({st.reason})\n"
        return explanation


@dataclass
class ScheduleConflict:
    """Represents a scheduling conflict."""
    message: str
    task_ids: List[str] = field(default_factory=list)


class Scheduler:
    """The scheduling logic engine."""

    def create_daily_schedule(self, owner: Owner, schedule_date: date) -> Schedule:
        """Create an optimized daily schedule for an owner."""
        # Get incomplete tasks
        tasks = owner.get_incomplete_tasks()

        # If no tasks, return empty schedule
        if not tasks:
            return Schedule(schedule_date=schedule_date)

        # Prioritize tasks
        prioritized = self._prioritize_tasks(tasks)

        # Fit tasks into available hours
        scheduled = self._fit_tasks_in_day(prioritized, owner.available_hours_per_day)

        # Create schedule
        schedule = Schedule(schedule_date=schedule_date)
        for scheduled_task in scheduled:
            schedule.add_scheduled_task(scheduled_task)

        return schedule

    def detect_conflicts(self, schedule: Schedule) -> List[ScheduleConflict]:
        """Detect scheduling conflicts (tasks at the same time)."""
        conflicts = []
        scheduled_tasks = schedule.get_tasks_by_time()

        # Check for exact time matches
        for i in range(len(scheduled_tasks)):
            for j in range(i + 1, len(scheduled_tasks)):
                task_i = scheduled_tasks[i]
                task_j = scheduled_tasks[j]

                # Check if tasks overlap (same start time)
                if abs(task_i.start_hour - task_j.start_hour) < 0.01:  # Account for float precision
                    conflict = ScheduleConflict(
                        message=f"Conflict: '{task_i.task.description}' and '{task_j.task.description}' are scheduled at the same time ({task_i.start_hour:.1f}h)",
                        task_ids=[task_i.task.task_id, task_j.task.task_id]
                    )
                    conflicts.append(conflict)

        return conflicts

    def _prioritize_tasks(self, tasks: List[Task]) -> List[Task]:
        """Sort tasks by priority (high to low)."""
        return sorted(tasks, key=lambda t: t.priority.value, reverse=True)

    def _fit_tasks_in_day(self, tasks: List[Task], hours_available: float) -> List[ScheduledTask]:
        """Fit prioritized tasks into available hours."""
        scheduled_tasks = []
        current_hour = 0.0
        minutes_available = hours_available * 60

        for task in tasks:
            if current_hour * 60 + task.duration_minutes <= minutes_available:
                start = current_hour
                end = current_hour + (task.duration_minutes / 60)

                reason = f"Priority {task.priority.name.lower()}, {task.frequency.value}"
                scheduled_task = ScheduledTask(
                    task=task,
                    start_hour=start,
                    end_hour=end,
                    reason=reason
                )
                scheduled_tasks.append(scheduled_task)
                current_hour = end

        return scheduled_tasks
