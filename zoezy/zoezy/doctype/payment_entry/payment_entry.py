# Copyright (c) 2026, mukunajohn329@gmail.com and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class PaymentEntry(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        amended_from: DF.Link | None
        amount: DF.Int
        invoice: DF.Link
        posting_date: DF.Datetime | None
    # end: auto-generated types

    pass

    def on_submit(self):
        self.update_invoice_outstanding_amount()

    def update_invoice_outstanding_amount(self):
        from zoezy.zoezy.doctype.client_invoice.client_invoice import ClientInvoice

        invoice: ClientInvoice = frappe.get_doc("Client Invoice", self.invoice)

        if invoice.outstanding_amount == 0:
            frappe.throw("Invoice is already fully paid.")

        new_amount = invoice.outstanding_amount - self.amount
        base_data = {"outstanding_amount": new_amount}

        conditions = [
            (lambda amount: amount > 0 and amount < invoice.total, "Partially Paid"),
            (lambda amount: amount == 0, "Paid"),
        ]

        for condition, status in conditions:
            if condition(new_amount):
                base_data["status"] = status
                break

        invoice.db_set(base_data, update_modified=False)
        invoice.reload()
