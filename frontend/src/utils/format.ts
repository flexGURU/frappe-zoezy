import { dayjs } from "frappe-ui"

export function formatMoney(amount: number | null | undefined, currency = "KES"): string {
	if (amount == null) return "–"
	try {
		return new Intl.NumberFormat(undefined, {
			style: "currency",
			currency,
			maximumFractionDigits: amount % 1 === 0 ? 0 : 2,
		}).format(amount)
	} catch {
		return `${currency} ${amount.toLocaleString()}`
	}
}

export function formatDate(date: string | null | undefined, format = "D MMM YYYY"): string {
	return date ? dayjs(date).format(format) : "–"
}

export function daysUntil(date: string): number {
	return dayjs(date).startOf("day").diff(dayjs().startOf("day"), "day")
}

export function formatWeight(kg: number | null | undefined): string {
	if (kg == null) return "–"
	return `${Number.isInteger(kg) ? kg : kg.toFixed(1)} kg`
}

export function plural(count: number, word: string): string {
	return `${count} ${word}${count === 1 ? "" : "s"}`
}
