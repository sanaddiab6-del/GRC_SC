import { error, fail } from '@sveltejs/kit';

import { BASE_API_URL } from '$lib/utils/constants';

import type { Actions, PageServerLoad } from './$types';

async function parseJson(response: Response) {
	if (!response.ok) {
		return {};
	}
	return response.json();
}

async function postAction(event: Parameters<Actions[string]>[0], endpoint: string, body?: Record<string, unknown>) {
	const response = await event.fetch(endpoint, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify(body || {})
	});

	if (!response.ok) {
		const errorData = await parseJson(response);
		return fail(response.status, { error: errorData });
	}

	return { success: true };
}

export const load: PageServerLoad = async ({ fetch, params }) => {
	const caseResponse = await fetch(`${BASE_API_URL}/workflow-cases/${params.id}/`);
	if (!caseResponse.ok) {
		throw error(caseResponse.status, 'Workflow case not found');
	}

	const [workflowCase, closureReadiness, traceability] = await Promise.all([
		caseResponse.json(),
		fetch(`${BASE_API_URL}/workflow-cases/${params.id}/closure_readiness/`).then(parseJson),
		fetch(`${BASE_API_URL}/workflow-cases/${params.id}/traceability/`).then(parseJson)
	]);

	return {
		title: `Workflow Case - ${workflowCase.name}`,
		workflowCase,
		closureReadiness,
		traceability
	};
};

export const actions: Actions = {
	submitReview: async (event) => {
		return postAction(
			event,
			`${BASE_API_URL}/workflow-cases/${event.params.id}/submit_for_review/`
		);
	},
	reassess: async (event) => {
		const formData = await event.request.formData();
		return postAction(
			event,
			`${BASE_API_URL}/workflow-cases/${event.params.id}/reassess_residual_risk/`,
			{ summary: String(formData.get('summary') || '').trim() }
		);
	},
	approve: async (event) => {
		const formData = await event.request.formData();
		const stepId = String(formData.get('step_id') || '');
		const notes = String(formData.get('notes') || '').trim();
		return postAction(event, `${BASE_API_URL}/workflow-case-approval-steps/${stepId}/approve/`, {
			notes
		});
	},
	reject: async (event) => {
		const formData = await event.request.formData();
		const stepId = String(formData.get('step_id') || '');
		const notes = String(formData.get('notes') || '').trim();
		return postAction(event, `${BASE_API_URL}/workflow-case-approval-steps/${stepId}/reject/`, {
			notes
		});
	},
	requestChanges: async (event) => {
		const formData = await event.request.formData();
		const stepId = String(formData.get('step_id') || '');
		const notes = String(formData.get('notes') || '').trim();
		return postAction(
			event,
			`${BASE_API_URL}/workflow-case-approval-steps/${stepId}/request_changes/`,
			{ notes }
		);
	}
};