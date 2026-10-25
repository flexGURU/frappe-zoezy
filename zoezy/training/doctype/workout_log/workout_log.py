# Copyright (c) 2026, mukunajohn329@gmail.com and contributors
# For license information, please see license.txt

import re

import frappe
from frappe.model.document import Document
from frappe.utils import flt

REPS_PATTERN = re.compile(r"^\d+(\s*-\s*\d+)?$")


class WorkoutLog(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		from zoezy.training.doctype.workout_log_exercise.workout_log_exercise import (
			WorkoutLogExercise,
		)

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
		title: DF.Data | None
		total_sets: DF.Int
	# end: auto-generated types

	def validate(self):
		self.title = f"{self.client_name or self.client} · {self.day} · {self.category}"
		self.validate_unique_session()
		self.validate_exercises()
		self.set_weights()
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
				f"{self.client_name} already has a {self.category} session on {self.day} ({existing})."
			)

	def validate_exercises(self):
		if not self.exercises:
			frappe.throw("Add at least one exercise.")

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
				frappe.throw(f"Row {row.idx}: {row.exercise} is listed more than once.")
			seen.add(row.exercise)

			if categories.get(row.exercise) != self.category:
				frappe.throw(f"Row {row.idx}: {row.exercise} is not a {self.category} exercise.")
			if row.sets < 1:
				frappe.throw(f"Row {row.idx}: Sets must be at least 1.")

			row.rep_range = (row.rep_range or "").strip().replace("\u2013", "-")
			if not REPS_PATTERN.match(row.rep_range):
				frappe.throw(f"Row {row.idx}: Reps must be a number (10) or a range (8-12).")

	def set_weights(self):
		for row in self.exercises:
			if row.progressive_overload:
				row.stagnant_weight = 0
				row.final_weight = flt(row.start_weight + row.progression_weight * (row.sets - 1), 2)
			else:
				row.start_weight = row.progression_weight = row.final_weight = 0
