<template>
	<div class="flex-1 flex flex-col overflow-hidden min-w-0">
		<main class="flex-1 overflow-y-auto px-5 md:px-8 py-6 pb-24 md:pb-6">
			<!-- Loading -->
			<div
				v-if="subscriptions.loading"
				class="flex items-center justify-center py-24 text-gray-500"
			>
				<LoadingIndicator class="w-6 h-6 mr-3" />
				<span class="text-base">Loading subscriptions...</span>
			</div>

			<template v-else>
				<!-- Empty -->
				<div
					v-if="!subscriptions.data?.length"
					class="bg-white border border-gray-200 rounded-2xl p-10 text-center max-w-lg mx-auto mt-8"
				>
					<p class="text-lg font-semibold text-gray-800">No subscriptions yet</p>
					<p class="text-base text-gray-500 mt-1">
						Your subscriptions will appear here once created.
					</p>
				</div>

				<!-- Cards grid -->
				<div v-else class="max-w-3xl space-y-4">
					<p class="text-gray-500 mb-1">
						{{ subscriptions.data.length }} subscription{{
							subscriptions.data.length !== 1 ? 's' : ''
						}}
					</p>

					<div
						v-for="sub in subscriptions.data"
						:key="sub.name"
						@click="openSubscription(sub)"
						class="bg-white rounded-xl border border-gray-200 p-5 cursor-pointer hover:shadow-md transition-shadow"
					>
						<!-- Top row: package name + status badge -->
						<div class="flex items-start justify-between gap-3 mb-3">
							<div class="min-w-0">
								<p class="font-bold text-gray-400 uppercase tracking-wide mb-0.5">
									{{ sub.name }}
								</p>
								<h3 class="text-lg font-bold text-gray-900 truncate">
									{{ sub.package_name || sub.package_type }}
								</h3>
							</div>
							<span
								class="shrink-0 inline-block font-bold px-2.5 py-1 rounded-lg"
								:class="statusClass(sub.status)"
							>
								{{ sub.status || 'Unknown' }}
							</span>
						</div>

						<!-- Date range -->
						<div class="flex items-center gap-4  text-gray-600">
							<div class="flex items-center gap-1.5">
								<span class="text-gray-400">Starts</span>
								<span class="font-semibold text-gray-800">{{
									formatDate(sub.from_date)
								}}</span>
							</div>
							<span class="text-gray-300">→</span>
							<div class="flex items-center gap-1.5">
								<span class="text-gray-400">Ends</span>
								<span class="font-semibold text-gray-800">{{
									formatDate(sub.to_date)
								}}</span>
							</div>
						</div>

						<!-- Items preview (first 3) -->
						<div v-if="sub.items?.length" class="mt-3 flex flex-wrap gap-1.5">
							<span
								v-for="item in sub.items.slice(0, 3)"
								:key="item"
								class="bg-gray-100 text-gray-700 rounded-lg px-2.5 py-1 font-medium"
							>
								{{ item }}
							</span>
							<span
								v-if="sub.items.length > 3"
								class="bg-gray-100 text-gray-400 rounded-lg px-2.5 py-1"
							>
								+{{ sub.items.length - 3 }} more
							</span>
						</div>

						<!-- Unit price -->
						<div class="mt-3 flex items-center justify-end">
							<p class="text-base font-bold text-gray-900">
								{{ formatAmount(sub.unit_price) }}
							</p>
						</div>
					</div>
				</div>
			</template>
		</main>

		<!-- Detail modal -->
		<Transition name="fade">
			<div
				v-if="selected"
				class="fixed inset-0 z-50 flex items-end sm:items-center justify-center px-4 pb-4 sm:pb-0"
			>
				<div class="absolute inset-0 bg-black/40" @click="selected = null" />

				<div
					class="relative bg-white rounded-2xl shadow-2xl w-full max-w-md overflow-hidden"
				>
					<!-- Modal header -->
					<div
						class="px-6 py-5 border-b border-gray-200 flex items-start justify-between gap-4"
					>
						<div class="min-w-0">
							<p class="font-bold text-gray-500 uppercase tracking-wide mb-1">
								Subscription
							</p>
							<h3 class="text-xl font-bold text-gray-900">
								{{ selected.package_name || selected.package_type }}
							</h3>
							<div class="flex items-center gap-3 mt-2">
								<span
									class="font-bold px-2.5 py-1 rounded-lg"
									:class="statusClass(selected.status)"
								>
									{{ selected.status || 'Unknown' }}
								</span>
								<span class=" text-gray-500">{{ selected.name }}</span>
							</div>
						</div>
						<button
							@click="selected = null"
							class="text-gray-400 hover:text-gray-700 text-2xl leading-none shrink-0 mt-1"
						>
							&times;
						</button>
					</div>

					<!-- Dates section -->
					<div class="px-6 py-4 border-b border-gray-100 grid grid-cols-2 gap-4">
						<div>
							<p class="font-bold text-gray-400 uppercase tracking-wide mb-1">
								Starts
							</p>
							<p class="text-base font-semibold text-gray-900">
								{{ formatDate(selected.from_date) }}
							</p>
						</div>
						<div>
							<p class="font-bold text-gray-400 uppercase tracking-wide mb-1">
								Ends
							</p>
							<p class="text-base font-semibold text-gray-900">
								{{ formatDate(selected.to_date) }}
							</p>
						</div>
					</div>

					<!-- Package contents -->
					<div class="px-6 py-4 max-h-56 overflow-y-auto">
						<p class="font-bold text-gray-500 uppercase tracking-wide mb-3">
							Package Contents
						</p>
						<ul v-if="selected.items?.length" class="space-y-2">
							<li
								v-for="item in selected.items"
								:key="item"
								class="flex items-center gap-2 p-3 rounded-xl bg-gray-50"
							>
								<span class="w-2 h-2 rounded-full bg-green-400 shrink-0"></span>
								<p class="text-base text-gray-800 font-medium">{{ item }}</p>
							</li>
						</ul>
						<p v-else class=" text-gray-400 italic text-center py-2">
							No items listed for this package
						</p>
					</div>

					<!-- Price footer -->
					<div
						class="px-6 py-4 border-t border-gray-200 flex items-center justify-between"
					>
						<p class="text-base font-semibold text-gray-700">Package Price</p>
						<p class="text-xl font-bold text-gray-900">
							{{ formatAmount(selected.unit_price) }}
						</p>
					</div>
				</div>
			</div>
		</Transition>
	</div>
</template>

<script setup>
import { ref } from 'vue'
import { createResource, LoadingIndicator } from 'frappe-ui'

const selected = ref(null)

const subscriptions = createResource({
	url: 'zoezy.api.user.get_client_subscriptions',
	auto: true,
})

function openSubscription(sub) {
	selected.value = sub
}

function formatDate(dateStr) {
	if (!dateStr) return '—'
	const d = new Date(dateStr)
	return d.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
}

function formatAmount(amount) {
	if (amount == null) return '—'
	return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(amount)
}

function statusClass(status) {
	if (status === 'Active') return 'bg-green-100 text-green-700'
	if (status === 'Expired') return 'bg-red-100 text-red-700'
	return 'bg-gray-100 text-gray-600'
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
