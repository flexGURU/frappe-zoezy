# Copyright (c) 2026, mukunajohn329@gmail.com and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from ....api.utils import log_throw_error
from frappe.utils import add_days
from datetime import datetime


class ClientSubscription(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        client: DF.Link
        from_date: DF.Date
        package_price: DF.Float
        package_type: DF.Link
        status: DF.Literal["Active", "Expired"]
        to_date: DF.Date
    # end: auto-generated types

    pass

    def validate(self) -> None:
        self.create_invoice()
        self.validate_duplicates()

    def validate_duplicates(self) -> None:
        existing = frappe.db.exists(
            "Client Subscription",
            {
                "client": self.client,
                "package_type": self.package_type,
                "status": "Active",
            },
        )
        if existing and existing != self.name:
            frappe.throw(
                "Duplicate active subscription found for the same client and package type."
            )

    @frappe.whitelist()
    def add_days_to_date(self) -> datetime.date:
        from ..zoezy_settings.zoezy_settings import ZoezySettings

        settings: ZoezySettings = frappe.get_single("Zoezy Settings")
        if settings.active_period_duration and self.from_date:
            return add_days(self.from_date, settings.active_period_duration)

    def create_invoice(self) -> None:

        if self.status == "Active":
            return

        from zoezy.zoezy.doctype.client_invoice.client_invoice import ClientInvoice
        from zoezy.zoezy.doctype.package_type.package_type import PackageType

        package: PackageType = frappe.get_doc("Package Type", self.package_type)

        invoice: ClientInvoice = frappe.new_doc("Client Invoice")
        invoice.client = self.client
        invoice.subscription = self.name
        invoice.posting_date = self.from_date
        invoice.total = package.unit_price

        invoice.append(
            "packages",
            {
                "package_name": self.package_type,
                "unit_price": package.unit_price,
            },
        )

        invoice.save()
        invoice.submit()


def handle_subscription_expiry() -> None:
    from frappe.utils import getdate

    subscriptions: list[str] = frappe.get_all(
        "Client Subscription", filters={"status": "Active"}, pluck="name"
    )

    for subscription_name in subscriptions:
        try:
            subscription: ClientSubscription = frappe.get_doc(
                "Client Subscription", subscription_name
            )
            if getdate(subscription.to_date) < getdate():
                subscription.status = "Expired"
                subscription.save()

        except Exception:
            log_throw_error("Error updating subscription status.")

    frappe.db.commit()
