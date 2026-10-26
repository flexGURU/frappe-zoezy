<script setup lang="ts">
import { Avatar, BottomSheet, Button, dialog } from "frappe-ui";
import { computed, ref, watch } from "vue";
import { useRoute } from "vue-router";

import BrandMark from "@/components/BrandMark.vue";
import ThemeSwitcher from "@/components/ThemeSwitcher.vue";
import { useProfile } from "@/data/resources";
import { session } from "@/data/session";
import { NAV } from "./nav";

const route = useRoute();
const profile = useProfile();
const menuOpen = ref(false);

const activeSection = computed(() =>
	NAV.find((s) => s.items.some((i) => route.matched.some((m) => m.name === i.to.name)))
);
const isActive = (name: string) => route.matched.some((m) => m.name === name);

watch(
	() => route.fullPath,
	() => (menuOpen.value = false)
);

function logout() {
	dialog.confirm({
		title: "Log out?",
		confirmLabel: "Log out",
		onConfirm: () => session.logout(),
	});
}
</script>

<template>
	<div class="min-h-dvh md:flex">
		<aside
			class="sticky top-0 hidden h-dvh w-64 shrink-0 flex-col overflow-y-auto border-r border-outline-gray-1 bg-surface-base px-3 py-5 md:flex"
		>
			<div class="flex items-center justify-between px-2">
				<BrandMark />
				<span class="rounded-full bg-night px-2 py-0.5 text-2xs-semibold text-volt"
					>Trainer</span
				>
			</div>

			<nav class="mt-6 space-y-5" aria-label="Back office">
				<section v-for="section in NAV" :key="section.label">
					<p class="eyebrow mb-1 flex items-center gap-2 px-3 text-ink-gray-5">
						<span :class="section.icon" class="size-3.5" /> {{ section.label }}
					</p>
					<RouterLink
						v-for="item in section.items"
						:key="item.label"
						:to="item.to"
						class="flex items-center gap-3 rounded-[12px] px-3 py-2 text-base-medium transition-colors"
						:class="
							isActive(item.to.name)
								? 'bg-night text-white dark:bg-volt dark:text-volt-ink'
								: 'text-ink-gray-6 hover:bg-surface-gray-2 hover:text-ink-gray-9'
						"
					>
						<span
							:class="[
								item.icon,
								isActive(item.to.name) ? 'text-volt dark:text-volt-ink' : '',
							]"
							class="size-4"
						/>
						{{ item.label }}
					</RouterLink>
				</section>
			</nav>

			<div class="mt-auto space-y-2 pt-6">
				<ThemeSwitcher />
				<a
					v-if="profile.data?.is_admin"
					href="/desk/zoezy"
					class="flex items-center gap-3 rounded-[12px] px-3 py-2 text-sm text-ink-gray-6 hover:bg-surface-gray-2"
				>
					<span class="lucide-wrench size-4" /> Open desk
				</a>
				<button
					type="button"
					class="flex w-full items-center gap-3 rounded-[16px] p-2 text-left hover:bg-surface-gray-2"
					@click="logout"
				>
					<Avatar
						:label="profile.data?.full_name"
						:image="profile.data?.image ?? undefined"
						size="lg"
					/>
					<div class="min-w-0 flex-1">
						<p class="truncate text-sm-semibold text-ink-gray-9">
							{{ profile.data?.full_name }}
						</p>
						<p class="truncate text-xs text-ink-gray-5">Log out</p>
					</div>
					<span class="lucide-log-out size-4 text-ink-gray-5" />
				</button>
			</div>
		</aside>

		<header
			class="sticky top-0 z-20 flex items-center justify-between border-b border-outline-gray-1 bg-surface-base/90 px-4 py-3 backdrop-blur-lg md:hidden"
		>
			<BrandMark />
			<Button
				:label="activeSection?.label ?? 'Menu'"
				icon-left="lucide-menu"
				variant="subtle"
				@click="menuOpen = true"
			/>
		</header>

		<BottomSheet v-model:open="menuOpen" title="Back office">
			<nav class="space-y-4 px-4 pb-6">
				<section v-for="section in NAV" :key="section.label">
					<p class="eyebrow mb-2 text-ink-gray-5">{{ section.label }}</p>
					<div class="grid grid-cols-3 gap-2">
						<RouterLink
							v-for="item in section.items"
							:key="item.label"
							:to="item.to"
							class="flex flex-col items-center gap-1.5 rounded-[16px] p-3 text-center text-xs-medium"
							:class="
								isActive(item.to.name)
									? 'bg-night text-white dark:bg-volt dark:text-volt-ink'
									: 'bg-surface-gray-2 text-ink-gray-7'
							"
						>
							<span
								:class="[
									item.icon,
									isActive(item.to.name) ? 'text-volt dark:text-volt-ink' : '',
								]"
								class="size-5"
							/>
							{{ item.label }}
						</RouterLink>
					</div>
				</section>
				<section>
					<p class="eyebrow mb-2 text-ink-gray-5">Appearance</p>
					<ThemeSwitcher />
				</section>
				<Button
					class="w-full"
					theme="red"
					icon-left="lucide-log-out"
					label="Log out"
					@click="logout"
				/>
			</nav>
		</BottomSheet>

		<main class="min-w-0 flex-1 pb-16">
			<div class="mx-auto w-full max-w-6xl px-4 pt-5 sm:px-6 md:pt-8">
				<RouterView />
			</div>
		</main>
	</div>
</template>
