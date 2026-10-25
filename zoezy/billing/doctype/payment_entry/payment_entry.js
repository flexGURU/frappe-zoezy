frappe.ui.form.on("Payment Entry", {
	setup(frm) {
		frm.set_query("invoice", () => ({
			filters: { docstatus: 1, outstanding_amount: [">", 0] },
		}));
	},

	async invoice(frm) {
		if (!frm.doc.invoice || frm.doc.amount) return;

		const { message } = await frappe.db.get_value(
			"Client Invoice",
			frm.doc.invoice,
			"outstanding_amount"
		);
		frm.set_value("amount", message?.outstanding_amount || 0);
	},
});
