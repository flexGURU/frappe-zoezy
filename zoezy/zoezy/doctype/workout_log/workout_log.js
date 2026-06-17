// Copyright (c) 2026, mukunajohn329@gmail.com and contributors
// For license information, please see license.txt

frappe.ui.form.on("Workout Log", {
	refresh(frm) {
		filterExercisesByCategory(frm);
	},

	category(frm) {
		filterExercisesByCategory(frm);
		frm.clear_table("exercises");
		frm.refresh_field("exercises");
	},
});

function filterExercisesByCategory(frm) {
	frm.set_query("exercise", "exercises", () => {
		if (!frm.doc.category) {
			return {
				filters: {
					name: ["in", []],
				},
			};
		}

		return {
			filters: {
				category: frm.doc.category,
			},
		};
	});
}
