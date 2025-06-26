                          +------------+           +------------+
                          | DIM_DATE   |  	   | DIM_ROLES  |
                          +------------+  	   +------------+
                               	|		         |
                                |			 |
                                v		         v
+----------------+      +-------------------+      +------------+
| DIM_EMPLOYEE   | ---> |  FACT_TIMESHEETS  | <--- | DIM_MEETS  |
+----------------+      +-------------------+      +------------+
                                |
                                |
               +-------------------------------+
               |          DIM_ABSENCES         |
               +-------------------------------+


1. DIM_EMPLOYEE
Connection: Linked to TIMESHEETS_FACT by employee_id.
Purpose: Provides employee-level details like name, department, or position.
Example: When analyzing how many hours a person worked or how many meetings they attended, this table tells you who the employee is.

2. DIM_ROLES
Connection: Linked to TIMESHEETS_FACT by role_id (or equivalent).
Purpose: Describes the role an employee played in a meeting, based on data from the Microsoft Teams Role field (e.g., presenter, attendee).
Example: Useful to break down meeting participation by roles like "Organizer" vs "Attendee".

3. DIM_MEETS
Connection: Linked to TIMESHEETS_FACT by meeting_id or meet_id.
Purpose: Represents Microsoft Teams meeting data.
	Includes things like join/leave timestamps, duration, participant ID, etc.
Example: Supports analysis like “How much time did employees spend in meetings?” or “Which meetings had the most participants?”

4. DIM_ABSENCES
Connection: Linked to TIMESHEETS_FACT via absence_id or a flag in the fact table.
Purpose: Contains information from a personal or shared absence calendar, like the screenshot you provided.
	Describes types of absences (e.g., "Exam", "University Attendance"), duration, time, and who organized them.
Example: Allows reporting on total time absent, absence types, or frequency of specific reasons like exams.

5. DIM_DATE
Connection: Linked to TIMESHEETS_FACT via date_id.
Purpose: A classic date dimension providing context like:
	Day of the week, month, year
	Holiday flag, workweek number
Example: Enables filtering and grouping facts over time: “Total hours worked in May 2025” or “Meetings per day”.

TIMESHEETS_FACT is the analytical center
Each of the dimension tables explains a different perspective of the data:
	WHO → EMPLOYEE_DIM
	WHEN → DATE_DIM
	WHAT (Meeting) → MEETS_DIM
	WHY (Absence) → ABSENCES_DIM
	HOW (Meeting Role) → ROLES_DIM