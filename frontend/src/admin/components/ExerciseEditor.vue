<script setup lang="ts">
import { Button, TabButtons, TextInput, Textarea } from "frappe-ui";
import { computed } from "vue";

import {
	type ExerciseDraft,
	MAX_SETS,
	exerciseErrors,
	progressiveWeight,
	resizeSets,
	switchMode,
} from "@/admin/plan";
import type { WeightMode } from "@/types";
import { formatWeight } from "@/utils/format";
import LinkSelect from "./LinkSelect.vue";

const props = defineProps<{
	exercise: ExerciseDraft;
	index: number;
	count: number;
	category: string;
	taken: string[];
	showErrors: boolean;
}>();
const emit = defineEmits<{ remove: []; move: [by: -1 | 1] }>();

const e = props.exercise;
const errors = computed(() => [
	...exerciseErrors(e),
	...(e.exercise && props.taken.includes(e.exercise)
		? ["This exercise is already in the plan."]
		: []),
]);
const mode = computed({
	get: () => e.weight_mode,
	set: (value: WeightMode) => switchMode(e, value),
});

function copyFirstSet() {
	const [first] = e.sets;
	e.sets.forEach((s) => {
		s.reps = first.reps;
		if (e.weight_mode === "Manual") s.weight = first.weight;
	});
}
</script>

<template>
	<article
		class="card overflow-hidden"
		:class="showErrors && errors.length ? 'ring-2 ring-outline-red-3' : ''"
	>
		<header class="flex items-center gap-3 border-b border-outline-gray-1 p-4">
			<span
				class="grid size-9 shrink-0 place-items-center rounded-[12px] bg-night font-display text-base font-semibold text-volt"
			>
				{{ index + 1 }}
			</span>
			<LinkSelect
				:key="category"
				v-model="e.exercise"
				class="min-w-0 flex-1"
				placeholder="Choose an exercise"
				:link="{ doctype: 'Exercise Type', filters: { category } }"
			/>
			<div class="flex shrink-0 gap-1">
				<Button
					icon="lucide-arrow-up"
					variant="ghost"
					aria-label="Move up"
					:disabled="index === 0"
					@click="emit('move', -1)"
				/>
				<Button
					icon="lucide-arrow-down"
					variant="ghost"
					aria-label="Move down"
					:disabled="index === count - 1"
					@click="emit('move', 1)"
				/>
				<Button
					icon="lucide-trash-2"
					variant="ghost"
					aria-label="Remove exercise"
					@click="emit('remove')"
				/>
			</div>
		</header>

		<div class="space-y-4 p-4">
			<div class="flex flex-wrap items-end gap-4">
				<div>
					<p class="mb-1.5 text-xs text-ink-gray-5">Sets</p>
					<div class="flex items-center gap-1">
						<Button
							icon="lucide-minus"
							aria-label="One set fewer"
							:disabled="e.sets.length <= 1"
							@click="resizeSets(e, e.sets.length - 1)"
						/>
						<span
							class="w-10 text-center font-display text-2xl font-semibold tabular-nums"
							>{{ e.sets.length }}</span
						>
						<Button
							icon="lucide-plus"
							aria-label="One more set"
							:disabled="e.sets.length >= MAX_SETS"
							@click="resizeSets(e, e.sets.length + 1)"
						/>
					</div>
				</div>
				<div>
					<p class="mb-1.5 text-xs text-ink-gray-5">Weights</p>
					<TabButtons
						v-model="mode"
						:options="[
							{ label: 'Set by set', value: 'Manual' },
							{ label: 'Fixed step', value: 'Progressive' },
						]"
					/>
				</div>
				<template v-if="e.weight_mode === 'Progressive'">
					<TextInput
						v-model="e.start_weight"
						class="w-32"
						type="number"
						label="Start (kg)"
						:min="0"
						size="md"
					/>
					<TextInput
						v-model="e.progression_weight"
						class="w-32"
						type="number"
						label="Add per set (kg)"
						:min="0"
						size="md"
					/>
				</template>
			</div>

			<div class="overflow-hidden rounded-[16px] border border-outline-gray-1">
				<div
					class="grid grid-cols-[3.5rem_1fr_1fr] gap-2 bg-surface-gray-1 px-3 py-2 text-xs-medium text-ink-gray-5"
				>
					<span>Set</span><span>Reps</span><span>Weight (kg)</span>
				</div>
				<div
					v-for="(s, i) in e.sets"
					:key="i"
					class="grid grid-cols-[3.5rem_1fr_1fr] items-center gap-2 border-t border-outline-gray-1 px-3 py-2"
				>
					<span class="font-display text-lg font-semibold text-ink-gray-7">{{
						i + 1
					}}</span>
					<TextInput
						v-model="s.reps"
						type="number"
						:min="1"
						size="md"
						:aria-label="`Set ${i + 1} reps`"
					/>
					<TextInput
						v-if="e.weight_mode === 'Manual'"
						v-model="s.weight"
						type="number"
						:min="0"
						size="md"
						placeholder="0 = bodyweight"
						:aria-label="`Set ${i + 1} weight`"
					/>
					<span
						v-else
						class="flex h-9 items-center rounded-[8px] bg-surface-gray-2 px-3 tabular-nums text-ink-gray-7"
					>
						{{ formatWeight(progressiveWeight(e, i)) }}
					</span>
				</div>
			</div>

			<div class="flex flex-wrap items-center justify-between gap-2">
				<Button
					v-if="e.sets.length > 1"
					size="sm"
					icon-left="lucide-copy"
					label="Copy set 1 to every set"
					@click="copyFirstSet"
				/>
				<span class="text-xs text-ink-gray-5">Up to {{ MAX_SETS }} sets</span>
			</div>

			<Textarea
				v-model="e.description"
				label="Coach's notes"
				:rows="2"
				size="md"
				placeholder="Cues the client sees under this exercise"
			/>

			<ul v-if="showErrors && errors.length" class="space-y-1 text-sm text-ink-red-6">
				<li v-for="err in errors" :key="err">{{ err }}</li>
			</ul>
		</div>
	</article>
</template>
