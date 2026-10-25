<script setup lang="ts">
import { ref, watch } from "vue";

import { branding } from "@/data/branding";

defineProps<{ inverted?: boolean }>();

const logoFailed = ref(false);
watch(
	() => branding.value.logo,
	() => (logoFailed.value = false)
);
</script>

<template>
	<div class="flex items-center gap-2.5">
		<img
			v-if="branding.logo && !logoFailed"
			:src="branding.logo"
			:alt="`${branding.brand_name} logo`"
			class="size-9 rounded-[12px] object-contain"
			@error="logoFailed = true"
		/>
		<span
			v-else
			class="grid size-9 place-items-center rounded-[12px] bg-volt text-volt-ink"
			aria-hidden="true"
		>
			<span class="lucide-zap size-5" />
		</span>
		<span
			class="font-display text-xl font-bold tracking-tight"
			:class="inverted ? 'text-white' : 'text-ink-gray-9'"
		>
			{{ branding.brand_name }}
		</span>
	</div>
</template>
