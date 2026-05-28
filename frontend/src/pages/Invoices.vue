<template>
	<div class="flex-1 flex flex-col overflow-hidden min-w-0">
		<main class="flex-1 overflow-y-auto px-5 md:px-8 py-6 pb-24 md:pb-6">
			<!-- Loading -->
			<div
				v-if="invoices.loading"
				class="flex items-center justify-center py-24 text-gray-500"
			>
				<LoadingIndicator class="w-6 h-6 mr-3" />
				<span class="text-base">Loading invoices...</span>
			</div>

			<template v-else>
				<!-- Empty -->
				<div
					v-if="!invoices.data?.length"
					class="bg-white border border-gray-200 rounded-2xl p-10 text-center max-w-lg mx-auto mt-8"
				>
					<p class="text-lg font-semibold text-gray-800">No invoices yet</p>
					<p class="text-base text-gray-500 mt-1">
						Your invoices will appear here once generated.
					</p>
				</div>

				<!-- Table -->
				<div v-else class="max-w-3xl">
					<p class="text-sm text-gray-500 mb-3">
						{{ invoices.data.length }} invoice{{
							invoices.data.length !== 1 ? 's' : ''
						}}
					</p>

					<div class="bg-white rounded-xl border border-gray-200 overflow-hidden">
						<!-- Header -->
						<div
							class="grid grid-cols-12 px-5 py-3 bg-gray-50 border-b border-gray-200"
						>
							<div
								class="col-span-4 text-xs font-bold text-gray-600 uppercase tracking-wide"
							>
								Invoice
							</div>
							<div
								class="col-span-3 text-xs font-bold text-gray-600 uppercase tracking-wide hidden sm:block"
							>
								Date
							</div>
							<div
								class="col-span-3 text-xs font-bold text-gray-600 uppercase tracking-wide"
							>
								Status
							</div>
							<div
								class="col-span-2 text-xs font-bold text-gray-600 uppercase tracking-wide text-right"
							>
								Total
							</div>
						</div>

						<!-- Rows -->
						<div
							v-for="inv in invoices.data"
							:key="inv.name"
							@click="openInvoice(inv)"
							class="grid grid-cols-12 px-5 py-4 border-b border-gray-100 last:border-0 items-center cursor-pointer hover:bg-gray-50 transition-colors"
						>
							<!-- Invoice name -->
							<div class="col-span-4 min-w-0">
								<p class="font-semibold text-base text-gray-900 truncate">
									{{ inv.name }}
								</p>
								<p
									v-if="inv.subscription"
									class="text-xs text-gray-500 mt-0.5 truncate"
								>
									{{ inv.subscription }}
								</p>
							</div>
							<!-- Date -->
							<div class="col-span-3 hidden sm:block">
								<p class="text-base text-gray-700">
									{{ formatDate(inv.posting_date) }}
								</p>
							</div>
							<!-- Status badge -->
							<div class="col-span-3">
								<span
									class="inline-block text-xs font-bold px-2.5 py-1 rounded-lg"
									:class="statusClass(inv.status)"
								>
									{{ inv.status || 'Unpaid' }}
								</span>
							</div>
							<!-- Total -->
							<div class="col-span-2 text-right">
								<p class="text-base font-bold text-gray-900">
									{{ formatAmount(inv.total) }}
								</p>
							</div>
						</div>
					</div>
				</div>
			</template>
		</main>

		<!-- Invoice detail modal -->
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
							<p
								class="text-xs font-bold text-gray-500 uppercase tracking-wide mb-1"
							>
								Invoice
							</p>
							<h3 class="text-xl font-bold text-gray-900">{{ selected.name }}</h3>
							<div class="flex items-center gap-3 mt-2">
								<span
									class="text-xs font-bold px-2.5 py-1 rounded-lg"
									:class="statusClass(selected.status)"
								>
									{{ selected.status || 'Unpaid' }}
								</span>
								<span class="text-sm text-gray-500">{{
									formatDate(selected.posting_date)
								}}</span>
							</div>
						</div>
						<button
							@click="selected = null"
							class="text-gray-400 hover:text-gray-700 text-2xl leading-none shrink-0 mt-1"
						>
							&times;
						</button>
					</div>

					<!-- Packages list -->
					<div class="px-6 py-4 space-y-2 max-h-64 overflow-y-auto">
						<p class="text-xs font-bold text-gray-500 uppercase tracking-wide mb-3">
							Packages
						</p>
						<div
							v-for="pkg in selected.packages"
							:key="pkg.package_name"
							class="flex items-center justify-between p-3 rounded-xl bg-gray-50"
						>
							<p class="font-semibold text-base text-gray-900">
								{{ pkg.package_name }}
							</p>
							<p class="text-base font-bold text-gray-800">
								{{ formatAmount(pkg.unit_price) }}
							</p>
						</div>
						<p
							v-if="!selected.packages?.length"
							class="text-sm text-gray-400 italic text-center py-2"
						>
							No packages listed
						</p>
					</div>

					<!-- Total footer -->
					<div
						class="px-6 py-4 border-t border-gray-200 flex items-center justify-between"
					>
						<p class="text-base font-semibold text-gray-700">Total</p>
						<p class="text-xl font-bold text-gray-900">
							{{ formatAmount(selected.total) }}
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

const invoices = createResource({
	url: 'zoezy.api.user.get_client_invoices',
	auto: true,
})

function openInvoice(inv) {
	selected.value = inv
}

function formatDate(dateStr) {
	if (!dateStr) return '—'
	return new Date(dateStr).toLocaleDateString('en-US', {
		year: 'numeric',
		month: 'short',
		day: 'numeric',
	})
}

function formatAmount(amount) {
	if (amount == null) return '—'
	return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(amount)
}

function statusClass(status) {
	if (status === 'Paid') return 'bg-green-100 text-green-800'
	if (status === 'Overdue') return 'bg-red-100 text-red-800'
	return 'bg-yellow-100 text-yellow-800'
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
