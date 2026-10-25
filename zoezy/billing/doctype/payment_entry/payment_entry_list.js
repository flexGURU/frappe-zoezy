frappe.listview_settings["Payment Entry"] = {
	get_indicator(doc) {
		if (doc.docstatus === 0) return [__("Draft"), "gray", "docstatus,=,0"];
		if (doc.docstatus === 2) return [__("Cancelled"), "red", "docstatus,=,2"];
		return [__("Received"), "green", "docstatus,=,1"];
	},
};
