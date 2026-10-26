<script setup lang="ts">
import {
	Button,
	ErrorMessage,
	type ErrorMessageValue,
	Select,
	call,
	dialog,
	toast,
} from "frappe-ui";
import { computed, reactive, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";

import AdminHeader from "@/admin/components/AdminHeader.vue";
import ExerciseEditor from "@/admin/components/ExerciseEditor.vue";
import LinkSelect from "@/admin/components/LinkSelect.vue";
import { adminCall, useDocList } from "@/admin/data";
import {
	type PlanDraft,
	type SavedPlan,
	exerciseErrors,
	fromSaved,
	newExercise,
	num,
	progressiveWeight,
	toPayload,
} from "@/admin/plan";
import SkeletonBlock from "@/components/SkeletonBlock.vue";
import { WEEKDAYS } from "@/utils/week";

const props = defineProps<{ name?: string }>();
const route = useRoute();
const router = useRouter();

const plan = reactive<PlanDraft>({
	client: (route.query.client as string) || null,
	day: null,
	category: null,
	exercises: [newExercise()],
});
const loading = ref(Boolean(props.name));
const saving = ref(false);
const showErrors = ref(false);
const error = ref<ErrorMessageValue>();

const categories = useDocList("Workout Category", { orderBy: "name asc" });

async function load(name: string) {
	loading.value = true;
	const saved = await adminCall<SavedPlan>("get_workout_plan", { name });
	Object.assign(plan, fromSaved(saved));
	loading.value = false;
}
if (props.name) load(props.name);

let lastCategory = plan.category;
watch(
	() => plan.category,
	(category, previous) => {
		if (loading.value || previous === null || category === lastCategory) {
			lastCategory = category;
			return;
		}
		if (plan.exercises.some((e) => e.exercise)) {
			dialog.confirm({
				title: "Change category?",
				message:
					"The exercises picked so far belong to the old category and will be cleared.",
				confirmLabel: "Change",
				onConfirm: () => {
					lastCategory = category;
					plan.exercises = [newExercise()];
				},
				onCancel: () => {
					plan.category = lastCategory;
				},
			});
		} else {
			lastCategory = category;
		}
	}
);

function move(index: number, by: -1 | 1) {
	const [item] = plan.exercises.splice(index, 1);
	plan.exercises.splice(index + by, 0, item);
}

const taken = (index: number) =>
	plan.exercises
		.filter((_, i) => i !== index)
		.map((e) => e.exercise)
		.filter(Boolean) as string[];

const summary = computed(() => {
	let sets = 0;
	let volume = 0;
	for (const e of plan.exercises) {
		e.sets.forEach((s, i) => {
			sets++;
			const weight =
				e.weight_mode === "Progressive" ? progressiveWeight(e, i) : num(s.weight) || 0;
			volume += (num(s.reps) || 0) * weight;
		});
	}
	return { sets, volume: Math.round(volume) };
});

const valid = computed(
	() =>
		plan.client &&
		plan.day &&
		plan.category &&
		plan.exercises.length > 0 &&
		plan.exercises.every(
			(e, i) => !exerciseErrors(e).length && !taken(i).includes(e.exercise ?? "")
		)
);

async function save() {
	showErrors.value = true;
	error.value = undefined;
	if (!valid.value) {
		error.value =
			!plan.client || !plan.day || !plan.category
				? "Choose a client, day and category."
				: "Fix the highlighted exercises first.";
		return;
	}
	saving.value = true;
	try {
		const name = await adminCall<string>("save_workout_plan", { plan: toPayload(plan) });
		toast.success("Workout plan saved");
		if (!props.name) router.replace({ name: "AdminPlan", params: { name } });
		else await load(name);
		showErrors.value = false;
	} catch (e) {
		error.value = e as Error;
	} finally {
		saving.value = false;
	}
}

function remove() {
	dialog.danger({
		title: "Delete this workout plan?",
		onConfirm: async () => {
			await call("frappe.client.delete", { doctype: "Workout Log", name: props.name });
			toast.success("Workout plan deleted");
			router.push({ name: "AdminPlans" });
		},
	});
}
</script>

<template>
	<div>
		<AdminHeader
			:title="name ? 'Edit workout plan' : 'New workout plan'"
			subtitle="Training"
			:back="{ label: 'Workout plans', to: { name: 'AdminPlans' } }"
		>
			<template #actions>
				<Button
					v-if="name"
					icon="lucide-trash-2"
					aria-label="Delete plan"
					@click="remove"
				/>
				<Button
					variant="solid"
					icon-left="lucide-check"
					:loading="saving"
					label="Save plan"
					@click="save"
				/>
			</template>
		</AdminHeader>

		<div v-if="loading" class="space-y-4">
			<SkeletonBlock class="h-24" />
			<SkeletonBlock class="h-72" />
		</div>

		<div v-else class="grid gap-4 lg:grid-cols-[1fr_18rem]">
			<div class="space-y-4">
				<section class="card grid gap-4 p-4 sm:grid-cols-3">
					<LinkSelect
						v-model="plan.client"
						label="Client"
						:link="{ doctype: 'Client', labelField: 'full_name' }"
						:disabled="Boolean(name)"
						required
					/>
					<Select
						v-model="plan.day"
						label="Day"
						placeholder="Choose a day"
						:options="WEEKDAYS.map((d) => ({ label: d, value: d }))"
						size="md"
					/>
					<Select
						v-model="plan.category"
						label="Category"
						placeholder="Choose a category"
						:options="(categories.data ?? []).map((c: { name: string }) => ({ label: c.name, value: c.name }))"
						size="md"
					/>
				</section>

				<p v-if="!plan.category" class="card p-6 text-center text-base text-ink-gray-5">
					Choose a category to start adding exercises.
				</p>
				<template v-else>
					<ExerciseEditor
						v-for="(exercise, i) in plan.exercises"
						:key="exercise.key"
						:exercise="exercise"
						:index="i"
						:count="plan.exercises.length"
						:category="plan.category"
						:taken="taken(i)"
						:show-errors="showErrors"
						@remove="plan.exercises.splice(i, 1)"
						@move="move(i, $event)"
					/>
					<Button
						class="w-full"
						size="lg"
						icon-left="lucide-plus"
						label="Add exercise"
						@click="plan.exercises.push(newExercise())"
					/>
				</template>
			</div>

			<aside class="space-y-3 lg:sticky lg:top-6 lg:self-start">
				<section class="card-night p-5">
					<p class="eyebrow text-volt">Session</p>
					<p class="mt-1 font-display text-3xl font-bold">{{ plan.category ?? "—" }}</p>
					<p class="text-sm text-white/60">{{ plan.day ?? "No day yet" }}</p>
					<dl class="mt-4 grid grid-cols-3 gap-2 text-center">
						<div>
							<dt class="text-2xs text-white/50">Exercises</dt>
							<dd class="font-display text-2xl font-semibold">
								{{ plan.exercises.length }}
							</dd>
						</div>
						<div>
							<dt class="text-2xs text-white/50">Sets</dt>
							<dd class="font-display text-2xl font-semibold">{{ summary.sets }}</dd>
						</div>
						<div>
							<dt class="text-2xs text-white/50">Volume</dt>
							<dd class="font-display text-2xl font-semibold">
								{{ summary.volume }}
							</dd>
						</div>
					</dl>
				</section>
				<ErrorMessage :message="error" />
				<Button
					class="w-full lg:hidden"
					variant="solid"
					size="lg"
					:loading="saving"
					label="Save plan"
					@click="save"
				/>
			</aside>
		</div>
	</div>
</template>
