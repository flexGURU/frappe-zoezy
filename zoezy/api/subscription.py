import frappe
from frappe import _
from frappe.query_builder import DocType

from .utils import get_session_client, log_throw_error


@frappe.whitelist()
def get_subscriptions() -> list[dict]:
	client = get_session_client()
	if not client:
		return []

	try:
		client_subscription = DocType("Client Subscription")
		package_type_items = DocType("Package Type Items")
		rows = (
			frappe.qb.from_(client_subscription)
			.left_join(package_type_items)
			.on(
				(package_type_items.parent == client_subscription.package_type)
				& (package_type_items.parenttype == "Package Type")
			)
			.where(client_subscription.client == client)
			.select(
				client_subscription.name,
				client_subscription.package_type,
				client_subscription.package_price,
				client_subscription.from_date,
				client_subscription.to_date,
				client_subscription.status,
				package_type_items.item,
			)
			.orderby(client_subscription.from_date, order=frappe.qb.desc)
			.orderby(package_type_items.idx)
		).run(as_dict=True)
	except Exception:
		log_throw_error(_("Error fetching subscriptions. Please try again."))

	subscriptions: dict[str, dict] = {}
	for row in rows:
		if row.name not in subscriptions:
			subscriptions[row.name] = {
				"name": row.name,
				"package_name": row.package_type,
				"price": row.package_price,
				"from_date": str(row.from_date),
				"to_date": str(row.to_date),
				"status": row.status,
				"items": [],
			}
		if row.item:
			subscriptions[row.name]["items"].append(row.item)

	return list(subscriptions.values())
