<script setup lang="ts">
defineProps<{ title: string; subtitle?: string }>();
</script>

<template>
	<header class="mb-6 flex items-end justify-between gap-4">
		<div class="min-w-0">
			<p v-if="subtitle" class="eyebrow text-ink-gray-5">{{ subtitle }}</p>
			<h1
				class="mt-1 font-display text-4xl font-bold tracking-tight text-ink-gray-9 md:text-6xl"
			>
				{{ title }}
			</h1>
		</div>
		<slot name="actions" />
	</header>
</template>
