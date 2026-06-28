
import { BASE_API_URL } from '$lib/utils/constants';
import type { PageServerLoad } from './$types';
import { m } from '$paraglide/messages';

const emptyMetrics = {
	controls: {
		total: 0,
		active: 0,
		deprecated: 0,
		to_do: 0,
		in_progress: 0,
		on_hold: 0,
		p1: 0,
		eta_missed: 0
	},
	csf_functions: {},
	compliance: {
		used_frameworks: 0,
		active_audits: 0,
		audits: 0,
		non_compliant_items: 0,
		evidences: 0,
		expired_evidences: 0
	},
	risk: {
		assessments: 0,
		scenarios: 0,
		threats: 0,
		acceptances: 0
	}
};

const emptyAuditsMetrics = {
	progress_avg: 0,
	audits_stats: {
		names: [],
		data: [],
		uuids: []
	}
};

const parseResults = async <T>(res: Response, fallback: T): Promise<T> => {
	if (!res.ok) return fallback;
	const data = await res.json();
	return data.results ?? fallback;
};

export const load: PageServerLoad = async ({ locals, fetch, cookies }) => {
	const currentYear = new Date().getFullYear();
	const token = cookies.get('token');
	const authFetch: typeof fetch = (input, init = {}) => {
		const headers = new Headers(init.headers);
		headers.set('content-type', 'application/json');
		if (token) headers.set('Authorization', `Token ${token}`);

		return fetch(input, { ...init, headers });
	};

	// All data is streamed — nothing blocks the initial page render.

	const appliedControlStatusPromise = authFetch(`${BASE_API_URL}/applied-controls/per_status/`)
		.then((res) => res.json())
		.then((res) => res.results)
		.catch(() => null);

	const taskTemplateStatusPromise = authFetch(`${BASE_API_URL}/task-templates/per_status/`)
		.then((res) => res.json())
		.then((res) => res.results)
		.catch(() => null);

	const risksCountPerLevelPromise = authFetch(`${BASE_API_URL}/risk-scenarios/count_per_level/`)
		.then((res) => res.json())
		.then((res) => res.results)
		.catch(() => ({ current: [], residual: [] }));

	const threatsCountPromise = authFetch(`${BASE_API_URL}/threats/threats_count/`)
		.then((res) => res.json())
		.catch(() => ({ results: { labels: [], values: [] } }));

	const qualificationsCountPromise = authFetch(`${BASE_API_URL}/risk-scenarios/qualifications_count/`)
		.then((res) => res.json())
		.catch(() => ({ results: { labels: [], values: [] } }));

	const complianceAnalyticsPromise = authFetch(`${BASE_API_URL}/compliance-assessments/analytics/`)
		.then((res) => res.json())
		.catch(() => ({}));

	const metricsPromise = authFetch(`${BASE_API_URL}/get_metrics/`)
		.then((res) => parseResults(res, emptyMetrics))
		.catch((error) => {
			console.error('Failed to fetch or parse metrics:', error);
			return emptyMetrics;
		});

	const auditsMetricsPromise = authFetch(`${BASE_API_URL}/get_audits_metrics/`)
		.then((res) => parseResults(res, emptyAuditsMetrics))
		.catch((error) => {
			console.error('Failed to fetch or parse audits metrics:', error);
			return emptyAuditsMetrics;
		});

	const countersPromise = authFetch(`${BASE_API_URL}/get_counters/`)
		.then((res) => res.json())
		.then((data) => data.results)
		.catch((error) => {
			console.error('failed to fetch or parse counters:', error);
			return null;
		});

	const combinedAssessmentsStatusPromise = authFetch(`${BASE_API_URL}/get_combined_assessments_status/`)
		.then((res) => res.json())
		.then((data) => data.results)
		.catch((error) => {
			console.error('failed to fetch or parse combined assessments status:', error);
			return null;
		});

	const governanceCalendarDataPromise = authFetch(
		`${BASE_API_URL}/get_governance_calendar_data/?year=${currentYear}`
	)
		.then((res) => res.json())
		.then((data) => data.results)
		.catch((error) => {
			console.error('Failed to fetch governance calendar data:', error);
			return [];
		});

	const vulnerabilitySankeyDataPromise = authFetch(`${BASE_API_URL}/vulnerabilities/sankey_data/`)
		.then((res) => res.json())
		.catch((error) => {
			console.error('Failed to fetch vulnerability sankey data:', error);
			return [];
		});

	const findingsAssessmentSunburstDataPromise = authFetch(
		`${BASE_API_URL}/findings-assessments/sunburst_data/`
	)
		.then((res) => res.json())
		.catch((error) => {
			console.error('Failed to fetch findings assessment sunburst data:', error);
			return [];
		});

	// Start all operations analytics fetches in parallel
	const detectionPromise = authFetch(`${BASE_API_URL}/incidents/detection_breakdown/`)
		.then((res) => res.json())
		.catch((error) => {
			console.error('Failed to fetch incident detection breakdown:', error);
			return { results: [] };
		});

	const monthlyPromise = authFetch(`${BASE_API_URL}/incidents/monthly_metrics/`)
		.then((res) => res.json())
		.catch((error) => {
			console.error('Failed to fetch monthly incident metrics:', error);
			return { results: { months: [], monthly_counts: [], cumulative_counts: [] } };
		});

	const summaryPromise = authFetch(`${BASE_API_URL}/incidents/summary_stats/`)
		.then((res) => res.json())
		.catch((error) => {
			console.error('Failed to fetch incident summary stats:', error);
			return { results: { total_incidents: 0, incidents_this_month: 0, open_incidents: 0 } };
		});

	const severityPromise = authFetch(`${BASE_API_URL}/incidents/severity_breakdown/`)
		.then((res) => res.json())
		.catch((error) => {
			console.error('Failed to fetch incident severity breakdown:', error);
			return { results: [] };
		});

	const qualificationsPromise = authFetch(`${BASE_API_URL}/incidents/qualifications_breakdown/`)
		.then((res) => res.json())
		.catch((error) => {
			console.error('Failed to fetch incident qualifications breakdown:', error);
			return { results: { labels: [], values: [] } };
		});

	const exceptionSankeyPromise = authFetch(`${BASE_API_URL}/security-exceptions/sankey_data/`)
		.then((res) => res.json())
		.catch((error) => {
			console.error('Failed to fetch security exception Sankey data:', error);
			return { results: { nodes: [], links: [] } };
		});

	const sunburstPromise = authFetch(`${BASE_API_URL}/applied-controls/sunburst_data/`)
		.then((res) => res.json())
		.catch((error) => {
			console.error('Failed to fetch applied controls sunburst data:', error);
			return { results: [] };
		});

	const findingsSankeyPromise = authFetch(`${BASE_API_URL}/findings/sankey_data/`)
		.then((res) => res.json())
		.catch((error) => {
			console.error('Failed to fetch findings Sankey data:', error);
			return { results: { nodes: [], links: [] } };
		});

	const operationsAnalyticsPromise = Promise.all([
		detectionPromise,
		monthlyPromise,
		summaryPromise,
		severityPromise,
		qualificationsPromise,
		exceptionSankeyPromise,
		sunburstPromise,
		findingsSankeyPromise
	])
		.then(
			([
				detectionData,
				monthlyData,
				summaryData,
				severityData,
				qualificationsData,
				exceptionSankeyData,
				sunburstData,
				findingsSankeyData
			]) => ({
				incident_detection_breakdown: detectionData.results,
				monthly_metrics: monthlyData.results,
				summary_stats: summaryData.results,
				severity_breakdown: severityData.results,
				qualifications_breakdown: qualificationsData.results,
				exception_sankey: exceptionSankeyData.results,
				applied_controls_sunburst: sunburstData.results,
				findings_sankey: findingsSankeyData.results
			})
		)
		.catch((error) => {
			console.error('Failed to fetch operations analytics:', error);
			return null;
		});

	return {
		user: locals.user,
		title: m.analytics(),
		stream: {
			metrics: metricsPromise,
			auditsMetrics: auditsMetricsPromise,
			counters: countersPromise,
			combinedAssessmentsStatus: combinedAssessmentsStatusPromise,
			governanceCalendarData: governanceCalendarDataPromise,
			operationsAnalytics: operationsAnalyticsPromise,
			vulnerabilitySankeyData: vulnerabilitySankeyDataPromise,
			findingsAssessmentSunburstData: findingsAssessmentSunburstDataPromise,
			appliedControlStatus: appliedControlStatusPromise,
			taskTemplateStatus: taskTemplateStatusPromise,
			risksCountPerLevel: risksCountPerLevelPromise,
			threatsCount: threatsCountPromise,
			qualificationsCount: qualificationsCountPromise,
			complianceAnalytics: complianceAnalyticsPromise
		}
	};
};
