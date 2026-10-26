<script setup lang="ts">
import { Button, DatePicker, ErrorMessage, Select, call, dayjs } from "frappe-ui";
import { computed, reactive, ref, watch } from "vue";

import AdminHeader from "@/admin/components/AdminHeader.vue";
import LinkSelect from "@/admin/components/LinkSelect.vue";
import type { Row } from "@/admin/data";
import { useMoney } from "@/admin/money";
import SkeletonBlock from "@/components/SkeletonBlock.vue";

interface ReportResult {
	result: Row[];
	report_summary: { label: string; value: number; datatype: string; indicator: string }[];
}

const money = useMoney();
const filters = reactive({
	periodicity: "Monthly",
	from_date: dayjs().startOf("year").format("YYYY-MM-DD"),
	to_date: dayjs().format("YYYY-MM-DD"),
	client: null as string | null,
	status: "",
});

const report = ref<ReportResult | null>(null);
const loading = ref(false);
const error = ref<unknown>(null);

async function run() {
	loading.value = true;
	error.value = null;
	try {
		report.value = await call<ReportResult>("frappe.desk.query_report.run", {
			report_name: "Profit Analysis",
			filters: {
				...filters,
				client: filters.client || undefined,
				status: filters.status || undefined,
			},
			ignore_prepared_report: true,
		});
	} catch (e) {
		error.value = e;
	} finally {
		loading.value = false;
	}
}
watch(filters, run, { deep: true, immediate: true });

const rows = computed(() => (report.value?.result ?? []).filter((r) => r.period));
const peak = computed(() => Math.max(...rows.value.map((r) => r.invoiced), 1));

function formatSummary(item: ReportResult["report_summary"][number]) {
	return item.datatype === "Percent" ? `${item.value}%` : money(item.value);
}
</script>

<template>
	<div class="space-y-4">
		<AdminHeader title="Profit Analysis" subtitle="Billing">
			<template #actions>
				<Button aria-label="Refresh" tooltip="Refresh" :disabled="loading" @click="run">
					<span
						class="lucide-refresh-cw size-4"
						:class="loading ? 'animate-spin' : ''"
					/>
				</Button>
			</template>
		</AdminHeader>

		<section class="card grid gap-3 p-4 sm:grid-cols-2 lg:grid-cols-5">
			<Select
				v-model="filters.periodicity"
				label="Group by"
				size="md"
				:options="
					['Monthly', 'Weekly', 'Yearly', 'Date Range'].map((p) => ({
						label: p,
						value: p,
					}))
				"
			/>
			<DatePicker v-model="filters.from_date" label="From" size="md" />
			<DatePicker v-model="filters.to_date" label="To" size="md" />
			<LinkSelect
				v-model="filters.client"
				label="Client"
				placeholder="All clients"
				:link="{ doctype: 'Client', labelField: 'full_name' }"
			/>
			<Select
				v-model="filters.status"
				label="Invoice status"
				size="md"
				placeholder="Any status"
				:options="
					['', 'Unpaid', 'Partially Paid', 'Paid', 'Overdue'].map((s) => ({
						label: s || 'Any status',
						value: s,
					}))
				"
			/>
		</section>

		<ErrorMessage v-if="error" :message="error as Error" />

		<SkeletonBlock v-if="loading && !report" class="h-64" />
		<template v-else-if="report">
			<section class="grid grid-cols-2 gap-3 lg:grid-cols-4">
				<div
					v-for="(item, i) in report.report_summary"
					:key="item.label"
					:class="i === 0 ? 'card-night' : 'card'"
					class="p-5"
				>
					<p class="text-xs" :class="i === 0 ? 'text-white/60' : 'text-ink-gray-5'">
						{{ item.label }}
					</p>
					<p
						class="mt-2 font-display text-3xl font-semibold tabular-nums"
						:class="
							i === 0
								? ''
								: item.indicator === 'Red'
								? 'text-ink-red-6'
								: 'text-ink-gray-9'
						"
					>
						{{ formatSummary(item) }}
					</p>
				</div>
			</section>

			<section class="card p-5">
				<div class="mb-4 flex flex-wrap items-center justify-between gap-2">
					<h2 class="text-lg-semibold text-ink-gray-9">Collected vs outstanding</h2>
					<div class="flex items-center gap-4 text-xs text-ink-gray-6">
						<span class="flex items-center gap-1.5"
							><span class="size-2.5 rounded-sm bg-volt" /> Collected</span
						>
						<span class="flex items-center gap-1.5"
							><span class="size-2.5 rounded-sm bg-surface-red-5" />
							Outstanding</span
						>
					</div>
				</div>
				<p v-if="!rows.length" class="py-10 text-center text-base text-ink-gray-5">
					No invoices in this period.
				</p>
				<div v-else class="flex h-56 items-end gap-2 overflow-x-auto pb-1">
					<div
						v-for="r in rows"
						:key="r.period"
						class="flex h-full min-w-12 flex-1 flex-col items-center justify-end gap-1.5"
						:title="`${r.period}: ${money(r.collected)} collected, ${money(
							r.outstanding
						)} outstanding`"
					>
						<div
							class="flex w-full max-w-14 flex-col-reverse overflow-hidden rounded-[8px]"
							:style="{ height: `${(r.invoiced / peak) * 100}%` }"
						>
							<div
								class="bg-volt"
								:style="{
									height: `${
										r.invoiced ? (r.collected / r.invoiced) * 100 : 0
									}%`,
								}"
							/>
							<div
								class="bg-surface-red-5"
								:style="{
									height: `${
										r.invoiced ? (r.outstanding / r.invoiced) * 100 : 0
									}%`,
								}"
							/>
						</div>
						<span class="w-full truncate text-center text-2xs text-ink-gray-5">{{
							r.period
						}}</span>
					</div>
				</div>
			</section>

			<section class="card overflow-x-auto">
				<table class="w-full text-base">
					<thead>
						<tr
							class="border-b border-outline-gray-1 text-left text-sm text-ink-gray-5"
						>
							<th class="px-4 py-2.5 font-medium">Period</th>
							<th class="px-4 py-2.5 text-right font-medium">Invoices</th>
							<th class="px-4 py-2.5 text-right font-medium">Invoiced</th>
							<th class="px-4 py-2.5 text-right font-medium">Collected</th>
							<th class="px-4 py-2.5 text-right font-medium">Outstanding</th>
							<th class="px-4 py-2.5 text-right font-medium">Collected %</th>
						</tr>
					</thead>
					<tbody class="divide-y divide-outline-gray-1 tabular-nums">
						<tr v-for="r in rows" :key="r.period">
							<td class="px-4 py-3 font-medium text-ink-gray-9">{{ r.period }}</td>
							<td class="px-4 py-3 text-right">{{ r.invoice_count }}</td>
							<td class="px-4 py-3 text-right">{{ money(r.invoiced) }}</td>
							<td class="px-4 py-3 text-right text-ink-green-7">
								{{ money(r.collected) }}
							</td>
							<td
								class="px-4 py-3 text-right"
								:class="r.outstanding > 0 ? 'text-ink-red-6' : ''"
							>
								{{ money(r.outstanding) }}
							</td>
							<td class="px-4 py-3 text-right">{{ r.collection_rate }}%</td>
						</tr>
					</tbody>
				</table>
			</section>
		</template>
	</div>
</template>
