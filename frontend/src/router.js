import { createRouter, createWebHistory } from 'vue-router'

const routes = [
	{
		path: '/',
		name: 'Home',
		component: () => import('@/pages/Home.vue'),
	},
	{
		path: '/login',
		name: 'Login',
		component: () => import('../src/pages/Login.vue'),
	},
	{},
]

let router = createRouter({
	history: createWebHistory('/client-portal'),
	routes,
})

export default router
