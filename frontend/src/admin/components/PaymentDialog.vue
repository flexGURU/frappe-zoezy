<script setup lang="ts">
import { toast } from "frappe-ui";
import { computed } from "vue";

import { adminCall } from "@/admin/data";
import type { FieldDef } from "@/admin/fields";
import FormDialog from "./FormDialog.vue";

const props = defineProps<{ invoice?: string | null; outstanding?: number }>();
const emit = defineEmits<{ saved: [] }>();
const open = defineModel<boolean>("open", { required: true });

const fields = computed<FieldDef[]>(() => [
	...(props.invoice
		? []
		: [
				{
					fieldname: "invoice",
					label: "Invoice",
					type: "link",
					required: true,
					link: {
						doctype: "Client Invoice",
						labelField: "client_name",
						filters: { docstatus: 1, outstanding_amount: [">", 0] },
					},
				} as FieldDef,
		  ]),
	{ fieldname: "amount", label: "Amount", type: "currency", required: true },
	{
		fieldname: "mode_of_payment",
		label: "Paid by",
		type: "select",
		required: true,
		options: ["M-Pesa", "Cash", "Bank Transfer", "Card"],
	},
	{
		fieldname: "reference_no",
		label: "Reference",
		type: "text",
		placeholder: "e.g. M-Pesa code",
	},
	{ fieldname: "posting_date", label: "Date", type: "date" },
]);

const values = computed(() => ({
	invoice: props.invoice ?? "",
	amount: props.outstanding ?? "",
	mode_of_payment: "M-Pesa",
	reference_no: "",
	posting_date: "",
}));

async function save(form: Record<string, unknown>) {
	await adminCall("record_payment", {
		...form,
		invoice: props.invoice ?? form.invoice,
		posting_date: form.posting_date || null,
	});
	toast.success("Payment recorded");
	emit("saved");
}
</script>

<template>
	<FormDialog
		v-model:open="open"
		title="Record payment"
		submit-label="Record payment"
		:fields="fields"
		:values="values"
		:on-submit="save"
	/>
</template>
