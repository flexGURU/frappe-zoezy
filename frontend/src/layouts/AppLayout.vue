<script setup lang="ts">
import { Avatar } from "frappe-ui";
import { computed } from "vue";
import { useRoute } from "vue-router";

import BrandMark from "@/components/BrandMark.vue";
import { useProfile } from "@/data/resources";

const route = useRoute();
const profile = useProfile();

const tabs = [
	{ label: "Today", icon: "lucide-house", to: { name: "Today" } },
	{ label: "Plan", icon: "lucide-dumbbell", to: { name: "Plan" } },
	{ label: "Billing", icon: "lucide-wallet", to: { name: "Billing" } },
	{ label: "Profile", icon: "lucide-circle-user-round", to: { name: "Profile" } },
] as const;

const activeTab = computed(() => route.name);
</script>

<template>
	<div class="min-h-dvh md:flex">
		<aside
			class="sticky top-0 hidden h-dvh w-64 shrink-0 flex-col border-r border-outline-gray-1 bg-surface-base px-4 py-6 md:flex"
		>
			<BrandMark class="px-2" />

			<nav class="mt-10 flex flex-col gap-1" aria-label="Main">
				<RouterLink
					v-for="tab in tabs"
					:key="tab.label"
					:to="tab.to"
					class="flex items-center gap-3 rounded-[14px] px-3 py-2.5 text-base-medium transition-colors"
					:class="
						activeTab === tab.to.name
							? 'bg-night text-white'
							: 'text-ink-gray-6 hover:bg-surface-gray-2 hover:text-ink-gray-9'
					"
				>
					<span
						:class="[tab.icon, activeTab === tab.to.name ? 'text-volt' : '']"
						class="size-5"
					/>
					{{ tab.label }}
				</RouterLink>
			</nav>

			<RouterLink
				:to="{ name: 'Profile' }"
				class="mt-auto flex items-center gap-3 rounded-[16px] p-2 hover:bg-surface-gray-2"
			>
				<Avatar
					:label="profile.data?.full_name"
					:image="profile.data?.image ?? undefined"
					size="lg"
				/>
				<div class="min-w-0">
					<p class="truncate text-sm-semibold text-ink-gray-9">
						{{ profile.data?.full_name }}
					</p>
					<p class="truncate text-xs text-ink-gray-5">{{ profile.data?.email }}</p>
				</div>
			</RouterLink>
		</aside>

		<main class="min-w-0 flex-1 pb-28 md:pb-12">
			<div class="mx-auto w-full max-w-5xl px-4 pt-5 sm:px-6 md:pt-10">
				<RouterView />
			</div>
		</main>

		<nav
			class="pb-safe fixed inset-x-0 bottom-0 z-20 border-t border-outline-gray-1 bg-surface-base/90 backdrop-blur-lg md:hidden"
			aria-label="Main"
		>
			<div class="mx-auto grid max-w-md grid-cols-4 px-2 pt-2">
				<RouterLink
					v-for="tab in tabs"
					:key="tab.label"
					:to="tab.to"
					class="flex flex-col items-center gap-1 pb-2"
					:aria-current="activeTab === tab.to.name ? 'page' : undefined"
				>
					<span
						class="grid h-8 w-14 place-items-center rounded-full transition-colors"
						:class="
							activeTab === tab.to.name ? 'bg-night text-volt' : 'text-ink-gray-5'
						"
					>
						<span :class="tab.icon" class="size-5" />
					</span>
					<span
						class="text-2xs"
						:class="
							activeTab === tab.to.name
								? 'font-semibold text-ink-gray-9'
								: 'text-ink-gray-5'
						"
					>
						{{ tab.label }}
					</span>
				</RouterLink>
			</div>
		</nav>
	</div>
</template>
