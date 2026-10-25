<script setup lang="ts">
import {
	Avatar,
	Badge,
	Button,
	type ColorScheme,
	ErrorMessage,
	type ErrorMessageValue,
	TabButtons,
	TextInput,
	call,
	dialog,
	toast,
	useColorScheme,
	usePageMeta,
} from "frappe-ui";
import { computed, reactive, ref, watch } from "vue";

import ScreenHeader from "@/components/ScreenHeader.vue";
import { useProfile } from "@/data/resources";
import { session } from "@/data/session";
import { formatDate } from "@/utils/format";

usePageMeta(() => ({ title: "Profile" }));

const profile = useProfile();
const { colorScheme, setColorScheme } = useColorScheme();

const form = reactive({ first_name: "", last_name: "", phone: "" });
watch(
	() => profile.data,
	(data) => {
		if (!data) return;
		form.first_name = data.first_name ?? "";
		form.last_name = data.last_name ?? "";
		form.phone = data.phone ?? "";
	},
	{ immediate: true }
);

const dirty = computed(() => {
	const data = profile.data;
	return Boolean(
		data &&
			(form.first_name !== (data.first_name ?? "") ||
				form.last_name !== (data.last_name ?? "") ||
				form.phone !== (data.phone ?? ""))
	);
});

const saving = ref(false);
const error = ref<ErrorMessageValue>();

async function save() {
	saving.value = true;
	error.value = undefined;
	try {
		await call("zoezy.api.profile.update_profile", { ...form });
		await profile.reload();
		toast.success("Profile updated");
	} catch (e) {
		error.value = e as Error;
	} finally {
		saving.value = false;
	}
}

const schemes: { value: ColorScheme; label: string; iconLeft: string }[] = [
	{ value: "light", label: "Light", iconLeft: "lucide-sun" },
	{ value: "dark", label: "Dark", iconLeft: "lucide-moon" },
	{ value: "system", label: "Auto", iconLeft: "lucide-monitor" },
];
const scheme = computed({
	get: () => colorScheme.value,
	set: (value) => setColorScheme(value as ColorScheme),
});

function logout() {
	dialog.confirm({
		title: "Log out?",
		message: "You'll need your email and password to log back in.",
		confirmLabel: "Log out",
		onConfirm: () => session.logout(),
	});
}
</script>

<template>
	<div class="space-y-6">
		<ScreenHeader title="Profile" subtitle="Account" />

		<section
			class="card flex flex-col items-center gap-4 p-6 text-center sm:flex-row sm:text-left"
		>
			<Avatar
				:label="profile.data?.full_name"
				:image="profile.data?.image ?? undefined"
				size="3xl"
			/>
			<div class="min-w-0 flex-1">
				<p class="truncate text-3xl-semibold text-ink-gray-9">
					{{ profile.data?.full_name }}
				</p>
				<p class="truncate text-base text-ink-gray-5">{{ profile.data?.email }}</p>
				<p v-if="profile.data?.client?.date_joined" class="mt-1 text-sm text-ink-gray-5">
					Member since {{ formatDate(profile.data.client.date_joined, "MMMM YYYY") }}
				</p>
			</div>
			<Badge
				v-if="profile.data?.client"
				:label="profile.data.client.status"
				:theme="profile.data.client.status === 'Active' ? 'green' : 'gray'"
				size="lg"
			/>
		</section>

		<form class="card space-y-4 p-6" @submit.prevent="save">
			<h2 class="text-xl-semibold text-ink-gray-9">Your details</h2>
			<div class="grid gap-4 sm:grid-cols-2">
				<TextInput v-model="form.first_name" label="First name" size="md" required />
				<TextInput v-model="form.last_name" label="Last name" size="md" />
			</div>
			<TextInput
				v-model="form.phone"
				label="Phone"
				type="tel"
				size="md"
				placeholder="0712 345 678"
			/>
			<TextInput :model-value="profile.data?.email" label="Email" size="md" disabled />
			<ErrorMessage :message="error" />
			<div class="flex justify-end">
				<Button
					type="submit"
					variant="solid"
					size="md"
					:loading="saving"
					:disabled="!dirty"
					label="Save changes"
				/>
			</div>
		</form>

		<section
			class="card flex flex-col gap-4 p-6 sm:flex-row sm:items-center sm:justify-between"
		>
			<div>
				<h2 class="text-xl-semibold text-ink-gray-9">Appearance</h2>
				<p class="text-sm text-ink-gray-5">Auto follows your device setting.</p>
			</div>
			<TabButtons v-model="scheme" :options="schemes" />
		</section>

		<Button
			class="w-full"
			size="lg"
			theme="red"
			variant="subtle"
			icon-left="lucide-log-out"
			label="Log out"
			@click="logout"
		/>
	</div>
</template>
