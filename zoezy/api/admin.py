import frappe
from frappe import _
from frappe.utils import add_days, flt, now_datetime, today, validate_email_address

from zoezy.clients.doctype.client.client import setup_client_user

from .auth import PHONE_PATTERN, clean_name
from .permission import has_desk_permission

PLAN_FIELDS = ("client", "day", "category")
EXERCISE_FIELDS = (
	"exercise",
	"sets",
	"weight_mode",
	"start_weight",
	"progression_weight",
	"description",
)
SET_FIELDS = ("exercise", "set_no", "reps", "weight")


def require_staff() -> None:
	if not has_desk_permission():
		frappe.throw(_("Only trainers can do this."), frappe.PermissionError)


@frappe.whitelist()
def get_overview() -> dict:
	require_staff()
	soon = add_days(today(), 7)
	return {
		"active_clients": frappe.db.count("Client", {"status": "Active"}),
		"total_clients": frappe.db.count("Client"),
		"active_subscriptions": frappe.db.count("Client Subscription", {"status": "Active"}),
		"outstanding": flt(
			frappe.get_all(
				"Client Invoice",
				filters={"docstatus": 1},
				fields=[{"SUM": "outstanding_amount", "as": "total"}],
			)[0].total
		),
		"overdue_invoices": frappe.get_all(
			"Client Invoice",
			filters={"status": "Overdue", "docstatus": 1},
			fields=["name", "client_name", "outstanding_amount", "due_date"],
			order_by="due_date asc",
			limit=5,
		),
		"expiring_subscriptions": frappe.get_all(
			"Client Subscription",
			filters={"status": "Active", "to_date": ["between", [today(), soon]]},
			fields=["name", "client", "package_type", "to_date"],
			order_by="to_date asc",
			limit=5,
		),
		"recent_payments": frappe.get_all(
			"Payment Entry",
			filters={"docstatus": 1},
			fields=["name", "client_name", "amount", "mode_of_payment", "posting_date"],
			order_by="posting_date desc",
			limit=5,
		),
		"workout_plans": frappe.db.count("Workout Log"),
	}


@frappe.whitelist(methods=["POST"])
def create_client(
	first_name: str,
	last_name: str,
	email: str,
	phone: str | None = None,
	lead_source: str | None = None,
	age: int | str | None = None,
	send_invite: bool | int | str = True,
) -> str:
	require_staff()
	first_name, last_name = clean_name(first_name, _("First name")), clean_name(last_name, _("Last name"))
	phone = validate_phone(phone)
	email = (email or "").strip().lower()
	if not validate_email_address(email):
		frappe.throw(_("Please enter a valid email address."))
	if frappe.db.exists("Client", email):
		frappe.throw(_("{0} is already a client.").format(email))

	if frappe.db.exists("User", email):
		if frappe.db.get_value("User", email, "user_type") == "System User":
			frappe.throw(_("{0} belongs to a staff account and can't be added as a client.").format(email))
	else:
		frappe.get_doc(
			{
				"doctype": "User",
				"user_type": "Website User",
				"email": email,
				"first_name": first_name,
				"last_name": last_name,
				"phone": phone,
				"send_welcome_email": 1 if frappe.utils.cint(frappe.utils.sbool(send_invite)) else 0,
			}
		).insert(ignore_permissions=True)

	client = frappe.get_doc(
		{
			"doctype": "Client",
			"email": email,
			"phone_number": phone,
			"lead_source": lead_source or None,
			"age": frappe.utils.cint(age),
		}
	)
	client.insert()
	return client.name


@frappe.whitelist()
def get_client(name: str) -> dict:
	require_staff()
	client = frappe.get_doc("Client", name)
	client.check_permission("read")
	user = frappe.db.get_value(
		"User", client.email, ["first_name", "last_name", "enabled", "last_login"], as_dict=True
	)
	return {
		"name": client.name,
		"email": client.email,
		"full_name": client.full_name,
		"first_name": user.first_name,
		"last_name": user.last_name,
		"phone": client.phone_number,
		"age": client.age,
		"lead_source": client.lead_source,
		"status": client.status,
		"date_joined": client.date_joined,
		"portal_access": bool(user.enabled),
		"last_login": user.last_login,
		"subscriptions": frappe.get_all(
			"Client Subscription",
			filters={"client": name},
			fields=["name", "package_type", "package_price", "from_date", "to_date", "status"],
			order_by="from_date desc",
		),
		"invoices": frappe.get_all(
			"Client Invoice",
			filters={"client": name, "docstatus": ["<", 2]},
			fields=["name", "posting_date", "due_date", "total", "outstanding_amount", "status", "docstatus"],
			order_by="posting_date desc",
		),
		"plans": frappe.get_all(
			"Workout Log",
			filters={"client": name},
			fields=["name", "day", "category", "total_sets"],
		),
	}


