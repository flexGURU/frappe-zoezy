import frappe
from frappe import rate_limiter
from .utils import log_throw_error


@frappe.whitelist(allow_guest=True)
@rate_limiter(key="email", limit=1, seconds=3600)
def sign_up(name: str, email: str, password: str) -> None:

    if frappe.db.exists("User", email):
        frappe.throw("A user with this email already exists.")

    try:
        user = frappe.get_doc(
            {
                "doctype": "User",
                "first_name": name,
                "email": email,
                "enabled": 1,
                "new_password": password,
            }
        )
        user.insert()
        user.send_welcome_email()
    except Exception:
        log_throw_error("Error creating user account. Please try again.")
