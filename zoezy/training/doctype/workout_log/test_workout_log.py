# Copyright (c) 2026, mukunajohn329@gmail.com and contributors
# See license.txt

import frappe
from frappe.tests import IntegrationTestCase

from zoezy.tests.factories import make_client, make_exercise


class IntegrationTestWorkoutLog(IntegrationTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def setUp(self):
		self.client_name = make_client()
		self.squat = make_exercise("Test Squat", "Test Legs")
		self.lunge = make_exercise("Test Lunge", "Test Legs")
		self.bench = make_exercise("Test Bench Press", "Test Push")

	def make_log(self, day="Monday", exercises=None):
		return frappe.get_doc(
			{
				"doctype": "Workout Log",
				"client": self.client_name,
				"day": day,
				"category": "Test Legs",
				"exercises": exercises or [{"exercise": self.squat, "sets": 4, "rep_range": "8-12"}],
			}
		).insert()

	def test_same_category_on_different_days(self):
		self.make_log("Monday")
		self.make_log("Thursday")
		with self.assertRaises(frappe.ValidationError):
			self.make_log("Monday")

	def test_progressive_overload_final_weight(self):
		log = self.make_log(
			exercises=[
				{
					"exercise": self.squat,
					"sets": 4,
					"rep_range": "8 \u2013 10",
					"progressive_overload": 1,
					"start_weight": 40,
					"progression_weight": 2.5,
				},
				{"exercise": self.lunge, "sets": 3, "rep_range": "12", "stagnant_weight": 10},
			]
		)
		squat, lunge = log.exercises
		self.assertEqual(squat.final_weight, 47.5)
		self.assertEqual(squat.rep_range, "8 - 10")
		self.assertEqual(lunge.final_weight, 0)
		self.assertEqual(log.total_sets, 7)

	def test_invalid_rows_are_rejected(self):
		for row in (
			{"exercise": self.bench, "sets": 3, "rep_range": "10"},
			{"exercise": self.squat, "sets": 0, "rep_range": "10"},
			{"exercise": self.squat, "sets": 3, "rep_range": "lots"},
		):
			with self.assertRaises(frappe.ValidationError):
				self.make_log(exercises=[row])

		with self.assertRaises(frappe.ValidationError):
			self.make_log(
				exercises=[
					{"exercise": self.squat, "sets": 3, "rep_range": "10"},
					{"exercise": self.squat, "sets": 3, "rep_range": "10"},
				]
			)
