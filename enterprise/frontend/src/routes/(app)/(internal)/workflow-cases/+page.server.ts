import { fail, redirect } from '@sveltejs/kit';

import { BASE_API_URL } from '$lib/utils/constants';

import type { Actions, PageServerLoad } from './$types';

async function readJsonOrEmpty(response: Response) {
	if (!response.ok) {
		return {};
	}
	return response.json();
}

export const load: PageServerLoad = async ({ fetch }) => {
	const [casesResponse, foldersResponse, workflowTypesResponse, classificationsResponse] =
		await Promise.all([
			fetch(`${BASE_API_URL}/workflow-cases/?limit=100`),
			fetch(`${BASE_API_URL}/folders/?limit=200`),
			fetch(`${BASE_API_URL}/workflow-cases/workflow_type/`),
			fetch(`${BASE_API_URL}/workflow-cases/classification/`)
		]);

	const [casesData, foldersData, workflowTypeChoices, classificationChoices] = await Promise.all([
		readJsonOrEmpty(casesResponse),
		readJsonOrEmpty(foldersResponse),
		readJsonOrEmpty(workflowTypesResponse),
		readJsonOrEmpty(classificationsResponse)
	]);

	return {
		title: 'Workflow Cases',
		cases: casesData.results || [],
		folders: foldersData.results || [],
		workflowTypeChoices,
		classificationChoices
	};
};

export const actions: Actions = {
	create: async (event) => {
		const formData = await event.request.formData();
		const payload = {
			name: String(formData.get('name') || '').trim(),
			description: String(formData.get('description') || '').trim(),
			folder: String(formData.get('folder') || '').trim(),
			workflow_type: String(formData.get('workflow_type') || 'finding'),
			classification: String(formData.get('classification') || 'control_deficiency'),
			status: String(formData.get('status') || 'draft')
		};

		const response = await event.fetch(`${BASE_API_URL}/workflow-cases/`, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify(payload)
		});

		if (!response.ok) {
			const errorData = await readJsonOrEmpty(response);
			return fail(response.status, {
				action: 'create',
				error: errorData,
				values: payload
			});
		}

		const created = await response.json();
		redirect(303, `/workflow-cases/${created.id}`);
	}
};