frappe.ui.form.on("Workout Log", {
	refresh(frm) {
		filterExercisesByCategory(frm);
		frm.set_intro(
			__(
				"Trainers edit workout plans in the Zoezy app, where each set has its own reps and weight."
			),
			"blue"
		);
		frm.add_custom_button(__("Edit in Zoezy"), () => {
			window.open(`/zoezy/admin/plans/${encodeURIComponent(frm.doc.name)}`, "_blank");
		});
	},

	category(frm) {
		filterExercisesByCategory(frm);
		frm.clear_table("exercises");
		frm.clear_table("set_plan");
		frm.refresh_fields(["exercises", "set_plan"]);
	},
});

function filterExercisesByCategory(frm) {
	const filters = frm.doc.category ? { category: frm.doc.category } : { name: ["in", []] };
	frm.set_query("exercise", "exercises", () => ({ filters }));
	frm.set_query("exercise", "set_plan", () => ({
		filters: { name: ["in", (frm.doc.exercises || []).map((row) => row.exercise)] },
	}));
}
