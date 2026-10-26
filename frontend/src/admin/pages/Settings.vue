<script setup lang="ts">
import {
	Button,
	ErrorMessage,
	type ErrorMessageValue,
	FileUploader,
	Switch,
	TextInput,
	toast,
} from "frappe-ui";
import { reactive, ref, watch } from "vue";

import AdminHeader from "@/admin/components/AdminHeader.vue";
import LinkSelect from "@/admin/components/LinkSelect.vue";
import { useDoc } from "@/admin/data";
import SkeletonBlock from "@/components/SkeletonBlock.vue";
import { useProfile } from "@/data/resources";

const settings = useDoc("Zoezy Settings", "Zoezy Settings");
const profile = useProfile();

const form = reactive({
	brand_name: "",
	app_logo: "",
	default_currency: null as string | null,
	payment_number: "",
	active_period_duration: 30,
	invoice_due_days: 7,
	allow_client_signup: true,
});
watch(
	() => settings.doc,
	(doc) => {
		if (!doc) return;
		Object.assign(form, {
			brand_name: doc.brand_name ?? "",
			app_logo: doc.app_logo ?? "",
			default_currency: doc.default_currency ?? null,
			payment_number: doc.payment_number ?? "",
			active_period_duration: doc.active_period_duration,
			invoice_due_days: doc.invoice_due_days,
			allow_client_signup: Boolean(doc.allow_client_signup),
		});
	},
	{ immediate: true }
);

const error = ref<ErrorMessageValue>();
async function save() {
	error.value = undefined;
	try {
		await settings.setValue.submit({
			...form,
			active_period_duration: Number(form.active_period_duration),
			invoice_due_days: Number(form.invoice_due_days),
			allow_client_signup: form.allow_client_signup ? 1 : 0,
		});
		await profile.reload();
		toast.success("Settings saved");
	} catch (e) {
		error.value = e as Error;
	}
}
</script>

<template>
	<div>
		<AdminHeader title="Settings" subtitle="Zoezy" />

		<SkeletonBlock v-if="!settings.doc" class="h-96" />
		<form v-else class="grid gap-4 lg:grid-cols-2" @submit.prevent="save">
			<section class="card space-y-4 p-5">
				<h2 class="text-lg-semibold text-ink-gray-9">Brand</h2>
				<TextInput
					v-model="form.brand_name"
					label="Brand name"
					placeholder="Zoezy"
					size="md"
				/>
				<div>
					<p class="mb-1.5 text-xs text-ink-gray-5">Logo</p>
					<div class="flex items-center gap-4">
						<img
							:src="form.app_logo || '/assets/zoezy/icons/desktop_icons/zoezy.svg'"
							alt="Logo preview"
							class="size-16 rounded-[16px] border border-outline-gray-1 object-contain"
						/>
						<div class="flex flex-wrap gap-2">
							<FileUploader
								:file-types="['image/*']"
								:private="false"
								@success="(file) => (form.app_logo = file.file_url)"
							>
								<template #default="{ openFileSelector, uploading, progress }">
									<Button
										:loading="uploading"
										:label="
											uploading ? `Uploading ${progress}%` : 'Upload logo'
										"
										icon-left="lucide-upload"
										@click="openFileSelector"
									/>
								</template>
							</FileUploader>
							<Button
								v-if="form.app_logo"
								label="Use default"
								@click="form.app_logo = ''"
							/>
						</div>
					</div>
					<p class="mt-1.5 text-xs text-ink-gray-5">
						Shown in the client app. Square images work best.
					</p>
				</div>
			</section>

			<section class="card space-y-4 p-5">
				<h2 class="text-lg-semibold text-ink-gray-9">Billing</h2>
				<LinkSelect
					v-model="form.default_currency"
					label="Currency"
					:link="{ doctype: 'Currency', filters: { enabled: 1 } }"
				/>
				<TextInput
					v-model="form.payment_number"
					label="M-Pesa payment details"
					placeholder="Till / paybill number"
					size="md"
				/>
				<div class="grid grid-cols-2 gap-4">
					<TextInput
						v-model="form.active_period_duration"
						type="number"
						label="Membership length (days)"
						size="md"
					/>
					<TextInput
						v-model="form.invoice_due_days"
						type="number"
						label="Invoice due after (days)"
						size="md"
					/>
				</div>
			</section>

			<section class="card space-y-4 p-5 lg:col-span-2">
				<h2 class="text-lg-semibold text-ink-gray-9">Client app</h2>
				<Switch
					v-model="form.allow_client_signup"
					label="Let new clients sign up themselves"
					description="Turn off if you'd rather add every client yourself."
				/>
			</section>

			<div class="flex items-center justify-end gap-3 lg:col-span-2">
				<ErrorMessage :message="error" />
				<Button
					type="submit"
					variant="solid"
					:loading="settings.setValue.loading"
					label="Save settings"
				/>
			</div>
		</form>
	</div>
</template>
