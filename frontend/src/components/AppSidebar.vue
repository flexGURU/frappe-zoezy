<template>
	<!-- Desktop sidebar (hidden on mobile) -->
	<aside
		class="hidden md:flex h-screen w-64 bg-white border-r border-gray-200 flex-col shrink-0"
	>
		<!-- Logo -->
		<div class="px-6 py-5 border-b border-gray-200">
			<div class="flex items-center gap-3">
				<div
					class="h-9 w-9 rounded-xl bg-blue-600 flex items-center justify-center shrink-0"
				>
					<img src="/zoezy-logo.png" class="rounded-full" alt="" />
				</div>
				<span class="font-bold text-gray-900 text-xl">Zoezy</span>
			</div>
		</div>

		<!-- Nav -->
		<nav class="flex-1 px-4 py-5 space-y-1 overflow-y-auto">
			<router-link
				v-for="item in navItems"
				:key="item.to"
				:to="item.to"
				class="flex items-center gap-3 px-4 py-3 rounded-xl text-base font-medium transition-colors"
				:class="
					$route.path === item.to
						? 'bg-blue-50 text-blue-700'
						: 'text-gray-700 hover:bg-gray-100 hover:text-gray-900'
				"
			>
				<svg
					class="w-5 h-5 shrink-0"
					fill="none"
					stroke="currentColor"
					stroke-width="2"
					viewBox="0 0 24 24"
				>
					<path :d="item.iconPath" stroke-linecap="round" stroke-linejoin="round" />
				</svg>
				{{ item.label }}
			</router-link>
		</nav>

		<!-- User / logout -->
		<div class="px-4 py-4 border-t border-gray-200">
			<div class="flex items-center gap-3 px-3 py-3 rounded-xl bg-gray-50">
				<div
					class="h-9 w-9 rounded-full bg-blue-600 flex items-center justify-center shrink-0"
				>
					<span class="text-white font-bold text-sm">{{ userInitial }}</span>
				</div>
				<div class="flex-1 min-w-0">
					<p class="text-sm font-semibold text-gray-900 truncate">{{ displayName }}</p>
					<p class="text-xs text-gray-500 truncate">{{ auth.user }}</p>
				</div>
				<button
					@click="auth.logout()"
					class="text-gray-400 hover:text-red-500 transition-colors shrink-0 p-1 rounded-lg hover:bg-red-50"
					title="Logout"
				>
					<svg
						class="w-4 h-4"
						fill="none"
						stroke="currentColor"
						stroke-width="2"
						viewBox="0 0 24 24"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0 012-2h6a2 2 0 012 2v1"
						/>
					</svg>
				</button>
			</div>
		</div>
	</aside>

	<!-- Mobile bottom navigation -->
	<nav
		class="md:hidden fixed bottom-0 inset-x-0 z-40 bg-white border-t border-gray-200 flex items-stretch"
	>
		<router-link
			v-for="item in navItems"
			:key="item.to"
			:to="item.to"
			class="flex-1 flex flex-col items-center justify-center gap-1 py-3 text-xs font-medium transition-colors"
			:class="$route.path === item.to ? 'text-blue-600' : 'text-gray-500'"
		>
			<svg
				class="w-6 h-6"
				fill="none"
				stroke="currentColor"
				stroke-width="2"
				viewBox="0 0 24 24"
			>
				<path :d="item.iconPath" stroke-linecap="round" stroke-linejoin="round" />
			</svg>
			{{ item.label }}
		</router-link>
	</nav>
</template>

<script setup>
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()

const navItems = [
	{
		label: 'Profile',
		to: '/profile',
		iconPath:
			'M5.121 17.804A13.937 13.937 0 0112 16c2.5 0 4.847.655 6.879 1.804M15 10a3 3 0 11-6 0 3 3 0 016 0z',
	},
	{
		label: 'Home',
		to: '/dashboard',
		iconPath:
			'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0h6',
	},

	{
		label: 'Subscription',
		to: '/subscriptions',
		iconPath:
			'M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z',
	},

	{
		label: 'Invoices',
		to: '/invoices',
		iconPath:
			'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z',
	},
]

const userInitial = computed(() => {
	const u = auth.user || 'U'
	return u.split('@')[0].charAt(0).toUpperCase()
})

const displayName = computed(() => {
	if (!auth.user) return 'My Account'
	return auth.user
		.split('@')[0]
		.replace(/[._-]/g, ' ')
		.replace(/\b\w/g, (c) => c.toUpperCase())
})
</script>