@frappe.whitelist(methods=["POST"])
def update_client(
	name: str,
	first_name: str,
	last_name: str,
	phone: str | None = None,
	lead_source: str | None = None,
	age: int | str | None = None,
) -> str:
	require_staff()
	client = frappe.get_doc("Client", name)
	client.check_permission("write")

	user = frappe.get_doc("User", client.email)
	if user.user_type == "System User":
		frappe.throw(_("Staff accounts are managed by the administrator."))
	user.first_name = clean_name(first_name, _("First name"))
	user.last_name = clean_name(last_name, _("Last name"))
	user.phone = validate_phone(phone)
	user.save(ignore_permissions=True)

	client.phone_number = user.phone
	client.lead_source = lead_source or None
	client.age = frappe.utils.cint(age)
	client.save()
	return client.name


@frappe.whitelist(methods=["POST"])
def set_portal_access(name: str, enabled: bool | int | str) -> None:
	require_staff()
	frappe.get_doc("Client", name).check_permission("write")
	if frappe.db.get_value("User", name, "user_type") == "System User":
		frappe.throw(_("Staff accounts are managed by the administrator."))
	user = frappe.get_doc("User", name)
	user.enabled = 1 if frappe.utils.cint(frappe.utils.sbool(enabled)) else 0
	user.save(ignore_permissions=True)


@frappe.whitelist(methods=["POST"])
def send_invite(name: str) -> None:
	require_staff()
	frappe.get_doc("Client", name).check_permission("read")
	user = frappe.get_doc("User", name)
	if not user.enabled:
		frappe.throw(_("Turn on app access for this client first."))
	try:
		user._reset_password(send_email=True)
	except frappe.OutgoingEmailError:
		frappe.clear_messages()
		frappe.throw(
			_("Email isn't set up yet. Ask the administrator to add an outgoing email account."),
			title=_("Couldn't send the email"),
		)


@frappe.whitelist(methods=["POST"])
def save_workout_plan(plan: dict) -> str:
	require_staff()
	plan = frappe.parse_json(plan)
	values = {field: plan.get(field) for field in PLAN_FIELDS}
	values["exercises"] = [pick(row, EXERCISE_FIELDS) for row in plan.get("exercises") or []]
	values["set_plan"] = [pick(row, SET_FIELDS) for row in plan.get("set_plan") or []]

	if plan.get("name"):
		doc = frappe.get_doc("Workout Log", plan["name"])
		doc.check_permission("write")
		doc.update(values)
		doc.save()
	else:
		doc = frappe.get_doc({"doctype": "Workout Log", **values})
		doc.insert()
	return doc.name


@frappe.whitelist()
def get_workout_plan(name: str) -> dict:
	require_staff()
	doc = frappe.get_doc("Workout Log", name)
	doc.check_permission("read")
	return {
		"name": doc.name,
		"client_name": doc.client_name,
		**{field: doc.get(field) for field in PLAN_FIELDS},
		"exercises": [pick(row, (*EXERCISE_FIELDS, "rep_range", "final_weight")) for row in doc.exercises],
		"set_plan": [pick(row, SET_FIELDS) for row in doc.set_plan],
	}


@frappe.whitelist(methods=["POST"])
def create_invoice(
	client: str,
	subscription: str,
	packages: list | str,
	posting_date: str | None = None,
	due_date: str | None = None,
) -> str:
	require_staff()
	rows = [
		{"package_name": row.get("package_name"), "unit_price": flt(row.get("unit_price"))}
		for row in frappe.parse_json(packages) or []
	]
	if not rows:
		frappe.throw(_("Add at least one package."))

	invoice = frappe.get_doc(
		{
			"doctype": "Client Invoice",
			"client": client,
			"subscription": subscription,
			"posting_date": posting_date or today(),
			"due_date": due_date or None,
			"packages": rows,
		}
	)
	invoice.insert()
	invoice.submit()
	return invoice.name


@frappe.whitelist(methods=["POST"])
def record_payment(
	invoice: str,
	amount: float | str,
	mode_of_payment: str = "M-Pesa",
	reference_no: str | None = None,
	posting_date: str | None = None,
) -> str:
	require_staff()
	payment = frappe.get_doc(
		{
			"doctype": "Payment Entry",
			"invoice": invoice,
			"amount": flt(amount),
			"mode_of_payment": mode_of_payment,
			"reference_no": reference_no,
			"posting_date": posting_date or now_datetime(),
		}
	)
	payment.insert()
	payment.submit()
	return payment.name


@frappe.whitelist(methods=["POST"])
def cancel_document(doctype: str, name: str) -> None:
	require_staff()
	if doctype not in ("Client Invoice", "Payment Entry"):
		frappe.throw(_("Only invoices and payments can be cancelled here."), frappe.PermissionError)
	doc = frappe.get_doc(doctype, name)
	doc.cancel()


def pick(row, fields) -> dict:
	return {field: row.get(field) for field in fields}


def validate_phone(phone: str | None) -> str:
	phone = (phone or "").strip()
	if phone and not PHONE_PATTERN.match(phone):
		frappe.throw(_("Please enter a valid phone number."))
	return phone
