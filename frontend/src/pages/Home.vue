<template>
	<div class="min-h-screen bg-surface-gray-1">
		<!-- Nav -->
		<nav
			class="bg-surface-white border-b border-outline-gray-2 px-4 sm:px-6 py-3 flex items-center justify-between sticky top-0 z-10"
		>
			<span class="font-bold text-ink-blue-3 text-lg tracking-tight">Zoezy</span>
			<div class="flex items-center gap-2">
				<span class="text-sm text-ink-gray-6 hidden sm:block">
					{{ userDetails.data?.first_name }} {{ userDetails.data?.last_name }}
				</span>
				<button
					@click="toggleTheme()"
					class="w-8 h-8 rounded-lg flex items-center justify-center text-ink-gray-6 hover:bg-surface-gray-2 transition-colors"
					:title="currentTheme === 'dark' ? 'Switch to light' : 'Switch to dark'"
				>
					<FeatherIcon
						:name="currentTheme === 'dark' ? 'sun' : 'moon'"
						class="w-4 h-4"
					/>
				</button>
				<Button
					size="sm"
					variant="solid"
					theme="red"
					@click="session.logout.submit()"
					:loading="session.logout.loading"
				>
					Logout
				</Button>
			</div>
		</nav>

		<div class="max-w-4xl mx-auto px-4 py-6 sm:py-8 space-y-5">
			<!-- Greeting -->
			<div>
				<h2 class="text-xl sm:text-2xl font-bold text-ink-gray-9">
					Good {{ timeOfDay }}, {{ userDetails.data?.first_name || "..." }}!
				</h2>
				<p class="text-ink-gray-6 text-sm mt-0.5">{{ formattedToday }}</p>
			</div>

			<!-- Today hero card — always blue, content varies -->
			<div class="rounded-2xl bg-surface-blue-3 p-5 sm:p-6 space-y-4">
				<div class="flex items-start justify-between gap-3">
					<div class="min-w-0">
						<p class="text-ink-blue-1 text-xs font-semibold uppercase tracking-widest">
							Today's Workout
						</p>
						<h3 class="text-xl sm:text-2xl font-bold text-ink-white mt-0.5 truncate">
							{{ todayDayName }}
						</h3>
					</div>
					<div
						class="bg-white/10 rounded-xl px-3 sm:px-5 py-2 sm:py-3 text-center shrink-0"
					>
						<template v-if="workoutLogs.loading">
							<Spinner class="text-white mx-auto" />
						</template>
						<template v-else>
							<p class="text-2xl sm:text-3xl font-bold text-ink-white">
								{{ todayWorkouts.length }}
							</p>
							<p class="text-ink-blue-1 text-xs mt-0.5">
								Session{{ todayWorkouts.length !== 1 ? "s" : "" }}
							</p>
						</template>
					</div>
				</div>

				<div v-if="workoutLogs.loading" class="flex justify-center py-4">
					<Spinner class="text-white" />
				</div>

				<div
					v-else-if="todayWorkouts.length === 0"
					class="flex flex-col items-center gap-2 py-4 text-center"
				>
					<span class="text-4xl">🌙</span>
					<p class="font-semibold text-ink-white">Rest Day</p>
					<p class="text-ink-blue-1 text-sm">Recovery is part of the process.</p>
				</div>

				<div v-else class="space-y-3">
					<div
						v-for="log in todayWorkouts"
						:key="log.category"
						class="bg-white/10 rounded-xl p-3 sm:p-4"
					>
						<div class="flex items-center justify-between mb-2">
							<span class="font-semibold text-ink-white">{{ log.category }}</span>
							<span class="text-ink-blue-1 text-xs shrink-0 ml-2">
								{{ log.exercises.length }} exercise{{
									log.exercises.length !== 1 ? "s" : ""
								}}
							</span>
						</div>
						<div class="space-y-1.5">
							<div
								v-for="ex in log.exercises"
								:key="ex.exercise"
								class="flex justify-between text-sm gap-2"
							>
								<span class="text-ink-white truncate">{{ ex.exercise }}</span>
								<span class="text-ink-blue-1 font-medium tabular-nums shrink-0">
									{{ ex.sets }}&thinsp;×&thinsp;{{ ex.rep_range }} reps
								</span>
							</div>
						</div>
					</div>
				</div>
			</div>

			<!-- Weekly Schedule -->
			<div class="bg-surface-white rounded-2xl border border-outline-gray-2 p-4 sm:p-5">
				<p class="font-semibold text-ink-gray-9 mb-4">Weekly Schedule</p>
				<div class="grid grid-cols-7 gap-1">
					<button
						v-for="day in weekDays"
						:key="day.name"
						@click="openDayDialog(day)"
						class="flex flex-col items-center rounded-xl py-2 sm:py-3 px-0.5 transition-all"
						:class="day.isToday ? 'bg-surface-blue-3' : 'hover:bg-surface-gray-2'"
					>
						<span
							class="text-xs font-medium mb-1.5"
							:class="day.isToday ? 'text-ink-white' : 'text-ink-gray-6'"
						>
							{{ day.short }}
						</span>
						<div
							class="w-7 h-7 sm:w-8 sm:h-8 rounded-full flex items-center justify-center text-xs sm:text-sm font-bold"
							:class="day.isToday ? 'bg-white/20 text-ink-white' : 'text-ink-gray-8'"
						>
							{{ day.date }}
						</div>
						<div
							class="mt-2 w-1.5 h-1.5 rounded-full"
							:class="
								hasWorkout(day.name)
									? day.isToday
										? 'bg-white'
										: 'bg-surface-blue-3'
									: 'bg-transparent'
							"
						></div>
					</button>
				</div>
			</div>

			<!-- Subscription + Invoices -->
			<div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
				<!-- Current Subscription -->
				<div class="bg-surface-white rounded-2xl border border-outline-gray-2 p-4 sm:p-5">
					<p class="font-semibold text-ink-gray-9 mb-4">Current Subscription</p>
					<div v-if="subscriptions.loading" class="flex justify-center py-4">
						<Spinner />
					</div>
					<p v-else-if="!activeSubscription" class="text-ink-gray-6 text-sm italic">
						No active subscription.
					</p>
					<div v-else class="space-y-3">
						<div class="flex items-start justify-between gap-2">
							<div class="min-w-0">
								<p class="font-semibold text-ink-gray-9 truncate">
									{{ activeSubscription.package_name }}
								</p>
								<p class="text-xs text-ink-gray-5 mt-0.5">
									{{ formatDate(activeSubscription.from_date) }} –
									{{ formatDate(activeSubscription.to_date) }}
								</p>
							</div>
							<Badge
								:label="activeSubscription.status"
								:theme="activeSubscription.status === 'Active' ? 'green' : 'gray'"
								class="shrink-0"
							/>
						</div>
						<div class="pt-3 border-t border-outline-gray-1">
							<p class="text-xs text-ink-gray-5 mb-0.5">Monthly Rate</p>
							<p class="text-xl sm:text-2xl font-bold text-ink-gray-9">
								{{ formatCurrency(activeSubscription.unit_price) }}
							</p>
						</div>
					</div>
				</div>

				<!-- Recent Invoices -->
				<div class="bg-surface-white rounded-2xl border border-outline-gray-2 p-4 sm:p-5">
					<p class="font-semibold text-ink-gray-9 mb-4">Recent Invoices</p>
					<div v-if="invoices.loading" class="flex justify-center py-4">
						<Spinner />
					</div>
					<p v-else-if="!invoices.data?.length" class="text-ink-gray-6 text-sm italic">
						No invoices yet.
					</p>
					<div v-else class="divide-y divide-outline-gray-1">
						<div
							v-for="inv in invoices.data.slice(0, 4)"
							:key="inv.name"
							class="flex items-center justify-between py-2.5 gap-2 first:pt-0 last:pb-0"
						>
							<div class="min-w-0">
								<p class="text-sm font-medium text-ink-gray-8 truncate">
									{{ inv.name }}
								</p>
								<p class="text-xs text-ink-gray-5">
									{{ formatDate(inv.posting_date) }}
								</p>
							</div>
							<div class="flex items-center gap-2 shrink-0">
								<span class="text-sm font-semibold text-ink-gray-9">
									{{ formatCurrency(inv.total) }}
								</span>
								<Badge :label="inv.status" :theme="invoiceTheme(inv.status)" />
							</div>
						</div>
					</div>
				</div>
			</div>
		</div>

		<!-- Day Detail Dialog -->
		<Dialog
			v-model="showDayDialog"
			:options="{
				title: selectedDay ? selectedDay.name + ' Workout' : '',
				size: '2xl',
			}"
		>
			<template #body-content>
				<div v-if="!selectedDayWorkouts.length" class="py-6 text-center text-ink-gray-5">
					No workout scheduled for {{ selectedDay?.name }}.
				</div>
				<div v-else class="space-y-4 pb-2 lg:max-h-[78vh] lg:overflow-y-auto lg:pr-1">
					<div
						v-for="log in selectedDayWorkouts"
						:key="log.category"
						class="border border-outline-gray-2 rounded-xl p-4"
					>
						<p class="font-semibold text-ink-gray-9 mb-3">{{ log.category }}</p>
						<div class="divide-y divide-outline-gray-1">
							<div
								v-for="(ex, i) in log.exercises"
								:key="ex.exercise"
								class="py-2 first:pt-0 last:pb-0"
							>
								<button
									type="button"
									class="flex w-full items-center justify-between gap-2 text-left text-sm"
									:class="hasDetails(ex) ? 'cursor-pointer' : 'cursor-default'"
									@click="hasDetails(ex) && toggleExercise(log.category, i)"
								>
									<span class="flex items-center gap-1.5 text-ink-gray-8">
										{{ ex.exercise }}
										<FeatherIcon
											v-if="hasDetails(ex)"
											:name="
												isExpanded(log.category, i)
													? 'chevron-up'
													: 'chevron-down'
											"
											class="h-3.5 w-3.5 text-ink-gray-5"
										/>
									</span>
									<span
										class="text-ink-gray-5 font-medium tabular-nums shrink-0"
									>
										{{ ex.sets }} × {{ ex.rep_range }} reps
									</span>
								</button>

								<!-- Weight -->
								<div
									v-if="ex.progressive_overload"
									class="mt-1.5 flex flex-wrap items-center gap-1.5 text-xs"
								>
									<span
										class="inline-flex items-center gap-1 rounded-md bg-surface-green-2 px-1.5 py-0.5 font-medium text-ink-green-3"
									>
										<FeatherIcon name="trending-up" class="h-3 w-3" />
										Progressive
									</span>
									<span class="text-ink-gray-6 tabular-nums">
										Start
										<span class="font-semibold text-ink-gray-8"
											>{{ ex.start_weight }} kg</span
										>
									</span>
									<span class="text-ink-gray-4">·</span>
									<span class="text-ink-gray-6 tabular-nums">
										{{ ex.sets }} set{{ ex.sets !== 1 ? "s" : "" }}
									</span>
									<span class="text-ink-gray-4">·</span>
									<span class="text-ink-gray-6 tabular-nums">
										Final
										<span class="font-semibold text-ink-gray-8"
											>{{ ex.final_weight }} kg</span
										>
									</span>
								</div>
								<div
									v-else-if="ex.stagnant_weight"
									class="mt-1.5 text-xs text-ink-gray-6 tabular-nums"
								>
									<span class="font-semibold text-ink-gray-8"
										>{{ ex.stagnant_weight }} kg</span
									>
								</div>

								<div
									v-if="hasDetails(ex) && isExpanded(log.category, i)"
									class="mt-3 space-y-3"
								>
									<p
										v-if="ex.description"
										class="text-sm text-ink-gray-6 whitespace-pre-line"
									>
										{{ ex.description }}
									</p>
									<VideoEmbed
										v-if="ex.video_url"
										:url="ex.video_url"
										:title="ex.exercise"
									/>
								</div>
							</div>
						</div>
					</div>
				</div>
			</template>
		</Dialog>
	</div>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import { createResource, Toast, useTheme } from "frappe-ui";
