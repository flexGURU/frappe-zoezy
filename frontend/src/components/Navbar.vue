<template>
	<header class="bg-white border-b border-gray-200 px-5 md:px-8 py-3 shrink-0">
		<div class="flex items-center justify-between gap-4">
			<!-- Left: page title -->
			<div class="min-w-0">
				<h1 class="text-base md:text-xl font-bold text-gray-900 truncate">
					{{ pageTitle }}
				</h1>
				<p class="text-xs md:text-sm text-gray-500 mt-0.5 hidden sm:block">
					{{ fullDate }}
				</p>
			</div>

			<!-- Right: day badge + avatar -->
			<div class="flex items-center gap-3 shrink-0">
				<div class="relative" ref="avatarRef">
					<button
						@click="menuOpen = !menuOpen"
						class="h-9 w-9 rounded-full bg-blue-600 text-white font-bold text-sm flex items-center justify-center hover:bg-blue-700 transition-colors"
					>
						{{ userInitial }}
					</button>

					<Transition name="dropdown">
						<div
							v-if="menuOpen"
							class="absolute right-0 mt-2 w-56 bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden z-50"
						>
							<div class="px-4 py-3 border-b border-gray-100">
								<p class="text-sm font-semibold text-gray-900">
									{{ toRaw(user)?.full_name }}
								</p>
								<p class="text-xs truncate">
									{{ toRaw(user)?.email }}
								</p>
							</div>
							<button
								@click="logout"
								class="w-full flex items-center gap-3 px-4 py-3 text-sm text-red-600 hover:bg-red-50 transition-colors font-medium"
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
								Sign out
							</button>
						</div>
					</Transition>
				</div>
			</div>
		</div>
	</header>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch, toRaw } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useUserStore } from '@/stores/user'
import { storeToRefs } from 'pinia'

const auth = useAuthStore()
const userStore = useUserStore()
const { user } = storeToRefs(userStore)
const route = useRoute()
const menuOpen = ref(false)
const avatarRef = ref(null)

function onClickOutside(e) {
	if (avatarRef.value && !avatarRef.value.contains(e.target)) menuOpen.value = false
}
onMounted(() => document.addEventListener('mousedown', onClickOutside))
onBeforeUnmount(() => document.removeEventListener('mousedown', onClickOutside))

function logout() {
	menuOpen.value = false
	auth.logout()
}

const now = new Date()
const DAYS = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
const todayName = DAYS[now.getDay()]
const fullDate = now.toLocaleDateString('en-US', {
	weekday: 'long',
	month: 'long',
	day: 'numeric',
})

const userInitial = computed(() => toRaw(user.value)?.first_name?.charAt(0).toUpperCase())
const pageTitle = computed(() => route.meta?.title || route.name || 'Zoezy')
</script>

<style scoped>
.dropdown-enter-active,
.dropdown-leave-active {
	transition:
		opacity 0.15s ease,
		transform 0.15s ease;
}
.dropdown-enter-from,
.dropdown-leave-to {
	opacity: 0;
	transform: translateY(-6px);
}
</style>
