const INVOICE_COLORS = {
	Unpaid: "orange",
	"Partially Paid": "yellow",
	Paid: "green",
	Overdue: "red",
	Cancelled: "gray",
};

frappe.listview_settings["Client Invoice"] = {
	add_fields: ["status", "outstanding_amount"],
	has_indicator_for_draft: true,
	get_indicator(doc) {
		if (doc.docstatus === 0) return [__("Draft"), "gray", "docstatus,=,0"];
		return [__(doc.status), INVOICE_COLORS[doc.status] || "gray", `status,=,${doc.status}`];
	},
};
