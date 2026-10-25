<script setup lang="ts">
import { Badge, toast, usePageMeta } from "frappe-ui";
import { computed, ref } from "vue";

import EmptyState from "@/components/EmptyState.vue";
import InvoiceDetails from "@/components/InvoiceDetails.vue";
import ResponsiveSheet from "@/components/ResponsiveSheet.vue";
import ScreenHeader from "@/components/ScreenHeader.vue";
import SkeletonBlock from "@/components/SkeletonBlock.vue";
import { useInvoices, useProfile, useSubscriptions } from "@/data/resources";
import type { Invoice } from "@/types";
import { daysUntil, formatDate, formatMoney, plural } from "@/utils/format";
import { invoiceTheme, subscriptionTheme } from "@/utils/status";

usePageMeta(() => ({ title: "Billing" }));

const profile = useProfile();
const subscriptions = useSubscriptions();
const invoices = useInvoices();

const settings = computed(() => profile.data?.settings);
const money = (amount: number, currency?: string | null) =>
	formatMoney(amount, currency ?? settings.value?.currency);

const outstanding = computed(() =>
	(invoices.data ?? []).reduce((sum, i) => sum + i.outstanding_amount, 0)
);
const current = computed(
	() =>
		subscriptions.data?.find((s) => s.status === "Active") ??
		subscriptions.data?.find((s) => s.status === "Upcoming")
);
const history = computed(() => subscriptions.data?.filter((s) => s !== current.value) ?? []);

const selected = ref<Invoice | null>(null);
const sheetOpen = ref(false);
function openInvoice(invoice: Invoice) {
	selected.value = invoice;
	sheetOpen.value = true;
}

async function copyPaymentNumber() {
	if (!settings.value?.payment_number) return;
	try {
		await navigator.clipboard.writeText(settings.value.payment_number);
		toast.success("Payment number copied");
	} catch {
		toast.error("Couldn't copy — please copy it manually");
	}
}
</script>

<template>
	<div class="space-y-6">
		<ScreenHeader title="Billing" subtitle="Membership & payments" />

		<section class="card-night p-6 sm:p-8">
			<p class="eyebrow text-volt">Balance due</p>
			<p class="mt-2 font-display text-8xl font-bold tabular-nums tracking-tight">
				{{ money(outstanding) }}
			</p>
			<p class="mt-1 text-base text-white/60">
				{{
					outstanding > 0
						? "Across your open invoices"
						: "You're all paid up. Thank you!"
				}}
			</p>

			<div
				v-if="settings?.payment_number && outstanding > 0"
				class="mt-6 flex items-center justify-between gap-3 rounded-[18px] bg-white/5 p-4"
			>
				<div>
					<p class="text-xs text-white/50">Pay via M-Pesa</p>
					<p class="font-display text-3xl font-semibold tracking-wide">
						{{ settings.payment_number }}
					</p>
				</div>
				<button
					type="button"
					class="inline-flex h-10 items-center gap-2 rounded-full bg-volt px-4 text-sm-semibold text-volt-ink"
					@click="copyPaymentNumber"
				>
					<span class="lucide-copy size-4" /> Copy
				</button>
			</div>
		</section>

		<section>
			<h2 class="mb-3 text-xl-semibold text-ink-gray-9">Membership</h2>
			<SkeletonBlock v-if="!subscriptions.data && subscriptions.loading" class="h-40" />
			<div v-else-if="current" class="card p-5 sm:p-6">
				<div class="flex items-start justify-between gap-3">
					<div>
						<p class="text-2xl-semibold text-ink-gray-9">{{ current.package_name }}</p>
						<p class="mt-0.5 text-sm text-ink-gray-5">
							{{ formatDate(current.from_date) }} – {{ formatDate(current.to_date) }}
						</p>
					</div>
					<Badge
						:label="current.status"
						:theme="subscriptionTheme(current.status)"
						size="lg"
					/>
				</div>

				<div class="mt-5 flex items-end justify-between gap-3">
					<p class="font-display text-5xl font-semibold tabular-nums text-ink-gray-9">
						{{ money(current.price) }}
					</p>
					<p v-if="current.status === 'Active'" class="text-sm text-ink-gray-5">
						{{ plural(Math.max(daysUntil(current.to_date), 0), "day") }} left
					</p>
				</div>

				<ul
					v-if="current.items.length"
					class="mt-5 grid gap-2 border-t border-outline-gray-1 pt-5 sm:grid-cols-2"
				>
					<li
						v-for="item in current.items"
						:key="item"
						class="flex items-center gap-2 text-base text-ink-gray-7"
					>
						<span
							class="grid size-5 place-items-center rounded-full bg-volt text-volt-ink"
						>
							<span class="lucide-check size-3" />
						</span>
						{{ item }}
					</li>
				</ul>
			</div>
			<div v-else class="card">
				<EmptyState
					icon="lucide-id-card"
					title="No active membership"
					message="Your trainer will set up your package. It will appear here with its billing."
				/>
			</div>

			<ul v-if="history.length" class="mt-3 space-y-2">
				<li
					v-for="s in history"
					:key="s.name"
					class="flex items-center justify-between gap-3 rounded-[18px] px-4 py-3 text-base"
				>
					<span class="text-ink-gray-7">
						{{ s.package_name }}
						<span class="text-ink-gray-5"
							>· {{ formatDate(s.from_date, "MMM YYYY") }}</span
						>
					</span>
					<Badge :label="s.status" :theme="subscriptionTheme(s.status)" />
				</li>
			</ul>
		</section>

		<section>
			<h2 class="mb-3 text-xl-semibold text-ink-gray-9">Invoices</h2>
			<SkeletonBlock v-if="!invoices.data && invoices.loading" class="h-48" />
			<div
				v-else-if="invoices.data?.length"
				class="card divide-y divide-outline-gray-1 overflow-hidden"
			>
				<button
					v-for="invoice in invoices.data"
					:key="invoice.name"
					type="button"
					class="flex w-full items-center gap-4 p-4 text-left transition-colors hover:bg-surface-gray-1 sm:px-5"
					@click="openInvoice(invoice)"
				>
					<span
						class="grid size-11 shrink-0 place-items-center rounded-[14px] bg-surface-gray-2 text-ink-gray-6"
					>
						<span class="lucide-receipt-text size-5" />
					</span>
					<div class="min-w-0 flex-1">
						<p class="truncate text-base-semibold text-ink-gray-9">
							{{
								invoice.packages.map((p) => p.package_name).join(", ") ||
								invoice.name
							}}
						</p>
						<p class="text-sm text-ink-gray-5">
							{{ invoice.name }} ·
							{{ formatDate(invoice.posting_date, "D MMM YYYY") }}
						</p>
					</div>
					<div class="flex shrink-0 flex-col items-end gap-1">
						<span class="tabular-nums text-base-semibold text-ink-gray-9">
							{{ money(invoice.total, invoice.currency) }}
						</span>
						<Badge :label="invoice.status" :theme="invoiceTheme(invoice.status)" />
					</div>
				</button>
			</div>
			<div v-else class="card">
				<EmptyState
					icon="lucide-receipt"
					title="No invoices yet"
					message="Invoices from your trainer will show up here."
				/>
			</div>
		</section>

		<ResponsiveSheet
			v-if="selected"
			v-model:open="sheetOpen"
			:title="`Invoice ${selected.name}`"
		>
			<InvoiceDetails :invoice="selected" :currency="settings?.currency" />
		</ResponsiveSheet>
	</div>
</template>
