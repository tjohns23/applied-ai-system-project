# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?
Classes:
    Task - Includes a name duration and priority. These will go into the calendar and be tracked by the assistant. 
    Preference - Includes a description, task_type, and preferred time. These will be considered for scheduling tasks
    Pet - Includes a name, breed, and owner preferences. Its core responsibility is to list the owner's preferences. 
    DailySchedule - Includes a start time and end time. This is the schedule that contains the tasks for the pet. 
    Assistant - Includes a name, schedule, and pet. This is the high level assistant that manages the schedule and tasks for the pet. 

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

One change that was made was to add a ScheduledTask wrapper class around the task class. This creates a mapping from tasks to times that allows my DailySchedule to map tasks to their times.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

The scheduler checks all tasks (including completed ones) for conflicts, rather than filtering to only pending tasks. 

Tradeoff:
- Pro: Complete historical view—you can see what conflicts existed, even if tasks are done
- Con: More data to process; completed tasks clutter the conflict report; user might expect "conflicts in my *active* schedule" not past work

Why it's reasonable: For a pet owner planning ahead, showing all time slots (including completed tasks) is actually helpful for understanding the full picture of what they're trying to fit together. If they complete "Walk" at 9am but then realize they also need "Groom" at 9am on the same day, they'd want to know about that conflict. Filtering to pending-only would hide this planning problem.


---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?
I used AI for mostly for the coding and refactoring. Most of the design choices were my own. 
I particularly find that telling the agent what not to do in a prompt is helpful for getting outputs that are closer to what I expect. 

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?
When discussing tradeoffs between certain algorithms and logic implementations, copilot suggested adding some of the 'low-risk changes' like returning as soon as a conflict is found. I rejected these changes because the time complexity remains the same and the runtime improvement would've been marginal at best. Instead we keep a system that allows us to check all conflicts which is much more valuable for a UX perspective.

---

## 4. Testing and Verification

**a. What you tested**

Recurring task automation (daily/weekly tasks generate next instances when marked complete), conflict detection (multiple tasks at the same time), and task completion status. These matter because they're the core features. If tasks don't recur properly or conflicts aren't caught, the scheduler fails its main job.

**b. Confidence**

Moderately confident that core logic works. What I'd test next: edge cases like tasks at 11:59pm rolling into next day, month-end transitions for monthly recurring tasks, and conflicts across different pets on the same owner.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

I was satisfied with the design portion of this project. I was able to carve my own path to take and guide the AI assistant through that.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

I would extend the scheduler to be able to handle monthly tasks.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

I learned that there are always new ways to break things and ways a system can be improved. Copilot was a good partner in ensuring that the application was robust.
