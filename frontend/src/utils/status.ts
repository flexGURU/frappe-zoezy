import type { BadgeProps } from "frappe-ui"

import type { InvoiceStatus, SubscriptionStatus } from "@/types"

type Theme = NonNullable<BadgeProps["theme"]>

export function invoiceTheme(status: InvoiceStatus): Theme {
	const themes: Record<InvoiceStatus, Theme> = {
		Paid: "green",
		"Partially Paid": "amber",
		Unpaid: "blue",
		Overdue: "red",
		Cancelled: "gray",
	}
	return themes[status]
}

export function subscriptionTheme(status: SubscriptionStatus): Theme {
	return ({ Active: "green", Upcoming: "blue", Expired: "gray" } as const)[status]
}
