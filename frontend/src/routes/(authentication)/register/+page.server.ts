import { BASE_API_URL } from '$lib/utils/constants';
import { registrationSchema } from '$lib/utils/schemas';
import { fail, redirect, type Actions } from '@sveltejs/kit';
import { setError, superValidate } from 'sveltekit-superforms';
import { zod } from 'sveltekit-superforms/adapters';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ request, locals }) => {
	// redirect user if already logged in
	if (locals.user) {
		redirect(302, '/analytics');
	}

	const form = await superValidate(request, zod(registrationSchema));
	return { form };
};

export const actions: Actions = {
	register: async ({ request, fetch }) => {
		const form = await superValidate(request, zod(registrationSchema));
		if (!form.valid) {
			return fail(400, { form });
		}

		const endpoint = `${BASE_API_URL}/iam/registration-requests/`;

		const requestInitOptions: RequestInit = {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify(form.data)
		};

		const res = await fetch(endpoint, requestInitOptions);
		const body = await res.json();

		if (!res.ok) {
			// Map backend validation errors to form fields
			if (body && typeof body === 'object') {
				for (const [field, errors] of Object.entries(body)) {
					if (Array.isArray(errors)) {
						for (const error of errors) {
							setError(form, field as any, String(error));
						}
					} else if (typeof errors === 'string') {
						setError(form, field as any, errors);
					}
				}
			}
			return fail(res.status, { form });
		}

		return { form, success: true };
	}
};
