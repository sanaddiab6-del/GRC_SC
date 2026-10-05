import type { ListViewFilterConfig } from '$lib/utils/table';
import { z } from 'zod4';

/**
 * Pure half of ModelTable's filter-form logic, split out of filterFormState.svelte.ts so it can be
 * unit-tested without a Svelte/runes context. Behavior is unchanged from the inline implementation
 * this replaced in ModelTable.svelte; only the code's location moved.
 *
 * Uses Zod 4 (aliased as the "zod4" package, pinned to the exact version sveltekit-superforms
 * nests for its own zod4 adapter) instead of the app's usual Zod 3, and the `zod4` adapter instead
 * of `zod`. This is scoped to this one filter-form subsystem only: sveltekit-superforms's "zod" (v3)
 * adapter's type declarations import from Zod 4's own `zod/v3` compatibility layer rather than a
 * standalone v3 implementation, so checking a real Zod 3 schema against it forces TypeScript to
 * compare two independently-declared, deeply recursive generic hierarchies — reproduced in an 8-line
 * standalone file with plain tsc, consistently OOMing regardless of schema shape or file location.
 * Matching the schema's version to what the adapter actually expects (same major *and* minor Zod 4
 * version — verified empirically, a minor-version mismatch fails fast with a clear type error rather
 * than an accurate 0-vs-slow signal) avoids the cross-version comparison entirely and is fast.
 */

/** Initial `filterValues` for each filter field: URL search params win, falling back to the field's default. */
export function buildInitialFilterValues(
	filteredFields: string[],
	searchParams: URLSearchParams,
	defaultFilters: Record<string, unknown[]>
): Record<string, { value: unknown }[]> {
	return Object.fromEntries(
		filteredFields.map((field) => {
			const urlValues = searchParams.getAll(field).map((value) => ({ value }));
			const defaultValue = defaultFilters[field] || [];
			return [field, urlValues.length > 0 ? urlValues : defaultValue];
		})
	);
}

/** `filterInitialData` for superForm's `defaults()`: URL search params, backfilled from `filterValues`. */
export function buildFilterInitialData(
	filteredFields: string[],
	searchParams: URLSearchParams,
	filterValues: Record<string, { value: unknown }[]>
): Record<string, string[]> {
	const filterInitialData: Record<string, string[]> = {};
	for (const [key, value] of searchParams) {
		filterInitialData[key] ??= [];
		filterInitialData[key].push(value);
	}
	for (const field of filteredFields) {
		if (!filterInitialData[field] && filterValues[field]?.length > 0) {
			filterInitialData[field] = filterValues[field].map((v) => v.value as string);
		}
	}
	return filterInitialData;
}

/** The dynamic per-model Zod schema: every filter field accepts an optional/nullable string array. */
export function buildFiltersZodSchema(filters: Record<string, ListViewFilterConfig>) {
	const zodFiltersObject: Record<string, z.ZodTypeAny> = {};
	Object.keys(filters).forEach((k) => {
		zodFiltersObject[k] = z.array(z.string()).optional().nullable();
	});
	return z.object(zodFiltersObject);
}

/** Always-valid empty schema, for wrapper components that need a validators adapter but never validate. */
export function buildEmptyZodSchema() {
	return z.object({});
}

/** Sum of selected values across all filter fields, for the filter-count badge. */
export function countActiveFilters(
	filteredFields: string[],
	filterValues: Record<string, { value: unknown }[]>
): number {
	return filteredFields?.reduce((acc, field) => acc + (filterValues?.[field]?.length ?? 0), 0);
}
