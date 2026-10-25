<script setup lang="ts">
import { Avatar, dayjs, usePageMeta } from "frappe-ui";
import { computed } from "vue";
import { useRouter } from "vue-router";

import SkeletonBlock from "@/components/SkeletonBlock.vue";
import WeekStrip from "@/components/WeekStrip.vue";
import { useInvoices, usePlan, useProfile, useSubscriptions } from "@/data/resources";
import type { Weekday } from "@/types";
import { daysUntil, formatDate, formatMoney, plural } from "@/utils/format";
import { WEEKDAYS, daySummary, todayWeekday } from "@/utils/week";

usePageMeta(() => ({ title: "Today" }));

const router = useRouter();
const profile = useProfile();
const plan = usePlan();
const subscriptions = useSubscriptions();
const invoices = useInvoices();

const today = todayWeekday();
const currency = computed(() => profile.data?.settings.currency);

const greeting = computed(() => {
	const hour = dayjs().hour();
	if (hour < 12) return "Good morning";
	if (hour < 17) return "Good afternoon";
	return "Good evening";
});

const todayPlan = computed(() => plan.data?.find((d) => d.day === today));
const summary = computed(() => daySummary(todayPlan.value));
const previewExercises = computed(() =>
	(todayPlan.value?.sessions ?? []).flatMap((s) => s.exercises).slice(0, 4)
);

const nextTrainingDay = computed(() => {
	const start = WEEKDAYS.indexOf(today);
	for (let offset = 1; offset <= 7; offset++) {
		const day = plan.data?.find((d) => d.day === WEEKDAYS[(start + offset) % 7]);
		if (day?.sessions.length)
			return { day: day.day, label: daySummary(day).categories.join(" + ") };
	}
	return null;
});

const week = computed(() => {
	const days = plan.data ?? [];
	return {
		trainingDays: days.filter((d) => d.sessions.length).length,
		sets: days.reduce((n, d) => n + daySummary(d).sets, 0),
	};
});

const subscription = computed(
	() =>
		subscriptions.data?.find((s) => s.status === "Active") ??
		subscriptions.data?.find((s) => s.status === "Upcoming")
);
const subscriptionProgress = computed(() => {
	const s = subscription.value;
	if (!s) return 0;
	const total = dayjs(s.to_date).diff(dayjs(s.from_date), "day") || 1;
	const elapsed = dayjs().diff(dayjs(s.from_date), "day");
	return Math.min(Math.max((elapsed / total) * 100, 0), 100);
});

const balance = computed(() => {
	const open = (invoices.data ?? []).filter((i) => i.outstanding_amount > 0);
	const nextDue = open
		.map((i) => i.due_date)
		.filter(Boolean)
		.sort()[0];
	return {
		amount: open.reduce((sum, i) => sum + i.outstanding_amount, 0),
		overdue: open.some((i) => i.status === "Overdue"),
		nextDue,
	};
});

function openDay(day: Weekday) {
	router.push({ name: "Plan", params: { day } });
}
</script>

