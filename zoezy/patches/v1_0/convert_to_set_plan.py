import re

import frappe
from frappe.utils import flt

from zoezy.training.doctype.workout_log.workout_log import rep_summary


def execute():
	if not frappe.db.has_column("Workout Log Exercise", "progressive_overload"):
		return

	rows = frappe.db.sql(
		"""
		select name, parent, idx, exercise, sets, rep_range, progressive_overload,
			stagnant_weight, start_weight, progression_weight
		from `tabWorkout Log Exercise`
		where parenttype = 'Workout Log'
		order by parent, idx
		""",
		as_dict=True,
	)
	existing = set(frappe.get_all("Workout Log Set", pluck="parent", distinct=True))
	set_idx = {}

	for row in rows:
		if row.parent in existing:
			continue

		progressive = bool(row.progressive_overload)
		reps = first_number(row.rep_range) or 10
		sets = max(row.sets or 1, 1)
		weights = [
			flt(row.start_weight) + flt(row.progression_weight) * i
			if progressive
			else flt(row.stagnant_weight)
			for i in range(sets)
		]

		for set_no, weight in enumerate(weights, start=1):
			set_idx[row.parent] = set_idx.get(row.parent, 0) + 1
			frappe.get_doc(
				{
					"doctype": "Workout Log Set",
					"parent": row.parent,
					"parenttype": "Workout Log",
					"parentfield": "set_plan",
					"idx": set_idx[row.parent],
					"exercise": row.exercise,
					"set_no": set_no,
					"reps": reps,
					"weight": flt(weight, 2),
				}
			).db_insert()

		frappe.db.set_value(
			"Workout Log Exercise",
			row.name,
			{
				"weight_mode": "Progressive" if progressive and flt(row.progression_weight) > 0 else "Manual",
				"rep_range": rep_summary([reps]),
				"final_weight": flt(weights[-1], 2),
			},
			update_modified=False,
		)


def first_number(value) -> int | None:
	match = re.search(r"\d+", str(value or ""))
	return int(match.group()) if match else None
