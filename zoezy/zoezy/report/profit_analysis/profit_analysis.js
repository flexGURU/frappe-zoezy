// Copyright (c) 2026, mukunajohn329@gmail.com and contributors
// For license information, please see license.txt

frappe.query_reports["Profit Analysis"] = {
	filters: [
		{
			fieldname: "periodicity",
			label: __("Periodicity"),
			fieldtype: "Select",
			options: ["Yearly", "Monthly", "Weekly", "Date Range"].join("\n"),
			default: "Monthly",
			reqd: 1,
		},
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			default: frappe.datetime.year_start(),
			reqd: 1,
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			default: frappe.datetime.get_today(),
			reqd: 1,
		},
		{
			fieldname: "client",
			label: __("Client"),
			fieldtype: "Link",
			options: "Client",
		},
		{
			fieldname: "subscription",
			label: __("Subscription"),
			fieldtype: "Link",
			options: "Client Subscription",
			get_query: () => {
				const client = frappe.query_report.get_filter_value("client");
				return client ? { filters: { client } } : {};
			},
		},
		{
			fieldname: "status",
			label: __("Status"),
			fieldtype: "Select",
			options: ["", "Paid", "Partially Paid", "Overdue", "Unpaid"].join("\n"),
		},
		{
			fieldname: "chart_type",
			label: __("Chart Type"),
			fieldtype: "Select",
			options: ["Bar", "Line"].join("\n"),
			default: "Bar",
		},
	],

	formatter(value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);

		if (column.fieldname === "collection_rate" && data && data.invoice_count) {
			const colour = data.collection_rate >= 75 ? "green" : "orange";
			value = `<span style="color: var(--text-on-${colour}, ${colour})">${value}</span>`;
		}
		return value;
	},
};
