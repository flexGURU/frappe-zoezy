# Copyright (c) 2026, mukunajohn329@gmail.com and contributors
# See license.txt

from unittest.mock import patch

import frappe
from frappe.tests import IntegrationTestCase
from frappe.utils import add_days, today

from zoezy.billing.doctype.client_invoice.client_invoice import mark_overdue_invoices
from zoezy.tests.factories import make_client, make_package, make_subscription


class IntegrationTestPaymentEntry(IntegrationTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def setUp(self):
		subscription = make_subscription(make_client(), make_package(), today())
		self.invoice = frappe.db.get_value("Client Invoice", {"subscription": subscription.name})

	def pay(self, amount):
		return frappe.get_doc(
			{"doctype": "Payment Entry", "invoice": self.invoice, "amount": amount}
		).submit()

	def invoice_state(self):
		return frappe.db.get_value(
			"Client Invoice", self.invoice, ["outstanding_amount", "status"], as_dict=True
		)

	def test_partial_then_full_payment(self):
		payment = self.pay(1000)
		self.assertEqual(payment.client, frappe.db.get_value("Client Invoice", self.invoice, "client"))
		self.assertEqual(self.invoice_state(), {"outstanding_amount": 2000, "status": "Partially Paid"})

		self.pay(2000)
		self.assertEqual(self.invoice_state(), {"outstanding_amount": 0, "status": "Paid"})

	def test_cancelling_payment_restores_outstanding(self):
		payment = self.pay(3000)
		payment.cancel()
		self.assertEqual(self.invoice_state(), {"outstanding_amount": 3000, "status": "Unpaid"})

	def test_overpayment_and_zero_amount_are_rejected(self):
		with self.assertRaises(frappe.ValidationError):
			self.pay(3500)
		with self.assertRaises(frappe.ValidationError):
			self.pay(0)

	def test_paid_invoice_rejects_further_payments(self):
		self.pay(3000)
		with self.assertRaises(frappe.ValidationError):
			self.pay(1)

	def test_overdue_job(self):
		frappe.db.set_value("Client Invoice", self.invoice, "due_date", add_days(today(), -1))
		with patch.object(frappe.db, "commit"):
			mark_overdue_invoices()
		self.assertEqual(self.invoice_state().status, "Overdue")
