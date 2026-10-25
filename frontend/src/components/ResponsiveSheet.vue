<script setup lang="ts">
import { BottomSheet, Dialog } from "frappe-ui";

import { useIsMobile } from "@/composables/useIsMobile";

defineProps<{ title: string }>();
const open = defineModel<boolean>("open", { required: true });

const isMobile = useIsMobile();
</script>

<template>
	<BottomSheet v-if="isMobile" v-model:open="open" :title="title">
		<div class="px-4 pb-6">
			<slot />
		</div>
	</BottomSheet>
	<Dialog v-else v-model:open="open" :title="title" size="lg">
		<slot />
	</Dialog>
</template>
