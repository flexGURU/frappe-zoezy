# Copyright (c) 2026, mukunajohn329@gmail.com and contributors
# See license.txt

import frappe
from frappe.tests import IntegrationTestCase

from zoezy.tests.factories import make_client, make_exercise, manual_sets, plan_row


class IntegrationTestWorkoutLog(IntegrationTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def setUp(self):
		self.client_name = make_client()
		self.squat = make_exercise("Test Squat", "Test Legs")
		self.lunge = make_exercise("Test Lunge", "Test Legs")
		self.bench = make_exercise("Test Bench Press", "Test Push")

	def make_log(self, exercises, set_plan, day="Monday"):
		return frappe.get_doc(
			{
				"doctype": "Workout Log",
				"client": self.client_name,
				"day": day,
				"category": "Test Legs",
				"exercises": exercises,
				"set_plan": set_plan,
			}
		).insert()

	def squat_log(self, day="Monday"):
		return self.make_log(
			[plan_row(self.squat, 3)], manual_sets(self.squat, (10, 60), (8, 80), (6, 90)), day
		)

	def test_manual_weights_per_set(self):
		log = self.squat_log()
		self.assertEqual(
			[(s.set_no, s.reps, s.weight) for s in log.set_plan], [(1, 10, 60), (2, 8, 80), (3, 6, 90)]
		)
		row = log.exercises[0]
		self.assertEqual((row.rep_range, row.final_weight), ("6-10", 90))
		self.assertEqual(log.total_sets, 3)

	def test_progressive_weights_are_computed(self):
		log = self.make_log(
			[plan_row(self.squat, 4, "Progressive", start_weight=40, progression_weight=2.5)],
			manual_sets(self.squat, (10, 999), (10, 0), (8, 0), (8, 0)),
		)
		self.assertEqual([s.weight for s in log.set_plan], [40, 42.5, 45, 47.5])
		self.assertEqual((log.exercises[0].rep_range, log.exercises[0].final_weight), ("8-10", 47.5))

	def test_manual_mode_ignores_progression_fields(self):
		log = self.make_log(
			[plan_row(self.squat, 2, "Manual", start_weight=50, progression_weight=5)],
			manual_sets(self.squat, (10, 60), (10, 70)),
		)
		row = log.exercises[0]
		self.assertEqual((row.start_weight, row.progression_weight), (0, 0))
		self.assertEqual([s.weight for s in log.set_plan], [60, 70])

	def test_set_count_must_match(self):
		for set_plan in (
			manual_sets(self.squat, (10, 60), (8, 80)),
			manual_sets(self.squat, (10, 60), (8, 80), (6, 90), (6, 90)),
		):
			with self.assertRaises(frappe.ValidationError):
				self.make_log([plan_row(self.squat, 3)], set_plan)

	def test_set_numbers_must_run_in_order(self):
		sets = manual_sets(self.squat, (10, 60), (8, 80), (6, 90))
		sets[2]["set_no"] = 2
		with self.assertRaises(frappe.ValidationError):
			self.make_log([plan_row(self.squat, 3)], sets)

	def test_invalid_sets_are_rejected(self):
		cases = [
			([plan_row(self.squat, 1)], manual_sets(self.squat, (0, 60))),
			([plan_row(self.squat, 1)], manual_sets(self.squat, (10, -5))),
			([plan_row(self.squat, 1)], manual_sets(self.lunge, (10, 20))),
			([plan_row(self.squat, 21)], manual_sets(self.squat, *[(10, 20)] * 21)),
			([plan_row(self.squat, 1, "Progressive", start_weight=40)], manual_sets(self.squat, (10, 0))),
			([plan_row(self.bench, 1)], manual_sets(self.bench, (10, 20))),
		]
		for exercises, set_plan in cases:
			with self.assertRaises(frappe.ValidationError):
				self.make_log(exercises, set_plan)

	def test_sets_are_grouped_by_exercise(self):
		log = self.make_log(
			[plan_row(self.squat, 2), plan_row(self.lunge, 1)],
			manual_sets(self.lunge, (12, 10)) + list(reversed(manual_sets(self.squat, (10, 60), (8, 70)))),
		)
		self.assertEqual(
			[(s.exercise, s.set_no) for s in log.set_plan],
			[(self.squat, 1), (self.squat, 2), (self.lunge, 1)],
		)

	def test_same_category_on_different_days(self):
		self.squat_log("Monday")
		self.squat_log("Thursday")
		with self.assertRaises(frappe.ValidationError):
			self.squat_log("Monday")

	def test_duplicate_exercise_is_rejected(self):
		with self.assertRaises(frappe.ValidationError):
			self.make_log(
				[plan_row(self.squat, 1), plan_row(self.squat, 1)],
				manual_sets(self.squat, (10, 60)),
			)
