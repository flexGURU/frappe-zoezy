from collections import defaultdict

import frappe
from frappe import _

from .utils import get_session_client, log_throw_error

WEEKDAYS = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")


@frappe.whitelist()
def get_weekly_plan() -> list[dict]:
	week = {day: {"day": day, "sessions": []} for day in WEEKDAYS}

	client = get_session_client()
	if not client:
		return list(week.values())

	try:
		logs = frappe.get_all(
			"Workout Log",
			filters={"client": client},
			fields=["name", "day", "category", "total_sets"],
			order_by="creation asc",
		)
		names = [log.name for log in logs]
		exercises = frappe.get_all(
			"Workout Log Exercise",
			filters={"parent": ["in", names], "parenttype": "Workout Log"},
			fields=[
				"parent",
				"exercise",
				"sets",
				"rep_range",
				"weight_mode",
				"start_weight",
				"progression_weight",
				"final_weight",
				"video_url",
				"description",
			],
			order_by="idx asc",
		)
		sets = frappe.get_all(
			"Workout Log Set",
			filters={"parent": ["in", names], "parenttype": "Workout Log"},
			fields=["parent", "exercise", "set_no", "reps", "weight"],
			order_by="idx asc",
		)
	except Exception:
		log_throw_error(_("Error fetching your workout plan. Please try again."))

	sets_by_exercise = defaultdict(list)
	for s in sets:
		sets_by_exercise[(s.parent, s.exercise)].append(
			{"set_no": s.set_no, "reps": s.reps, "weight": s.weight}
		)

	exercises_by_log = defaultdict(list)
	for e in exercises:
		progressive = e.weight_mode == "Progressive"
		exercises_by_log[e.parent].append(
			{
				"exercise": e.exercise,
				"sets": e.sets,
				"reps": e.rep_range,
				"weight_mode": e.weight_mode,
				"start_weight": e.start_weight if progressive else None,
				"progression_weight": e.progression_weight if progressive else None,
				"final_weight": e.final_weight,
				"set_details": sets_by_exercise[(e.parent, e.exercise)],
				"video_url": e.video_url,
				"notes": e.description,
			}
		)

	for log in logs:
		if log.day in week:
			week[log.day]["sessions"].append(
				{
					"name": log.name,
					"category": log.category,
					"total_sets": log.total_sets,
					"exercises": exercises_by_log[log.name],
				}
			)

	return list(week.values())
