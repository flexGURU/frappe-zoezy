import { createResource, toast } from 'frappe-ui'
import { defineStore } from 'pinia'
import { ref } from 'vue'
import router from '../router'

export const useAuthStore = defineStore('auth', () => {
	const user = ref(null)
	const isLoggedIn = ref(false)

	const loginResource = createResource({
		url: 'login',
		onSuccess() {
			getSessionFromCookie()
			router.push('/dashboard')
		},
		onError(err) {
			toast({
				title: 'Login Failed',
				text: err.messages?.[0] || err.message || 'Invalid credentials',
				icon: 'x',
				iconClasses: 'text-red-500',
			})
		},
	})

	function login(username, password) {
		loginResource.submit({ usr: username, pwd: password })
	}

	function getSessionFromCookie() {
		let cookies = new URLSearchParams(document.cookie.split('; ').join('&'))
		let _sessionUser = cookies.get('user_id')
		const isGuest = !_sessionUser || _sessionUser === 'Guest'
		user.value = isGuest ? null : _sessionUser
		isLoggedIn.value = !isGuest
	}

	function logout() {
		user.value = null
		isLoggedIn.value = false
		router.push('/login')
	}

	return { user, isLoggedIn, loginResource, login, getSessionFromCookie, logout }
})
