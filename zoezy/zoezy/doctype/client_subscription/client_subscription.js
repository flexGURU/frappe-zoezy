// Copyright (c) 2026, mukunajohn329@gmail.com and contributors
// For license information, please see license.txt

frappe.ui.form.on("Client Subscription", {
	from_date: async (frm) => {
		if (frm.doc.from_date) {
			const response = await frm.call("add_days_to_date");
			if (response.message) {
				frm.set_value("to_date", response.message);
			}
		}
	},
});
