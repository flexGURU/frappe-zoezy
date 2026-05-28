<template>
	<div class="min-h-screen bg-gray-50 flex items-center justify-center px-4 py-10">
		<div class="w-full max-w-md">
			<div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-8">
				<div class="mb-8 text-center">
					<img src="/zoezy-logo.png" alt="Zoezy Logo" class="mx-auto h-12 w-auto mb-4" />
					<h1 class="text-2xl font-semibold text-gray-900">Welcome to Zoezy</h1>
					<p class="text-gray-500 mt-1">
						{{
							activeView === 'login'
								? 'Sign in to your account'
								: 'Create your account'
						}}
					</p>
				</div>

				<form
					v-if="activeView === 'login'"
					id="login"
					@submit.prevent="handleLogin"
					class="space-y-4"
				>
					<div>
						<label class="block font-medium text-gray-700 mb-1"
							>Email / Username</label
						>
						<Input
							v-model="form.username"
							type="email"
							placeholder="you@example.com"
							:disabled="auth.loginResource.loading"
							autocomplete="username"
							class="w-full"
							required
						/>
					</div>

					<div>
						<label class="block font-medium text-gray-700 mb-1">Password</label>
						<Input
							v-model="form.password"
							type="password"
							placeholder="Enter your password"
							autocomplete="current-password"
							class="w-full"
							required
						/>
					</div>

					<ErrorMessage
						v-if="auth.loginResource.error"
						:message="
							auth.loginResource.error?.messages?.[0] ||
							auth.loginResource.error?.message ||
							'Login failed'
						"
					/>

					<Button
						size="md"
						theme="blue"
						:loading="auth.loginResource.loading"
						class="w-full"
					>
						{{ auth.loginResource.loading ? 'Signing in...' : 'Sign In' }}
					</Button>

					<p class="text-center text-sm text-gray-600 mt-2">
						Don't have an account?
						<a
							href="#signup"
							class="font-medium text-blue-600 hover:text-blue-700"
							@click.prevent="activeView = 'signup'"
						>
							Sign up
						</a>
					</p>
				</form>

				<form v-else id="signup" @submit.prevent="handleSignup" class="space-y-4">
					<div class="grid grid-cols-2 gap-4">
						<div>
							<label class="block font-medium text-gray-700 mb-1">
								First name <span class="text-red-500">*</span>
							</label>
							<Input
								v-model="signupForm.firstName"
								type="text"
								placeholder="John"
								class="w-full"
								autocomplete="given-name"
								required
							/>
						</div>
						<div>
							<label class="block font-medium text-gray-700 mb-1">
								Last name <span class="text-red-500">*</span>
							</label>
							<Input
								v-model="signupForm.lastName"
								type="text"
								placeholder="Doe"
								class="w-full"
								autocomplete="family-name"
								required
							/>
						</div>
					</div>

					<div>
						<label class="block font-medium text-gray-700 mb-1">
							Email <span class="text-red-500">*</span>
						</label>
						<Input
							v-model="signupForm.email"
							type="email"
							placeholder="you@example.com"
							class="w-full"
							autocomplete="email"
							required
						/>
					</div>

					<div>
						<label class="block font-medium text-gray-700 mb-1">
							Phone number <span class="text-red-500">*</span>
						</label>
						<Input
							v-model="signupForm.phone"
							placeholder="0712345678"
							class="w-full"
							autocomplete="tel"
							required
						/>
					</div>

					<ErrorMessage :message="signup.error" />

					<Button size="md" theme="blue" :loading="signup.loading" class="w-full"
						>Sign Up</Button
					>

					<p class="text-center text-sm text-gray-600 mt-2">
						Already have an account?
						<a
							href="#login"
							class="font-medium text-blue-600 hover:text-blue-700"
							@click.prevent="activeView = 'login'"
						>
							Sign in
						</a>
					</p>
				</form>
			</div>

			<p class="text-center text-xs text-gray-800 mt-6">
				&copy; {{ new Date().getFullYear() }} Zoezy. All rights reserved.
			</p>
		</div>
	</div>
</template>

<script setup>
import { onBeforeMount, reactive, ref, watch } from 'vue'
import { Button, Input, toast, ErrorMessage, createResource } from 'frappe-ui'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()

onBeforeMount(() => {
	if (auth.isLoggedIn) {
		window.location.href = '/zoezy/dashboard'
	}
})

const activeView = ref('login')
const signupError = ref('')

const form = reactive({
	username: '',
	password: '',
})

const signupForm = reactive({
	firstName: '',
	lastName: '',
	email: '',
	phone: '',
})

function handleLogin() {
	if (!form.username || !form.password) return
	auth.login(form.username, form.password)
}

function handleSignup() {
	signupError.value = ''
	const { firstName, lastName, email, phone } = signupForm
	if (!firstName || !lastName || !email || !phone) {
		signupError.value = 'All fields are required.'
		return
	}
	signup.submit()
}

const signup = createResource({
	url: 'zoezy.api.user.sign_up',
	makeParams: () => ({
		first_name: signupForm.firstName,
		last_name: signupForm.lastName,
		email: signupForm.email,
		phone: signupForm.phone,
	}),
	onSuccess() {
		toast({
			title: 'Successful! Please check your email for login details.',
			icon: 'check',
			iconClasses: 'text-green-500',
		})
		setTimeout(() => {
			activeView.value = 'login'
		}, 5000)
	},
	onError(err) {
		signupError.value = err.messages?.[0] || err.message || 'Signup failed.'
	},
})
watch(activeView, (newView) => {
	if (newView === 'login') {
		auth.loginResource.error = null
		signupForm.firstName = ''
		signupForm.lastName = ''
		signupForm.email = ''
		signupForm.phone = ''
		signupError.value = ''
	}
})
</script>
