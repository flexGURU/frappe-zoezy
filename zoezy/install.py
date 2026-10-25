import frappe

from zoezy.zoezy.doctype.zoezy_settings.zoezy_settings import DEFAULT_LOGO


def after_install():
	set_desk_logo()


def set_desk_logo():
	if not frappe.db.get_single_value("Navbar Settings", "app_logo"):
		frappe.db.set_single_value("Navbar Settings", "app_logo", DEFAULT_LOGO)
