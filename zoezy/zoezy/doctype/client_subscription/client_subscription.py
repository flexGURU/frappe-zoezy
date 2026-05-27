# Copyright (c) 2026, mukunajohn329@gmail.com and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class ClientSubscription(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		client: DF.Link
		from_date: DF.Date
		package_type: DF.Link
		status: DF.Literal["Active", "Expired"]
		to_date: DF.Date
	# end: auto-generated types

	pass
