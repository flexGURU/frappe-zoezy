<script setup lang="ts">
import CrudPage from "@/admin/components/CrudPage.vue";
import type { Row } from "@/admin/data";
import type { FieldDef } from "@/admin/fields";
import { useMoney } from "@/admin/money";

const money = useMoney();
const fields: FieldDef[] = [
	{ fieldname: "package_name", label: "Name", type: "text", required: true, createOnly: true },
	{ fieldname: "unit_price", label: "Price", type: "currency", required: true },
	{
		fieldname: "items",
		label: "What's included",
		type: "list",
		placeholder: "e.g. 4 coached sessions a week",
	},
];

const toForm = (doc: Row) => ({
	package_name: doc.package_name,
	unit_price: doc.unit_price,
	items: (doc.items ?? []).map((row: Row) => row.item),
});
const toDoc = (values: Record<string, unknown>) => ({
	package_name: values.package_name,
	unit_price: Number(values.unit_price),
	items: (values.items as string[]).filter((item) => item.trim()).map((item) => ({ item })),
});
</script>

<template>
	<CrudPage
		doctype="Package Type"
		title="Packages"
		subtitle="Billing"
		singular="Package"
		empty-icon="lucide-package"
		:fields="fields"
		:list-fields="['name', 'unit_price']"
		:columns="[
			{ key: 'name', label: 'Package', primary: true },
			{
				key: 'unit_price',
				label: 'Price',
				align: 'right',
				format: (r) => money(r.unit_price),
			},
		]"
		:search-keys="['name']"
		:to-form="toForm"
		:to-doc="toDoc"
		order-by="name asc"
	/>
</template>
