import { useProfile } from "@/data/resources";
import { formatMoney } from "@/utils/format";

export function useMoney() {
	const profile = useProfile();
	return (amount: number | null | undefined) =>
		formatMoney(amount ?? 0, profile.data?.settings.currency);
}
