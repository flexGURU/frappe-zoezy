import { useMediaQuery } from "@vueuse/core"

const isMobile = useMediaQuery("(max-width: 767px)")

export function useIsMobile() {
	return isMobile
}
