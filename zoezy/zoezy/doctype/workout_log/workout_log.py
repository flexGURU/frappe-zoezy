# Copyright (c) 2026, mukunajohn329@gmail.com and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class WorkoutLog(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF
        from zoezy.zoezy.doctype.workout_log_exercise.workout_log_exercise import (
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

    pass

    def before_insert(self):
        self.title = f"{self.client_name}-{self.category}"

    def validate(self):
        self.set_total_sets()
        self.validate_exercise()

    def set_total_sets(self):
        self.total_sets = sum(exercise.sets for exercise in self.exercises)

    def validate_exercise(self):
        seen = set()

        for row in self.exercises:
            exercise = row.exercise

            if exercise in seen:
                frappe.throw(f"Duplicate exercise '{exercise}' found.")

            seen.add(exercise)