<template>
	<div class="space-y-6">
		<header class="flex items-center justify-between gap-4">
			<div class="min-w-0">
				<p class="text-base text-ink-gray-5">{{ greeting }},</p>
				<h1
					class="truncate font-display text-5xl font-bold tracking-tight text-ink-gray-9 md:text-7xl"
				>
					{{ profile.data?.first_name ?? "…" }}
				</h1>
			</div>
			<RouterLink :to="{ name: 'Profile' }" class="shrink-0 md:hidden" aria-label="Profile">
				<Avatar
					:label="profile.data?.full_name"
					:image="profile.data?.image ?? undefined"
					size="2xl"
				/>
			</RouterLink>
		</header>

		<SkeletonBlock v-if="!plan.data && plan.loading" class="h-72" />
		<section v-else class="card-night overflow-hidden p-6 sm:p-8">
			<div class="flex items-center justify-between gap-3">
				<p class="eyebrow text-volt">Today · {{ today }}</p>
				<span
					v-if="summary.sessions"
					class="rounded-full bg-white/10 px-3 py-1 text-xs-medium text-white/80"
				>
					{{ plural(summary.sessions, "session") }}
				</span>
			</div>

			<template v-if="summary.sessions">
				<h2
					class="mt-3 font-display text-[40px] font-bold leading-[1.05] tracking-tight sm:text-[56px]"
				>
					{{ summary.categories.join(" + ") }}
				</h2>

				<dl class="mt-6 flex gap-8">
					<div>
						<dt class="text-xs text-white/50">Exercises</dt>
						<dd class="font-display text-5xl font-semibold tabular-nums">
							{{ summary.exercises }}
						</dd>
					</div>
					<div>
						<dt class="text-xs text-white/50">Total sets</dt>
						<dd class="font-display text-5xl font-semibold tabular-nums">
							{{ summary.sets }}
						</dd>
					</div>
				</dl>

				<ul class="mt-6 divide-y divide-white/10 border-y border-white/10">
					<li
						v-for="e in previewExercises"
						:key="e.exercise"
						class="flex items-center justify-between gap-3 py-3 text-base"
					>
						<span class="truncate text-white/90">{{ e.exercise }}</span>
						<span class="shrink-0 tabular-nums text-white/50"
							>{{ e.sets }} × {{ e.reps }}</span
						>
					</li>
				</ul>

				<button
					type="button"
					class="mt-6 inline-flex h-12 w-full items-center justify-center gap-2 rounded-full bg-volt px-6 text-base-semibold text-volt-ink transition-transform hover:scale-[1.01] active:scale-[0.99] sm:w-auto"
					@click="openDay(today)"
				>
					Open today's session
					<span class="lucide-arrow-right size-4" />
				</button>
			</template>

			<template v-else>
				<div class="mt-4 flex items-start gap-4">
					<span
						class="grid size-14 shrink-0 place-items-center rounded-[18px] bg-white/10 text-volt"
					>
						<span class="lucide-bed-double size-7" />
					</span>
					<div>
						<h2 class="font-display text-5xl font-bold tracking-tight">Rest day</h2>
						<p class="mt-1 text-base text-white/60">
							Recovery is where the gains are made.
						</p>
					</div>
				</div>
				<button
					v-if="nextTrainingDay"
					type="button"
					class="mt-6 flex w-full items-center justify-between rounded-[18px] bg-white/5 p-4 text-left transition-colors hover:bg-white/10"
					@click="openDay(nextTrainingDay.day)"
				>
					<span>
						<span class="block text-xs text-white/50"
							>Next up · {{ nextTrainingDay.day }}</span
						>
						<span class="text-lg-semibold">{{ nextTrainingDay.label }}</span>
					</span>
					<span class="lucide-arrow-right size-5 text-volt" />
				</button>
				<p v-else-if="plan.data" class="mt-6 text-base text-white/60">
					Your trainer hasn't published a plan yet. It will show up here as soon as they
					do.
				</p>
			</template>
		</section>

		<section>
			<div class="mb-3 flex items-baseline justify-between">
				<h2 class="text-xl-semibold text-ink-gray-9">This week</h2>
				<RouterLink
					:to="{ name: 'Plan' }"
					class="text-sm-medium text-ink-gray-5 hover:text-ink-gray-9"
				>
					Full plan
				</RouterLink>
			</div>
			<WeekStrip :plan="plan.data" :selected="today" @select="openDay" />

			<div class="mt-3 grid grid-cols-2 gap-3">
				<div class="card p-4 sm:p-5">
					<span class="lucide-calendar-check size-5 text-ink-gray-5" />
					<p
						class="mt-3 font-display text-5xl font-semibold tabular-nums text-ink-gray-9"
					>
						{{ week.trainingDays }}<span class="text-2xl text-ink-gray-4">/7</span>
					</p>
					<p class="text-sm text-ink-gray-5">Training days</p>
				</div>
				<div class="card p-4 sm:p-5">
					<span class="lucide-flame size-5 text-ink-gray-5" />
					<p
						class="mt-3 font-display text-5xl font-semibold tabular-nums text-ink-gray-9"
					>
						{{ week.sets }}
					</p>
					<p class="text-sm text-ink-gray-5">Sets this week</p>
				</div>
			</div>
		</section>

		<section class="grid gap-3 md:grid-cols-2">
			<RouterLink
				:to="{ name: 'Billing' }"
				class="card block p-5 transition-colors hover:border-outline-gray-3"
			>
				<div class="flex items-center justify-between">
					<p class="eyebrow text-ink-gray-5">Membership</p>
					<span class="lucide-chevron-right size-4 text-ink-gray-4" />
				</div>
				<template v-if="subscription">
					<p class="mt-2 text-2xl-semibold text-ink-gray-9">
						{{ subscription.package_name }}
					</p>
					<div class="mt-4 h-2 overflow-hidden rounded-full bg-surface-gray-2">
						<div
							class="h-full rounded-full bg-surface-gray-10"
							:style="{ width: `${subscriptionProgress}%` }"
						/>
					</div>
					<p class="mt-2 text-sm text-ink-gray-5">
						<template v-if="subscription.status === 'Upcoming'">
							Starts {{ formatDate(subscription.from_date, "D MMM") }}
						</template>
						<template v-else>
							{{ plural(Math.max(daysUntil(subscription.to_date), 0), "day") }} left
							· renews
							{{ formatDate(subscription.to_date, "D MMM") }}
						</template>
					</p>
				</template>
				<p v-else class="mt-2 text-base text-ink-gray-6">
					No active membership. Talk to your trainer to get started.
				</p>
			</RouterLink>

			<RouterLink
				:to="{ name: 'Billing' }"
				class="card block p-5 transition-colors hover:border-outline-gray-3"
			>
				<div class="flex items-center justify-between">
					<p class="eyebrow text-ink-gray-5">Balance due</p>
					<span class="lucide-chevron-right size-4 text-ink-gray-4" />
				</div>
				<p
					class="mt-2 font-display text-5xl font-semibold tabular-nums"
					:class="balance.overdue ? 'text-ink-red-6' : 'text-ink-gray-9'"
				>
					{{ formatMoney(balance.amount, currency) }}
				</p>
				<p class="mt-1 text-sm text-ink-gray-5">
					<template v-if="balance.overdue">Overdue — please settle soon</template>
					<template v-else-if="balance.nextDue"
						>Due {{ formatDate(balance.nextDue, "D MMM") }}</template
					>
					<template v-else>You're all paid up</template>
				</p>
			</RouterLink>
		</section>
	</div>
</template>
