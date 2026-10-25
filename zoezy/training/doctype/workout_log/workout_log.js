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

frappe.ui.form.on("Workout Log Exercise", {
	sets: setFinalWeight,
	start_weight: setFinalWeight,
	progression_weight: setFinalWeight,
	progressive_overload: setFinalWeight,
});

function setFinalWeight(frm, cdt, cdn) {
	const row = locals[cdt][cdn];
	const finalWeight = row.progressive_overload
		? (row.start_weight || 0) +
		  (row.progression_weight || 0) * Math.max((row.sets || 1) - 1, 0)
		: 0;
	frappe.model.set_value(cdt, cdn, "final_weight", finalWeight);
}

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
