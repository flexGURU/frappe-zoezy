import frappe


def make_client(email: str = "test-client@zoezy.test", first_name: str = "Test") -> str:
	if not frappe.db.exists("User", email):
		frappe.get_doc(
			{
				"doctype": "User",
				"email": email,
				"first_name": first_name,
				"last_name": "Client",
				"send_welcome_email": 0,
			}
		).insert(ignore_permissions=True)
	if not frappe.db.exists("Client", email):
		frappe.get_doc({"doctype": "Client", "email": email}).insert(ignore_permissions=True)
	return email


def make_package(name: str = "Test Package", price: float = 3000) -> str:
	if not frappe.db.exists("Package Type", name):
		frappe.get_doc(
			{
				"doctype": "Package Type",
				"package_name": name,
				"unit_price": price,
				"items": [{"item": "4 sessions a week"}],
			}
		).insert(ignore_permissions=True)
	return name


def make_subscription(client: str, package: str, from_date, to_date=None):
	return frappe.get_doc(
		{
			"doctype": "Client Subscription",
			"client": client,
			"package_type": package,
			"from_date": from_date,
			"to_date": to_date,
		}
	).insert(ignore_permissions=True)


def make_trainer(email: str = "test-trainer@zoezy.test") -> str:
	if not frappe.db.exists("User", email):
		user = frappe.get_doc(
			{"doctype": "User", "email": email, "first_name": "Test", "send_welcome_email": 0}
		).insert(ignore_permissions=True)
		user.add_roles("Trainer")
	return email


def manual_sets(exercise: str, *sets: tuple[int, float]) -> list[dict]:
	return [
		{"exercise": exercise, "set_no": i, "reps": reps, "weight": weight}
		for i, (reps, weight) in enumerate(sets, start=1)
	]


def plan_row(exercise: str, sets: int, mode: str = "Manual", **extra) -> dict:
	return {"exercise": exercise, "sets": sets, "weight_mode": mode, **extra}


def make_exercise(name: str, category: str) -> str:
	if not frappe.db.exists("Workout Category", category):
		frappe.get_doc({"doctype": "Workout Category", "category_name": category}).insert()
	if not frappe.db.exists("Exercise Type", name):
		frappe.get_doc({"doctype": "Exercise Type", "exercise_name": name, "category": category}).insert()
	return name
