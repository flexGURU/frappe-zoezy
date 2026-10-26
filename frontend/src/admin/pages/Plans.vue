<script setup lang="ts">
import { Button } from "frappe-ui";
import { ref, watch } from "vue";
import { useRouter } from "vue-router";

import AdminHeader from "@/admin/components/AdminHeader.vue";
import DataTable from "@/admin/components/DataTable.vue";
import LinkSelect from "@/admin/components/LinkSelect.vue";
import { usePagedList } from "@/admin/data";

const router = useRouter();
const client = ref<string | null>(null);

const plans = usePagedList("Workout Log", {
	fields: ["name", "client", "client_name", "day", "category", "total_sets"],
	orderBy: "client_name asc, creation asc",
	searchFields: ["client_name", "category", "day"],
});
watch(client, (value) => plans.setFilters(value ? { client: value } : {}));
</script>

<template>
	<div>
		<AdminHeader title="Workout plans" subtitle="Training">
			<template #actions>
				<Button
					variant="solid"
					icon-left="lucide-plus"
					label="New plan"
					@click="router.push({ name: 'AdminPlanNew', query: client ? { client } : {} })"
				/>
			</template>
		</AdminHeader>

		<div class="mb-4 max-w-sm">
			<LinkSelect
				v-model="client"
				placeholder="All clients"
				:link="{ doctype: 'Client', labelField: 'full_name' }"
			/>
		</div>

		<DataTable
			:list="plans"
			:columns="[
				{ key: 'client_name', label: 'Client', primary: true },
				{ key: 'day', label: 'Day' },
				{ key: 'category', label: 'Session' },
				{ key: 'total_sets', label: 'Sets', align: 'right' },
			]"
			empty-icon="lucide-dumbbell"
			empty-title="No workout plans yet"
			@select="(row) => router.push({ name: 'AdminPlan', params: { name: row.name } })"
		/>
	</div>
</template>
