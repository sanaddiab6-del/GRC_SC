import { BASE_API_URL } from '$lib/utils/constants';
import { redirect } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ fetch, locals }) => {
	if (!locals.user) {
		redirect(302, '/login');
	}

	// Fetch pending registration requests
	const [pendingRes, allRes, userGroupsRes, foldersRes] = await Promise.all([
		fetch(`${BASE_API_URL}/iam/registration-requests/list/?status=pending`),
		fetch(`${BASE_API_URL}/iam/registration-requests/list/`),
		fetch(`${BASE_API_URL}/user-groups/?limit=200`),
		fetch(`${BASE_API_URL}/folders/?content_type=DO&limit=200`)
	]);

	if (pendingRes.status === 403 || allRes.status === 403) {
		redirect(302, '/analytics');
	}

	const pending = pendingRes.ok ? await pendingRes.json() : [];
	const all = allRes.ok ? await allRes.json() : [];
	const userGroupsData = userGroupsRes.ok ? await userGroupsRes.json() : { results: [] };
	const foldersData = foldersRes.ok ? await foldersRes.json() : { results: [] };

	return {
		pendingRequests: pending,
		allRequests: all,
		userGroups: userGroupsData.results || userGroupsData,
		folders: foldersData.results || foldersData
	};
};
