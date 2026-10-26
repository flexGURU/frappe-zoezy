export interface NavItem {
	label: string;
	icon: string;
	to: { name: string };
}

export interface NavSection {
	label: string;
	icon: string;
	items: NavItem[];
}

export const NAV: NavSection[] = [
	{
		label: "Zoezy",
		icon: "lucide-zap",
		items: [
			{ label: "Overview", icon: "lucide-layout-dashboard", to: { name: "AdminOverview" } },
			{ label: "Settings", icon: "lucide-settings", to: { name: "AdminSettings" } },
		],
	},
	{
		label: "Clients",
		icon: "lucide-users",
		items: [
			{ label: "Clients", icon: "lucide-users", to: { name: "AdminClients" } },
			{ label: "Subscriptions", icon: "lucide-calendar-range", to: { name: "AdminSubscriptions" } },
			{ label: "Lead Sources", icon: "lucide-megaphone", to: { name: "AdminLeadSources" } },
		],
	},
	{
		label: "Billing",
		icon: "lucide-receipt-text",
		items: [
			{ label: "Invoices", icon: "lucide-receipt-text", to: { name: "AdminInvoices" } },
			{ label: "Payments", icon: "lucide-hand-coins", to: { name: "AdminPayments" } },
			{ label: "Packages", icon: "lucide-package", to: { name: "AdminPackages" } },
			{ label: "Profit Analysis", icon: "lucide-chart-column", to: { name: "AdminProfitAnalysis" } },
		],
	},
	{
		label: "Training",
		icon: "lucide-dumbbell",
		items: [
			{ label: "Workout Plans", icon: "lucide-dumbbell", to: { name: "AdminPlans" } },
			{ label: "Exercises", icon: "lucide-activity", to: { name: "AdminExercises" } },
			{ label: "Categories", icon: "lucide-tags", to: { name: "AdminCategories" } },
		],
	},
];
