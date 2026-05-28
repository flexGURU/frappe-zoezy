# Copyright (c) 2026, mukunajohn329@gmail.com and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Client(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        age: DF.Int
        date_joined: DF.Date | None
        email: DF.Data
        first_name: DF.Data
        full_name: DF.Data | None
        last_name: DF.Data | None
        lead_source: DF.Link | None
        phone_number: DF.Data
        profile_image: DF.AttachImage | None
        status: DF.Literal["Active", "Inactive"]
        user_id: DF.Link
    # end: auto-generated types

    pass

    def validate(self):
        self.set_full_name()

    def on_update(self):
        self.create_user()

    def set_full_name(self):
        self.full_name = f"{self.first_name} {self.last_name or ''}".strip()

    def create_user(self):
        if not frappe.db.exists("User", self.email):
            try:
                user = frappe.get_doc(
                    {
                        "doctype": "User",
                        "email": self.email,
                        "first_name": self.first_name,
                        "last_name": self.last_name,
                        "enabled": 1,
                    }
                )
                user.insert(ignore_permissions=True)
            except Exception:
                frappe.log_error(
                    f"Failed to create user for client {self.name}",
                    frappe.get_traceback(),
                )
            else:
                self.user_id = user.name
