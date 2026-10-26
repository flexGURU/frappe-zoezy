export type FieldType =
	| "text"
	| "email"
	| "tel"
	| "int"
	| "float"
	| "currency"
	| "date"
	| "select"
	| "link"
	| "textarea"
	| "check"
	| "list";

export interface LinkOptions {
	doctype: string;
	labelField?: string;
	filters?: Record<string, unknown>;
}

export interface FieldDef {
	fieldname: string;
	label: string;
	type: FieldType;
	required?: boolean;
	options?: string[];
	link?: LinkOptions;
	placeholder?: string;
	description?: string;
	createOnly?: boolean;
	wide?: boolean;
	default?: unknown;
}

export function emptyValues(fields: FieldDef[]) {
	return Object.fromEntries(
		fields.map((f) => [
			f.fieldname,
			f.default ?? (f.type === "check" ? false : f.type === "list" ? [] : ""),
		])
	);
}

export function missingRequired(fields: FieldDef[], values: Record<string, unknown>) {
	return fields.filter((f) => {
		if (!f.required) return false;
		const value = values[f.fieldname];
		return value === "" || value == null || (Array.isArray(value) && !value.length);
	});
}
