<template>
	<div class="flex flex-col flex-1 overflow-hidden min-w-0">
		<!-- Body -->
		<main class="flex-1 overflow-y-auto px-5 md:px-8 py-6 pb-24 md:pb-6">
			<!-- Loading -->
			<div
				v-if="workoutLogs.loading"
				class="flex items-center justify-center py-24 text-gray-500"
			>
				<LoadingIndicator class="w-6 h-6 mr-3" />
				<span class="text-base">Loading your schedule...</span>
			</div>

			<template v-else>
				<!-- Today's banner -->
				<div v-if="todayWorkouts.length" class="mb-6">
					<div class="bg-blue-600 text-white rounded-2xl p-5 md:p-6">
						<div class="flex items-start justify-between gap-4">
							<div class="min-w-0">
								<p
									class="text-blue-200 text-sm font-semibold uppercase tracking-wide mb-1"
								>
									Today · {{ todayName }}
								</p>
								<h2 class="text-xl md:text-2xl font-bold mb-2 truncate">
									{{ todayWorkouts.map((w) => w.category).join(' & ') }}
								</h2>
								<p class="text-blue-100 text-sm md:text-base">
									{{ todayTotalExercises }} exercise{{
										todayTotalExercises !== 1 ? 's' : ''
									}}
									&bull; {{ todayTotalSets }} sets
								</p>
							</div>
							<button
								@click="openLog(todayWorkouts[0])"
								class="shrink-0 bg-white text-blue-700 text-sm font-bold px-4 py-2.5 rounded-xl hover:bg-blue-50 transition-colors"
							>
								View
							</button>
						</div>
					</div>
				</div>
				<div
					v-else
					class="mb-6 bg-white border border-gray-200 rounded-2xl p-6 text-center"
				>
					<p class="text-lg font-semibold text-gray-800">Rest day — enjoy it!</p>
					<p class="text-base text-gray-500 mt-1">
						No sessions scheduled for {{ todayName }}.
					</p>
				</div>

				<!-- Weekly schedule -->
				<div class="max-w-2xl">
					<h2 class="text-base md:text-lg font-bold text-gray-900 mb-3">
						Weekly Schedule
					</h2>

					<p
						v-if="!workoutLogs.data?.length"
						class="text-base text-gray-500 py-8 text-center"
					>
						No workout schedule assigned yet.
					</p>

					<div v-else class="bg-white rounded-xl border border-gray-200 overflow-hidden">
						<!-- Header row -->
						<div
							class="grid grid-cols-10 px-4 md:px-5 py-3 bg-gray-50 border-b border-gray-200"
						>
							<div
								class="col-span-4 text-xs font-bold text-gray-600 uppercase tracking-wide"
							>
								Day
							</div>
							<div
								class="col-span-4 text-xs font-bold text-gray-600 uppercase tracking-wide"
							>
								Category
							</div>
							<div
								class="col-span-2 text-xs font-bold text-gray-600 uppercase tracking-wide text-right"
							>
								Sets
							</div>
						</div>

						<!-- Data rows -->
						<div
							v-for="log in sortedLogs"
							:key="log.day + log.category"
							@click="openLog(log)"
							class="grid grid-cols-10 px-4 md:px-5 py-4 border-b border-gray-100 last:border-0 items-center cursor-pointer transition-colors"
							:class="
								log.day === todayName
									? 'bg-blue-50 hover:bg-blue-100'
									: 'hover:bg-gray-50'
							"
						>
							<!-- Day -->
							<div class="col-span-4 flex items-center gap-2 min-w-0">
								<span
									class="font-semibold text-base truncate"
									:class="
										log.day === todayName ? 'text-blue-700' : 'text-gray-900'
									"
								>
									{{ log.day }}
								</span>
								<span
									v-if="log.day === todayName"
									class="hidden sm:inline text-xs bg-blue-600 text-white px-2 py-0.5 rounded-full font-semibold shrink-0"
								>
									Today
								</span>
							</div>
							<!-- Category -->
							<div class="col-span-4 min-w-0">
								<span
									class="inline-block text-sm font-semibold px-3 py-1 rounded-lg truncate max-w-full"
									:class="
										log.day === todayName
											? 'bg-blue-100 text-blue-800'
											: 'bg-gray-100 text-gray-800'
									"
								>
									{{ log.category }}
								</span>
							</div>
							<!-- Sets -->
							<div class="col-span-2 text-right">
								<span class="text-base font-bold text-gray-900">
									{{ log.exercises.reduce((s, e) => s + (e.sets || 0), 0) }}
								</span>
								<span class="text-xs text-gray-500 ml-1">sets</span>
							</div>
						</div>
					</div>
				</div>
			</template>
		</main>
	</div>

	<!-- Exercise detail modal -->
	<Transition name="fade">
		<div
			v-if="selectedLog"
			class="fixed inset-0 z-50 flex items-end sm:items-center justify-center px-4 pb-4 sm:pb-0"
		>
			<div class="absolute inset-0 bg-black/40" @click="selectedLog = null" />
			<div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-md overflow-hidden">
				<!-- Modal header -->
				<div
					class="px-6 py-5 border-b border-gray-200 flex items-start justify-between gap-4"
				>
					<div class="min-w-0">
						<p class="text-sm font-bold text-gray-500 uppercase tracking-wide mb-1">
							{{ selectedLog.day
							}}<span v-if="selectedLog.day === todayName" class="ml-2 text-blue-600"
								>· Today</span
							>
						</p>
						<h3 class="text-xl font-bold text-gray-900">
							{{ selectedLog.category }}
						</h3>
						<p class="text-base text-gray-600 mt-1">
							{{ selectedLog.exercises.length }} exercises &bull;
							{{ selectedLog.exercises.reduce((s, e) => s + (e.sets || 0), 0) }}
							sets
						</p>
					</div>
					<button
						@click="selectedLog = null"
						class="text-gray-400 hover:text-gray-700 text-2xl leading-none shrink-0 mt-1"
					>
						&times;
					</button>
				</div>
				<!-- Exercise list -->
				<div class="px-6 py-4 space-y-3 max-h-[60vh] overflow-y-auto">
					<div
						v-for="(ex, i) in selectedLog.exercises"
						:key="ex.exercise"
						class="flex items-center gap-4 p-4 rounded-xl bg-gray-50"
					>
						<div
							class="h-9 w-9 rounded-full bg-blue-600 text-white font-bold text-sm flex items-center justify-center shrink-0"
						>
							{{ i + 1 }}
						</div>
						<div class="flex-1 min-w-0">
							<p class="font-semibold text-base text-gray-900">
								{{ ex.exercise }}
							</p>
							<p v-if="ex.rep_range" class="text-sm text-gray-600 mt-0.5">
								{{ ex.rep_range }} reps per set
							</p>
						</div>
						<div class="text-right shrink-0">
							<p class="text-lg font-bold text-gray-900">{{ ex.sets }}</p>
							<p class="text-xs text-gray-500">sets</p>
						</div>
					</div>
				</div>
			</div>
		</div>
	</Transition>
