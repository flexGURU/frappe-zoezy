<script setup lang="ts">
import { computed } from "vue";

import type { PlanDay, Weekday } from "@/types";
import { currentWeek } from "@/utils/week";

const props = defineProps<{ plan: PlanDay[] | null; selected?: Weekday }>();
const emit = defineEmits<{ select: [day: Weekday] }>();

const days = computed(() =>
	currentWeek().map((d) => ({
		...d,
		short: d.day.slice(0, 3),
		trains: Boolean(props.plan?.find((p) => p.day === d.day)?.sessions.length),
	}))
);
</script>

<template>
	<div class="grid grid-cols-7 gap-1.5 sm:gap-2" role="tablist" aria-label="Days of the week">
		<button
			v-for="d in days"
			:key="d.day"
			type="button"
			role="tab"
			:aria-selected="selected === d.day"
			:aria-label="`${d.day}${d.trains ? ', training day' : ', rest day'}`"
			class="group flex flex-col items-center gap-1.5 rounded-[18px] py-2.5 transition-all focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-volt sm:py-3"
			:class="[
				selected === d.day
					? 'bg-night text-white shadow-lg'
					: 'bg-surface-base text-ink-gray-7 hover:bg-surface-gray-2',
				d.isToday && selected !== d.day ? 'ring-2 ring-inset ring-volt' : '',
			]"
			@click="emit('select', d.day)"
		>
			<span
				class="text-2xs-medium uppercase tracking-wider"
				:class="selected === d.day ? 'text-white/60' : 'text-ink-gray-5'"
			>
				{{ d.short }}
			</span>
			<span class="font-display text-xl font-semibold leading-none">{{ d.date }}</span>
			<span
				class="size-1.5 rounded-full"
				:class="
					d.trains
						? selected === d.day
							? 'bg-volt'
							: 'bg-surface-gray-10'
						: 'bg-transparent'
				"
			/>
		</button>
	</div>
</template>
