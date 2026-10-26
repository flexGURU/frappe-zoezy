# Copyright (c) 2026, mukunajohn329@gmail.com and contributors
# For license information, please see license.txt

from collections import defaultdict

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt

MAX_SETS = 20


class WorkoutLog(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		from zoezy.training.doctype.workout_log_exercise.workout_log_exercise import (
			WorkoutLogExercise,
		)
		from zoezy.training.doctype.workout_log_set.workout_log_set import WorkoutLogSet

		category: DF.Link
		client: DF.Link
		client_name: DF.Data | None
		day: DF.Literal[
			"",
			"Monday",
			"Tuesday",
			"Wednesday",
			"Thursday",
			"Friday",
			"Saturday",
			"Sunday",
		]
		exercises: DF.Table[WorkoutLogExercise]
		set_plan: DF.Table[WorkoutLogSet]
		title: DF.Data | None
		total_sets: DF.Int
	# end: auto-generated types

	def validate(self):
		self.title = f"{self.client_name or self.client} · {self.day} · {self.category}"
		self.validate_unique_session()
		self.validate_exercises()
		self.validate_set_plan()
		self.total_sets = sum(row.sets for row in self.exercises)

	def validate_unique_session(self):
		existing = frappe.db.get_value(
			"Workout Log",
			{
				"client": self.client,
				"day": self.day,
				"category": self.category,
				"name": ["!=", self.name],
			},
			"name",
		)
		if existing:
			frappe.throw(
				_("{0} already has a {1} session on {2} ({3}).").format(
					self.client_name, self.category, self.day, existing
				)
			)

	def validate_exercises(self):
		if not self.exercises:
			frappe.throw(_("Add at least one exercise."))

		categories = dict(
			frappe.get_all(
				"Exercise Type",
				filters={"name": ["in", [row.exercise for row in self.exercises]]},
				fields=["name", "category"],
				as_list=True,
			)
		)
		seen = set()
		for row in self.exercises:
			if row.exercise in seen:
				frappe.throw(_("{0} is listed more than once.").format(row.exercise))
			seen.add(row.exercise)

			if categories.get(row.exercise) != self.category:
				frappe.throw(_("{0} is not a {1} exercise.").format(row.exercise, self.category))
			if not 1 <= (row.sets or 0) <= MAX_SETS:
				frappe.throw(_("{0}: sets must be between 1 and {1}.").format(row.exercise, MAX_SETS))
			if row.weight_mode not in ("Manual", "Progressive"):
				frappe.throw(_("{0}: choose Manual or Progressive weights.").format(row.exercise))

	def validate_set_plan(self):
		planned = {row.exercise for row in self.exercises}
		sets_by_exercise = defaultdict(list)
		for set_row in self.set_plan:
			if set_row.exercise not in planned:
				frappe.throw(
					_("Set {0} is for {1}, which isn't in this plan.").format(
						set_row.set_no, set_row.exercise
					)
				)
			sets_by_exercise[set_row.exercise].append(set_row)

		ordered = []
		for row in self.exercises:
			sets = sorted(sets_by_exercise[row.exercise], key=lambda s: s.set_no or 0)
			if len(sets) != row.sets:
				frappe.throw(
					_("{0}: {1} sets are planned but {2} have been filled in.").format(
						row.exercise, row.sets, len(sets)
					)
				)
			if [s.set_no for s in sets] != list(range(1, row.sets + 1)):
				frappe.throw(_("{0}: sets must be numbered 1 to {1}.").format(row.exercise, row.sets))

			for s in sets:
				if (s.reps or 0) < 1:
					frappe.throw(_("{0}, set {1}: reps must be at least 1.").format(row.exercise, s.set_no))

			if row.weight_mode == "Progressive":
				self.apply_progression(row, sets)
			else:
				row.start_weight = row.progression_weight = 0
				for s in sets:
					if flt(s.weight) < 0:
						frappe.throw(
							_("{0}, set {1}: weight cannot be negative.").format(row.exercise, s.set_no)
						)

			row.final_weight = flt(sets[-1].weight, 2)
			row.rep_range = rep_summary([s.reps for s in sets])
			ordered.extend(sets)

		self.set_plan = ordered
		for idx, s in enumerate(self.set_plan, start=1):
			s.idx = idx

	def apply_progression(self, row, sets):
		if flt(row.start_weight) < 0:
			frappe.throw(_("{0}: start weight cannot be negative.").format(row.exercise))
		if flt(row.progression_weight) <= 0:
			frappe.throw(_("{0}: the step per set must be more than 0 kg.").format(row.exercise))
		for s in sets:
			s.weight = flt(row.start_weight + row.progression_weight * (s.set_no - 1), 2)


def rep_summary(reps: list[int]) -> str:
	low, high = min(reps), max(reps)
	return str(low) if low == high else f"{low}-{high}"
