<script setup lang="ts">
import { computed } from "vue";

import type { Exercise } from "@/types";
import { formatWeight } from "@/utils/format";

const props = defineProps<{ exercise: Exercise }>();

const sets = computed(() => props.exercise.set_details);
const heaviest = computed(() => Math.max(...sets.value.map((s) => s.weight), 1));
const hasWeight = computed(() => sets.value.some((s) => s.weight > 0));
</script>

<template>
	<div v-if="sets.length" class="flex items-end gap-1.5" aria-label="Weight and reps per set">
		<div
			v-for="set in sets"
			:key="set.set_no"
			class="flex min-w-0 flex-1 flex-col items-center gap-1"
		>
			<span class="text-2xs-semibold tabular-nums text-ink-gray-7">
				{{ set.weight > 0 ? formatWeight(set.weight) : "BW" }}
			</span>
			<div
				v-if="hasWeight"
				class="flex h-12 w-full items-end overflow-hidden rounded-[8px] bg-surface-gray-2"
			>
				<div
					class="w-full rounded-[8px] transition-[height] duration-500"
					:class="
						exercise.weight_mode === 'Progressive' ? 'bg-volt' : 'bg-surface-gray-8'
					"
					:style="{ height: `${Math.max((set.weight / heaviest) * 100, 18)}%` }"
				/>
			</div>
			<span class="text-2xs tabular-nums text-ink-gray-6">× {{ set.reps }}</span>
			<span class="text-2xs text-ink-gray-5">Set {{ set.set_no }}</span>
		</div>
	</div>
</template>
