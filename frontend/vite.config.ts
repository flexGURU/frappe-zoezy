import path from "node:path"
import vue from "@vitejs/plugin-vue"
import frappeui from "frappe-ui/vite"
import { defineConfig } from "vite"

export default defineConfig({
	plugins: [
		frappeui({
			frontendRoute: "/zoezy",
			buildConfig: {
				outDir: "../zoezy/public/frontend",
				indexHtmlPath: "../zoezy/www/zoezy.html",
			},
		}),
		vue(),
	],
	build: {
		chunkSizeWarningLimit: 1500,
		target: "es2020",
	},
	resolve: {
		alias: {
			"@": path.resolve(__dirname, "src"),
		},
	},
	server: {
		allowedHosts: true,
	},
})
