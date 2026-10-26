<script setup lang="ts">
import { Badge, Button, TabButtons, call, createResource, dialog, toast } from "frappe-ui";
import { computed, reactive, ref, watch } from "vue";

import AdminHeader from "@/admin/components/AdminHeader.vue";
import DataTable from "@/admin/components/DataTable.vue";
import InvoiceDialog from "@/admin/components/InvoiceDialog.vue";
import PaymentDialog from "@/admin/components/PaymentDialog.vue";
import { type Row, adminCall, usePagedList } from "@/admin/data";
import { useMoney } from "@/admin/money";
import ResponsiveSheet from "@/components/ResponsiveSheet.vue";
import type { InvoiceStatus } from "@/types";
import { formatDate } from "@/utils/format";
import { invoiceTheme } from "@/utils/status";

const money = useMoney();
const status = ref("Open");
const filters = computed(() => {
	if (status.value === "Open") return { docstatus: 1, outstanding_amount: [">", 0] };
	if (status.value === "All") return {};
	return { status: status.value };
});

const invoices = usePagedList("Client Invoice", {
	fields: [
		"name",
		"client_name",
		"posting_date",
		"due_date",
		"total",
		"outstanding_amount",
		"status",
		"docstatus",
	],
	orderBy: "posting_date desc",
	filters: filters.value,
	searchFields: ["client_name", "name"],
});
watch(filters, (f) => invoices.setFilters(f));

const selected = ref<Row | null>(null);
const sheetOpen = ref(false);
const detail = createResource({
	url: "frappe.client.get",
	makeParams: (name: string) => ({ doctype: "Client Invoice", name }),
});
const payments = createResource({
	url: "frappe.client.get_list",
	makeParams: (invoice: string) => ({
		doctype: "Payment Entry",
		filters: { invoice, docstatus: 1 },
		fields: ["name", "amount", "mode_of_payment", "reference_no", "posting_date"],
		order_by: "posting_date desc",
	}),
});

function open(row: Row) {
	selected.value = row;
	sheetOpen.value = true;
	detail.submit(row.name);
	payments.submit(row.name);
}

async function refresh() {
	await invoices.reload();
	if (selected.value) {
		await detail.submit(selected.value.name);
		await payments.submit(selected.value.name);
		selected.value = detail.data;
	}
}

const newOpen = ref(false);
const payment = reactive({ open: false });

function cancel(row: Row) {
	dialog.danger({
		title: `Cancel ${row.name}?`,
		message: "Cancel any payments on it first. The client will no longer see it as owed.",
		confirmLabel: "Cancel invoice",
		onConfirm: async () => {
			try {
				await adminCall("cancel_document", { doctype: "Client Invoice", name: row.name });
				toast.success("Invoice cancelled");
				await refresh();
			} catch (e) {
				toast.error((e as { messages?: string[] }).messages?.[0] ?? "Couldn't cancel it.");
			}
		},
	});
}

function remove(row: Row) {
	dialog.danger({
		title: `Delete ${row.name}?`,
		onConfirm: async () => {
			try {
				await call("frappe.client.delete", { doctype: "Client Invoice", name: row.name });
				sheetOpen.value = false;
				toast.success("Invoice deleted");
				await invoices.reload();
			} catch (e) {
				toast.error((e as { messages?: string[] }).messages?.[0] ?? "Couldn't delete it.");
			}
		},
	});
}
</script>

