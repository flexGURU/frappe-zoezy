import frappeUIPreset, { content as frappeUIContent } from "frappe-ui/tailwind"
import type { Config } from "tailwindcss"

export default {
	presets: [frappeUIPreset],
	content: [...frappeUIContent, "./index.html", "./src/**/*.{vue,ts}"],
	theme: {
		extend: {
			colors: {
				volt: {
					DEFAULT: "#C8F31D",
					soft: "#E9FBA6",
					ink: "#1B2400",
				},
				night: {
					DEFAULT: "#111311",
					raised: "#1C1F1C",
					line: "#2A2E2A",
				},
			},
			fontFamily: {
				display: ["Lexend", "Inter Variable", "system-ui", "sans-serif"],
			},
		},
	},
} satisfies Config
