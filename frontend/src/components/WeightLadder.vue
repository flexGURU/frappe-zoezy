<script setup lang="ts">
import { computed } from "vue";

import type { Exercise } from "@/types";
import { formatWeight } from "@/utils/format";
import { setWeights } from "@/utils/week";

const props = defineProps<{ exercise: Exercise }>();

const weights = computed(() => setWeights(props.exercise));
const heaviest = computed(() => Math.max(...weights.value, 1));
</script>

<template>
	<div v-if="weights.length" class="flex items-end gap-1.5" aria-label="Weight per set">
		<div
			v-for="(kg, i) in weights"
			:key="i"
			class="flex min-w-0 flex-1 flex-col items-center gap-1"
		>
			<span class="text-2xs-semibold tabular-nums text-ink-gray-7">{{
				formatWeight(kg)
			}}</span>
			<div
				class="flex h-12 w-full items-end overflow-hidden rounded-[8px] bg-surface-gray-2"
			>
				<div
					class="w-full rounded-[8px] transition-[height] duration-500"
					:class="exercise.progressive_overload ? 'bg-volt' : 'bg-surface-gray-8'"
					:style="{ height: `${Math.max((kg / heaviest) * 100, 18)}%` }"
				/>
			</div>
			<span class="text-2xs text-ink-gray-5">Set {{ i + 1 }}</span>
		</div>
	</div>
</template>
