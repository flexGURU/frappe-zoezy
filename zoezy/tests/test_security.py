from unittest.mock import patch

import frappe
from frappe.tests import IntegrationTestCase
from frappe.utils import today

from zoezy.api import auth, invoice, profile, subscription, workout
from zoezy.tests.factories import make_client, make_exercise, make_package, make_subscription

ALICE = "alice@zoezy.test"
BOB = "bob@zoezy.test"
CLIENT_ENDPOINTS = [
	profile.get_profile,
	profile.update_profile,
	workout.get_weekly_plan,
	subscription.get_subscriptions,
	invoice.get_invoices,
]


class TestPortalSecurity(IntegrationTestCase):
	def setUp(self):
		frappe.set_user("Administrator")
		exercise = make_exercise("Test Squat", "Test Legs")
		for email in (ALICE, BOB):
			make_client(email, first_name=email.split("@")[0].title())
			make_subscription(email, make_package(), today())
			frappe.get_doc(
				{
					"doctype": "Workout Log",
					"client": email,
					"day": "Monday",
					"category": "Test Legs",
					"exercises": [{"exercise": exercise, "sets": 3, "rep_range": "10"}],
				}
			).insert()

	def tearDown(self):
		frappe.set_user("Administrator")
		frappe.db.rollback()

	def test_guests_cannot_call_client_endpoints(self):
		frappe.set_user("Guest")
		for endpoint in CLIENT_ENDPOINTS:
			with self.assertRaises(frappe.PermissionError, msg=endpoint.__name__):
				frappe.is_whitelisted(endpoint)
		with self.assertRaises(frappe.AuthenticationError):
			invoice.get_invoices()

		frappe.is_whitelisted(auth.sign_up)

	def test_each_client_only_sees_their_own_data(self):
		bob_invoices = set(frappe.get_all("Client Invoice", {"client": BOB}, pluck="name"))
		bob_subscriptions = set(frappe.get_all("Client Subscription", {"client": BOB}, pluck="name"))
		bob_plans = set(frappe.get_all("Workout Log", {"client": BOB}, pluck="name"))

		frappe.set_user(ALICE)
		invoices = {i["name"] for i in invoice.get_invoices()}
		subscriptions = {s["name"] for s in subscription.get_subscriptions()}
		plans = {s["name"] for d in workout.get_weekly_plan() for s in d["sessions"]}

		self.assertTrue(invoices and subscriptions and plans)
		self.assertFalse(invoices & bob_invoices)
		self.assertFalse(subscriptions & bob_subscriptions)
		self.assertFalse(plans & bob_plans)
		self.assertEqual(profile.get_profile()["email"], ALICE)

	def test_clients_have_no_generic_document_access(self):
		bob_invoice = frappe.get_all("Client Invoice", {"client": BOB}, pluck="name")[0]

		frappe.set_user(ALICE)
		for doctype in ("Client", "Client Invoice", "Client Subscription", "Payment Entry", "Workout Log"):
			self.assertFalse(frappe.has_permission(doctype, "read"), doctype)
			with self.assertRaises(frappe.PermissionError):
				frappe.get_list(doctype)
		with self.assertRaises(frappe.PermissionError):
			frappe.get_doc("Client Invoice", bob_invoice).check_permission("read")

	def test_update_profile_cannot_escalate(self):
		frappe.set_user(ALICE)
		frappe.call(
			profile.update_profile,
			first_name="Alice",
			roles=[{"role": "System Manager"}],
			user_type="System User",
			email=BOB,
		)
		frappe.set_user("Administrator")
		self.assertNotIn("System Manager", frappe.get_roles(ALICE))
		self.assertEqual(frappe.db.get_value("User", ALICE, "user_type"), "Website User")
		self.assertEqual(frappe.db.get_value("User", BOB, "first_name"), "Bob")

	def test_sign_up_validates_input(self):
		frappe.set_user("Guest")
		frappe.local.request_ip = "127.0.0.1"
		for args in (
			("<script>", "X", "new1@zoezy.test", "0712345678"),
			("Ok", "Name", "not-an-email", "0712345678"),
			("Ok", "Name", "new2@zoezy.test", "call me"),
		):
			with self.assertRaises(frappe.ValidationError):
				auth.sign_up(*args)

		with patch("zoezy.api.auth.signup_allowed", return_value=False):
			with self.assertRaises(frappe.PermissionError):
				auth.sign_up("Ok", "Name", "new3@zoezy.test", "0712345678")

	def test_sign_up_lands_clients_in_zoezy(self):
		frappe.set_user("Guest")
		frappe.local.request_ip = "127.0.0.1"
		auth.sign_up("New", "Client", "new.client@zoezy.test", "0712345678")
		frappe.set_user("Administrator")
		user = frappe.db.get_value(
			"User", "new.client@zoezy.test", ["user_type", "default_app"], as_dict=True
		)
		self.assertEqual(user, {"user_type": "Website User", "default_app": "zoezy"})
		self.assertEqual(frappe.get_roles("new.client@zoezy.test").count("Client"), 1)

	def test_app_page_rejects_users_without_a_zoezy_role(self):
		from zoezy.www import zoezy as page

		outsider = "outsider@zoezy.test"
		frappe.get_doc(
			{"doctype": "User", "email": outsider, "first_name": "Out", "send_welcome_email": 0}
		).insert(ignore_permissions=True)

		with patch.object(frappe.db, "commit"):
			frappe.set_user(outsider)
			with self.assertRaises(frappe.PermissionError):
				page.get_context()

			frappe.set_user(ALICE)
			self.assertIn("branding", page.get_context().boot)
