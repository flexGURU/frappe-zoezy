<script setup lang="ts">
defineProps<{ icon: string; title: string; message?: string }>();
</script>

<template>
	<div class="flex flex-col items-center px-6 py-10 text-center">
		<span
			class="grid size-14 place-items-center rounded-[18px] bg-surface-gray-2 text-ink-gray-6"
		>
			<span :class="icon" class="size-6" />
		</span>
		<p class="mt-4 text-lg-semibold text-ink-gray-9">{{ title }}</p>
		<p v-if="message" class="mt-1 max-w-sm text-base text-ink-gray-5">{{ message }}</p>
		<div v-if="$slots.default" class="mt-5"><slot /></div>
	</div>
</template>
