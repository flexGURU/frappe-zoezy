# Copyright (c) 2026, mukunajohn329@gmail.com and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class ZoezySettings(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		active_period_duration: DF.Int
		brand_name: DF.Data | None
		default_currency: DF.Link | None
		payment_number: DF.Data | None
	# end: auto-generated types

	pass
