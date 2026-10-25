
export type Weekday =
	| "Monday"
	| "Tuesday"
	| "Wednesday"
	| "Thursday"
	| "Friday"
	| "Saturday"
	| "Sunday"

export interface Exercise {
	exercise: string
	sets: number
	reps: string
	video_url: string | null
	notes: string | null
	progressive_overload: boolean
	weight: number | null
	start_weight: number | null
	progression_weight: number | null
	final_weight: number | null
}

export interface Session {
	name: string
	category: string
	total_sets: number
	exercises: Exercise[]
}

export interface PlanDay {
	day: Weekday
	sessions: Session[]
}

export interface Branding {
	brand_name: string
	logo: string | null
	default_logo: string
	allow_signup: boolean
}

export interface AppSettings extends Branding {
	currency: string
	payment_number: string | null
}

export interface Profile {
	first_name: string
	last_name: string | null
	full_name: string
	email: string
	phone: string | null
	image: string | null
	client: {
		status: "Active" | "Inactive"
		date_joined: string | null
		age: number | null
	} | null
	settings: AppSettings
}

export type SubscriptionStatus = "Active" | "Upcoming" | "Expired"

export interface Subscription {
	name: string
	package_name: string
	price: number
	from_date: string
	to_date: string
	status: SubscriptionStatus
	items: string[]
}

export type InvoiceStatus = "Unpaid" | "Partially Paid" | "Paid" | "Overdue" | "Cancelled"

export interface Payment {
	name: string
	amount: number
	posting_date: string
	mode_of_payment: string | null
}

export interface Invoice {
	name: string
	posting_date: string
	due_date: string | null
	status: InvoiceStatus
	currency: string | null
	total: number
	outstanding_amount: number
	subscription: string
	packages: { package_name: string; unit_price: number }[]
	payments: Payment[]
}