<template>
	<div>
		<AdminHeader title="Invoices" subtitle="Billing">
			<template #actions>
				<Button
					icon-left="lucide-hand-coins"
					label="Record payment"
					@click="payment.open = true"
				/>
				<Button
					variant="solid"
					icon-left="lucide-plus"
					label="New invoice"
					@click="newOpen = true"
				/>
			</template>
		</AdminHeader>

		<TabButtons
			v-model="status"
			class="mb-4"
			:options="
				['Open', 'Overdue', 'Paid', 'Cancelled', 'All'].map((s) => ({
					label: s,
					value: s,
				}))
			"
		/>

		<DataTable
			:list="invoices"
			:columns="[
				{ key: 'client_name', label: 'Client', primary: true },
				{ key: 'name', label: 'Invoice' },
				{ key: 'posting_date', label: 'Date', format: (r: Row) => formatDate(r.posting_date) },
				{ key: 'total', label: 'Total', align: 'right', format: (r: Row) => money(r.total) },
				{ key: 'outstanding_amount', label: 'Due', align: 'right', format: (r: Row) => money(r.outstanding_amount) },
				{ key: 'status', label: 'Status' },
			]"
			empty-icon="lucide-receipt-text"
			empty-title="No invoices here"
			@select="open"
		>
			<template #cell-status="{ row }">
				<Badge :label="row.status" :theme="invoiceTheme(row.status as InvoiceStatus)" />
			</template>
		</DataTable>

		<ResponsiveSheet
			v-if="selected"
			v-model:open="sheetOpen"
			:title="`Invoice ${selected.name}`"
		>
			<div v-if="detail.data" class="space-y-5">
				<div class="flex items-start justify-between gap-3">
					<div>
						<p class="text-lg-semibold text-ink-gray-9">
							{{ detail.data.client_name }}
						</p>
						<p class="text-sm text-ink-gray-5">
							Issued {{ formatDate(detail.data.posting_date) }} · due
							{{ formatDate(detail.data.due_date) }}
						</p>
					</div>
					<Badge
						:label="detail.data.status"
						:theme="invoiceTheme(detail.data.status)"
						size="lg"
					/>
				</div>

				<div class="rounded-[18px] bg-surface-gray-1 p-4">
					<div
						v-for="p in detail.data.packages"
						:key="p.name"
						class="flex justify-between py-1 text-base"
					>
						<span class="text-ink-gray-7">{{ p.package_name }}</span>
						<span class="tabular-nums">{{ money(p.unit_price) }}</span>
					</div>
					<div
						class="mt-2 flex justify-between border-t border-outline-gray-2 pt-3 text-base-semibold"
					>
						<span>Outstanding</span>
						<span class="tabular-nums"
							>{{ money(detail.data.outstanding_amount) }} of
							{{ money(detail.data.total) }}</span
						>
					</div>
				</div>

				<div>
					<p class="eyebrow mb-2 text-ink-gray-5">Payments</p>
					<p v-if="!payments.data?.length" class="text-base text-ink-gray-5">
						None yet.
					</p>
					<ul v-else class="divide-y divide-outline-gray-1">
						<li
							v-for="p in payments.data"
							:key="p.name"
							class="flex justify-between py-2 text-base"
						>
							<span
								>{{ p.mode_of_payment }}
								<span class="text-ink-gray-5"
									>· {{ formatDate(p.posting_date) }}
									{{ p.reference_no ? `· ${p.reference_no}` : "" }}</span
								></span
							>
							<span class="tabular-nums">{{ money(p.amount) }}</span>
						</li>
					</ul>
				</div>

				<div class="flex flex-wrap justify-end gap-2">
					<Button
						v-if="detail.data.docstatus === 1"
						theme="red"
						label="Cancel invoice"
						@click="cancel(detail.data)"
					/>
					<Button
						v-if="detail.data.docstatus === 2"
						theme="red"
						label="Delete"
						@click="remove(detail.data)"
					/>
					<Button
						v-if="detail.data.docstatus === 1 && detail.data.outstanding_amount > 0"
						variant="solid"
						label="Record payment"
						@click="payment.open = true"
					/>
				</div>
			</div>
		</ResponsiveSheet>

		<InvoiceDialog v-model:open="newOpen" @saved="invoices.reload()" />
		<PaymentDialog
			v-model:open="payment.open"
			:invoice="sheetOpen ? selected?.name : null"
			:outstanding="sheetOpen ? detail.data?.outstanding_amount : undefined"
			@saved="refresh"
		/>
	</div>
</template>
