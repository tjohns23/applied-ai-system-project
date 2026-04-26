from pawpal_system import Task, Pet, Owner, Scheduler
from datetime import time


def main():
    # Create an Owner
    owner = Owner(name="John Smith", owner_id=1)
    
    # Create Pets
    dog = Pet(name="Buddy", breed="Golden Retriever", owner_id=1)
    cat = Pet(name="Whiskers", breed="Siamese", owner_id=1)
    
    # Add pets to owner
    owner.add_pet(dog)
    owner.add_pet(cat)
    
    # Create Tasks with different times
    task1 = Task(description="Walk Buddy", time=time(9, 0), frequency="daily")
    task2 = Task(description="Feed Whiskers", time=time(12, 0), frequency="daily")
    task3 = Task(description="Groom Buddy", time=time(14, 30), frequency="weekly")
    task4 = Task(description="Play with Whiskers", time=time(16, 0), frequency="daily")
    task5 = Task(description="Feed Buddy", time=time(18, 0), frequency="daily")
    
    # Add tasks to pets
    dog.add_task(task1)
    dog.add_task(task3)
    dog.add_task(task5)
    
    cat.add_task(task2)
    cat.add_task(task4)
    
    # Create a Scheduler
    scheduler = Scheduler(owner=owner)
    
    # Print Today's Schedule
    print("=" * 60)
    print("TODAY'S SCHEDULE FOR OWNER:", owner.name)
    print("=" * 60)
    
    organized_tasks = scheduler.organize_tasks()
    
    for task in organized_tasks:
        status = "✓ DONE" if task.is_completed() else "PENDING"
        print(f"{task.get_time().strftime('%H:%M')} - {task.get_description():30} [{status}] ({task.get_frequency()})")
    
    print("=" * 60)
    print(f"Total Tasks: {len(organized_tasks)}")
    print(f"Pending Tasks: {len(scheduler.get_pending_tasks())}")
    print("=" * 60)
    
    # Example: Mark a task as completed
    print("\nMarking 'Walk Buddy' as completed...")
    scheduler.mark_task_completed(task1)
    
    print("\nUPDATED PENDING TASKS:")
    print("=" * 60)
    for task in scheduler.get_pending_tasks():
        print(f"{task.get_time().strftime('%H:%M')} - {task.get_description():30} ({task.get_frequency()})")
    print("=" * 60)


if __name__ == "__main__":
    main()
