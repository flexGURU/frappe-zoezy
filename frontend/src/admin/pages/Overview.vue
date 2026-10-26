<script setup lang="ts">
import { createResource } from "frappe-ui";

import AdminHeader from "@/admin/components/AdminHeader.vue";
import { useMoney } from "@/admin/money";
import SkeletonBlock from "@/components/SkeletonBlock.vue";
import { useProfile } from "@/data/resources";
import { formatDate } from "@/utils/format";

const money = useMoney();
const profile = useProfile();
const overview = createResource({ url: "zoezy.api.admin.get_overview", auto: true });

const actions = [
	{ label: "New client", icon: "lucide-user-plus", to: { name: "AdminClients" } },
	{ label: "New workout plan", icon: "lucide-dumbbell", to: { name: "AdminPlanNew" } },
	{ label: "New invoice", icon: "lucide-receipt-text", to: { name: "AdminInvoices" } },
	{ label: "Record payment", icon: "lucide-hand-coins", to: { name: "AdminPayments" } },
];
</script>

<template>
	<div class="space-y-6">
		<AdminHeader :title="`Hi, ${profile.data?.first_name ?? 'coach'}`" subtitle="Overview" />

		<SkeletonBlock v-if="!overview.data" class="h-32" />
		<section v-else class="grid grid-cols-2 gap-3 lg:grid-cols-4">
			<RouterLink :to="{ name: 'AdminClients' }" class="card-night p-5">
				<p class="text-xs text-white/60">Active clients</p>
				<p class="mt-2 font-display text-5xl font-semibold">
					{{ overview.data.active_clients }}
				</p>
				<p class="text-xs text-white/50">of {{ overview.data.total_clients }}</p>
			</RouterLink>
			<RouterLink :to="{ name: 'AdminSubscriptions' }" class="card p-5">
				<p class="text-xs text-ink-gray-5">Active subscriptions</p>
				<p class="mt-2 font-display text-5xl font-semibold text-ink-gray-9">
					{{ overview.data.active_subscriptions }}
				</p>
			</RouterLink>
			<RouterLink :to="{ name: 'AdminInvoices' }" class="card p-5">
				<p class="text-xs text-ink-gray-5">Outstanding</p>
				<p class="mt-2 font-display text-3xl font-semibold text-ink-gray-9">
					{{ money(overview.data.outstanding) }}
				</p>
				<p class="text-xs text-ink-red-6">
					{{ overview.data.overdue_invoices.length }} overdue
				</p>
			</RouterLink>
			<RouterLink :to="{ name: 'AdminPlans' }" class="card p-5">
				<p class="text-xs text-ink-gray-5">Workout plans</p>
				<p class="mt-2 font-display text-5xl font-semibold text-ink-gray-9">
					{{ overview.data.workout_plans }}
				</p>
			</RouterLink>
		</section>

		<section class="grid grid-cols-2 gap-3 sm:grid-cols-4">
			<RouterLink
				v-for="a in actions"
				:key="a.label"
				:to="a.to"
				class="card flex items-center gap-3 p-4 text-base-medium text-ink-gray-8 transition-colors hover:border-outline-gray-3"
			>
				<span class="grid size-9 place-items-center rounded-[12px] bg-volt text-volt-ink"
					><span :class="a.icon" class="size-4"
				/></span>
				{{ a.label }}
			</RouterLink>
		</section>

		<div v-if="overview.data" class="grid gap-4 lg:grid-cols-3">
			<section class="card p-5">
				<h2 class="mb-3 text-lg-semibold text-ink-gray-9">Overdue invoices</h2>
				<p v-if="!overview.data.overdue_invoices.length" class="text-base text-ink-gray-5">
					Nothing overdue.
				</p>
				<ul class="divide-y divide-outline-gray-1">
					<li
						v-for="inv in overview.data.overdue_invoices"
						:key="inv.name"
						class="flex justify-between gap-2 py-2 text-base"
					>
						<span class="truncate"
							>{{ inv.client_name }}
							<span class="text-ink-gray-5"
								>· {{ formatDate(inv.due_date, "D MMM") }}</span
							></span
						>
						<span class="tabular-nums text-ink-red-6">{{
							money(inv.outstanding_amount)
						}}</span>
					</li>
				</ul>
			</section>
			<section class="card p-5">
				<h2 class="mb-3 text-lg-semibold text-ink-gray-9">Ending this week</h2>
				<p
					v-if="!overview.data.expiring_subscriptions.length"
					class="text-base text-ink-gray-5"
				>
					No memberships ending soon.
				</p>
				<ul class="divide-y divide-outline-gray-1">
					<li
						v-for="s in overview.data.expiring_subscriptions"
						:key="s.name"
						class="py-2 text-base"
					>
						<RouterLink
							:to="{ name: 'AdminClient', params: { name: s.client } }"
							class="flex justify-between gap-2"
						>
							<span class="truncate">{{ s.client }}</span>
							<span class="text-ink-gray-5">{{
								formatDate(s.to_date, "D MMM")
							}}</span>
						</RouterLink>
					</li>
				</ul>
			</section>
			<section class="card p-5">
				<h2 class="mb-3 text-lg-semibold text-ink-gray-9">Recent payments</h2>
				<p v-if="!overview.data.recent_payments.length" class="text-base text-ink-gray-5">
					No payments yet.
				</p>
				<ul class="divide-y divide-outline-gray-1">
					<li
						v-for="p in overview.data.recent_payments"
						:key="p.name"
						class="flex justify-between gap-2 py-2 text-base"
					>
						<span class="truncate"
							>{{ p.client_name }}
							<span class="text-ink-gray-5">· {{ p.mode_of_payment }}</span></span
						>
						<span class="tabular-nums text-ink-green-7">{{ money(p.amount) }}</span>
					</li>
				</ul>
			</section>
		</div>
	</div>
</template>
