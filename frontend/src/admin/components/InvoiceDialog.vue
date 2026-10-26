<script setup lang="ts">
import {
	Button,
	DatePicker,
	Dialog,
	ErrorMessage,
	type ErrorMessageValue,
	TextInput,
	call,
	toast,
} from "frappe-ui";
import { reactive, ref, watch } from "vue";

import { adminCall } from "@/admin/data";
import LinkSelect from "./LinkSelect.vue";

const emit = defineEmits<{ saved: [name: string] }>();
const open = defineModel<boolean>("open", { required: true });

const form = reactive({
	client: null as string | null,
	subscription: null as string | null,
	posting_date: "",
	due_date: "",
	packages: [] as { package_name: string | null; unit_price: number | string }[],
});
const saving = ref(false);
const error = ref<ErrorMessageValue>();

watch(open, (isOpen) => {
	if (!isOpen) return;
	Object.assign(form, {
		client: null,
		subscription: null,
		posting_date: "",
		due_date: "",
		packages: [{ package_name: null, unit_price: "" }],
	});
	error.value = undefined;
});
watch(
	() => form.client,
	() => (form.subscription = null)
);

async function setPackage(index: number, name: string | null) {
	form.packages[index].package_name = name;
	if (!name) return;
	const { unit_price } = await call<{ unit_price: number }>("frappe.client.get_value", {
		doctype: "Package Type",
		filters: name,
		fieldname: "unit_price",
	});
	form.packages[index].unit_price = unit_price;
}

async function save() {
	saving.value = true;
	error.value = undefined;
	try {
		const name = await adminCall<string>("create_invoice", {
			client: form.client,
			subscription: form.subscription,
			posting_date: form.posting_date || null,
			due_date: form.due_date || null,
			packages: form.packages.filter((p) => p.package_name),
		});
		toast.success(`Invoice ${name} issued`);
		open.value = false;
		emit("saved", name);
	} catch (e) {
		error.value = e as Error;
	} finally {
		saving.value = false;
	}
}
</script>

<template>
	<Dialog v-model:open="open" title="New invoice" size="xl">
		<div class="space-y-4">
			<div class="grid gap-4 sm:grid-cols-2">
				<LinkSelect
					v-model="form.client"
					label="Client"
					:link="{ doctype: 'Client', labelField: 'full_name' }"
					required
				/>
				<LinkSelect
					:key="form.client ?? 'none'"
					v-model="form.subscription"
					label="Subscription"
					:link="{
						doctype: 'Client Subscription',
						labelField: 'package_type',
						filters: { client: form.client ?? '' },
					}"
					:disabled="!form.client"
					required
				/>
				<DatePicker
					v-model="form.posting_date"
					label="Invoice date"
					placeholder="Today"
					size="md"
				/>
				<DatePicker
					v-model="form.due_date"
					label="Due date"
					placeholder="From settings"
					size="md"
				/>
			</div>

			<div class="space-y-2">
				<p class="text-xs text-ink-gray-5">Packages</p>
				<div v-for="(row, i) in form.packages" :key="i" class="flex items-end gap-2">
					<LinkSelect
						class="flex-1"
						:model-value="row.package_name"
						:link="{ doctype: 'Package Type' }"
						placeholder="Package"
						@update:model-value="setPackage(i, $event)"
					/>
					<TextInput
						v-model="row.unit_price"
						class="w-32"
						type="number"
						size="md"
						placeholder="Price"
					/>
					<Button
						icon="lucide-x"
						aria-label="Remove package"
						:disabled="form.packages.length === 1"
						@click="form.packages.splice(i, 1)"
					/>
				</div>
				<Button
					icon-left="lucide-plus"
					size="sm"
					label="Add package"
					@click="form.packages.push({ package_name: null, unit_price: '' })"
				/>
			</div>
			<ErrorMessage :message="error" />
		</div>
		<template #actions>
			<div class="flex justify-end gap-2">
				<Button label="Cancel" @click="open = false" />
				<Button variant="solid" :loading="saving" label="Issue invoice" @click="save" />
			</div>
		</template>
	</Dialog>
</template>
