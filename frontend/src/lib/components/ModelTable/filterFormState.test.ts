import { describe, expect, it } from 'vitest';
import {
	buildFilterInitialData,
	buildFiltersZodSchema,
	buildInitialFilterValues,
	countActiveFilters
} from './filterFormState';

describe('buildInitialFilterValues', () => {
	it('uses URL search params when present, over the field default', () => {
		const params = new URLSearchParams('status=active&status=pending');
		const result = buildInitialFilterValues(['status', 'folder'], params, { folder: ['root'] });
		expect(result.status).toEqual([{ value: 'active' }, { value: 'pending' }]);
		expect(result.folder).toEqual(['root']);
	});

	it('falls back to an empty array when neither URL params nor a default exist', () => {
		const params = new URLSearchParams();
		const result = buildInitialFilterValues(['status'], params, {});
		expect(result.status).toEqual([]);
	});
});

describe('buildFilterInitialData', () => {
	it('collects every URL search param key, not just the known filter fields', () => {
		const params = new URLSearchParams('status=active&other=1');
		const result = buildFilterInitialData(['status'], params, {});
		expect(result.status).toEqual(['active']);
		expect(result.other).toEqual(['1']);
	});

	it('backfills a filter field from filterValues when the URL has no param for it', () => {
		const params = new URLSearchParams();
		const filterValues = { status: [{ value: 'active' }, { value: 'pending' }] };
		const result = buildFilterInitialData(['status'], params, filterValues);
		expect(result.status).toEqual(['active', 'pending']);
	});

	it('does not overwrite a URL-provided value with the filterValues backfill', () => {
		const params = new URLSearchParams('status=active');
		const filterValues = { status: [{ value: 'pending' }] };
		const result = buildFilterInitialData(['status'], params, filterValues);
		expect(result.status).toEqual(['active']);
	});
});

describe('buildFiltersZodSchema', () => {
	it('accepts a string array, null, or undefined for every filter field, and rejects other shapes', () => {
		const schema = buildFiltersZodSchema({
			status: {} as any,
			folder: {} as any
		});

		expect(schema.safeParse({ status: ['active'], folder: null }).success).toBe(true);
		expect(schema.safeParse({ status: undefined, folder: undefined }).success).toBe(true);
		expect(schema.safeParse({}).success).toBe(true);
		expect(schema.safeParse({ status: 'active' }).success).toBe(false);
		expect(schema.safeParse({ status: [1, 2] }).success).toBe(false);
	});

	it('produces one schema key per filter, matching the filter set exactly', () => {
		const schema = buildFiltersZodSchema({ a: {} as any, b: {} as any, c: {} as any });
		expect(Object.keys(schema.shape)).toEqual(['a', 'b', 'c']);
	});
});

describe('countActiveFilters', () => {
	it('sums the number of selected values across all filter fields', () => {
		const count = countActiveFilters(['status', 'folder'], {
			status: [{ value: 'active' }, { value: 'pending' }],
			folder: [{ value: 'root' }]
		});
		expect(count).toBe(3);
	});

	it('treats a field with no entry as contributing zero', () => {
		const count = countActiveFilters(['status', 'folder'], {
			status: [{ value: 'active' }]
		});
		expect(count).toBe(1);
	});
});