import { Badge, Button, Dialog, FeatherIcon, Spinner } from "frappe-ui";
import { session } from "../data/session";
import VideoEmbed from "../components/VideoEmbed.vue";

const { currentTheme, toggleTheme } = useTheme();

const userDetails = createResource({ url: "zoezy.api.user.get_user_details", auto: true });
const workoutLogs = createResource({ url: "zoezy.api.user.get_client_workout_logs", auto: true });
const subscriptions = createResource({
	url: "zoezy.api.user.get_client_subscriptions",
	auto: true,
});
const invoices = createResource({ url: "zoezy.api.user.get_client_invoices", auto: true });

const today = new Date();
const DAY_NAMES = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
const todayDayName = DAY_NAMES[today.getDay()];

const timeOfDay = computed(() => {
	const h = today.getHours();
	if (h < 12) return "morning";
	if (h < 17) return "afternoon";
	return "evening";
});

const formattedToday = today.toLocaleDateString("en-US", {
	weekday: "long",
	year: "numeric",
	month: "long",
	day: "numeric",
});

const weekDays = computed(() => {
	const dow = today.getDay();
	const monday = new Date(today);
	monday.setDate(today.getDate() - (dow === 0 ? 6 : dow - 1));

	return ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"].map(
		(name, i) => {
			const d = new Date(monday);
			d.setDate(monday.getDate() + i);
			return {
				name,
				short: name.slice(0, 3),
				date: d.getDate(),
				isToday: d.toDateString() === today.toDateString(),
			};
		},
	);
});

