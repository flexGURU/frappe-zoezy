import { dayjs } from "frappe-ui"

import type { Exercise, PlanDay, Weekday } from "@/types"

export const WEEKDAYS: Weekday[] = [
	"Monday",
	"Tuesday",
	"Wednesday",
	"Thursday",
	"Friday",
	"Saturday",
	"Sunday",
]

export function todayWeekday(): Weekday {
	return WEEKDAYS[(dayjs().day() + 6) % 7]
}

export function isWeekday(value: unknown): value is Weekday {
	return WEEKDAYS.includes(value as Weekday)
}

export function currentWeek() {
	const monday = dayjs().subtract((dayjs().day() + 6) % 7, "day")
	return WEEKDAYS.map((day, i) => {
		const date = monday.add(i, "day")
		return { day, date: date.date(), isToday: date.isSame(dayjs(), "day") }
	})
}

export function daySummary(plan: PlanDay | undefined) {
	const sessions = plan?.sessions ?? []
	return {
		sessions: sessions.length,
		exercises: sessions.reduce((n, s) => n + s.exercises.length, 0),
		sets: sessions.reduce((n, s) => n + s.total_sets, 0),
		categories: sessions.map((s) => s.category),
	}
}

export function setWeights(exercise: Exercise): number[] {
	if (exercise.progressive_overload) {
		const start = exercise.start_weight ?? 0
		const step = exercise.progression_weight ?? 0
		return Array.from({ length: exercise.sets }, (_, i) => start + step * i)
	}
	return exercise.weight ? Array(exercise.sets).fill(exercise.weight) : []
}
