module.exports = {
	presets: [require('frappe-ui/src/utils/tailwind.config')],
	content: [
		'./index.html',
		'./src/**/*.{vue,js,ts,jsx,tsx}',
		'./node_modules/frappe-ui/src/components/**/*.{vue,js,ts,jsx,tsx}',
	],
	theme: {
		extend: {
			fontFamily: {
				sans: ['Lexend', 'ui-sans-serif', 'system-ui', 'sans-serif'],
			},
		},
	},
	plugins: [],
}
