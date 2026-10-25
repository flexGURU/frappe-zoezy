frappe.ui.form.on("Client Subscription", {
	async from_date(frm) {
		if (!frm.doc.from_date) return;

		const { message } = await frm.call("add_days_to_date");
		if (message) {
			frm.set_value("to_date", message);
		}
	},
});
