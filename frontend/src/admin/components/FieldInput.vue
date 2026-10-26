<script setup lang="ts">
import { Button, Checkbox, DatePicker, Select, TextInput, Textarea } from "frappe-ui";
import { computed } from "vue";

import type { FieldDef } from "@/admin/fields";
import LinkSelect from "./LinkSelect.vue";

const props = defineProps<{ field: FieldDef; disabled?: boolean }>();
const model = defineModel<any>();

const inputType = computed(() => {
	const t = props.field.type;
	if (t === "int" || t === "float" || t === "currency") return "number";
	if (t === "email" || t === "tel") return t;
	return "text";
});

const listItems = computed<string[]>(() => (Array.isArray(model.value) ? model.value : []));

function setItem(index: number, value: string) {
	const next = [...listItems.value];
	next[index] = value;
	model.value = next;
}

function removeItem(index: number) {
	model.value = listItems.value.filter((_, i) => i !== index);
}
</script>

<template>
	<LinkSelect
		v-if="field.type === 'link' && field.link"
		v-model="model"
		:link="field.link"
		:label="field.label"
		:placeholder="field.placeholder"
		:required="field.required"
		:disabled="disabled"
	/>
	<Select
		v-else-if="field.type === 'select'"
		v-model="model"
		:label="field.label"
		:options="(field.options ?? []).map((o) => ({ label: o, value: o }))"
		:placeholder="field.placeholder"
		:disabled="disabled"
		size="md"
	/>
	<DatePicker
		v-else-if="field.type === 'date'"
		v-model="model"
		:label="field.label"
		:placeholder="field.placeholder"
		:disabled="disabled"
		size="md"
	/>
	<Textarea
		v-else-if="field.type === 'textarea'"
		v-model="model"
		:label="field.label"
		:placeholder="field.placeholder"
		:description="field.description"
		:disabled="disabled"
		:rows="3"
		size="md"
	/>
	<Checkbox
		v-else-if="field.type === 'check'"
		v-model="model"
		:label="field.label"
		:description="field.description"
		:disabled="disabled"
	/>
	<div v-else-if="field.type === 'list'" class="space-y-2">
		<p class="text-xs text-ink-gray-5">{{ field.label }}</p>
		<div v-for="(item, i) in listItems" :key="i" class="flex items-center gap-2">
			<TextInput
				class="flex-1"
				:model-value="item"
				:placeholder="field.placeholder"
				size="md"
				@update:model-value="setItem(i, String($event ?? ''))"
			/>
			<Button icon="lucide-x" :aria-label="`Remove ${item}`" @click="removeItem(i)" />
		</div>
		<Button
			icon-left="lucide-plus"
			label="Add"
			size="sm"
			@click="model = [...listItems, '']"
		/>
	</div>
	<TextInput
		v-else
		v-model="model"
		:type="inputType"
		:label="field.label"
		:placeholder="field.placeholder"
		:description="field.description"
		:required="field.required"
		:disabled="disabled"
		:min="inputType === 'number' ? 0 : undefined"
		size="md"
	/>
</template>
