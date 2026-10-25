frappe.ui.form.on("Client Invoice", {
	setup(frm) {
		frm.set_query("subscription", () => ({
			filters: frm.doc.client ? { client: frm.doc.client } : {},
		}));
	},

	refresh(frm) {
		if (frm.doc.docstatus === 1 && frm.doc.outstanding_amount > 0) {
			frm.add_custom_button(__("Record Payment"), () => {
				frappe.new_doc("Payment Entry", {
					invoice: frm.doc.name,
					amount: frm.doc.outstanding_amount,
				});
			});
		}
	},

	client(frm) {
		frm.set_value("subscription", null);
	},

	async subscription(frm) {
		if (!frm.doc.subscription) return;

		const { message } = await frappe.db.get_value(
			"Client Subscription",
			frm.doc.subscription,
			["package_type", "package_price"]
		);
		if (!message?.package_type) return;

		frm.clear_table("packages");
		frm.add_child("packages", {
			package_name: message.package_type,
			unit_price: message.package_price,
		});
		frm.refresh_field("packages");
		set_total(frm);
	},
});

frappe.ui.form.on("Client Invoice Package", {
	async package_name(frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		if (!row.package_name) return;

		const { message } = await frappe.db.get_value(
			"Package Type",
			row.package_name,
			"unit_price"
		);
		await frappe.model.set_value(cdt, cdn, "unit_price", message?.unit_price || 0);
	},

	unit_price: set_total,
	packages_remove: set_total,
});

function set_total(frm) {
	const total = (frm.doc.packages || []).reduce((sum, row) => sum + (row.unit_price || 0), 0);
	frm.set_value("total", total);
}
