import { createResource, toast } from 'frappe-ui'
import { defineStore } from 'pinia'
import { ref } from 'vue'
import router from '../router'

export const useAuthStore = defineStore('auth', () => {
	const user = ref(getUserFromCookie())
	const isLoggedIn = ref(getSessionFromCookie())

	const loginResource = createResource({
		url: 'login',
		onSuccess() {
			if (getSessionFromCookie()) {
				isLoggedIn.value = true
				user.value = getUserFromCookie()
			}
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
		if (_sessionUser == 'Guest' || !_sessionUser) {
			return false
		} else return true
	}

	function getUserFromCookie() {
		let cookies = new URLSearchParams(document.cookie.split('; ').join('&'))
		let _sessionUser = cookies.get('user_id')
		if (_sessionUser == 'Guest' || !_sessionUser) return null
		return decodeURIComponent(_sessionUser)
	}

	const logoutResource = createResource({
		url: 'logout',
		onSuccess: () => {
			getSessionFromCookie()
		},
	})

	function logout() {
		logoutResource.submit()
	}

	return { user, isLoggedIn, loginResource, login, logout }
})
