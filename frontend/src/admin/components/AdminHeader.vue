<script setup lang="ts">
import { usePageMeta } from "frappe-ui";

const props = defineProps<{
	title: string;
	subtitle?: string;
	back?: { label: string; to: object };
}>();
usePageMeta(() => ({ title: props.title }));
</script>

<template>
	<header class="mb-6">
		<RouterLink
			v-if="back"
			:to="back.to"
			class="mb-2 inline-flex items-center gap-1 text-sm text-ink-gray-5 hover:text-ink-gray-9"
		>
			<span class="lucide-arrow-left size-4" /> {{ back.label }}
		</RouterLink>
		<div class="flex flex-wrap items-end justify-between gap-3">
			<div class="min-w-0">
				<p v-if="subtitle" class="eyebrow text-ink-gray-5">{{ subtitle }}</p>
				<h1
					class="mt-1 truncate font-display text-4xl font-bold tracking-tight text-ink-gray-9 md:text-5xl"
				>
					{{ title }}
				</h1>
			</div>
			<div class="flex flex-wrap gap-2"><slot name="actions" /></div>
		</div>
	</header>
</template>
