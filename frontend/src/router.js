import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from './stores/auth'

const routes = [
	{
		path: '/',
		redirect: '/dashboard',
	},
	{
		path: '/login',
		name: 'Login',
		component: () => import('@/pages/Login.vue'),
	},
	{
		path: '/dashboard',
		name: 'Dashboard',
		component: () => import('@/pages/Dashboard.vue'),
		meta: { requiresAuth: true, title: 'Dashboard' },
	},
	{
		path: '/invoices',
		name: 'Invoices',
		component: () => import('@/pages/Invoices.vue'),
		meta: { requiresAuth: true, title: 'My Invoices' },
	},
	{
		path: '/subscriptions',
		name: 'Subscriptions',
		component: () => import('@/pages/Subscription.vue'),
		meta: { requiresAuth: true, title: 'My Subscription' },
	},
	{
		path: '/profile',
		name: 'Profile',
		component: () => import('@/pages/Profile.vue'),
		meta: { requiresAuth: true, title: 'My Profile' },
	},
]

let router = createRouter({
	history: createWebHistory('/zoezy'),
	routes,
})

router.beforeEach((to, from, next) => {
	const { isLoggedIn } = useAuthStore()

	if (to.meta.requiresAuth && !isLoggedIn) {
		next({ name: 'Login', query: { redirect: to.fullPath } })
	} else {
		next()
	}
})
export default router
