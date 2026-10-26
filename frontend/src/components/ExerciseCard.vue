<script setup lang="ts">
import { computed, ref } from "vue";

import type { Exercise } from "@/types";
import { formatWeight } from "@/utils/format";
import VideoEmbed from "./VideoEmbed.vue";
import WeightLadder from "./WeightLadder.vue";

const props = defineProps<{ exercise: Exercise; index: number }>();

const open = ref(false);
const progressive = computed(() => props.exercise.weight_mode === "Progressive");
const weights = computed(() => props.exercise.set_details.map((s) => s.weight));
const hasDetails = computed(
	() =>
		props.exercise.set_details.length > 0 ||
		Boolean(props.exercise.notes || props.exercise.video_url)
);
const weightSummary = computed(() => {
	const loaded = weights.value.filter((w) => w > 0);
	if (!loaded.length) return null;
	const low = Math.min(...loaded);
	const high = Math.max(...loaded);
	return low === high ? formatWeight(low) : `${formatWeight(low)} → ${formatWeight(high)}`;
});
</script>

<template>
	<article class="card overflow-hidden">
		<button
			type="button"
			class="flex w-full items-center gap-4 p-4 text-left sm:p-5"
			:class="hasDetails ? 'cursor-pointer' : 'cursor-default'"
			:aria-expanded="hasDetails ? open : undefined"
			@click="hasDetails && (open = !open)"
		>
			<span
				class="grid size-11 shrink-0 place-items-center rounded-[14px] bg-surface-gray-2 font-display text-lg font-semibold text-ink-gray-8"
			>
				{{ String(index + 1).padStart(2, "0") }}
			</span>

			<div class="min-w-0 flex-1">
				<p class="truncate text-lg-semibold text-ink-gray-9">{{ exercise.exercise }}</p>
				<div
					class="mt-1 flex flex-wrap items-center gap-x-3 gap-y-1 text-sm text-ink-gray-6"
				>
					<span class="tabular-nums">
						<b class="font-semibold text-ink-gray-8">{{ exercise.sets }}</b> sets ×
						<b class="font-semibold text-ink-gray-8">{{ exercise.reps }}</b> reps
					</span>
					<span v-if="weightSummary" class="inline-flex items-center gap-1 tabular-nums">
						<span
							:class="
								progressive
									? 'lucide-trending-up text-ink-green-6'
									: 'lucide-weight'
							"
							class="size-3.5"
						/>
						{{ weightSummary }}
					</span>
					<span v-if="exercise.video_url" class="inline-flex items-center gap-1">
						<span class="lucide-circle-play size-3.5" /> Demo
					</span>
				</div>
			</div>

			<span
				v-if="hasDetails"
				class="lucide-chevron-down size-5 shrink-0 text-ink-gray-5 transition-transform"
				:class="open ? 'rotate-180' : ''"
			/>
		</button>

		<div v-if="open" class="space-y-5 border-t border-outline-gray-1 p-4 sm:p-5">
			<div v-if="exercise.set_details.length">
				<p class="eyebrow mb-3 text-ink-gray-5">
					{{ progressive ? "Progressive overload" : "Your sets" }}
					<span v-if="progressive" class="normal-case tracking-normal">
						· +{{ formatWeight(exercise.progression_weight) }} each set
					</span>
				</p>
				<WeightLadder :exercise="exercise" />
			</div>

			<div v-if="exercise.notes">
				<p class="eyebrow mb-1.5 text-ink-gray-5">Coach's notes</p>
				<p class="whitespace-pre-line text-base text-ink-gray-7">{{ exercise.notes }}</p>
			</div>

			<VideoEmbed
				v-if="exercise.video_url"
				:url="exercise.video_url"
				:title="exercise.exercise"
			/>
		</div>
	</article>
</template>
