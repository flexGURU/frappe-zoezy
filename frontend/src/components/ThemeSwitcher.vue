<script setup lang="ts">
import { type ColorScheme, useColorScheme } from "frappe-ui";

const { colorScheme, setColorScheme } = useColorScheme();

const options: { value: ColorScheme; label: string; icon: string }[] = [
	{ value: "light", label: "Light", icon: "lucide-sun" },
	{ value: "dark", label: "Dark", icon: "lucide-moon" },
	{ value: "system", label: "Auto", icon: "lucide-monitor" },
];
</script>

<template>
	<div
		class="grid grid-cols-3 gap-1 rounded-[12px] bg-surface-gray-2 p-1"
		role="radiogroup"
		aria-label="Theme"
	>
		<button
			v-for="option in options"
			:key="option.value"
			type="button"
			role="radio"
			:aria-checked="colorScheme === option.value"
			class="flex items-center justify-center gap-1.5 rounded-[9px] py-1.5 text-xs-medium transition-colors"
			:class="
				colorScheme === option.value
					? 'bg-surface-base text-ink-gray-9 shadow-sm'
					: 'text-ink-gray-5 hover:text-ink-gray-8'
			"
			@click="setColorScheme(option.value)"
		>
			<span :class="option.icon" class="size-3.5" />
			{{ option.label }}
		</button>
	</div>
</template>
