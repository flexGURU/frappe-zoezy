import { createRouter, createWebHistory } from "vue-router"

import { session } from "./data/session"
import { isWeekday, todayWeekday } from "./utils/week"

const router = createRouter({
	history: createWebHistory("/zoezy"),
	routes: [
		{
			path: "/login",
			name: "Login",
			component: () => import("@/pages/Login.vue"),
			meta: { public: true },
		},
		{
			path: "/",
			component: () => import("@/layouts/AppLayout.vue"),
			children: [
				{ path: "", name: "Today", component: () => import("@/pages/Today.vue") },
				{
					path: "plan/:day?",
					name: "Plan",
					component: () => import("@/pages/Plan.vue"),
					beforeEnter: (to) => {
						if (!isWeekday(to.params.day)) {
							return { name: "Plan", params: { day: todayWeekday() } }
						}
					},
				},
				{ path: "billing", name: "Billing", component: () => import("@/pages/Billing.vue") },
				{ path: "profile", name: "Profile", component: () => import("@/pages/Profile.vue") },
			],
		},
		{ path: "/:pathMatch(.*)*", redirect: "/" },
	],
	scrollBehavior: () => ({ top: 0 }),
})

router.beforeEach((to) => {
	if (!to.meta.public && !session.isLoggedIn.value) return { name: "Login" }
	if (to.name === "Login" && session.isLoggedIn.value) return { name: "Today" }
})

export default router
