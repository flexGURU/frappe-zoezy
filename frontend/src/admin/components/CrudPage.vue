<script setup lang="ts">
import { Button, call, dialog, toast } from "frappe-ui";
import { ref } from "vue";

import { type Row, usePagedList } from "@/admin/data";
import { type FieldDef, emptyValues } from "@/admin/fields";
import AdminHeader from "./AdminHeader.vue";
import DataTable, { type Column } from "./DataTable.vue";
import FormDialog from "./FormDialog.vue";

const props = defineProps<{
	doctype: string;
	title: string;
	subtitle?: string;
	singular: string;
	fields: FieldDef[];
	columns: Column<Row>[];
	listFields: string[];
	orderBy?: string;
	filters?: Record<string, unknown>;
	searchKeys?: string[];
	emptyIcon?: string;
	toForm?: (doc: Row) => Record<string, unknown>;
	toDoc?: (values: Record<string, unknown>) => Record<string, unknown>;
	canDelete?: (row: Row) => boolean;
}>();

const list = usePagedList(props.doctype, {
	fields: props.listFields,
	orderBy: props.orderBy,
	filters: props.filters,
	searchFields: props.searchKeys,
});

const formOpen = ref(false);
const editing = ref<Row | null>(null);
const formValues = ref<Record<string, unknown>>({});

function openNew() {
	editing.value = null;
	formValues.value = emptyValues(props.fields);
	formOpen.value = true;
}

async function openEdit(row: Row) {
	const doc = await call<Row>("frappe.client.get", { doctype: props.doctype, name: row.name });
	editing.value = doc;
	formValues.value = props.toForm
		? props.toForm(doc)
		: Object.fromEntries(props.fields.map((f) => [f.fieldname, doc[f.fieldname] ?? ""]));
	formOpen.value = true;
}

async function save(values: Record<string, unknown>) {
	const doc = props.toDoc ? props.toDoc(values) : values;
	if (editing.value) {
		await call("frappe.client.set_value", {
			doctype: props.doctype,
			name: editing.value.name,
			fieldname: doc,
		});
		toast.success(`${props.singular} updated`);
	} else {
		await call("frappe.client.insert", { doc: { doctype: props.doctype, ...doc } });
		toast.success(`${props.singular} created`);
	}
	await list.reload();
}

function remove(row: Row) {
	dialog.danger({
		title: `Delete ${props.singular.toLowerCase()}?`,
		message: `${row.name} will be permanently deleted.`,
		onConfirm: async () => {
			try {
				await call("frappe.client.delete", { doctype: props.doctype, name: row.name });
				toast.success(`${props.singular} deleted`);
				await list.reload();
			} catch (e) {
				toast.error((e as { messages?: string[] }).messages?.[0] ?? "Couldn't delete it.");
			}
		},
	});
}

defineExpose({ reload: () => list.reload() });
</script>

<template>
	<div>
		<AdminHeader :title="title" :subtitle="subtitle">
			<template #actions>
				<Button
					variant="solid"
					icon-left="lucide-plus"
					:label="`New ${singular.toLowerCase()}`"
					@click="openNew"
				/>
			</template>
		</AdminHeader>

		<DataTable
			:list="list"
			:columns="columns"
			:empty-icon="emptyIcon"
			:empty-title="`No ${title.toLowerCase()} yet`"
			@select="openEdit"
		>
			<template v-for="col in columns" #[`cell-${col.key}`]="{ row }">
				<slot :name="`cell-${col.key}`" :row="row">{{
					col.format ? col.format(row) : row[col.key] ?? "–"
				}}</slot>
			</template>
			<template #actions="{ row }">
				<Button
					v-if="!canDelete || canDelete(row)"
					icon="lucide-trash-2"
					variant="ghost"
					:aria-label="`Delete ${row.name}`"
					@click="remove(row)"
				/>
			</template>
		</DataTable>

		<FormDialog
			v-model:open="formOpen"
			:title="editing ? `Edit ${singular.toLowerCase()}` : `New ${singular.toLowerCase()}`"
			:fields="fields"
			:values="formValues"
			:is-edit="Boolean(editing)"
			:on-submit="save"
		/>
	</div>
</template>
