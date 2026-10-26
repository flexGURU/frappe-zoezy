<script setup lang="ts">
import { Badge, Button, call, dialog, toast } from "frappe-ui";
import { ref } from "vue";

import AdminHeader from "@/admin/components/AdminHeader.vue";
import DataTable from "@/admin/components/DataTable.vue";
import PaymentDialog from "@/admin/components/PaymentDialog.vue";
import { type Row, adminCall, usePagedList } from "@/admin/data";
import { useMoney } from "@/admin/money";
import { formatDate } from "@/utils/format";

const money = useMoney();
const payments = usePagedList("Payment Entry", {
	fields: [
		"name",
		"client_name",
		"invoice",
		"amount",
		"mode_of_payment",
		"reference_no",
		"posting_date",
		"docstatus",
	],
	orderBy: "posting_date desc",
	searchFields: ["client_name", "invoice", "reference_no"],
});
const open = ref(false);

function cancel(row: Row) {
	dialog.danger({
		title: `Cancel payment ${row.name}?`,
		message: `${money(row.amount)} will be added back to ${row.invoice}.`,
		confirmLabel: "Cancel payment",
		onConfirm: async () => {
			try {
				await adminCall("cancel_document", { doctype: "Payment Entry", name: row.name });
				toast.success("Payment cancelled");
				await payments.reload();
			} catch (e) {
				toast.error((e as { messages?: string[] }).messages?.[0] ?? "Couldn't cancel it.");
			}
		},
	});
}

function remove(row: Row) {
	dialog.danger({
		title: `Delete payment ${row.name}?`,
		onConfirm: async () => {
			try {
				await call("frappe.client.delete", { doctype: "Payment Entry", name: row.name });
				toast.success("Payment deleted");
				await payments.reload();
			} catch (e) {
				toast.error((e as { messages?: string[] }).messages?.[0] ?? "Couldn't delete it.");
			}
		},
	});
}
</script>

<template>
	<div>
		<AdminHeader title="Payments" subtitle="Billing">
			<template #actions>
				<Button
					variant="solid"
					icon-left="lucide-plus"
					label="Record payment"
					@click="open = true"
				/>
			</template>
		</AdminHeader>

		<DataTable
			:list="payments"
			:columns="[
				{ key: 'client_name', label: 'Client', primary: true },
				{ key: 'invoice', label: 'Invoice' },
				{ key: 'posting_date', label: 'Date', format: (r: Row) => formatDate(r.posting_date) },
				{ key: 'mode_of_payment', label: 'Method', format: (r: Row) => [r.mode_of_payment, r.reference_no].filter(Boolean).join(' · ') },
				{ key: 'amount', label: 'Amount', align: 'right', format: (r: Row) => money(r.amount) },
				{ key: 'docstatus', label: 'Status' },
			]"
			empty-icon="lucide-hand-coins"
			empty-title="No payments yet"
		>
			<template #cell-docstatus="{ row }">
				<Badge
					:label="['Draft', 'Received', 'Cancelled'][row.docstatus]"
					:theme="(['gray', 'green', 'red'] as const)[row.docstatus]"
				/>
			</template>
			<template #actions="{ row }">
				<Button
					v-if="row.docstatus === 1"
					size="sm"
					variant="ghost"
					label="Cancel"
					@click="cancel(row)"
				/>
				<Button
					v-else
					icon="lucide-trash-2"
					variant="ghost"
					:aria-label="`Delete ${row.name}`"
					@click="remove(row)"
				/>
			</template>
		</DataTable>

		<PaymentDialog v-model:open="open" @saved="payments.reload()" />
	</div>
</template>
