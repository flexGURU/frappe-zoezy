import { call } from "frappe-ui"
import { computed, ref } from "vue"

function userFromCookie(): string | null {
	const cookies = new URLSearchParams(document.cookie.split("; ").join("&"))
	const user = cookies.get("user_id")
	return user && user !== "Guest" ? user : null
}

const user = ref(userFromCookie())

export const session = {
	user,
	isLoggedIn: computed(() => Boolean(user.value)),

	async login(email: string, password: string) {
		await call("login", { usr: email, pwd: password })
		window.location.href = "/zoezy"
	},

	async logout() {
		await call("logout")
		window.location.href = "/zoezy/login"
	},

	signUp(details: { first_name: string; last_name: string; email: string; phone: string }) {
		return call("zoezy.api.auth.sign_up", details)
	},
}
