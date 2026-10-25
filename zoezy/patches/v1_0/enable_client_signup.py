import frappe


def execute():
	if not frappe.db.exists("Singles", {"doctype": "Zoezy Settings", "field": "allow_client_signup"}):
		frappe.db.set_single_value("Zoezy Settings", "allow_client_signup", 1)
