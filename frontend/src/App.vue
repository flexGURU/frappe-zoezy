<script setup lang="ts">
import { FrappeUIProvider, useColorScheme } from "frappe-ui";

useColorScheme();
</script>

<template>
	<FrappeUIProvider>
		<RouterView />
	</FrappeUIProvider>
</template>
