<script setup lang="ts">
import {
	Badge,
	Button,
	ErrorMessage,
	type ErrorMessageValue,
	Switch,
	call,
	createResource,
	dialog,
	toast,
} from "frappe-ui";
import { computed, reactive, ref, watch } from "vue";
import { useRouter } from "vue-router";

import AdminHeader from "@/admin/components/AdminHeader.vue";
import FieldInput from "@/admin/components/FieldInput.vue";
import FormDialog from "@/admin/components/FormDialog.vue";
import PaymentDialog from "@/admin/components/PaymentDialog.vue";
import { type Row, adminCall } from "@/admin/data";
import type { FieldDef } from "@/admin/fields";
import { useMoney } from "@/admin/money";
import SkeletonBlock from "@/components/SkeletonBlock.vue";
import type { InvoiceStatus, SubscriptionStatus } from "@/types";
import { formatDate } from "@/utils/format";
import { invoiceTheme, subscriptionTheme } from "@/utils/status";
import { WEEKDAYS } from "@/utils/week";

const props = defineProps<{ name: string }>();
const router = useRouter();
const money = useMoney();

const client = createResource({
	url: "zoezy.api.admin.get_client",
	params: { name: props.name },
	auto: true,
});

const profileFields: FieldDef[] = [
	{ fieldname: "first_name", label: "First name", type: "text", required: true },
	{ fieldname: "last_name", label: "Last name", type: "text", required: true },
	{ fieldname: "phone", label: "Phone", type: "tel" },
	{ fieldname: "age", label: "Age", type: "int" },
	{
		fieldname: "lead_source",
		label: "Lead source",
		type: "link",
		link: { doctype: "Lead Source" },
	},
];
const form = reactive<Record<string, any>>({});
watch(
	() => client.data,
	(data) => {
		if (data) for (const f of profileFields) form[f.fieldname] = data[f.fieldname] ?? "";
	},
	{ immediate: true }
);

const saving = ref(false);
const error = ref<ErrorMessageValue>();
async function saveProfile() {
	saving.value = true;
	error.value = undefined;
	try {
		await adminCall("update_client", { name: props.name, ...form });
		await client.reload();
		toast.success("Client updated");
	} catch (e) {
		error.value = e as Error;
	} finally {
		saving.value = false;
	}
}

async function toggleAccess(enabled: boolean) {
	try {
		await adminCall("set_portal_access", { name: props.name, enabled });
		await client.reload();
		toast.success(enabled ? "App access turned on" : "App access turned off");
	} catch (e) {
		toast.error((e as { messages?: string[] }).messages?.[0] ?? "Couldn't change access.");
	}
}

async function sendInvite() {
	try {
		await adminCall("send_invite", { name: props.name });
		toast.success("Password link sent");
	} catch (e) {
		toast.error((e as { messages?: string[] }).messages?.[0] ?? "Couldn't send the email.");
	}
}

const subscriptionOpen = ref(false);
const subscriptionFields: FieldDef[] = [
	{
		fieldname: "package_type",
		label: "Package",
		type: "link",
		required: true,
		link: { doctype: "Package Type" },
	},
	{ fieldname: "from_date", label: "Starts", type: "date", required: true },
	{
		fieldname: "to_date",
		label: "Ends",
		type: "date",
		description: "Leave empty for the standard period.",
	},
];
async function addSubscription(values: Record<string, unknown>) {
	await call("frappe.client.insert", {
		doc: {
			doctype: "Client Subscription",
			client: props.name,
			...values,
			to_date: values.to_date || null,
		},
	});
	toast.success("Subscription added and invoiced");
	await client.reload();
}

const payment = reactive({ open: false, invoice: "", outstanding: 0 });
function recordPayment(invoice: Row) {
	Object.assign(payment, {
		open: true,
		invoice: invoice.name,
		outstanding: invoice.outstanding_amount,
	});
}

const plansByDay = computed(() =>
	WEEKDAYS.map((day) => ({
		day,
		plans: (client.data?.plans ?? []).filter((p: Row) => p.day === day),
	}))
);

function remove() {
	dialog.danger({
		title: "Delete client?",
		message: "This only works for clients with no subscriptions, invoices or plans.",
		onConfirm: async () => {
			try {
				await call("frappe.client.delete", { doctype: "Client", name: props.name });
				toast.success("Client deleted");
				router.push({ name: "AdminClients" });
			} catch (e) {
				toast.error(
					(e as { messages?: string[] }).messages?.[0] ?? "Couldn't delete this client."
				);
			}
		},
	});
}
</script>

