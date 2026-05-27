# Copyright (c) 2026, mukunajohn329@gmail.com and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class PackageType(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF
		from zoezy.zoezy.doctype.package_type_items.package_type_items import PackageTypeItems

		items: DF.Table[PackageTypeItems]
		package_name: DF.Data
		unit_price: DF.Float
	# end: auto-generated types

	pass
