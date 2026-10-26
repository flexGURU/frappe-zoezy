<script setup lang="ts">
import CrudPage from "@/admin/components/CrudPage.vue";
import type { FieldDef } from "@/admin/fields";

const fields: FieldDef[] = [
	{
		fieldname: "category_name",
		label: "Name",
		type: "text",
		required: true,
		createOnly: true,
		wide: true,
	},
];
</script>

<template>
	<CrudPage
		doctype="Workout Category"
		title="Categories"
		subtitle="Training"
		singular="Category"
		empty-icon="lucide-tags"
		:fields="fields"
		:list-fields="['name']"
		:columns="[{ key: 'name', label: 'Name', primary: true }]"
		:search-keys="['name']"
		order-by="name asc"
	/>
</template>
