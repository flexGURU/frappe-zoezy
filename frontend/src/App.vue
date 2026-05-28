<template>
	<div class="flex h-screen overflow-hidden bg-gray-50">
		<!-- Sidebar: only shown for authenticated pages -->
		<AppSidebar v-if="isLoggedIn" />

		<!-- Main column -->
		<div class="flex-1 flex flex-col overflow-hidden min-w-0">
			<Navbar v-if="isLoggedIn" />
			<router-view />
		</div>

		<Toasts />
	</div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { Toasts } from 'frappe-ui'
import AppSidebar from '@/components/AppSidebar.vue'
import Navbar from '@/components/Navbar.vue'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const auth = useAuthStore()
const isLoggedIn = computed(() => auth.isLoggedIn && route.name !== 'Login')
</script>
