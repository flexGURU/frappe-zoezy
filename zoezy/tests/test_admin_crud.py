import frappe
import frappe.client as client_api
from frappe.tests import IntegrationTestCase
from frappe.utils import add_days, today

from zoezy.api import admin
from zoezy.tests.factories import (
	make_client,
	make_exercise,
	make_package,
	make_subscription,
	make_trainer,
	manual_sets,
	plan_row,
)

NEW_CLIENT = "new.client@zoezy.test"


class TestTrainerCrud(IntegrationTestCase):
	def setUp(self):
		frappe.set_user("Administrator")
		self.trainer = make_trainer()
		self.client_name = make_client()
		self.package = make_package()
		self.squat = make_exercise("Test Squat", "Test Legs")
		self.lunge = make_exercise("Test Lunge", "Test Legs")
		frappe.set_user(self.trainer)

	def tearDown(self):
		frappe.set_user("Administrator")
		frappe.db.rollback()

	def assert_crud(self, doctype, values, updates):
		doc = client_api.insert({"doctype": doctype, **values})
		self.assertIn(doc["name"], [row.name for row in client_api.get_list(doctype, limit_page_length=0)])
		self.assertEqual(client_api.get(doctype, doc["name"])["name"], doc["name"])

		updated = client_api.set_value(doctype, doc["name"], updates)
		for field, value in updates.items():
			if not isinstance(value, list):
				self.assertEqual(updated[field], value)

		client_api.delete(doctype, doc["name"])
		self.assertFalse(frappe.db.exists(doctype, doc["name"]))
		return updated

	def test_lead_source_crud(self):
		self.assert_crud("Lead Source", {"lead_source_name": "Instagram"}, {"lead_source_name": "Instagram"})

	def test_workout_category_crud(self):
		self.assert_crud("Workout Category", {"category_name": "Mobility"}, {"category_name": "Mobility"})

	def test_exercise_type_crud(self):
		self.assert_crud(
			"Exercise Type",
			{"exercise_name": "Hip Thrust", "category": "Test Legs"},
			{"video_url": "https://youtu.be/abc123"},
		)

	def test_package_type_crud_with_items(self):
		updated = self.assert_crud(
			"Package Type",
			{"package_name": "Online Coaching", "unit_price": 4000, "items": [{"item": "Weekly check-in"}]},
			{"unit_price": 4500, "items": [{"item": "Weekly check-in"}, {"item": "Custom meal plan"}]},
		)
		self.assertEqual([row["item"] for row in updated["items"]], ["Weekly check-in", "Custom meal plan"])

	def test_client_crud(self):
		name = admin.create_client("New", "Client", NEW_CLIENT, "0712345678", age=30, send_invite=False)
		frappe.set_user("Administrator")
		self.assertEqual(frappe.db.get_value("User", NEW_CLIENT, "user_type"), "Website User")
		self.assertIn("Client", frappe.get_roles(NEW_CLIENT))
		frappe.set_user(self.trainer)

		self.assertIn(name, [row.name for row in client_api.get_list("Client", limit_page_length=0)])
		details = admin.get_client(name)
		self.assertEqual(
			(details["full_name"], details["portal_access"], details["age"]), ("New Client", True, 30)
		)

		admin.update_client(name, "Renamed", "Client", "0700000000", age=31)
		client = client_api.get("Client", name)
		self.assertEqual(
			(client["full_name"], client["phone_number"], client["age"]), ("Renamed Client", "0700000000", 31)
		)

		admin.set_portal_access(name, False)
		self.assertEqual(frappe.db.get_value("User", NEW_CLIENT, "enabled"), 0)
		admin.set_portal_access(name, True)
		self.assertEqual(frappe.db.get_value("User", NEW_CLIENT, "enabled"), 1)

		client_api.delete("Client", name)
		self.assertFalse(frappe.db.exists("Client", name))

		with self.assertRaises(frappe.ValidationError):
			admin.create_client("Dup", "Client", self.client_name)

	def test_subscription_crud(self):
		sub = client_api.insert(
			{
				"doctype": "Client Subscription",
				"client": self.client_name,
				"package_type": self.package,
				"from_date": today(),
			}
		)
		invoice = frappe.db.get_value("Client Invoice", {"subscription": sub["name"]})
		self.assertTrue(invoice)

		new_end = add_days(today(), 60)
		updated = client_api.set_value("Client Subscription", sub["name"], {"to_date": new_end})
		self.assertEqual(str(updated["to_date"]), new_end)

		with self.assertRaises(frappe.LinkExistsError):
			client_api.delete("Client Subscription", sub["name"])

		admin.cancel_document("Client Invoice", invoice)
		client_api.delete("Client Invoice", invoice)
		client_api.delete("Client Subscription", sub["name"])
		self.assertFalse(frappe.db.exists("Client Subscription", sub["name"]))

	def test_invoice_crud(self):
		sub = make_subscription(self.client_name, self.package, add_days(today(), 40))
		name = admin.create_invoice(
			self.client_name,
			sub.name,
			[
				{"package_name": self.package, "unit_price": 1200},
				{"package_name": self.package, "unit_price": 300},
			],
		)
		invoice = client_api.get("Client Invoice", name)
		self.assertEqual((invoice["docstatus"], invoice["total"], invoice["status"]), (1, 1500, "Unpaid"))
		self.assertIn(name, [row.name for row in client_api.get_list("Client Invoice", limit_page_length=0)])

		admin.cancel_document("Client Invoice", name)
		self.assertEqual(frappe.db.get_value("Client Invoice", name, "status"), "Cancelled")
		client_api.delete("Client Invoice", name)
		self.assertFalse(frappe.db.exists("Client Invoice", name))

		with self.assertRaises(frappe.ValidationError):
			admin.create_invoice(self.client_name, sub.name, [])

	def test_payment_crud(self):
		sub = make_subscription(self.client_name, self.package, today())
		invoice = frappe.db.get_value("Client Invoice", {"subscription": sub.name})

		name = admin.record_payment(invoice, 1000, "Cash", "RCPT-1")
		payment = client_api.get("Payment Entry", name)
		self.assertEqual(
			(payment["docstatus"], payment["amount"], payment["client"]), (1, 1000, self.client_name)
		)
		self.assertEqual(frappe.db.get_value("Client Invoice", invoice, "status"), "Partially Paid")
		self.assertIn(name, [row.name for row in client_api.get_list("Payment Entry", limit_page_length=0)])

		admin.cancel_document("Payment Entry", name)
		self.assertEqual(frappe.db.get_value("Client Invoice", invoice, "outstanding_amount"), 3000)
		client_api.delete("Payment Entry", name)
		self.assertFalse(frappe.db.exists("Payment Entry", name))

	def test_workout_plan_crud(self):
		name = admin.save_workout_plan(
			{
				"client": self.client_name,
				"day": "Tuesday",
				"category": "Test Legs",
				"exercises": [
					plan_row(self.squat, 3),
					plan_row(self.lunge, 2, "Progressive", start_weight=10, progression_weight=5),
				],
				"set_plan": manual_sets(self.squat, (10, 60), (8, 80), (6, 90))
				+ manual_sets(self.lunge, (12, 0), (12, 0)),
			}
		)
		plan = admin.get_workout_plan(name)
		self.assertEqual(
			[(s["exercise"], s["weight"]) for s in plan["set_plan"]][-2:],
			[(self.lunge, 10), (self.lunge, 15)],
		)
		self.assertIn(name, [row.name for row in client_api.get_list("Workout Log", limit_page_length=0)])

		plan["exercises"] = [plan_row(self.squat, 2)]
		plan["set_plan"] = manual_sets(self.squat, (5, 100), (5, 110))
		admin.save_workout_plan(plan)
		updated = admin.get_workout_plan(name)
		self.assertEqual([(s["reps"], s["weight"]) for s in updated["set_plan"]], [(5, 100), (5, 110)])
		self.assertEqual(len(updated["exercises"]), 1)

		with self.assertRaises(frappe.ValidationError):
			plan["set_plan"] = manual_sets(self.squat, (5, 100))
			admin.save_workout_plan(plan)

		client_api.delete("Workout Log", name)
		self.assertFalse(frappe.db.exists("Workout Log", name))

	def test_settings_update(self):
		updated = client_api.set_value(
			"Zoezy Settings", "Zoezy Settings", {"brand_name": "Coach Amani", "invoice_due_days": 10}
		)
		self.assertEqual((updated["brand_name"], updated["invoice_due_days"]), ("Coach Amani", 10))

	def test_overview(self):
		make_subscription(self.client_name, self.package, today())
		overview = admin.get_overview()
		self.assertGreaterEqual(overview["active_clients"], 1)
		self.assertGreaterEqual(overview["outstanding"], 3000)

	def test_clients_cannot_write_through_generic_api(self):
		frappe.set_user(self.client_name)
		with self.assertRaises(frappe.PermissionError):
			client_api.insert({"doctype": "Lead Source", "lead_source_name": "Spam"})
		with self.assertRaises(frappe.PermissionError):
			client_api.set_value("Zoezy Settings", "Zoezy Settings", {"brand_name": "Hacked"})
		with self.assertRaises(frappe.PermissionError):
			client_api.delete("Package Type", self.package)

	def test_paged_list_queries(self):
		for i in range(3):
			client_api.insert({"doctype": "Lead Source", "lead_source_name": f"Paged Source {i}"})

		page = client_api.get_list(
			"Lead Source",
			fields=["name"],
			or_filters=[["name", "like", "%Paged Source%"]],
			order_by="name asc",
			limit_start=1,
			limit_page_length=1,
		)
		self.assertEqual([row.name for row in page], ["Paged Source 1"])

		count = client_api.get_list(
			"Lead Source",
			fields=[{"COUNT": "*", "as": "total"}],
			or_filters=[["name", "like", "%Paged Source%"]],
			limit_page_length=1,
		)
		self.assertEqual(count[0].total, 3)

	def test_profit_analysis_report(self):
		from frappe.desk.query_report import run

		sub = make_subscription(self.client_name, self.package, today())
		admin.record_payment(frappe.db.get_value("Client Invoice", {"subscription": sub.name}), 1000)

		report = run(
			"Profit Analysis",
			filters={"periodicity": "Monthly", "client": self.client_name},
			ignore_prepared_report=True,
		)
		rows = [row for row in report["result"] if isinstance(row, dict) and row.get("period")]
		self.assertTrue(rows)
		self.assertEqual(sum(row["collected"] for row in rows), 1000)
		self.assertEqual(sum(row["outstanding"] for row in rows), 2000)