</template>

<script setup>
import { ref, computed } from 'vue'
import { createResource, LoadingIndicator } from 'frappe-ui'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()

const displayName = computed(() => {
	if (!auth.user) return 'there'
	return auth.user
		.split('@')[0]
		.replace(/[._-]/g, ' ')
		.replace(/\b\w/g, (c) => c.toUpperCase())
})

const now = new Date()
const DAYS = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
const DAY_ORDER = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
const todayName = DAYS[now.getDay()]

const fullDate = now.toLocaleDateString('en-US', {
	weekday: 'long',
	year: 'numeric',
	month: 'long',
	day: 'numeric',
})
const hour = now.getHours()
const greeting = hour < 12 ? 'Good morning' : hour < 17 ? 'Good afternoon' : 'Good evening'

const workoutLogs = createResource({
	url: 'zoezy.api.user.get_client_workout_logs',
	auto: true,
	cache: 'workout_logs',
})

const sortedLogs = computed(() => {
	if (!workoutLogs.data) return []
	return [...workoutLogs.data].sort(
		(a, b) => DAY_ORDER.indexOf(a.day) - DAY_ORDER.indexOf(b.day),
	)
})

const todayWorkouts = computed(() => (workoutLogs.data ?? []).filter((l) => l.day === todayName))

const todayTotalExercises = computed(() =>
	todayWorkouts.value.reduce((s, l) => s + l.exercises.length, 0),
)

const todayTotalSets = computed(() =>
	todayWorkouts.value.reduce(
		(s, l) => s + l.exercises.reduce((ss, e) => ss + (e.sets || 0), 0),
		0,
	),
)

const selectedLog = ref(null)
function openLog(log) {
	selectedLog.value = log
}
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
	transition: opacity 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
	opacity: 0;
}
</style>
