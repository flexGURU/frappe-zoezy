<script setup lang="ts">
import { computed, ref } from "vue";

import type { Exercise } from "@/types";
import { formatWeight } from "@/utils/format";
import VideoEmbed from "./VideoEmbed.vue";
import WeightLadder from "./WeightLadder.vue";

const props = defineProps<{ exercise: Exercise; index: number }>();

const open = ref(false);
const hasWeights = computed(
	() => props.exercise.progressive_overload || Boolean(props.exercise.weight)
);
const hasDetails = computed(
	() => hasWeights.value || Boolean(props.exercise.notes || props.exercise.video_url)
);
const weightSummary = computed(() => {
	const e = props.exercise;
	if (e.progressive_overload)
		return `${formatWeight(e.start_weight)} → ${formatWeight(e.final_weight)}`;
	return e.weight ? formatWeight(e.weight) : null;
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
								exercise.progressive_overload
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
			<div v-if="hasWeights">
				<p class="eyebrow mb-3 text-ink-gray-5">
					{{ exercise.progressive_overload ? "Progressive overload" : "Working weight" }}
					<span v-if="exercise.progressive_overload" class="normal-case tracking-normal">
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
