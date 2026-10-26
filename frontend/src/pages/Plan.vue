<script setup lang="ts">
import { Button, usePageMeta } from "frappe-ui";
import { computed } from "vue";
import { useRoute, useRouter } from "vue-router";

import EmptyState from "@/components/EmptyState.vue";
import ExerciseCard from "@/components/ExerciseCard.vue";
import ScreenHeader from "@/components/ScreenHeader.vue";
import SkeletonBlock from "@/components/SkeletonBlock.vue";
import WeekStrip from "@/components/WeekStrip.vue";
import { usePlan } from "@/data/resources";
import type { Weekday } from "@/types";
import { plural } from "@/utils/format";
import { WEEKDAYS, todayWeekday } from "@/utils/week";

const route = useRoute();
const router = useRouter();
const plan = usePlan();

const day = computed(() => route.params.day as Weekday);
const dayPlan = computed(() => plan.data?.find((d) => d.day === day.value));

usePageMeta(() => ({ title: `${day.value} · Plan` }));

function select(next: Weekday) {
	router.replace({ name: "Plan", params: { day: next } });
}

function step(by: 1 | -1) {
	select(WEEKDAYS[(WEEKDAYS.indexOf(day.value) + by + 7) % 7]);
}
</script>

<template>
	<div>
		<ScreenHeader title="Your plan" subtitle="Weekly program">
			<template #actions>
				<div class="hidden gap-2 sm:flex">
					<Button
						variant="outline"
						icon="lucide-chevron-left"
						aria-label="Previous day"
						@click="step(-1)"
					/>
					<Button
						variant="outline"
						icon="lucide-chevron-right"
						aria-label="Next day"
						@click="step(1)"
					/>
				</div>
			</template>
		</ScreenHeader>

		<WeekStrip :plan="plan.data" :selected="day" @select="select" />

		<div class="mt-8 flex items-baseline justify-between gap-3">
			<h2 class="font-display text-4xl font-bold tracking-tight text-ink-gray-9">
				{{ day }}
				<span
					v-if="day === todayWeekday()"
					class="ml-1 align-middle text-sm-semibold text-ink-gray-5"
				>
					· Today
				</span>
			</h2>
		</div>

		<div v-if="!plan.data && plan.loading" class="mt-4 space-y-3">
			<SkeletonBlock v-for="i in 3" :key="i" class="h-20" />
		</div>

		<div v-else-if="dayPlan?.sessions.length" class="mt-4 space-y-8">
			<section v-for="session in dayPlan.sessions" :key="session.name">
				<div class="mb-3 flex flex-wrap items-center gap-2">
					<span class="rounded-full bg-night px-3 py-1 text-sm-semibold text-volt">
						{{ session.category }}
					</span>
					<span class="text-sm text-ink-gray-5">
						{{ plural(session.exercises.length, "exercise") }} ·
						{{ plural(session.total_sets, "set") }}
					</span>
				</div>
				<div class="space-y-3">
					<ExerciseCard
						v-for="(exercise, i) in session.exercises"
						:key="exercise.exercise"
						:exercise="exercise"
						:index="i"
					/>
				</div>
			</section>
		</div>

		<div v-else class="card mt-4">
			<EmptyState
				icon="lucide-bed-double"
				title="Rest day"
				message="Nothing scheduled. Stretch, walk, sleep well — you'll come back stronger."
			/>
		</div>
	</div>
</template>
