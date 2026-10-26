<script setup lang="ts">
import { Combobox } from "frappe-ui";
import { computed } from "vue";

import { type Row, useDocList } from "@/admin/data";
import type { LinkOptions } from "@/admin/fields";

const props = defineProps<{
	link: LinkOptions;
	label?: string;
	placeholder?: string;
	required?: boolean;
	disabled?: boolean;
}>();
const model = defineModel<string | null>({ default: null });

const labelField = props.link.labelField;
const list = useDocList(props.link.doctype, {
	fields: labelField ? ["name", labelField] : ["name"],
	filters: props.link.filters,
	orderBy: labelField ? `${labelField} asc` : "name asc",
});

const options = computed(() =>
	(list.data ?? []).map((row: Row) => ({
		value: row.name,
		label: (labelField && row[labelField]) || row.name,
	}))
);
</script>

<template>
	<Combobox
		v-model="model"
		:options="options"
		:label="label"
		:placeholder="placeholder ?? `Select ${label?.toLowerCase() ?? ''}`"
		:required="required"
		:disabled="disabled"
		:loading="list.list.loading"
		size="md"
	/>
</template>