const todayWorkouts = computed(() => {
	if (!workoutLogs.data) return [];
	return workoutLogs.data.filter((l) => l.day === todayDayName);
});

function hasWorkout(dayName) {
	if (!workoutLogs.data) return false;
	return workoutLogs.data.some((l) => l.day === dayName);
}

const activeSubscription = computed(() => {
	if (!subscriptions.data?.length) return null;
	return subscriptions.data.find((s) => s.status === "Active") ?? subscriptions.data[0];
});

const showDayDialog = ref(false);
const selectedDay = ref(null);

const selectedDayWorkouts = computed(() => {
	if (!selectedDay.value || !workoutLogs.data) return [];
	return workoutLogs.data.filter((l) => l.day === selectedDay.value.name);
});

const expandedExercises = ref(new Set());

function openDayDialog(day) {
	selectedDay.value = day;
	expandedExercises.value = new Set();
	showDayDialog.value = true;
}

function hasDetails(ex) {
	return Boolean(ex.description || ex.video_url);
}

function isExpanded(category, index) {
	return expandedExercises.value.has(`${category}-${index}`);
}

function toggleExercise(category, index) {
	const key = `${category}-${index}`;
	const next = new Set(expandedExercises.value);
	next.has(key) ? next.delete(key) : next.add(key);
	expandedExercises.value = next;
}

function formatDate(str) {
	if (!str) return "–";
	return new Date(str).toLocaleDateString("en-US", {
		month: "short",
		day: "numeric",
		year: "numeric",
	});
}

function formatCurrency(val) {
	if (val == null) return "–";
	return new Intl.NumberFormat("en-KE", { style: "currency", currency: "KES" }).format(val);
}

function invoiceTheme(status) {
	return { Paid: "green", Overdue: "red", Unpaid: "orange" }[status] ?? "gray";
}
</script>
