import { createRouter, createWebHistory } from "vue-router"

import { useProfile } from "./data/resources"
import { session } from "./data/session"
import { isWeekday, todayWeekday } from "./utils/week"

const admin = (path: string, name: string, page: () => Promise<unknown>, props = false) => ({
	path,
	name,
	component: page,
	props,
})

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
			meta: { client: true },
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
		{
			path: "/admin",
			component: () => import("@/admin/AdminLayout.vue"),
			meta: { staff: true },
			children: [
				admin("", "AdminOverview", () => import("@/admin/pages/Overview.vue")),
				admin("settings", "AdminSettings", () => import("@/admin/pages/Settings.vue")),
				admin("clients", "AdminClients", () => import("@/admin/pages/Clients.vue")),
				admin("clients/:name", "AdminClient", () => import("@/admin/pages/ClientDetail.vue"), true),
				admin("subscriptions", "AdminSubscriptions", () => import("@/admin/pages/Subscriptions.vue")),
				admin("lead-sources", "AdminLeadSources", () => import("@/admin/pages/LeadSources.vue")),
				admin("invoices", "AdminInvoices", () => import("@/admin/pages/Invoices.vue")),
				admin("payments", "AdminPayments", () => import("@/admin/pages/Payments.vue")),
				admin("packages", "AdminPackages", () => import("@/admin/pages/Packages.vue")),
				admin(
					"reports/profit-analysis",
					"AdminProfitAnalysis",
					() => import("@/admin/pages/ProfitAnalysis.vue")
				),
				admin("plans", "AdminPlans", () => import("@/admin/pages/Plans.vue")),
				admin("plans/new", "AdminPlanNew", () => import("@/admin/pages/PlanEditor.vue")),
				admin("plans/:name", "AdminPlan", () => import("@/admin/pages/PlanEditor.vue"), true),
				admin("exercises", "AdminExercises", () => import("@/admin/pages/Exercises.vue")),
				admin("categories", "AdminCategories", () => import("@/admin/pages/Categories.vue")),
			],
		},
		{ path: "/:pathMatch(.*)*", redirect: "/" },
	],
	scrollBehavior: () => ({ top: 0 }),
})

async function isStaff() {
	const profile = useProfile()
	if (!profile.data) await profile.reload()
	return Boolean(profile.data?.is_staff)
}

router.beforeEach(async (to) => {
	if (!to.meta.public && !session.isLoggedIn.value) return { name: "Login" }
	if (to.name === "Login" && session.isLoggedIn.value) return { name: "Today" }
	if (to.meta.public) return

	const staff = await isStaff()
	if (to.meta.staff && !staff) return { name: "Today" }
	if (to.meta.client && staff) return { name: "AdminOverview" }
})

export default router
