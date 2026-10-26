<script setup lang="ts">
import { Button, Dialog, ErrorMessage, type ErrorMessageValue } from "frappe-ui";
import { ref, useId, watch } from "vue";

import { type FieldDef, cleanValues, missingRequired } from "@/admin/fields";
import FieldInput from "./FieldInput.vue";

const props = defineProps<{
	title: string;
	fields: FieldDef[];
	values: Record<string, unknown>;
	submitLabel?: string;
	isEdit?: boolean;
	onSubmit: (values: Record<string, unknown>) => Promise<unknown>;
}>();
const open = defineModel<boolean>("open", { required: true });

const formId = `form-${useId()}`;
const form = ref<Record<string, unknown>>({});
const saving = ref(false);
const error = ref<ErrorMessageValue>();

watch(
	open,
	(isOpen) => {
		if (!isOpen) return;
		form.value = JSON.parse(JSON.stringify(props.values));
		error.value = undefined;
	},
	{ immediate: true }
);

async function submit() {
	const missing = missingRequired(props.fields, form.value);
	if (missing.length) {
		error.value = `Please fill in ${missing.map((f) => f.label).join(", ")}.`;
		return;
	}
	saving.value = true;
	error.value = undefined;
	try {
		await props.onSubmit(cleanValues(props.fields, form.value));
		open.value = false;
	} catch (e) {
		error.value = e as Error;
	} finally {
		saving.value = false;
	}
}
</script>

<template>
	<Dialog v-model:open="open" :title="title" size="xl">
		<form :id="formId" class="grid gap-4 sm:grid-cols-2" @submit.prevent="submit">
			<div
				v-for="field in fields"
				:key="field.fieldname"
				:class="
					field.wide || ['textarea', 'list'].includes(field.type) ? 'sm:col-span-2' : ''
				"
			>
				<FieldInput
					v-model="form[field.fieldname]"
					:field="field"
					:disabled="isEdit && field.createOnly"
				/>
			</div>
			<ErrorMessage class="sm:col-span-2" :message="error" />
		</form>
		<template #actions>
			<div class="flex justify-end gap-2">
				<Button label="Cancel" @click="open = false" />
				<Button
					type="submit"
					:form="formId"
					variant="solid"
					:loading="saving"
					:label="submitLabel ?? 'Save'"
				/>
			</div>
		</template>
	</Dialog>
</template>
