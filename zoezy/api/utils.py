import frappe


def log_throw_error(error_message: str) -> None:

    frappe.log_error(title=error_message, message=frappe.get_traceback())
    frappe.throw(error_message)
