<script setup lang="ts">
import { Badge, Button, toast } from "frappe-ui";
import { ref } from "vue";
import { useRouter } from "vue-router";

import AdminHeader from "@/admin/components/AdminHeader.vue";
import DataTable from "@/admin/components/DataTable.vue";
import FormDialog from "@/admin/components/FormDialog.vue";
import { type Row, adminCall, usePagedList } from "@/admin/data";
import { type FieldDef, emptyValues } from "@/admin/fields";
import { formatDate } from "@/utils/format";

const router = useRouter();
const clients = usePagedList("Client", {
	fields: ["name", "full_name", "phone_number", "status", "lead_source", "date_joined"],
	orderBy: "full_name asc",
	searchFields: ["full_name", "name", "phone_number"],
});

const fields: FieldDef[] = [
	{ fieldname: "first_name", label: "First name", type: "text", required: true },
	{ fieldname: "last_name", label: "Last name", type: "text", required: true },
	{
		fieldname: "email",
		label: "Email",
		type: "email",
		required: true,
		description: "They log in with this.",
	},
	{ fieldname: "phone", label: "Phone", type: "tel", placeholder: "0712 345 678" },
	{
		fieldname: "lead_source",
		label: "How they found you",
		type: "link",
		link: { doctype: "Lead Source" },
	},
	{ fieldname: "age", label: "Age", type: "int" },
	{
		fieldname: "send_invite",
		label: "Email them an invite to set a password",
		type: "check",
		default: true,
		wide: true,
	},
];

const open = ref(false);

async function create(values: Record<string, unknown>) {
	const name = await adminCall<string>("create_client", values);
	toast.success("Client added");
	router.push({ name: "AdminClient", params: { name } });
}
</script>

<template>
	<div>
		<AdminHeader title="Clients" subtitle="Clients">
			<template #actions>
				<Button
					variant="solid"
					icon-left="lucide-user-plus"
					label="New client"
					@click="open = true"
				/>
			</template>
		</AdminHeader>

		<DataTable
			:list="clients"
			:columns="[
				{ key: 'full_name', label: 'Name', primary: true },
				{ key: 'name', label: 'Email' },
				{ key: 'phone_number', label: 'Phone' },
				{ key: 'date_joined', label: 'Joined', format: (r: Row) => formatDate(r.date_joined) },
				{ key: 'status', label: 'Status' },
			]"
			empty-icon="lucide-users"
			empty-title="No clients yet"
			@select="(row) => router.push({ name: 'AdminClient', params: { name: row.name } })"
		>
			<template #cell-status="{ row }">
				<Badge :label="row.status" :theme="row.status === 'Active' ? 'green' : 'gray'" />
			</template>
		</DataTable>

		<FormDialog
			v-model:open="open"
			title="New client"
			submit-label="Add client"
			:fields="fields"
			:values="emptyValues(fields)"
			:on-submit="create"
		/>
	</div>
</template>
