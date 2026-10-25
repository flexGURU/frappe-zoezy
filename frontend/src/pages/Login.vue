<script setup lang="ts">
import {
	Button,
	ErrorMessage,
	type ErrorMessageValue,
	Password,
	TabButtons,
	TextInput,
	usePageMeta,
} from "frappe-ui";
import { reactive, ref } from "vue";

import BrandMark from "@/components/BrandMark.vue";
import { branding } from "@/data/branding";
import { session } from "@/data/session";

type Mode = "login" | "signup" | "done";

usePageMeta(() => ({ title: "Welcome" }));

const mode = ref<Mode>("login");
const loading = ref(false);
const error = ref<ErrorMessageValue>();

const login = reactive({ email: "", password: "" });
const signup = reactive({ first_name: "", last_name: "", email: "", phone: "" });

const tabs = [
	{ value: "login", label: "Log in" },
	{ value: "signup", label: "Sign up" },
];

function switchMode(next: Mode) {
	error.value = undefined;
	mode.value = next;
}

async function submit(action: () => Promise<unknown>, onSuccess?: () => void) {
	loading.value = true;
	error.value = undefined;
	try {
		await action();
		onSuccess?.();
	} catch (e) {
		error.value = e as Error;
	} finally {
		loading.value = false;
	}
}

const submitLogin = () => submit(() => session.login(login.email, login.password));
const submitSignup = () =>
	submit(
		() => session.signUp({ ...signup }),
		() => {
			login.email = signup.email;
			switchMode("done");
		}
	);

const highlights = [
	{ icon: "lucide-calendar-days", text: "Your weekly program, day by day" },
	{ icon: "lucide-trending-up", text: "Weights that climb with every set" },
	{ icon: "lucide-wallet", text: "Membership and invoices in one place" },
];
</script>

<template>
	<div class="grid min-h-dvh bg-surface-base lg:grid-cols-[1.1fr_1fr]">
		<section
			class="card-night relative flex flex-col overflow-hidden rounded-none px-6 pb-14 pt-8 sm:px-10 lg:p-14"
		>
			<BrandMark inverted />

			<div class="relative z-10 mt-12 lg:mt-auto">
				<p class="eyebrow text-volt">Personal training, organised</p>
				<h1
					class="mt-4 font-display text-[44px] font-bold leading-[1.02] tracking-tight sm:text-[64px] lg:text-[80px]"
				>
					Train with<br />
					<span class="text-volt">intent.</span>
				</h1>
				<ul class="mt-8 hidden space-y-3 lg:block">
					<li
						v-for="h in highlights"
						:key="h.text"
						class="flex items-center gap-3 text-lg text-white/70"
					>
						<span
							class="grid size-9 place-items-center rounded-full bg-white/10 text-volt"
						>
							<span :class="h.icon" class="size-4" />
						</span>
						{{ h.text }}
					</li>
				</ul>
			</div>

			<div
				class="pointer-events-none absolute -right-24 -top-24 size-80 rounded-full border-[28px] border-volt/15 lg:-bottom-32 lg:-right-32 lg:top-auto lg:size-[28rem]"
				aria-hidden="true"
			/>
			<div
				class="pointer-events-none absolute right-10 top-24 size-16 rounded-full bg-volt/80 blur-[2px] lg:bottom-28 lg:right-40 lg:top-auto"
				aria-hidden="true"
			/>
		</section>

		<section
			class="relative -mt-8 flex items-start justify-center rounded-t-[32px] bg-surface-base px-6 pb-10 pt-8 lg:mt-0 lg:items-center lg:rounded-none lg:p-14"
		>
			<div class="w-full max-w-md">
				<template v-if="mode !== 'done'">
					<h2 class="font-display text-5xl font-bold tracking-tight text-ink-gray-9">
						{{ mode === "login" ? "Welcome back" : "Create your account" }}
					</h2>
					<p class="mt-1 text-base text-ink-gray-5">
						{{
							mode === "login"
								? "Log in to see today's session."
								: "Join in under a minute."
						}}
					</p>

					<TabButtons
						v-if="branding.allow_signup"
						class="mt-6"
						:model-value="mode"
						:options="tabs"
						@update:model-value="switchMode($event as Mode)"
					/>

					<form
						v-if="mode === 'login'"
						class="mt-6 space-y-4"
						@submit.prevent="submitLogin"
					>
						<TextInput
							v-model="login.email"
							label="Email"
							type="email"
							size="lg"
							placeholder="you@example.com"
							autocomplete="email"
							required
						/>
						<Password
							v-model="login.password"
							label="Password"
							size="lg"
							placeholder="••••••••"
							autocomplete="current-password"
							required
						/>
						<ErrorMessage :message="error" />
						<Button
							type="submit"
							variant="solid"
							size="lg"
							class="w-full"
							:loading="loading"
							label="Log in"
						/>
						<p class="text-center text-sm text-ink-gray-5">
							Forgot your password?
							<a
								href="/login#forgot"
								class="font-medium text-ink-gray-9 underline-offset-4 hover:underline"
								>Reset it</a
							>
						</p>
					</form>

					<form v-else class="mt-6 space-y-4" @submit.prevent="submitSignup">
						<div class="grid grid-cols-2 gap-3">
							<TextInput
								v-model="signup.first_name"
								label="First name"
								size="lg"
								autocomplete="given-name"
								required
							/>
							<TextInput
								v-model="signup.last_name"
								label="Last name"
								size="lg"
								autocomplete="family-name"
								required
							/>
						</div>
						<TextInput
							v-model="signup.email"
							label="Email"
							type="email"
							size="lg"
							placeholder="you@example.com"
							autocomplete="email"
							required
						/>
						<TextInput
							v-model="signup.phone"
							label="Phone"
							type="tel"
							size="lg"
							placeholder="0712 345 678"
							autocomplete="tel"
							required
						/>
						<ErrorMessage :message="error" />
						<Button
							type="submit"
							variant="solid"
							size="lg"
							class="w-full"
							:loading="loading"
							label="Create account"
						/>
					</form>
				</template>

				<div v-else class="text-center lg:text-left">
					<span
						class="mx-auto grid size-16 place-items-center rounded-[20px] bg-volt text-volt-ink lg:mx-0"
					>
						<span class="lucide-mail-check size-8" />
					</span>
					<h2
						class="mt-6 font-display text-5xl font-bold tracking-tight text-ink-gray-9"
					>
						Check your inbox
					</h2>
					<p class="mt-2 text-base text-ink-gray-6">
						We sent a link to <b class="text-ink-gray-9">{{ login.email }}</b
						>. Open it to set your password, then come back to log in.
					</p>
					<Button
						class="mt-8 w-full"
						size="lg"
						label="Back to log in"
						@click="switchMode('login')"
					/>
				</div>
			</div>
		</section>
	</div>
</template>
