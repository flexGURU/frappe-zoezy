import { computed, watchEffect } from "vue"

import type { Branding } from "@/types"
import { useProfile } from "./resources"
import { session } from "./session"

declare global {
	interface Window {
		branding?: Branding
	}
}

const FALLBACK: Branding = {
	brand_name: "Zoezy",
	logo: null,
	default_logo: "/assets/zoezy/icons/desktop_icons/zoezy.svg",
	allow_signup: true,
}

export const branding = computed<Branding>(() => {
	const fromProfile = session.isLoggedIn.value ? useProfile().data?.settings : undefined
	return { ...FALLBACK, ...window.branding, ...fromProfile }
})

export function syncFavicon() {
	watchEffect(() => {
		const href = branding.value.logo || branding.value.default_logo
		let link = document.querySelector<HTMLLinkElement>("link[rel~='icon']")
		if (!link) {
			link = document.createElement("link")
			link.rel = "icon"
			document.head.appendChild(link)
		}
		link.href = href
	})
}
