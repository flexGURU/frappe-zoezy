<script setup lang="ts">
import { Badge } from "frappe-ui";

import type { Invoice } from "@/types";
import { formatDate, formatMoney } from "@/utils/format";
import { invoiceTheme } from "@/utils/status";

const props = defineProps<{ invoice: Invoice; currency?: string }>();
const money = (amount: number) => formatMoney(amount, props.invoice.currency ?? props.currency);
</script>

<template>
	<div class="space-y-5">
		<div class="flex items-start justify-between gap-3">
			<div>
				<p class="text-sm text-ink-gray-5">
					Issued {{ formatDate(invoice.posting_date) }}
				</p>
				<p v-if="invoice.due_date" class="text-sm text-ink-gray-5">
					Due {{ formatDate(invoice.due_date) }}
				</p>
			</div>
			<Badge :label="invoice.status" :theme="invoiceTheme(invoice.status)" size="lg" />
		</div>

		<div class="rounded-[18px] bg-surface-gray-1 p-4">
			<div
				v-for="item in invoice.packages"
				:key="item.package_name"
				class="flex justify-between gap-3 py-1 text-base"
			>
				<span class="text-ink-gray-7">{{ item.package_name }}</span>
				<span class="tabular-nums text-ink-gray-9">{{ money(item.unit_price) }}</span>
			</div>
			<div
				class="mt-2 flex justify-between border-t border-outline-gray-2 pt-3 text-base-semibold"
			>
				<span>Total</span>
				<span class="tabular-nums">{{ money(invoice.total) }}</span>
			</div>
			<div class="mt-1 flex justify-between text-base-semibold">
				<span>Outstanding</span>
				<span
					class="tabular-nums"
					:class="invoice.outstanding_amount > 0 ? 'text-ink-red-6' : 'text-ink-green-6'"
				>
					{{ money(invoice.outstanding_amount) }}
				</span>
			</div>
		</div>

		<div>
			<p class="eyebrow mb-2 text-ink-gray-5">Payments</p>
			<p v-if="!invoice.payments.length" class="text-base text-ink-gray-5">
				No payments recorded yet.
			</p>
			<ul v-else class="divide-y divide-outline-gray-1">
				<li
					v-for="p in invoice.payments"
					:key="p.name"
					class="flex items-center justify-between gap-3 py-2.5"
				>
					<div class="flex items-center gap-3">
						<span
							class="grid size-9 place-items-center rounded-full bg-surface-green-2 text-ink-green-7"
						>
							<span class="lucide-check size-4" />
						</span>
						<div>
							<p class="text-base-medium text-ink-gray-9">
								{{ p.mode_of_payment ?? "Payment" }}
							</p>
							<p class="text-xs text-ink-gray-5">{{ formatDate(p.posting_date) }}</p>
						</div>
					</div>
					<span class="tabular-nums text-base-semibold text-ink-gray-9">{{
						money(p.amount)
					}}</span>
				</li>
			</ul>
		</div>
	</div>
</template>
