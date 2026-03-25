# PawPal+ System UML Diagram

```mermaid
classDiagram
    Owner "1" -- "*" Pet : owns
    Pet "1" -- "*" Task : has
    Scheduler "1" -- "1" Owner : schedules_for
    Schedule "1" -- "*" ScheduledTask : contains
    ScheduledTask "1" -- "1" Task : wraps

    class Owner {
        -name: str
        -available_hours_per_day: float
        -preferences: dict
        +add_pet(pet: Pet) void
        +remove_pet(pet_name: str) void
        +get_all_tasks() List~Task~
        +get_pets() List~Pet~
    }

    class Pet {
        -name: str
        -species: str
        -age: int
        -breed: str
        -tasks: List~Task~
        +add_task(task: Task) void
        +remove_task(task_id: str) void
        +get_tasks() List~Task~
        +get_incomplete_tasks() List~Task~
    }

    class Task {
        -task_id: str
        -description: str
        -duration_minutes: int
        -priority: str
        -completed: bool
        -frequency: str
        +mark_complete() void
        +mark_incomplete() void
        +is_urgent() bool
    }

    class Schedule {
        -scheduled_tasks: List~ScheduledTask~
        -total_duration_minutes: int
        -date: date
        +get_tasks_by_time() List~ScheduledTask~
        +get_explanation() str
    }

    class ScheduledTask {
        -task: Task
        -start_hour: float
        -end_hour: float
        -reason: str
    }

    class Scheduler {
        +create_daily_schedule(owner: Owner, date: date) Schedule
        -prioritize_tasks(tasks: List~Task~) List~Task~
        -fit_tasks_in_day(tasks: List~Task~, hours_available: float) List~ScheduledTask~
    }
```

## Key Relationships

- **Owner has many Pets** (1:many) — A pet owner can manage multiple pets
- **Pet has many Tasks** (1:many) — Each pet needs multiple care tasks
- **Scheduler works with Owner** (1:1) — Takes owner data and generates schedules
- **Schedule contains ScheduledTasks** (1:many) — Each schedule is a collection of tasks placed in time slots
- **ScheduledTask wraps Task** — Adds timing and reasoning to a base task

## Design Rationale

- **Task as dataclass** — Simple, immutable data structure for care activities
- **Pet as container** — Organizes tasks by which pet needs them
- **Owner as aggregate** — Central entity that holds all pets and provides access to global constraints
- **Scheduler as utility** — Stateless logic engine that takes owner state and produces schedules
- **Schedule as result object** — Captures the output (what tasks, when, why) so it can be explained and displayed
