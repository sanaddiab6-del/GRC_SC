import { BASE_API_URL } from '$lib/utils/constants';
import { getModelInfo } from '$lib/utils/crud';
import { error, type NumericRange, type RequestEvent } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

const aiOnboardingActionEndpoints: Record<string, string> = {
	aiAssetSuggest: '/ai/onboarding/assets/suggest/',
	aiAssetCommit: '/ai/onboarding/assets/commit/',
	aiAppliedControlSuggest: '/ai/onboarding/applied-controls/suggest/',
	aiAppliedControlCommit: '/ai/onboarding/applied-controls/commit/',
	aiEvidenceFindingSuggest: '/ai/onboarding/evidence-findings/suggest/',
	aiEvidenceFindingCommit: '/ai/onboarding/evidence-findings/commit/'
};

function getNamedAction(url: URL) {
	if (url.search.startsWith('?/')) {
		return decodeURIComponent(url.search.slice(2)).split('&', 1)[0].replace(/=$/, '');
	}

	for (const key of url.searchParams.keys()) {
		if (key.startsWith('/')) return key.slice(1);
	}

	return null;
}

async function readAiPayload(request: Request) {
	const contentType = request.headers.get('content-type')?.toLowerCase() ?? '';

	if (contentType.includes('application/json')) {
		try {
			return await request.json();
		} catch {
			return null;
		}
	}

	if (
		contentType.includes('application/x-www-form-urlencoded') ||
		contentType.includes('multipart/form-data')
	) {
		try {
			const formData = await request.formData();
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
	const payload = await readAiPayload(event.request);
	if (!payload) {
		return new Response(JSON.stringify({ detail: 'Invalid AI request payload.' }), {
			status: 400,
			headers: {
				'Content-Type': 'application/json'
			}
		});
	}

	const response = await event.fetch(`${BASE_API_URL}${endpoint}`, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify(payload)
	});
	const responseBody = await readResponseBody(response);

	return new Response(responseBody === null ? '' : JSON.stringify(responseBody), {
		status: response.status,
		headers: {
			'Content-Type': 'application/json'
		}
	});
}

export const GET: RequestHandler = async ({ fetch, params, url }) => {
	const model = getModelInfo(params.model);
	const endpoint = `${BASE_API_URL}/${model.endpointUrl ? model.endpointUrl : params.model}/${
		url.searchParams ? '?' + url.searchParams.toString() : ''
	}`;

	const res = await fetch(endpoint);
	if (!res.ok) {
		error(res.status as NumericRange<400, 599>, await res.json());
	}
	const data = await res.json();

	return new Response(JSON.stringify(data), {
		status: res.status,
		headers: {
			'Content-Type': 'application/json'
		}
	});
};

export const POST: RequestHandler = async (event) => {
	const action = getNamedAction(event.url);
	const endpoint = action ? aiOnboardingActionEndpoints[action] : null;

	if (event.params.model !== 'assets' || !endpoint) {
		return new Response(JSON.stringify({ detail: 'POST method not allowed' }), {
			status: 405,
			headers: {
				Allow: 'GET, HEAD',
				'Content-Type': 'application/json'
			}
		});
	}

	return proxyAiOnboardingAction(event, endpoint);
};
