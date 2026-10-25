import frappe


def log_throw_error(error_message: str) -> None:
	frappe.log_error(title=error_message, message=frappe.get_traceback())
	frappe.throw(error_message)


def get_session_client() -> str | None:
	user = frappe.session.user
	if user == "Guest":
		frappe.throw("Please log in to continue.", frappe.AuthenticationError)

	return user if frappe.db.exists("Client", user) else None
