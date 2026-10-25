import frappe


def execute():
	frappe.delete_doc_if_exists("Dashboard", "Zoezy Stats")
