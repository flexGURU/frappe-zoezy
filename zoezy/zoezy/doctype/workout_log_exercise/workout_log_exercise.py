# Copyright (c) 2026, mukunajohn329@gmail.com and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class WorkoutLogExercise(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		description: DF.SmallText | None
		exercise: DF.Link
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		rep_range: DF.Int
		sets: DF.Int
		video_url: DF.SmallText | None
	# end: auto-generated types

	pass
