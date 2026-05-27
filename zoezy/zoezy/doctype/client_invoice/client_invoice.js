// Copyright (c) 2026, mukunajohn329@gmail.com and contributors
// For license information, please see license.txt

frappe.ui.form.on("Client Invoice", {
	validate: (frm) => {
		setTotal(frm);
	},
});
frappe.ui.form.on("Client Invoice Package", {
	package_name: async (frm, cdt, cdn) => {
		const row = locals[cdt][cdn];

		if (row.package_name) {
			const response = await frappe.db.get_value(
				"Package Type",
				row.package_name,
				"unit_price",
			);
			let unit_price = response?.message?.unit_price;

			unit_price
				? frappe.model.set_value(cdt, cdn, "unit_price", unit_price)
				: frappe.throw("Unit price not found for the selected package.");
		}
	},
});

function setTotal(frm) {
	let total = 0;
	frm.doc.packages.reduce((acc, row) => {
		total = acc + (row.unit_price || 0);
		return total;
	}, 0);

	frm.doc.total = total;
	frm.refresh_field("total");
}
