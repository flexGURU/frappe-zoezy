import frappe
from frappe.query_builder import DocType

from .utils import get_session_client, log_throw_error

WEEKDAYS = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")


@frappe.whitelist()
def get_weekly_plan() -> list[dict]:
	week = {day: {"day": day, "sessions": []} for day in WEEKDAYS}

	client = get_session_client()
	if not client:
		return list(week.values())

	try:
		workout_log = DocType("Workout Log")
		workout_log_exercise = DocType("Workout Log Exercise")
		rows = (
			frappe.qb.from_(workout_log)
			.join(workout_log_exercise)
			.on(workout_log.name == workout_log_exercise.parent)
			.where(workout_log.client == client)
			.select(
				workout_log.name,
				workout_log.day,
				workout_log.category,
				workout_log.total_sets,
				workout_log_exercise.exercise,
				workout_log_exercise.sets,
				workout_log_exercise.rep_range,
				workout_log_exercise.video_url,
				workout_log_exercise.description,
				workout_log_exercise.progressive_overload,
				workout_log_exercise.stagnant_weight,
				workout_log_exercise.start_weight,
				workout_log_exercise.progression_weight,
				workout_log_exercise.final_weight,
			)
			.orderby(workout_log.creation)
			.orderby(workout_log_exercise.idx)
		).run(as_dict=True)
	except Exception:
		log_throw_error("Error fetching your workout plan. Please try again.")

	sessions: dict[str, dict] = {}
	for row in rows:
		if row.day not in week:
			continue

		if row.name not in sessions:
			sessions[row.name] = {
				"name": row.name,
				"category": row.category,
				"total_sets": row.total_sets,
				"exercises": [],
			}
			week[row.day]["sessions"].append(sessions[row.name])

		progressive = bool(row.progressive_overload)
		sessions[row.name]["exercises"].append(
			{
				"exercise": row.exercise,
				"sets": row.sets,
				"reps": row.rep_range,
				"video_url": row.video_url,
				"notes": row.description,
				"progressive_overload": progressive,
				"weight": None if progressive else (row.stagnant_weight or None),
				"start_weight": row.start_weight if progressive else None,
				"progression_weight": row.progression_weight if progressive else None,
				"final_weight": row.final_weight if progressive else None,
			}
		)

	return list(week.values())
