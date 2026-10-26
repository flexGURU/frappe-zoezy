# Copyright (c) 2026, mukunajohn329@gmail.com and contributors
# For license information, please see license.txt

from frappe.model.document import Document


class WorkoutLogSet(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		exercise: DF.Link
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		reps: DF.Int
		set_no: DF.Int
		weight: DF.Float
	# end: auto-generated types

	pass
