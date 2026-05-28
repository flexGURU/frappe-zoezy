<template>
	<div class="flex-1 overflow-y-auto px-5 md:px-8 py-6 pb-24 md:pb-6">
		<!-- Loading -->
		<div v-if="!userStore.user" class="flex items-center justify-center py-24 text-gray-500">
			<LoadingIndicator class="w-6 h-6 mr-3" />
			<span class="text-base">Loading profile...</span>
		</div>

		<div v-else class="max-w-xl">
			<!-- Avatar card -->
			<div
				class="bg-white rounded-2xl border border-gray-200 p-6 mb-5 flex items-center gap-5"
			>
				<div
					class="h-16 w-16 rounded-full bg-blue-600 text-white font-bold text-2xl flex items-center justify-center shrink-0"
				>
					{{ initials }}
				</div>
				<div class="min-w-0">
					<h2 class="text-xl font-bold text-gray-900">{{ fullName }}</h2>
					<p class="text-base text-gray-500 mt-0.5">{{ userStore.user.email }}</p>
				</div>
			</div>

			<!-- Details card -->
			<div class="bg-white rounded-2xl border border-gray-200 overflow-hidden">
				<div class="px-6 py-4 border-b border-gray-100">
					<h3 class="text-base font-bold text-gray-900">Personal Details</h3>
				</div>
				<div class="divide-y divide-gray-100">
					<div
						v-for="field in fields"
						:key="field.label"
						class="px-6 py-4 flex items-center justify-between gap-4"
					>
						<p class="text-sm font-semibold text-gray-500 shrink-0 w-28">
							{{ field.label }}
						</p>
						<p class="text-base text-gray-900 text-right truncate">
							{{ field.value || '—' }}
						</p>
					</div>
				</div>
			</div>
		</div>
	</div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { LoadingIndicator } from 'frappe-ui'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

onMounted(() => {
	if (!userStore.user) userStore.fetchUserResource.fetch()
})

const fullName = computed(() => {
	if (!userStore.user) return ''
	return [userStore.user.first_name, userStore.user.last_name].filter(Boolean).join(' ')
})

const initials = computed(() =>
	fullName.value
		.split(' ')
		.slice(0, 2)
		.map((w) => w[0]?.toUpperCase())
		.join(''),
)

const fields = computed(() => {
	const u = userStore.user
	if (!u) return []
	return [
		{ label: 'First Name', value: u.first_name },
		{ label: 'Last Name', value: u.last_name },
		{ label: 'Email', value: u.email },
		{ label: 'Phone', value: u.phone },
	]
})
</script>
