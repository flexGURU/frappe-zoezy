<script setup lang="ts">
import { Badge } from "frappe-ui";

import CrudPage from "@/admin/components/CrudPage.vue";
import { useClientNames } from "@/admin/data";
import type { FieldDef } from "@/admin/fields";
import { useMoney } from "@/admin/money";
import type { SubscriptionStatus } from "@/types";
import { formatDate } from "@/utils/format";
import { subscriptionTheme } from "@/utils/status";

const money = useMoney();
const { byName } = useClientNames();

const fields: FieldDef[] = [
	{
		fieldname: "client",
		label: "Client",
		type: "link",
		required: true,
		createOnly: true,
		link: { doctype: "Client", labelField: "full_name" },
	},
	{
		fieldname: "package_type",
		label: "Package",
		type: "link",
		required: true,
		createOnly: true,
		link: { doctype: "Package Type" },
	},
	{ fieldname: "from_date", label: "Starts", type: "date", required: true },
	{
		fieldname: "to_date",
		label: "Ends",
		type: "date",
		description: "Leave empty to use the standard period from Settings.",
	},
];

const toDoc = (values: Record<string, unknown>) => ({
	...values,
	to_date: values.to_date || null,
});
</script>

<template>
	<CrudPage
		doctype="Client Subscription"
		title="Subscriptions"
		subtitle="Clients"
		singular="Subscription"
		empty-icon="lucide-calendar-range"
		:fields="fields"
		:list-fields="[
			'name',
			'client',
			'package_type',
			'package_price',
			'from_date',
			'to_date',
			'status',
		]"
		:columns="[
			{
				key: 'client',
				label: 'Client',
				primary: true,
				format: (r) => byName[r.client] ?? r.client,
			},
			{ key: 'package_type', label: 'Package' },
			{
				key: 'from_date',
				label: 'Period',
				format: (r) =>
					`${formatDate(r.from_date, 'D MMM')} – ${formatDate(r.to_date, 'D MMM YYYY')}`,
			},
			{
				key: 'package_price',
				label: 'Price',
				align: 'right',
				format: (r) => money(r.package_price),
			},
			{ key: 'status', label: 'Status' },
		]"
		:search-keys="['client', 'package_type', 'status']"
		:to-doc="toDoc"
		order-by="from_date desc"
	>
		<template #cell-status="{ row }">
			<Badge
				:label="row.status"
				:theme="subscriptionTheme(row.status as SubscriptionStatus)"
			/>
		</template>
	</CrudPage>
</template>
