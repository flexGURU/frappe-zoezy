frappe.listview_settings["Client Subscription"] = {
	add_fields: ["status"],
	get_indicator(doc) {
		const color = { Active: "green", Upcoming: "blue", Expired: "gray" }[doc.status] || "gray";
		return [__(doc.status), color, `status,=,${doc.status}`];
	},
};
