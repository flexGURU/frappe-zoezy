<script setup lang="ts">
import { Button, ErrorMessage, Select, TextInput } from "frappe-ui";
import { computed } from "vue";

import { PAGE_SIZES, type PagedList, type Row } from "@/admin/data";
import EmptyState from "@/components/EmptyState.vue";
import SkeletonBlock from "@/components/SkeletonBlock.vue";

export interface Column<R> {
	key: string;
	label: string;
	align?: "left" | "right";
	format?: (row: R) => string | number | null | undefined;
	primary?: boolean;
}

const props = defineProps<{
	list: PagedList;
	columns: Column<Row>[];
	emptyTitle?: string;
	emptyIcon?: string;
	rowKey?: string;
}>();
const emit = defineEmits<{ select: [row: Row] }>();

const state = computed(() => props.list.state);
const range = computed(() => {
	const { page, pageLength, total, rows } = state.value;
	if (!total) return "0";
	const first = (page - 1) * pageLength + 1;
	return `${first}–${first + rows.length - 1} of ${total}`;
});
const pageSize = computed({
	get: () => String(state.value.pageLength),
	set: (value: string) => props.list.setPageLength(Number(value)),
});

function display(row: Row, column: Column<Row>) {
	const value = column.format ? column.format(row) : row[column.key];
	return value === null || value === undefined || value === "" ? "–" : value;
}
</script>

<template>
	<div class="card overflow-hidden">
		<div class="flex items-center gap-2 border-b border-outline-gray-1 p-3">
			<TextInput
				v-if="list.searchable"
				v-model="list.state.search"
				class="flex-1"
				type="search"
				placeholder="Search…"
				size="md"
			>
				<template #prefix><span class="lucide-search size-4 text-ink-gray-5" /></template>
			</TextInput>
			<div v-else class="flex-1 text-sm text-ink-gray-5">{{ range }}</div>
			<slot name="toolbar" />
			<Button
				aria-label="Refresh"
				tooltip="Refresh"
				size="md"
				:disabled="state.loading"
				@click="list.reload()"
			>
				<span
					class="lucide-refresh-cw size-4"
					:class="state.loading ? 'animate-spin' : ''"
				/>
			</Button>
		</div>

		<ErrorMessage v-if="state.error" class="p-3" :message="state.error as Error" />

		<div v-if="state.loading && !state.rows.length" class="space-y-2 p-3">
			<SkeletonBlock v-for="i in 4" :key="i" class="h-12 !rounded-[12px]" />
		</div>

		<EmptyState
			v-else-if="!state.rows.length"
			:icon="emptyIcon ?? 'lucide-inbox'"
			:title="state.search ? 'No matches' : emptyTitle ?? 'Nothing here yet'"
		>
			<slot name="empty" />
		</EmptyState>

		<div v-else :class="state.loading ? 'opacity-60 transition-opacity' : ''">
			<table class="hidden w-full text-base md:table">
				<thead>
					<tr class="border-b border-outline-gray-1 text-left text-sm text-ink-gray-5">
						<th
							v-for="col in columns"
							:key="col.key"
							class="px-4 py-2.5 font-medium"
							:class="col.align === 'right' ? 'text-right' : ''"
						>
							{{ col.label }}
						</th>
						<th v-if="$slots.actions" class="w-px" />
					</tr>
				</thead>
				<tbody class="divide-y divide-outline-gray-1">
					<tr
						v-for="row in state.rows"
						:key="row[rowKey ?? 'name']"
						class="cursor-pointer transition-colors hover:bg-surface-gray-1"
						@click="emit('select', row)"
					>
						<td
							v-for="col in columns"
							:key="col.key"
							class="px-4 py-3"
							:class="[
								col.align === 'right' ? 'text-right tabular-nums' : '',
								col.primary ? 'font-medium text-ink-gray-9' : 'text-ink-gray-7',
							]"
						>
							<slot :name="`cell-${col.key}`" :row="row">{{
								display(row, col)
							}}</slot>
						</td>
						<td v-if="$slots.actions" class="px-2 py-2" @click.stop>
							<slot name="actions" :row="row" />
						</td>
					</tr>
				</tbody>
			</table>

			<ul class="divide-y divide-outline-gray-1 md:hidden">
				<li
					v-for="row in state.rows"
					:key="row[rowKey ?? 'name']"
					class="flex items-center gap-3 p-4"
					@click="emit('select', row)"
				>
					<div class="min-w-0 flex-1 space-y-1">
						<p class="truncate text-base-semibold text-ink-gray-9">
							<slot :name="`cell-${columns[0].key}`" :row="row">{{
								display(row, columns[0])
							}}</slot>
						</p>
						<p class="flex flex-wrap gap-x-3 gap-y-1 text-sm text-ink-gray-6">
							<span v-for="col in columns.slice(1)" :key="col.key">
								<slot :name="`cell-${col.key}`" :row="row">{{
									display(row, col)
								}}</slot>
							</span>
						</p>
					</div>
					<div v-if="$slots.actions" @click.stop><slot name="actions" :row="row" /></div>
				</li>
			</ul>
		</div>

		<footer
			v-if="state.total"
			class="flex flex-wrap items-center justify-between gap-3 border-t border-outline-gray-1 px-3 py-2.5"
		>
			<div class="flex items-center gap-2 text-sm text-ink-gray-5">
				<span>Show</span>
				<Select
					v-model="pageSize"
					class="w-20"
					size="sm"
					:options="PAGE_SIZES.map((n) => ({ label: String(n), value: String(n) }))"
				/>
				<span class="tabular-nums">{{ range }}</span>
			</div>
			<div class="flex items-center gap-1">
				<Button
					icon="lucide-chevron-left"
					aria-label="Previous page"
					:disabled="state.page <= 1 || state.loading"
					@click="list.goTo(state.page - 1)"
				/>
				<span class="px-2 text-sm tabular-nums text-ink-gray-6">
					Page {{ state.page }} of {{ list.pageCount }}
				</span>
				<Button
					icon="lucide-chevron-right"
					aria-label="Next page"
					:disabled="state.page >= list.pageCount || state.loading"
					@click="list.goTo(state.page + 1)"
				/>
			</div>
		</footer>
	</div>
</template>
