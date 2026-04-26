import unittest
from datetime import time, date, timedelta
from pawpal_system import Task, Pet, Owner, Scheduler


class TestPawpalSystem(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test."""
        self.task = Task(description="Walk dog", time=time(9, 0), frequency="daily")
        self.pet = Pet(name="Buddy", breed="Golden Retriever", owner_id=1)
        self.owner = Owner(name="John", owner_id=1)
    
    def test_task_completion(self):
        """Verify that calling mark_completed() changes the task's status."""
        # Initially, task should not be completed
        self.assertFalse(self.task.is_completed(), "Task should initially be incomplete")
        
        # Mark task as completed
        self.task.mark_completed()
        
        # Task should now be completed
        self.assertTrue(self.task.is_completed(), "Task should be marked as completed")
    
    def test_task_addition_to_pet(self):
        """Verify that adding a task to a Pet increases that pet's task count."""
        # Initially, pet should have no tasks
        self.assertEqual(len(self.pet.get_tasks()), 0, "Pet should start with 0 tasks")
        
        # Add first task
        self.pet.add_task(self.task)
        self.assertEqual(len(self.pet.get_tasks()), 1, "Pet should have 1 task after adding")
        
        # Add second task
        task2 = Task(description="Feed dog", time=time(12, 0), frequency="daily")
        self.pet.add_task(task2)
        self.assertEqual(len(self.pet.get_tasks()), 2, "Pet should have 2 tasks after adding second task")
    
    def test_daily_task_is_recurring(self):
        """Verify that daily tasks are marked as recurring."""
        daily_task = Task(description="Feed", time=time(8, 0), frequency="daily")
        self.assertTrue(daily_task.is_recurring(), "Daily task should be recurring")
    
    def test_weekly_task_is_recurring(self):
        """Verify that weekly tasks are marked as recurring."""
        weekly_task = Task(description="Groom", time=time(10, 0), frequency="weekly")
        self.assertTrue(weekly_task.is_recurring(), "Weekly task should be recurring")
    
    def test_once_task_is_not_recurring(self):
        """Verify that 'once' frequency tasks are not recurring."""
        once_task = Task(description="Vet visit", time=time(14, 0), frequency="once")
        self.assertFalse(once_task.is_recurring(), "Once-only task should not be recurring")
    
    def test_get_next_occurrence_daily(self):
        """Verify that next occurrence of daily task is tomorrow."""
        daily_task = Task(description="Walk", time=time(9, 0), frequency="daily", date=date(2026, 3, 30))
        next_task = daily_task.get_next_occurrence()
        
        self.assertEqual(next_task.get_date(), date(2026, 3, 31), "Daily task next occurrence should be tomorrow")
        self.assertEqual(next_task.get_description(), daily_task.get_description(), "Description should match")
        self.assertFalse(next_task.is_completed(), "Next occurrence should be incomplete")
    
    def test_get_next_occurrence_weekly(self):
        """Verify that next occurrence of weekly task is in 7 days."""
        weekly_task = Task(description="Groom", time=time(10, 0), frequency="weekly", date=date(2026, 3, 30))
        next_task = weekly_task.get_next_occurrence()
        
        self.assertEqual(next_task.get_date(), date(2026, 4, 6), "Weekly task next occurrence should be in 7 days")
    
    def test_get_next_occurrence_none_recur(self):
        """Verify that 'once' tasks return None for next occurrence."""
        once_task = Task(description="Vet visit", time=time(14, 0), frequency="once")
        next_task = once_task.get_next_occurrence()
        
        self.assertIsNone(next_task, "Non-recurring task should return None for next occurrence")
    
    def test_auto_create_next_occurrence_on_complete(self):
        """Verify that marking a recurring task complete auto-creates the next occurrence."""
        self.owner.add_pet(self.pet)
        daily_task = Task(description="Walk", time=time(9, 0), frequency="daily", date=date(2026, 3, 30))
        self.pet.add_task(daily_task)
        
        scheduler = Scheduler(owner=self.owner)
        
        # Pet should have 1 task initially
        self.assertEqual(len(self.pet.get_tasks()), 1, "Pet should start with 1 task")
        
        # Mark task as completed
        scheduler.mark_task_completed(daily_task)
        
        # Pet should now have 2 tasks (original + next occurrence)
        self.assertEqual(len(self.pet.get_tasks()), 2, "Pet should have 2 tasks after marking recurring task complete")
        
        # Check that next task is today + 1
        next_task = [t for t in self.pet.get_tasks() if not t.is_completed()][0]
        self.assertEqual(next_task.get_date(), date(2026, 3, 31), "New task should be scheduled for next day")
    
    def test_no_conflicts_with_different_times(self):
        """Verify that tasks at different times don't conflict."""
        self.owner.add_pet(self.pet)
        task1 = Task(description="Walk", time=time(9, 0), frequency="daily")
        task2 = Task(description="Feed", time=time(12, 0), frequency="daily")
        
        self.pet.add_task(task1)
        self.pet.add_task(task2)
        
        scheduler = Scheduler(owner=self.owner)
        conflicts = scheduler.find_scheduling_conflicts()
        
        self.assertEqual(len(conflicts), 0, "Tasks at different times should have no conflicts")
        self.assertFalse(scheduler.has_conflicts(), "has_conflicts() should return False")
    
    def test_detect_conflict_same_time(self):
        """Verify that tasks scheduled at the same time are detected as conflicts."""
        self.owner.add_pet(self.pet)
        task1 = Task(description="Walk", time=time(9, 0), frequency="daily")
        task2 = Task(description="Groom", time=time(9, 0), frequency="daily")
        
        self.pet.add_task(task1)
        self.pet.add_task(task2)
        
        scheduler = Scheduler(owner=self.owner)
        conflicts = scheduler.find_scheduling_conflicts()
        
        self.assertEqual(len(conflicts), 1, "Should find 1 conflicting time slot")
        self.assertTrue(time(9, 0) in conflicts, "9:00 should be in conflicts")
        self.assertEqual(len(conflicts[time(9, 0)]), 2, "9:00 should have 2 tasks")
        self.assertTrue(scheduler.has_conflicts(), "has_conflicts() should return True")
    
    def test_detect_multiple_conflicts(self):
        """Verify that multiple time conflicts are all detected."""
        self.owner.add_pet(self.pet)
        # Create 3 tasks at 9:00 and 2 tasks at 14:00
        task1 = Task(description="Walk", time=time(9, 0), frequency="daily")
        task2 = Task(description="Groom", time=time(9, 0), frequency="daily")
        task3 = Task(description="Play", time=time(9, 0), frequency="daily")
        task4 = Task(description="Training", time=time(14, 0), frequency="daily")
        task5 = Task(description="Nap time", time=time(14, 0), frequency="daily")
        
        for task in [task1, task2, task3, task4, task5]:
            self.pet.add_task(task)
        
        scheduler = Scheduler(owner=self.owner)
        conflicts = scheduler.find_scheduling_conflicts()
        
        self.assertEqual(len(conflicts), 2, "Should find 2 conflicting time slots")
        self.assertEqual(len(conflicts[time(9, 0)]), 3, "9:00 should have 3 tasks")
        self.assertEqual(len(conflicts[time(14, 0)]), 2, "14:00 should have 2 tasks")
    
    def test_conflict_summary_no_conflicts(self):
        """Verify that conflict summary is clear when there are no conflicts."""
        self.owner.add_pet(self.pet)
        task1 = Task(description="Walk", time=time(9, 0), frequency="daily")
        self.pet.add_task(task1)
        
        scheduler = Scheduler(owner=self.owner)
        summary = scheduler.get_conflict_summary()
        
        self.assertIn("No scheduling conflicts", summary, "Summary should indicate no conflicts")
    
    def test_conflict_summary_with_conflicts(self):
        """Verify that conflict summary shows all conflicts clearly."""
        self.owner.add_pet(self.pet)
        task1 = Task(description="Walk", time=time(9, 0), frequency="daily")
        task2 = Task(description="Groom", time=time(9, 0), frequency="daily")
        
        self.pet.add_task(task1)
        self.pet.add_task(task2)
        
        scheduler = Scheduler(owner=self.owner)
        summary = scheduler.get_conflict_summary()
        
        self.assertIn("09:00", summary, "Summary should show the conflicting time")
        self.assertIn("Walk", summary, "Summary should include task names")
        self.assertIn("Groom", summary, "Summary should include task names")
    
    # ===== SORTING CORRECTNESS TESTS =====
    
    def test_organize_tasks_empty_list(self):
        """Verify that sorting an empty task list returns empty list."""
        self.owner.add_pet(self.pet)
        scheduler = Scheduler(owner=self.owner)
        
        organized = scheduler.organize_tasks()
        self.assertEqual(len(organized), 0, "Empty task list should return empty list")
        self.assertIsInstance(organized, list, "Result should be a list")
    
    def test_organize_tasks_single_task(self):
        """Verify that a single task sorts trivially."""
        self.owner.add_pet(self.pet)
        task = Task(description="Walk", time=time(14, 30), frequency="once")
        self.pet.add_task(task)
        
        scheduler = Scheduler(owner=self.owner)
        organized = scheduler.organize_tasks()
        
        self.assertEqual(len(organized), 1, "Should have 1 task")
        self.assertEqual(organized[0].get_description(), "Walk", "Task description should match")
    
    def test_organize_tasks_already_sorted(self):
        """Verify tasks already in time order remain sorted."""
        self.owner.add_pet(self.pet)
        task1 = Task(description="Early", time=time(6, 0), frequency="daily")
        task2 = Task(description="Mid", time=time(12, 0), frequency="daily")
        task3 = Task(description="Late", time=time(18, 0), frequency="daily")
        
        for task in [task1, task2, task3]:
            self.pet.add_task(task)
        
        scheduler = Scheduler(owner=self.owner)
        organized = scheduler.organize_tasks()
        
        self.assertEqual(organized[0].get_time(), time(6, 0), "First task should be 6:00")
        self.assertEqual(organized[1].get_time(), time(12, 0), "Second task should be 12:00")
        self.assertEqual(organized[2].get_time(), time(18, 0), "Third task should be 18:00")
    
    def test_organize_tasks_reverse_order(self):
        """Verify that tasks added in reverse time order are sorted correctly."""
        self.owner.add_pet(self.pet)
        task1 = Task(description="Late", time=time(20, 0), frequency="daily")
        task2 = Task(description="Mid", time=time(12, 0), frequency="daily")
        task3 = Task(description="Early", time=time(8, 0), frequency="daily")
        
        for task in [task1, task2, task3]:
            self.pet.add_task(task)
        
        scheduler = Scheduler(owner=self.owner)
        organized = scheduler.organize_tasks()
        
        times = [task.get_time() for task in organized]
        self.assertEqual(times, [time(8, 0), time(12, 0), time(20, 0)], "Tasks should be sorted by time")
    
    def test_organize_tasks_midnight_edge_case(self):
        """Verify that midnight (00:00) sorts to the beginning."""
        self.owner.add_pet(self.pet)
        task1 = Task(description="Morning", time=time(9, 0), frequency="daily")
        task2 = Task(description="Midnight", time=time(0, 0), frequency="daily")
        task3 = Task(description="Evening", time=time(18, 0), frequency="daily")
        
        for task in [task1, task2, task3]:
            self.pet.add_task(task)
        
        scheduler = Scheduler(owner=self.owner)
        organized = scheduler.organize_tasks()
        
        self.assertEqual(organized[0].get_time(), time(0, 0), "Midnight should be first")
        self.assertEqual(organized[1].get_time(), time(9, 0), "Morning should be second")
        self.assertEqual(organized[2].get_time(), time(18, 0), "Evening should be last")
    
    def test_organize_tasks_multiple_same_time_stable(self):
        """Verify that multiple tasks at same time maintain relative order (stable sort)."""
        self.owner.add_pet(self.pet)
        task1 = Task(description="Task A", time=time(9, 0), frequency="daily")
        task2 = Task(description="Task B", time=time(9, 0), frequency="daily")
        task3 = Task(description="Task C", time=time(9, 0), frequency="daily")
        
        for task in [task1, task2, task3]:
            self.pet.add_task(task)
        
        scheduler = Scheduler(owner=self.owner)
        organized = scheduler.organize_tasks()
        
        self.assertEqual(len(organized), 3, "Should have 3 tasks")
        for i, expected_task in enumerate([task1, task2, task3]):
            self.assertEqual(organized[i].get_description(), expected_task.get_description(), 
                           f"Order at position {i} should be preserved")
    
    def test_organize_tasks_mixed_times_descending(self):
        """Verify complex mixed sorting scenario."""
        self.owner.add_pet(self.pet)
        times_and_descs = [
            (time(19, 45), "Dinner"),
            (time(7, 0), "Breakfast"),
            (time(19, 45), "Evening walk"),
            (time(12, 30), "Lunch"),
            (time(7, 0), "Morning walk"),
        ]
        
        for t, desc in times_and_descs:
            self.pet.add_task(Task(description=desc, time=t, frequency="daily"))
        
        scheduler = Scheduler(owner=self.owner)
        organized = scheduler.organize_tasks()
        
        times = [task.get_time() for task in organized]
        self.assertEqual(times, sorted(times), "Tasks should be sorted in ascending time order")
        self.assertEqual(times[0], time(7, 0), "Earliest time first")
        self.assertEqual(times[-1], time(19, 45), "Latest time last")
    
    # ===== RECURRENCE LOGIC EDGE CASES =====
    
    def test_recurring_task_completion_chain(self):
        """Verify that multiple mark_completed calls create proper chain."""
        self.owner.add_pet(self.pet)
        original_task = Task(description="Daily walk", time=time(9, 0), 
                            frequency="daily", date=date(2026, 3, 30))
        self.pet.add_task(original_task)
        
        scheduler = Scheduler(owner=self.owner)
        
        # First completion: creates March 31 task
        scheduler.mark_task_completed(original_task)
        self.assertEqual(len(self.pet.get_tasks()), 2, "Should have 2 tasks after first completion")
        
        # Get the new pending task
        pending = [t for t in self.pet.get_tasks() if not t.is_completed()][0]
        self.assertEqual(pending.get_date(), date(2026, 3, 31), "New task should be March 31")
        
        # Second completion: creates April 1 task
        scheduler.mark_task_completed(pending)
        self.assertEqual(len(self.pet.get_tasks()), 3, "Should have 3 tasks after second completion")
        
        # Verify dates are sequential
        all_tasks = sorted(self.pet.get_tasks(), key=lambda t: t.get_date())
        self.assertEqual(all_tasks[0].get_date(), date(2026, 3, 30))
        self.assertEqual(all_tasks[1].get_date(), date(2026, 3, 31))
        self.assertEqual(all_tasks[2].get_date(), date(2026, 4, 1))
    
    def test_monthly_task_month_end_edge_case(self):
        """Verify that monthly tasks handle month-end dates correctly."""
        # Start on Jan 31 - next occurrence should be sensible (around Feb 28)
        jan_31_task = Task(description="Groom", time=time(10, 0), 
                           frequency="monthly", date=date(2026, 1, 31))
        next_task = jan_31_task.get_next_occurrence()
        
        # Current implementation adds 30 days: Jan 31 + 30 days = Mar 2
        self.assertEqual(next_task.get_date(), date(2026, 3, 2), 
                        "Monthly task from Jan 31 should be March 2 (30 days forward)")
    
    def test_monthly_task_leap_year(self):
        """Verify monthly tasks work in leap year scenarios."""
        # Feb 28 in leap year 2024 + 30 days = Mar 29
        feb_28_task = Task(description="Checkup", time=time(14, 0), 
                          frequency="monthly", date=date(2024, 2, 28))
        next_task = feb_28_task.get_next_occurrence()
        
        expected_date = date(2024, 2, 28) + timedelta(days=30)
        self.assertEqual(next_task.get_date(), expected_date, 
                        "Monthly task should advance 30 days regardless of leap year")
    
    def test_get_next_occurrence_monthly(self):
        """Verify that next occurrence of monthly task is in ~30 days."""
        monthly_task = Task(description="Checkup", time=time(10, 0), 
                           frequency="monthly", date=date(2026, 3, 15))
        next_task = monthly_task.get_next_occurrence()
        
        expected_date = date(2026, 4, 14)  # March 15 + 30 days
        self.assertEqual(next_task.get_date(), expected_date, 
                        "Monthly task next occurrence should be ~30 days later")
    
    def test_non_recurring_task_never_creates_occurrence(self):
        """Verify that 'once' tasks don't auto-create occurrences."""
        self.owner.add_pet(self.pet)
        once_task = Task(description="Vet visit", time=time(14, 0), 
                        frequency="once", date=date(2026, 3, 30))
        self.pet.add_task(once_task)
        
        scheduler = Scheduler(owner=self.owner)
        
        # Mark the once task as completed
        scheduler.mark_task_completed(once_task)
        
        # Should still have only 1 task (not auto-created)
        self.assertEqual(len(self.pet.get_tasks()), 1, 
                        "Once task should not auto-create next occurrence")
        self.assertTrue(self.pet.get_tasks()[0].is_completed(), 
                       "Original task should be marked complete")
    
    def test_get_tasks_by_frequency_daily(self):
        """Verify filtering tasks by daily frequency."""
        self.owner.add_pet(self.pet)
        daily1 = Task(description="Walk", time=time(9, 0), frequency="daily")
        daily2 = Task(description="Feed", time=time(18, 0), frequency="daily")
        weekly = Task(description="Groom", time=time(10, 0), frequency="weekly")
        
        for task in [daily1, daily2, weekly]:
            self.pet.add_task(task)
        
        scheduler = Scheduler(owner=self.owner)
        daily_tasks = scheduler.get_tasks_by_frequency("daily")
        
        self.assertEqual(len(daily_tasks), 2, "Should find 2 daily tasks")
        self.assertIn(daily1, daily_tasks, "First daily task should be in results")
        self.assertIn(daily2, daily_tasks, "Second daily task should be in results")
        self.assertNotIn(weekly, daily_tasks, "Weekly task should not be in results")
    
    def test_get_tasks_by_frequency_all_types(self):
        """Verify frequency filtering works for all frequency types."""
        self.owner.add_pet(self.pet)
        daily = Task(description="Daily", time=time(8, 0), frequency="daily")
        weekly = Task(description="Weekly", time=time(9, 0), frequency="weekly")
        monthly = Task(description="Monthly", time=time(10, 0), frequency="monthly")
        once = Task(description="Once", time=time(11, 0), frequency="once")
        
        for task in [daily, weekly, monthly, once]:
            self.pet.add_task(task)
        
        scheduler = Scheduler(owner=self.owner)
        
        self.assertEqual(len(scheduler.get_tasks_by_frequency("daily")), 1, "1 daily task")
        self.assertEqual(len(scheduler.get_tasks_by_frequency("weekly")), 1, "1 weekly task")
        self.assertEqual(len(scheduler.get_tasks_by_frequency("monthly")), 1, "1 monthly task")
        self.assertEqual(len(scheduler.get_tasks_by_frequency("once")), 1, "1 once task")
    
    # ===== CONFLICT DETECTION EDGE CASES =====
    
    def test_conflict_detection_empty_schedule(self):
        """Verify conflict detection safely handles empty schedule."""
        self.owner.add_pet(self.pet)
        scheduler = Scheduler(owner=self.owner)
        
        conflicts = scheduler.find_scheduling_conflicts()
        self.assertEqual(len(conflicts), 0, "Empty schedule should have no conflicts")
        self.assertFalse(scheduler.has_conflicts(), "has_conflicts should return False")
    
    def test_conflict_detection_ignore_completed_tasks(self):
        """Verify whether completed tasks count toward conflicts."""
        self.owner.add_pet(self.pet)
        task1 = Task(description="Walk", time=time(9, 0), frequency="daily")
        task2 = Task(description="Groom", time=time(9, 0), frequency="daily")
        
        self.pet.add_task(task1)
        self.pet.add_task(task2)
        
        # Mark one as completed
        task1.mark_completed()
        
        scheduler = Scheduler(owner=self.owner)
        conflicts = scheduler.find_scheduling_conflicts()
        
        # Current behavior: both are included in conflicts regardless of completion
        # This test documents the behavior - adjust assertion based on desired behavior
        self.assertEqual(len(conflicts[time(9, 0)]), 2, 
                        "Both completed and pending tasks are included in conflict detection")
    
    def test_conflict_detection_many_tasks_same_time(self):
        """Verify all tasks in a major conflict are properly detected (5+ tasks)."""
        self.owner.add_pet(self.pet)
        for i in range(5):
            task = Task(description=f"Task {i+1}", time=time(9, 0), frequency="daily")
            self.pet.add_task(task)
        
        scheduler = Scheduler(owner=self.owner)
        conflicts = scheduler.find_scheduling_conflicts()
        
        self.assertEqual(len(conflicts), 1, "Should find 1 conflicting time")
        self.assertEqual(len(conflicts[time(9, 0)]), 5, "All 5 tasks should be in conflict list")
    
    def test_conflict_with_all_tasks_same_time(self):
        """Verify detection when 100% of tasks conflict."""
        self.owner.add_pet(self.pet)
        for i in range(3):
            task = Task(description=f"Simultaneous {i+1}", time=time(15, 30), frequency="daily")
            self.pet.add_task(task)
        
        scheduler = Scheduler(owner=self.owner)
        
        self.assertTrue(scheduler.has_conflicts(), "Should detect conflict")
        conflicts = scheduler.find_scheduling_conflicts()
        self.assertEqual(len(conflicts), 1, "Should have 1 conflicting time")
        self.assertEqual(len(conflicts[time(15, 30)]), 3, "All 3 tasks should conflict")
    
    def test_conflict_across_multiple_pets(self):
        """Verify conflict detection works across multiple pets."""
        pet1 = Pet(name="Buddy", breed="Golden", owner_id=1)
        pet2 = Pet(name="Max", breed="Lab", owner_id=1)
        self.owner.add_pet(pet1)
        self.owner.add_pet(pet2)
        
        task1 = Task(description="Buddy walk", time=time(9, 0), frequency="daily")
        task2 = Task(description="Max walk", time=time(9, 0), frequency="daily")
        
        pet1.add_task(task1)
        pet2.add_task(task2)
        
        scheduler = Scheduler(owner=self.owner)
        conflicts = scheduler.find_scheduling_conflicts()
        
        self.assertEqual(len(conflicts), 1, "Should detect conflict across pets")
        self.assertEqual(len(conflicts[time(9, 0)]), 2, "Both pet tasks should conflict")
    
    def test_get_tasks_for_specific_time(self):
        """Verify retrieval of all tasks at a specific time."""
        self.owner.add_pet(self.pet)
        task1 = Task(description="Walk", time=time(9, 0), frequency="daily")
        task2 = Task(description="Groom", time=time(9, 0), frequency="daily")
        task3 = Task(description="Feed", time=time(12, 0), frequency="daily")
        
        for task in [task1, task2, task3]:
            self.pet.add_task(task)
        
        scheduler = Scheduler(owner=self.owner)
        tasks_at_9 = scheduler.get_tasks_for_time(time(9, 0))
        tasks_at_12 = scheduler.get_tasks_for_time(time(12, 0))
        
        self.assertEqual(len(tasks_at_9), 2, "Should find 2 tasks at 9:00")
        self.assertEqual(len(tasks_at_12), 1, "Should find 1 task at 12:00")
        self.assertIn(task1, tasks_at_9, "Walk should be at 9:00")
        self.assertIn(task3, tasks_at_12, "Feed should be at 12:00")
    
    def test_get_pending_tasks_filters_completed(self):
        """Verify that get_pending_tasks excludes completed tasks."""
        self.owner.add_pet(self.pet)
        task1 = Task(description="Walk", time=time(9, 0), frequency="daily")
        task2 = Task(description="Feed", time=time(12, 0), frequency="daily")
        
        self.pet.add_task(task1)
        self.pet.add_task(task2)
        
        task1.mark_completed()
        
        scheduler = Scheduler(owner=self.owner)
        pending = scheduler.get_pending_tasks()
        
        self.assertEqual(len(pending), 1, "Should have 1 pending task")
        self.assertNotIn(task1, pending, "Completed task should not be pending")
        self.assertIn(task2, pending, "Incomplete task should be pending")


if __name__ == "__main__":
    unittest.main()
