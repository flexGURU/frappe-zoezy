import frappe
from frappe.tests import IntegrationTestCase
from frappe.utils import today

from zoezy.api import auth, invoice, profile, subscription, workout
from zoezy.tests.factories import make_exercise, make_package, make_subscription

EMAIL = "api-client@zoezy.test"


class TestClientAPI(IntegrationTestCase):
	def setUp(self):
		frappe.set_user("Guest")
		frappe.local.request_ip = "127.0.0.1"
		auth.sign_up("Api", "Client", EMAIL, "0712345678")
		frappe.set_user("Administrator")

	def tearDown(self):
		frappe.set_user("Administrator")
		frappe.db.rollback()

	def test_sign_up_creates_client_with_role(self):
		self.assertIn("Client", frappe.get_roles(EMAIL))
		self.assertEqual(frappe.db.get_value("Client", EMAIL, "status"), "Inactive")
		with self.assertRaises(frappe.ValidationError):
			auth.sign_up("Api", "Client", EMAIL, "0712345678")

	def test_client_sees_own_plan_and_billing(self):
		squat = make_exercise("Test Squat", "Test Legs")
		frappe.get_doc(
			{
				"doctype": "Workout Log",
				"client": EMAIL,
				"day": "Wednesday",
				"category": "Test Legs",
				"exercises": [
					{
						"exercise": squat,
						"sets": 3,
						"rep_range": "10",
						"progressive_overload": 1,
						"start_weight": 20,
						"progression_weight": 5,
					}
				],
			}
		).insert()
		make_subscription(EMAIL, make_package(), today())

		frappe.set_user(EMAIL)

		me = profile.get_profile()
		self.assertEqual(me["full_name"], "Api Client")
		self.assertEqual(me["client"]["status"], "Active")

		week = workout.get_weekly_plan()
		self.assertEqual([d["day"] for d in week][:3], ["Monday", "Tuesday", "Wednesday"])
		self.assertEqual(len(week), 7)
		exercise = week[2]["sessions"][0]["exercises"][0]
		self.assertEqual((exercise["reps"], exercise["final_weight"]), ("10", 30))

		subs = subscription.get_subscriptions()
		self.assertEqual(subs[0]["items"], ["4 sessions a week"])

		invoices = invoice.get_invoices()
		self.assertEqual(invoices[0]["outstanding_amount"], 3000)
		self.assertEqual(invoices[0]["packages"][0]["package_name"], "Test Package")

	def test_update_profile(self):
		frappe.set_user(EMAIL)
		updated = profile.update_profile("Renamed", "Person", "0700000000")
		self.assertEqual(updated["full_name"], "Renamed Person")
		self.assertEqual(frappe.db.get_value("Client", EMAIL, "full_name"), "Renamed Person")
