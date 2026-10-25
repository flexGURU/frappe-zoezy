frappe.listview_settings["Client"] = {
	add_fields: ["status"],
	get_indicator(doc) {
		const color = doc.status === "Active" ? "green" : "gray";
		return [__(doc.status), color, `status,=,${doc.status}`];
	},
};
