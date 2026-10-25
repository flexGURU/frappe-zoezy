import { useCall } from "frappe-ui"

import type { Invoice, PlanDay, Profile, Subscription } from "@/types"
import { session } from "./session"

function shared<T>(method: string) {
	let instance: ReturnType<typeof useCall<T>> | undefined
	return () => {
		instance ??= useCall<T>({
			url: `/api/v2/method/zoezy.api.${method}`,
			cacheKey: ["zoezy", method, session.user.value ?? "guest"],
		})
		return instance
	}
}

export const useProfile = shared<Profile>("profile.get_profile")
export const usePlan = shared<PlanDay[]>("workout.get_weekly_plan")
export const useSubscriptions = shared<Subscription[]>("subscription.get_subscriptions")
export const useInvoices = shared<Invoice[]>("invoice.get_invoices")
