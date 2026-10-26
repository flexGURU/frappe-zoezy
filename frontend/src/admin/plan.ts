import type { WeightMode } from "@/types";

export const MAX_SETS = 20;

export interface SetDraft {
	reps: number | string;
	weight: number | string;
}

export interface ExerciseDraft {
	key: number;
	exercise: string | null;
	weight_mode: WeightMode;
	start_weight: number | string;
	progression_weight: number | string;
	description: string;
	sets: SetDraft[];
}

export interface PlanDraft {
	name?: string;
	client: string | null;
	day: string | null;
	category: string | null;
	exercises: ExerciseDraft[];
}

export interface SavedPlan {
	name: string;
	client: string;
	day: string;
	category: string;
	exercises: {
		exercise: string;
		sets: number;
		weight_mode: WeightMode;
		start_weight: number;
		progression_weight: number;
		description: string | null;
	}[];
	set_plan: { exercise: string; set_no: number; reps: number; weight: number }[];
}

let nextKey = 1;

export function newExercise(): ExerciseDraft {
	return {
		key: nextKey++,
		exercise: null,
		weight_mode: "Manual",
		start_weight: "",
		progression_weight: 5,
		description: "",
		sets: [
			{ reps: 10, weight: "" },
			{ reps: 10, weight: "" },
			{ reps: 10, weight: "" },
		],
	};
}

export const num = (value: number | string) => (value === "" || value == null ? NaN : Number(value));

export function progressiveWeight(e: ExerciseDraft, index: number) {
	return (num(e.start_weight) || 0) + (num(e.progression_weight) || 0) * index;
}

export function resizeSets(e: ExerciseDraft, count: number) {
	const target = Math.min(Math.max(count, 1), MAX_SETS);
	while (e.sets.length < target) {
		const last = e.sets[e.sets.length - 1] ?? { reps: 10, weight: "" };
		e.sets.push({ ...last });
	}
	e.sets.splice(target);
}

export function switchMode(e: ExerciseDraft, mode: WeightMode) {
	if (mode === e.weight_mode) return;
	if (mode === "Progressive") {
		const first = num(e.sets[0]?.weight);
		if (e.start_weight === "" && !Number.isNaN(first)) e.start_weight = first;
	} else {
		e.sets.forEach((s, i) => (s.weight = progressiveWeight(e, i)));
	}
	e.weight_mode = mode;
}

export function exerciseErrors(e: ExerciseDraft): string[] {
	const errors: string[] = [];
	if (!e.exercise) errors.push("Pick an exercise.");
	e.sets.forEach((s, i) => {
		const reps = num(s.reps);
		if (!Number.isInteger(reps) || reps < 1) errors.push(`Set ${i + 1}: reps must be a whole number of at least 1.`);
		if (e.weight_mode === "Manual" && num(s.weight) < 0) errors.push(`Set ${i + 1}: weight can't be negative.`);
	});
	if (e.weight_mode === "Progressive") {
		if (Number.isNaN(num(e.start_weight)) || num(e.start_weight) < 0) errors.push("Enter a start weight.");
		if (!(num(e.progression_weight) > 0)) errors.push("The step per set must be more than 0 kg.");
	}
	return errors;
}

export function toPayload(plan: PlanDraft) {
	return {
		name: plan.name,
		client: plan.client,
		day: plan.day,
		category: plan.category,
		exercises: plan.exercises.map((e) => ({
			exercise: e.exercise,
			sets: e.sets.length,
			weight_mode: e.weight_mode,
			start_weight: e.weight_mode === "Progressive" ? num(e.start_weight) : 0,
			progression_weight: e.weight_mode === "Progressive" ? num(e.progression_weight) : 0,
			description: e.description,
		})),
		set_plan: plan.exercises.flatMap((e) =>
			e.sets.map((s, i) => ({
				exercise: e.exercise,
				set_no: i + 1,
				reps: num(s.reps),
				weight: e.weight_mode === "Progressive" ? progressiveWeight(e, i) : num(s.weight) || 0,
			}))
		),
	};
}

export function fromSaved(saved: SavedPlan): PlanDraft {
	return {
		name: saved.name,
		client: saved.client,
		day: saved.day,
		category: saved.category,
		exercises: saved.exercises.map((e) => ({
			key: nextKey++,
			exercise: e.exercise,
			weight_mode: e.weight_mode,
			start_weight: e.weight_mode === "Progressive" ? e.start_weight : "",
			progression_weight: e.weight_mode === "Progressive" ? e.progression_weight : 5,
			description: e.description ?? "",
			sets: saved.set_plan
				.filter((s) => s.exercise === e.exercise)
				.sort((a, b) => a.set_no - b.set_no)
				.map((s) => ({ reps: s.reps, weight: s.weight })),
		})),
	};
}
