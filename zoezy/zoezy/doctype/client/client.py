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
        email: DF.Link
        first_name: DF.Data | None
        full_name: DF.Data | None
        last_name: DF.Data | None
        lead_source: DF.Link | None
        phone_number: DF.Data | None
        profile_image: DF.AttachImage | None
        status: DF.Literal["Active", "Inactive"]
        userid: DF.Link | None
    # end: auto-generated types

    pass

    def validate(self):
        self.set_full_name()
        self.userid = self.email

    def set_full_name(self):
        self.full_name = f"{self.first_name or ''} {self.last_name or ''}"

    @property
    def user(self) -> str | None:
        return self.user_id
