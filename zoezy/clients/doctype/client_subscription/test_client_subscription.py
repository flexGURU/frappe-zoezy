# Copyright (c) 2026, mukunajohn329@gmail.com and contributors
# See license.txt

from unittest.mock import patch

import frappe
from frappe.tests import IntegrationTestCase
from frappe.utils import add_days, today

from zoezy.clients.doctype.client_subscription.client_subscription import (
	update_subscription_statuses,
)
from zoezy.tests.factories import make_client, make_package, make_subscription


class IntegrationTestClientSubscription(IntegrationTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def setUp(self):
		self.client_name = make_client()
		self.package = make_package()

	def test_creates_submitted_invoice_and_activates_client(self):
		subscription = make_subscription(self.client_name, self.package, today())

		self.assertEqual(subscription.status, "Active")
		self.assertTrue(subscription.to_date, "to_date defaults from Zoezy Settings")

		invoice = frappe.get_doc("Client Invoice", {"subscription": subscription.name})
		self.assertEqual(invoice.docstatus, 1)
		self.assertEqual(invoice.total, 3000)
		self.assertEqual(invoice.outstanding_amount, 3000)
		self.assertEqual(invoice.status, "Unpaid")
		self.assertEqual(frappe.db.get_value("Client", self.client_name, "status"), "Active")

	def test_status_follows_dates(self):
		upcoming = make_subscription(self.client_name, self.package, add_days(today(), 10))
		self.assertEqual(upcoming.status, "Upcoming")

		expired = make_subscription(
			self.client_name, self.package, add_days(today(), -60), add_days(today(), -31)
		)
		self.assertEqual(expired.status, "Expired")

	def test_overlapping_subscription_is_rejected(self):
		make_subscription(self.client_name, self.package, today(), add_days(today(), 30))
		with self.assertRaises(frappe.ValidationError):
			make_subscription(self.client_name, self.package, add_days(today(), 15))

	def test_to_date_before_from_date_is_rejected(self):
		with self.assertRaises(frappe.ValidationError):
			make_subscription(self.client_name, self.package, today(), add_days(today(), -1))

	def test_daily_job_expires_subscription_and_deactivates_client(self):
		subscription = make_subscription(self.client_name, self.package, today())
		frappe.db.set_value("Client Subscription", subscription.name, "to_date", add_days(today(), -1))

		with patch.object(frappe.db, "commit"):
			update_subscription_statuses()

		self.assertEqual(frappe.db.get_value("Client Subscription", subscription.name, "status"), "Expired")
		self.assertEqual(frappe.db.get_value("Client", self.client_name, "status"), "Inactive")
