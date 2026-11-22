import { page } from '$app/state';
import { breadcrumbs } from '$lib/utils/breadcrumbs';
import type { ListViewFilterConfig } from '$lib/utils/table';
import type { urlModel } from '$lib/utils/types.js';
import { defaults, superForm } from 'sveltekit-superforms';
import { zod4 } from 'sveltekit-superforms/adapters';
import type { DataHandler } from '@vincjo/datatables/remote';
import {
	buildEmptyZodSchema,
	buildFilterInitialData,
	buildFiltersZodSchema,
	buildInitialFilterValues,
	countActiveFilters
} from './filterFormState';

/**
 * Filter form state and machinery for ModelTable, extracted verbatim from the component's script
 * (same runtime behavior, same reactive graph) into this small, isolated file. Originally moved
 * here to reduce ModelTable's own script size; the actual OOM turned out to be independent of file
 * size or scope, caused by sveltekit-superforms's "zod" (v3) adapter type-checking a real Zod 3
 * schema against Zod 4's `zod/v3` compatibility types (see git history for the full isolation).
 * This subsystem now uses the `zod4` adapter with a real Zod 4 schema (via the "zod4" aliased
 * package, pinned to the exact Zod version sveltekit-superforms nests for that adapter) instead,
 * which avoids the cross-version comparison. Every other form in the app keeps using Zod 3 as
 * before; this migration is intentionally scoped to ModelTable's filter form only.
 */
export function createFilterFormState(params: {
	filters: Record<string, ListViewFilterConfig>;
	defaultFilters: Record<string, unknown[]>;
	overrideFilters: Record<string, unknown[]>;
	handler: DataHandler;
	URLModel: urlModel | undefined;
	onFilterChange: (filters: Record<string, unknown>) => void;
}) {
	const { filters, defaultFilters, overrideFilters, handler, URLModel, onFilterChange } = params;

	const filteredFields = Object.keys(filters);

	const filterValues: { [key: string]: any } = $state(
		buildInitialFilterValues(filteredFields, page.url.searchParams, defaultFilters)
	);

	$effect(() => onFilterChange(filterValues));

	$effect(() => {
		for (const field of filteredFields) {
			const filterValue = filterValues[field];
			const overrideFilterValue = overrideFilters[field];
			const finalFilterValue = overrideFilterValue || filterValue;

			const fieldFilterParams = finalFilterValue
				? finalFilterValue.map((v: Record<string, any>) => v.value)
				: [];
			handler.filter(fieldFilterParams, field);
			page.url.searchParams.delete(field);
			if (finalFilterValue) {
				finalFilterValue.forEach(({ value }) => page.url.searchParams.append(field, value));
			}

			const hrefPattern = new RegExp(`^/${URLModel}(\\?.*)?$`);
			const fullPath = page.url.pathname + page.url.search;
			if (hrefPattern.test(fullPath)) {
				breadcrumbs.updateCrumb(hrefPattern, { href: fullPath });
			}
		}
		history.replaceState(history.state, '', page.url.pathname + page.url.search);
		setTimeout(() => {
			handler.invalidate();
		}, 10);
	});

	const filterInitialData = buildFilterInitialData(filteredFields, page.url.searchParams, filterValues);
	const filtersSchema = buildFiltersZodSchema(filters);
	const filtersAdapter = zod4(filtersSchema);
	const form = superForm(defaults(filterInitialData, filtersAdapter), {
		SPA: true,
		validators: filtersAdapter,
		dataType: 'json',
		invalidateAll: false,
		applyAction: false,
		resetForm: false,
		taintedMessage: false,
		validationMethod: 'auto'
	});

	const filterCount = $derived(countActiveFilters(filteredFields, filterValues));

	// Per-field filter components are wrapped in their own nested <SuperForm> (see ModelTable's
	// template) that requires a `validators` adapter but never actually validates anything itself —
	// real validation happens on `form` above. Kept as an always-valid, empty-schema zod4 adapter to
	// match the original empty-Zod-3-schema behavior exactly, now on the same Zod version as `form`.
	const noopValidators = zod4(buildEmptyZodSchema());

	return {
		filteredFields,
		filterValues,
		form,
		noopValidators,
		get filterCount() {
			return filterCount;
		},
		get filters() {
			return filters;
		}
	};
}
