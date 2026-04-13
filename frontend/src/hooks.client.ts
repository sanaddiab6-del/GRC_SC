import { page } from '$app/state';
import { DEFAULT_LANGUAGE } from '$lib/utils/constants';
import { defineCustomClientStrategy } from '$paraglide/runtime';
import type { HandleClientError, Init } from '@sveltejs/kit';

defineCustomClientStrategy('custom-userPreference', {
	getLocale: () => {
		return page?.data?.user?.preferences?.lang;
	},
	/**
	 * NOTE: setLocale is delegated to paraglide's cookie strategy
	 */
	setLocale: async () => {}
});

defineCustomClientStrategy('custom-fallback', {
	getLocale: () => {
		return DEFAULT_LANGUAGE;
	},
	setLocale: async () => {}
});

export const init: Init = async () => {};

export const handleError: HandleClientError = ({ error }) => {
	console.error(error);
};
