# PawPal+ System UML Diagram

## Class Diagram (Mermaid)

```mermaid
classDiagram
    class Task {
        -description: str
        -time: time
        -frequency: str
        -date: date
        -completion_status: bool
        +get_description() str
        +get_time() time
        +get_frequency() str
        +get_date() date
        +is_completed() bool
        +mark_completed() void
        +is_recurring() bool
        +get_next_occurrence() Task
    }
    
    class Pet {
        -name: str
        -breed: str
        -owner_id: int
        -tasks: List[Task]
        +add_task(task: Task) void
        +remove_task(task: Task) void
        +get_tasks() List[Task]
    }
    
    class Owner {
        -name: str
        -owner_id: int
        -pets: List[Pet]
        +add_pet(pet: Pet) void
        +remove_pet(pet: Pet) void
        +get_pets() List[Pet]
        +get_all_tasks() List[Task]
    }
    
    class Scheduler {
        -owner: Owner
        +get_tasks_for_time(task_time) List[Task]
        +get_tasks_by_frequency(frequency) List[Task]
        +organize_tasks() List[Task]
        +mark_task_completed(task) void
        +get_pending_tasks() List[Task]
        +find_scheduling_conflicts() dict
        +has_conflicts() bool
        +get_conflict_summary() str
    }
    
    Pet "1" --> "*" Task : contains
    Owner "1" --> "*" Pet : manages
    Scheduler "1" --> "1" Owner : uses
    
    note "Scheduler orchestrates\nthe entire system,\nusing Owner data\nto organize & track tasks"
```

## Architecture Overview

- **Task**: Represents a single pet care activity with time, frequency, and completion status
- **Pet**: Manages a collection of tasks for a specific pet
- **Owner**: Manages multiple pets and aggregates all their tasks
- **Scheduler**: Orchestrates the system, providing sorting, conflict detection, and recurring task management
