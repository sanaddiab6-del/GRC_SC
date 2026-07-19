import { BASE_API_URL } from '$lib/utils/constants';
import { quickStartSchema } from '$lib/utils/schemas';
import { fail as kitFail, type Actions, type RequestEvent } from '@sveltejs/kit';
import { fail, message, setError, superValidate } from 'sveltekit-superforms';
import { zod } from 'sveltekit-superforms/adapters';

async function readAiPayload(event: RequestEvent) {
	const contentType = event.request.headers.get('content-type')?.toLowerCase() ?? '';

	if (contentType.includes('application/json')) {
		try {
			return await event.request.json();
		} catch {
			return null;
		}
	}

	if (
		contentType.includes('application/x-www-form-urlencoded') ||
		contentType.includes('multipart/form-data')
	) {
		try {
			const formData = await event.request.formData();
			const rawPayload = formData.get('payload');
			if (typeof rawPayload !== 'string' || !rawPayload.trim()) return null;
			return JSON.parse(rawPayload);
		} catch {
			return null;
		}
	}

	return null;
}

async function readResponseBody(response: Response) {
	const text = await response.text();
	if (!text) return null;
	try {
		return JSON.parse(text);
	} catch {
		return { detail: text };
	}
}

async function proxyAiOnboardingAction(event: RequestEvent, endpoint: string) {
	const payload = await readAiPayload(event);
	if (!payload) return kitFail(400, { aiError: { detail: 'Invalid AI request payload.' } });

	const response = await event.fetch(`${BASE_API_URL}${endpoint}`, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify(payload)
	});
	const responseBody = await readResponseBody(response);

	if (!response.ok) return kitFail(response.status, { aiError: responseBody });
	return { aiResult: responseBody };
}

export const actions: Actions = {
	aiCaseIntake: async (event) => {
		return proxyAiOnboardingAction(event, '/ai/onboarding/case-intake/');
	},
	aiCaseSetup: async (event) => {
		return proxyAiOnboardingAction(event, '/ai/onboarding/case-setup/');
	},
	create: async (event) => {
		const formData = await event.request.formData();
		if (!formData) {
			return fail(400, { form: null });
		}

		const form = await superValidate(formData, zod(quickStartSchema));

		const requestInitOptions: RequestInit = {
			method: 'POST',
			body: JSON.stringify(form.data)
		};

		const endpoint = `${BASE_API_URL}/quick-start/`;
		const res = await event.fetch(endpoint, requestInitOptions);

		if (!res.ok) {
			const response = await res.json();
			console.error(response);
			if (response.errors) {
				response.errors.forEach((error) => {
					setError(form, error.param, error.code);
				});
			}
			return fail(res.status, { form });
		}

		const response = await res.json();

		return message(form, {
			redirect: `/compliance-assessments/${response.complianceassessment.id}`
		});
	}
};
