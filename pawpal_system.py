from dataclasses import dataclass, field
from typing import List
from datetime import time, date, timedelta


@dataclass
class Task:
    """Represents a single activity."""
    description: str
    time: time
    frequency: str  # daily, weekly, monthly, once
    date: date = field(default_factory=date.today)
    completion_status: bool = False
    
    def get_description(self) -> str:
        return self.description
    
    def get_time(self) -> time:
        return self.time
    
    def get_frequency(self) -> str:
        return self.frequency
    
    def get_date(self) -> date:
        return self.date
    
    def is_completed(self) -> bool:
        return self.completion_status
    
    def mark_completed(self) -> None:
        self.completion_status = True
    
    def is_recurring(self) -> bool:
        """Check if this task recurs based on frequency."""
        return self.frequency in ["daily", "weekly", "monthly"]
    
    def get_next_occurrence(self) -> 'Task':
        """Create a new task instance for the next recurrence."""
        if not self.is_recurring():
            return None
        
        if self.frequency == "daily":
            next_date = self.date + timedelta(days=1)
        elif self.frequency == "weekly":
            next_date = self.date + timedelta(weeks=1)
        elif self.frequency == "monthly":
            next_date = self.date + timedelta(days=30)
        else:
            return None
        
        return Task(
            description=self.description,
            time=self.time,
            frequency=self.frequency,
            date=next_date,
            completion_status=False
        )


@dataclass
class Pet:
    """Stores pet details and a list of tasks."""
    name: str
    breed: str
    owner_id: int
    tasks: List[Task] = field(default_factory=list)
    
    def add_task(self, task: Task) -> None:
        self.tasks.append(task)
    
    def remove_task(self, task: Task) -> None:
        if task in self.tasks:
            self.tasks.remove(task)
    
    def get_tasks(self) -> List[Task]:
        return self.tasks


@dataclass
class Owner:
    """Manages multiple pets and provides access to all their tasks."""
    name: str
    owner_id: int
    pets: List[Pet] = field(default_factory=list)
    
    def add_pet(self, pet: Pet) -> None:
        self.pets.append(pet)
    
    def remove_pet(self, pet: Pet) -> None:
        if pet in self.pets:
            self.pets.remove(pet)
    
    def get_pets(self) -> List[Pet]:
        return self.pets
    
    def get_all_tasks(self) -> List[Task]:
        all_tasks = []
        for pet in self.pets:
            all_tasks.extend(pet.get_tasks())
        return all_tasks


@dataclass
class Scheduler:
    """The "Brain" that retrieves, organizes, and manages tasks across pets."""
    owner: Owner
    
    def get_tasks_for_time(self, task_time: time) -> List[Task]:
        all_tasks = self.owner.get_all_tasks()
        return [task for task in all_tasks if task.get_time() == task_time]
    
    def get_tasks_by_frequency(self, frequency: str) -> List[Task]:
        all_tasks = self.owner.get_all_tasks()
        return [task for task in all_tasks if task.get_frequency() == frequency]
    
    def organize_tasks(self) -> List[Task]:
        all_tasks = self.owner.get_all_tasks()
        return sorted(all_tasks, key=lambda task: task.get_time())
    
    def mark_task_completed(self, task: Task) -> None:
        """Mark a task complete and auto-create next occurrence if recurring."""
        all_tasks = self.owner.get_all_tasks()
        if task in all_tasks:
            task.mark_completed()
            
            # If task is recurring, create next occurrence
            if task.is_recurring():
                next_task = task.get_next_occurrence()
                if next_task:
                    # Find which pet owns this task and add the next occurrence
                    for pet in self.owner.get_pets():
                        if task in pet.get_tasks():
                            pet.add_task(next_task)
                            break
    
    def get_pending_tasks(self) -> List[Task]:
        all_tasks = self.owner.get_all_tasks()
        return [task for task in all_tasks if not task.is_completed()]
    
    def find_scheduling_conflicts(self) -> dict:
        """
        Detect if multiple tasks are scheduled at the same time.
        Returns a dictionary where keys are times and values are lists of conflicting tasks.
        """
        all_tasks = self.owner.get_all_tasks()
        time_groups = {}
        
        for task in all_tasks:
            task_time = task.get_time()
            if task_time not in time_groups:
                time_groups[task_time] = []
            time_groups[task_time].append(task)
        
        # Filter to only return times with multiple tasks (conflicts)
        conflicts = {time: tasks for time, tasks in time_groups.items() if len(tasks) > 1}
        return conflicts
    
    def has_conflicts(self) -> bool:
        """Check if there are any scheduling conflicts."""
        return len(self.find_scheduling_conflicts()) > 0
    
    def get_conflict_summary(self) -> str:
        """Generate a human-readable summary of scheduling conflicts."""
        conflicts = self.find_scheduling_conflicts()
        
        if not conflicts:
            return "No scheduling conflicts detected ✓"
        
        summary = f"⚠️  Found {len(conflicts)} time slot(s) with conflicts:\n"
        for task_time, tasks in sorted(conflicts.items()):
            summary += f"\n  {task_time.strftime('%H:%M')} - {len(tasks)} tasks scheduled:\n"
            for task in tasks:
                summary += f"    • {task.get_description()}\n"
        
        return summary
