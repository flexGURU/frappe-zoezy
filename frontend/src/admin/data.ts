import { call, createDocumentResource, createListResource } from "frappe-ui";
import { computed, reactive, watch } from "vue";

export type Row = Record<string, any>;

export interface ListOptions {
	fields?: string[];
	filters?: Record<string, unknown>;
	orderBy?: string;
	pageLength?: number;
}

export function useDocList(doctype: string, options: ListOptions = {}) {
	return createListResource({
		doctype,
		fields: options.fields ?? ["name"],
		filters: options.filters ?? {},
		orderBy: options.orderBy ?? "modified desc",
		pageLength: options.pageLength ?? 500,
		auto: true,
	});
}

export const PAGE_SIZES = [20, 50, 100];

export interface PagedListOptions {
	fields: string[];
	filters?: Record<string, unknown>;
	orderBy?: string;
	searchFields?: string[];
	pageLength?: number;
}

export type PagedList = ReturnType<typeof usePagedList>;

export function usePagedList(doctype: string, options: PagedListOptions) {
	const state = reactive({
		rows: [] as Row[],
		total: 0,
		page: 1,
		pageLength: options.pageLength ?? PAGE_SIZES[0],
		search: "",
		filters: { ...(options.filters ?? {}) } as Record<string, unknown>,
		loading: false,
		error: null as unknown,
	});

	const query = () => {
		const term = state.search.trim();
		return {
			doctype,
			filters: state.filters,
			or_filters:
				term && options.searchFields?.length
					? options.searchFields.map((field) => [field, "like", `%${term}%`])
					: undefined,
		};
	};

	let requestId = 0;
	async function reload() {
		const id = ++requestId;
		state.loading = true;
		state.error = null;
		try {
			const [rows, count] = await Promise.all([
				call<Row[]>("frappe.client.get_list", {
					...query(),
					fields: options.fields,
					order_by: options.orderBy ?? "modified desc",
					limit_start: (state.page - 1) * state.pageLength,
					limit_page_length: state.pageLength,
				}),
				call<Row[]>("frappe.client.get_list", {
					...query(),
					fields: [{ COUNT: "*", as: "total" }],
					limit_page_length: 1,
				}),
			]);
			if (id !== requestId) return;
			state.rows = rows;
			state.total = Number(count?.[0]?.total ?? 0);
			if (!rows.length && state.page > 1) {
				state.page = Math.max(1, Math.ceil(state.total / state.pageLength));
				await reload();
			}
		} catch (e) {
			if (id === requestId) state.error = e;
		} finally {
			if (id === requestId) state.loading = false;
		}
	}

	const pageCount = computed(() => Math.max(1, Math.ceil(state.total / state.pageLength)));

	function goTo(page: number) {
		state.page = Math.min(Math.max(1, page), pageCount.value);
		reload();
	}

	function setPageLength(length: number) {
		state.pageLength = length;
		state.page = 1;
		reload();
	}

	function setFilters(filters: Record<string, unknown>) {
		state.filters = { ...filters };
		state.page = 1;
		reload();
	}

	let searchTimer: ReturnType<typeof setTimeout> | undefined;
	watch(
		() => state.search,
		() => {
			clearTimeout(searchTimer);
			searchTimer = setTimeout(() => {
				state.page = 1;
				reload();
			}, 300);
		}
	);

	reload();

	return reactive({
		state,
		pageCount,
		searchable: Boolean(options.searchFields?.length),
		reload,
		goTo,
		setPageLength,
		setFilters,
	});
}

export function useDoc(doctype: string, name: string) {
	return createDocumentResource({ doctype, name, auto: true });
}

export function adminCall<T = unknown>(method: string, args: Record<string, unknown> = {}) {
	return call<T>(`zoezy.api.admin.${method}`, args);
}

export function useClientNames() {
	const clients = useDocList("Client", { fields: ["name", "full_name"], orderBy: "full_name asc" });
	const byName = computed<Record<string, string>>(() =>
		Object.fromEntries((clients.data ?? []).map((c: Row) => [c.name, c.full_name || c.name]))
	);
	return { clients, byName };
}
