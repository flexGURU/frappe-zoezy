<script setup lang="ts">
import CrudPage from "@/admin/components/CrudPage.vue";
import type { FieldDef } from "@/admin/fields";

const fields: FieldDef[] = [
	{ fieldname: "exercise_name", label: "Name", type: "text", required: true, createOnly: true },
	{
		fieldname: "category",
		label: "Category",
		type: "link",
		required: true,
		link: { doctype: "Workout Category" },
	},
	{
		fieldname: "video_url",
		label: "Demo video",
		type: "text",
		placeholder: "https://youtube.com/watch?v=…",
		description: "YouTube, Vimeo or a direct video link. Clients see it under the exercise.",
		wide: true,
	},
];
</script>

<template>
	<CrudPage
		doctype="Exercise Type"
		title="Exercises"
		subtitle="Training"
		singular="Exercise"
		empty-icon="lucide-activity"
		:fields="fields"
		:list-fields="['name', 'category', 'video_url']"
		:columns="[
			{ key: 'name', label: 'Exercise', primary: true },
			{ key: 'category', label: 'Category' },
			{ key: 'video_url', label: 'Demo', format: (r) => (r.video_url ? 'Video' : '') },
		]"
		:search-keys="['name', 'category']"
		order-by="name asc"
	/>
</template>
