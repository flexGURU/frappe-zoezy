# Copyright (c) 2026, mukunajohn329@gmail.com and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ClientInvoice(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF
        from zoezy.zoezy.doctype.client_invoice_package.client_invoice_package import ClientInvoicePackage

        amended_from: DF.Link | None
        client: DF.Link
        client_name: DF.Data | None
        currency: DF.Link | None
        outstanding_amount: DF.Float
        packages: DF.Table[ClientInvoicePackage]
        posting_date: DF.Date
        status: DF.Literal["", "Paid", "Partially Paid", "Overdue", "Unpaid"]
        subscription: DF.Link
        total: DF.Float
    # end: auto-generated types

    pass

    def before_submit(self):
        self.set_outstanding_amount()

    def on_submit(self) -> None:
        self.send_email_notification()

    def send_email_notification(self) -> None:
        if self.status == "Unpaid":
            from ..client.client import Client

            client_doc: Client = frappe.get_doc("Client", self.client)
            if client_doc.user_id:
                email_args = self.as_dict()
                email_args["brand"] = (
                    frappe.get_single_value("Zoezy Settings", "brand_name") or "Zoezy"
                )
                frappe.sendmail(
                    recipients=client_doc.user_id,
                    subject=f"Invoice {self.name} - Unpaid",
                    template="invoice",
                    args=email_args,
                )

    def set_outstanding_amount(self):
        self.outstanding_amount = self.total
