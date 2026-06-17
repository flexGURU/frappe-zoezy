import frappe
from frappe.rate_limiter import rate_limit
from .utils import log_throw_error
from frappe.core.doctype.user.user import User
from frappe.query_builder import DocType


@frappe.whitelist(allow_guest=True)
@rate_limit(key="email", limit=5, seconds=1800)
def sign_up(first_name: str, last_name: str, email: str, phone: str) -> None:

    if frappe.db.exists("User", email):
        frappe.throw("A user with this email already exists.")

    try:
        user: User = frappe.get_doc(
            {
                "doctype": "User",
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "phone": phone,
                "enabled": 1,
            }
        )
        user.insert(ignore_permissions=True)
        user.add_roles("Client")
        frappe.db.commit()
    except Exception:
        frappe.db.rollback()
        log_throw_error("Error creating user account. Please try again.")


@frappe.whitelist()
def get_user_details() -> dict:
    user = frappe.session.user
    if user == "Guest":
        return {"is_guest": True}

    user_doc: User = frappe.get_doc("User", user)

    user_details = frappe._dict()
    user_details.first_name = user_doc.first_name
    user_details.last_name = user_doc.last_name
    user_details.email = user_doc.email
    user_details.phone = user_doc.phone

    return user_details


@frappe.whitelist()
def get_client_invoices() -> list[dict]:
    try:
        client_invoice = DocType("Client Invoice")
        client_invoice_package = DocType("Client Invoice Package")

        rows = (
            frappe.qb.from_(client_invoice)
            .left_join(client_invoice_package)
            .on(client_invoice_package.parent == client_invoice.name)
            .where(client_invoice.client == frappe.session.user)
            .where(client_invoice.docstatus == 1)
            .select(
                client_invoice.name,
                client_invoice.posting_date,
                client_invoice.status,
                client_invoice.total,
                client_invoice.subscription,
                client_invoice_package.package_name,
                client_invoice_package.unit_price,
            )
            .orderby(client_invoice.posting_date, order=frappe.qb.desc)
        ).run(as_dict=True)

        # Group packages back into their invoice
        invoices: dict = {}
        for row in rows:
            inv_name = row["name"]
            if inv_name not in invoices:
                invoices[inv_name] = {
                    "name": inv_name,
                    "posting_date": str(row["posting_date"]),
                    "status": row["status"],
                    "total": row["total"],
                    "subscription": row["subscription"],
                    "packages": [],
                }
            if row["package_name"]:
                invoices[inv_name]["packages"].append(
                    {
                        "package_name": row["package_name"],
                        "unit_price": row["unit_price"],
                    }
                )

        return list(invoices.values())
    except Exception:
        log_throw_error("Error fetching invoices. Please try again.")


@frappe.whitelist()
def get_client_subscriptions() -> list[dict]:
    client_subscription = DocType("Client Subscription")
    package_type = DocType("Package Type")
    package_type_items = DocType("Package Type Items")
    try:

        rows = (
            frappe.qb.from_(client_subscription)
            .left_join(package_type)
            .on(client_subscription.package_type == package_type.name)
            .left_join(package_type_items)
            .on(package_type_items.parent == package_type.name)
            .where(client_subscription.client == frappe.session.user)
            .select(
                client_subscription.name,
                client_subscription.package_type,
                client_subscription.from_date,
                client_subscription.to_date,
                client_subscription.status,
                package_type.package_name,
                package_type.unit_price,
                package_type_items.item,
            )
            .orderby(client_subscription.from_date, order=frappe.qb.desc)
        ).run(as_dict=True)

        # Group items back into their subscription
        subscriptions: dict = {}
        for row in rows:
            sub_name = row["name"]
            if sub_name not in subscriptions:
                subscriptions[sub_name] = {
                    "name": sub_name,
                    "package_type": row["package_type"],
                    "package_name": row["package_name"],
                    "unit_price": row["unit_price"],
                    "from_date": str(row["from_date"]) if row["from_date"] else None,
                    "to_date": str(row["to_date"]) if row["to_date"] else None,
                    "status": row["status"],
                    "items": [],
                }
            if row["item"]:
                subscriptions[sub_name]["items"].append(row["item"])

        return list(subscriptions.values())
    except Exception:
        log_throw_error("Error fetching subscriptions. Please try again.")


@frappe.whitelist()
def get_client_workout_logs() -> list[dict]:

    def process_workout_logs(logs: list[dict]) -> list[dict]:
        grouped = {}

        for log in logs:
            day = log.get("day")
            category = log.get("category")
            exercise = log.get("exercise")
            sets = log.get("sets")
            rep_range = log.get("rep_range")

            key = (day, category)
            if key not in grouped:
                grouped[key] = {
                    "day": day,
                    "category": category,
                    "exercises": [],
                }
            grouped[key]["exercises"].append(
                {
                    "exercise": exercise,
                    "sets": sets,
                    "rep_range": rep_range,
                    "video_url": log.get("video_url"),
                    "description": log.get("description"),
                    "progressive_overload": log.get("progressive_overload"),
                    "stagnant_weight": log.get("stagnant_weight"),
                    "start_weight": log.get("start_weight"),
                    "progression_weight": log.get("progression_weight"),
                    "final_weight": log.get("final_weight"),
                }
            )

        return list(grouped.values())

    try:
        workout_log = DocType("Workout Log")
        workout_log_exercise = DocType("Workout Log Exercise")
        logs = (
            frappe.qb.from_(workout_log)
            .join(workout_log_exercise)
            .on(workout_log.name == workout_log_exercise.parent)
            .where(workout_log.client == frappe.session.user)
            .select(
                workout_log.day,
                workout_log.category,
                workout_log_exercise.exercise,
                workout_log_exercise.sets,
                workout_log_exercise.rep_range,
                workout_log_exercise.video_url,
                workout_log_exercise.description,
                workout_log_exercise.progressive_overload,
                workout_log_exercise.stagnant_weight,
                workout_log_exercise.start_weight,
                workout_log_exercise.progression_weight,
                workout_log_exercise.final_weight,
            )
            .distinct()
            .orderby(workout_log.name)
            .orderby(workout_log_exercise.idx)
        )

        return process_workout_logs(logs.run(as_dict=True))
    except Exception:
        log_throw_error("Error fetching workout logs. Please try again.")
