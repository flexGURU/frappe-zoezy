<template>
	<div class="min-h-screen flex items-center justify-center bg-gray-50 p-4">
		<div class="w-full max-w-sm bg-white rounded-xl shadow-sm border border-gray-200 p-6">
			<div class="text-center mb-6">
				<h1 class="text-2xl font-bold text-gray-900">Zoezy</h1>
				<p class="text-sm text-gray-500 mt-1">Trainer-Client Platform</p>
			</div>

			<div class="flex border-b border-gray-200 mb-5">
				<button
					@click="switchMode('login')"
					class="flex-1 py-2 text-sm font-medium border-b-2 transition-colors"
					:class="
						mode === 'login'
							? 'border-blue-500 text-blue-600'
							: 'border-transparent text-gray-500 hover:text-gray-700'
					"
				>
					Log In
				</button>
				<button
					@click="switchMode('signup')"
					class="flex-1 py-2 text-sm font-medium border-b-2 transition-colors"
					:class="
						mode === 'signup'
							? 'border-blue-500 text-blue-600'
							: 'border-transparent text-gray-500 hover:text-gray-700'
					"
				>
					Sign Up
				</button>
			</div>

			<form
				v-if="mode === 'login'"
				@submit.prevent="submitLogin"
				class="flex flex-col gap-3"
			>
				<Input
					required
					type="text"
					label="Email"
					placeholder="johndoe@email.com"
					v-model="loginData.email"
				/>
				<Input
					required
					type="password"
					label="Password"
					placeholder="••••••"
					v-model="loginData.password"
				/>
				<ErrorMessage :message="session.login.error" />
				<Button
					:loading="session.login.loading"
					theme="blue"
					variant="solid"
					type="submit"
				>
					Log In
				</Button>
			</form>

			<form
				v-else-if="mode === 'signup'"
				@submit.prevent="submitSignup"
				class="flex flex-col gap-3"
			>
				<div class="flex gap-2">
					<Input
						required
						type="text"
						label="First Name"
						placeholder="John"
						v-model="signupData.firstName"
					/>
					<Input
						required
						type="text"
						label="Last Name"
						placeholder="Doe"
						v-model="signupData.lastName"
					/>
				</div>
				<Input
					required
					type="email"
					label="Email"
					placeholder="johndoe@email.com"
					v-model="signupData.email"
				/>
				<Input
					required
					type="text"
					label="Phone Number"
					placeholder="0712345678"
					v-model="signupData.phone"
				/>
				<ErrorMessage :message="session.signup.error" />
				<Button
					:loading="session.signup.loading"
					theme="blue"
					variant="solid"
					type="submit"
				>
					Create Account
				</Button>
			</form>

			<div v-else class="flex flex-col items-center gap-4 py-4 text-center">
				<div
					class="w-12 h-12 rounded-full bg-green-100 flex items-center justify-center text-green-600 text-xl"
				>
					&#10003;
				</div>
				<div>
					<p class="font-medium text-gray-900">Account created!</p>
					<p class="text-sm text-gray-500 mt-1">
						Check your email to set your password.
					</p>
				</div>
				<Button variant="outline" @click="switchMode('login')">Back to Log In</Button>
			</div>
		</div>
	</div>
</template>

<script setup>
import { reactive, ref, watch } from "vue";
import { session } from "../data/session";
import { Button, ErrorMessage, Input, toast } from "frappe-ui";

const mode = ref("login");

const loginData = reactive({ email: "", password: "" });
const signupData = reactive({ firstName: "", lastName: "", email: "", phone: "" });

function switchMode(target) {
	session.login.reset();
	session.signup.reset();
	mode.value = target;
}

function submitLogin() {
	session.login.submit({ email: loginData.email, password: loginData.password });
}

function submitSignup() {
	session.signup.submit(
		{
			first_name: signupData.firstName,
			last_name: signupData.lastName,
			email: signupData.email,
			phone: signupData.phone,
		},
		{
			onSuccess: () => {
				toast.success("Signup successful! Please check your email to set your password.");
				setTimeout(() => {
					window.location.href = "/zoezy/login";
				}, 5000);
			},
			onError: (err) => {
				toast.error("Signup failed. Please try again.");
			},
		},
	);
}

watch(
	() => session.signup.data,
	(val) => {
		if (val !== undefined && val !== null && !session.signup.error) {
			mode.value = "success";
			session.signup.reset();
			signupData.firstName = "";
			signupData.lastName = "";
			signupData.email = "";
			signupData.phone = "";
		}
	},
);
</script>