<template>
	<div>
		<AdminHeader
			:title="client.data?.full_name ?? 'Client'"
			subtitle="Client"
			:back="{ label: 'Clients', to: { name: 'AdminClients' } }"
		>
			<template #actions>
				<Button
					icon-left="lucide-dumbbell"
					label="New plan"
					@click="router.push({ name: 'AdminPlanNew', query: { client: name } })"
				/>
				<Button icon="lucide-trash-2" aria-label="Delete client" @click="remove" />
			</template>
		</AdminHeader>

		<div v-if="!client.data" class="grid gap-4 lg:grid-cols-3">
			<SkeletonBlock class="h-80 lg:col-span-2" />
			<SkeletonBlock class="h-80" />
		</div>

		<div v-else class="grid gap-4 lg:grid-cols-3">
			<form class="card space-y-4 p-5 lg:col-span-2" @submit.prevent="saveProfile">
				<div class="flex items-center justify-between">
					<h2 class="text-xl-semibold text-ink-gray-9">Details</h2>
					<Badge
						:label="client.data.status"
						:theme="client.data.status === 'Active' ? 'green' : 'gray'"
					/>
				</div>
				<div class="grid gap-4 sm:grid-cols-2">
					<FieldInput
						v-for="field in profileFields"
						:key="field.fieldname"
						v-model="form[field.fieldname]"
						:field="field"
					/>
				</div>
				<p class="text-sm text-ink-gray-5">
					{{ client.data.email }} · joined {{ formatDate(client.data.date_joined) }}
				</p>
				<ErrorMessage :message="error" />
				<div class="flex justify-end">
					<Button type="submit" variant="solid" :loading="saving" label="Save details" />
				</div>
			</form>

			<section class="card space-y-4 p-5">
				<h2 class="text-xl-semibold text-ink-gray-9">App access</h2>
				<Switch
					:model-value="client.data.portal_access"
					label="Can log in to the Zoezy app"
					:description="
						client.data.last_login
							? `Last seen ${formatDate(client.data.last_login)}`
							: 'Hasn\'t logged in yet'
					"
					@update:model-value="toggleAccess"
				/>
				<Button
					class="w-full"
					icon-left="lucide-mail"
					label="Email a password link"
					:disabled="!client.data.portal_access"
					@click="sendInvite"
				/>
			</section>

			<section class="card p-5 lg:col-span-3">
				<div class="mb-3 flex items-center justify-between">
					<h2 class="text-xl-semibold text-ink-gray-9">Subscriptions</h2>
					<Button icon-left="lucide-plus" label="Add" @click="subscriptionOpen = true" />
				</div>
				<p v-if="!client.data.subscriptions.length" class="text-base text-ink-gray-5">
					No subscriptions yet.
				</p>
				<ul v-else class="divide-y divide-outline-gray-1">
					<li
						v-for="s in client.data.subscriptions"
						:key="s.name"
						class="flex flex-wrap items-center justify-between gap-2 py-2.5"
					>
						<div>
							<p class="text-base-medium text-ink-gray-9">{{ s.package_type }}</p>
							<p class="text-sm text-ink-gray-5">
								{{ formatDate(s.from_date) }} – {{ formatDate(s.to_date) }}
							</p>
						</div>
						<div class="flex items-center gap-3">
							<span class="tabular-nums text-ink-gray-7">{{
								money(s.package_price)
							}}</span>
							<Badge
								:label="s.status"
								:theme="subscriptionTheme(s.status as SubscriptionStatus)"
							/>
						</div>
					</li>
				</ul>
			</section>

			<section class="card p-5 lg:col-span-2">
				<h2 class="mb-3 text-xl-semibold text-ink-gray-9">Invoices</h2>
				<p v-if="!client.data.invoices.length" class="text-base text-ink-gray-5">
					No invoices yet.
				</p>
				<ul v-else class="divide-y divide-outline-gray-1">
					<li
						v-for="inv in client.data.invoices"
						:key="inv.name"
						class="flex flex-wrap items-center justify-between gap-2 py-2.5"
					>
						<div>
							<p class="text-base-medium text-ink-gray-9">{{ inv.name }}</p>
							<p class="text-sm text-ink-gray-5">
								{{ formatDate(inv.posting_date) }} · {{ money(inv.total) }}
								<template v-if="inv.outstanding_amount > 0">
									· {{ money(inv.outstanding_amount) }} due</template
								>
							</p>
						</div>
						<div class="flex items-center gap-2">
							<Badge
								:label="inv.status"
								:theme="invoiceTheme(inv.status as InvoiceStatus)"
							/>
							<Button
								v-if="inv.docstatus === 1 && inv.outstanding_amount > 0"
								size="sm"
								label="Record payment"
								@click="recordPayment(inv)"
							/>
						</div>
					</li>
				</ul>
			</section>

			<section class="card p-5">
				<h2 class="mb-3 text-xl-semibold text-ink-gray-9">Weekly plan</h2>
				<ul class="space-y-1.5">
					<li
						v-for="d in plansByDay"
						:key="d.day"
						class="flex items-start justify-between gap-2 text-base"
					>
						<span class="w-24 shrink-0 text-ink-gray-5">{{ d.day.slice(0, 3) }}</span>
						<span class="flex flex-1 flex-wrap justify-end gap-1">
							<RouterLink
								v-for="p in d.plans"
								:key="p.name"
								:to="{ name: 'AdminPlan', params: { name: p.name } }"
								class="rounded-full bg-night px-2.5 py-0.5 text-xs-semibold text-volt"
							>
								{{ p.category }} · {{ p.total_sets }}
							</RouterLink>
							<span v-if="!d.plans.length" class="text-ink-gray-4">Rest</span>
						</span>
					</li>
				</ul>
			</section>
		</div>

		<FormDialog
			v-model:open="subscriptionOpen"
			title="Add subscription"
			submit-label="Add & invoice"
			:fields="subscriptionFields"
			:values="{ package_type: '', from_date: '', to_date: '' }"
			:on-submit="addSubscription"
		/>
		<PaymentDialog
			v-model:open="payment.open"
			:invoice="payment.invoice"
			:outstanding="payment.outstanding"
			@saved="client.reload()"
		/>
	</div>
</template>
