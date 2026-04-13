<script lang="ts">
	import type { ActionData, PageData } from './$types';

	let { data, form }: { data: PageData; form: ActionData } = $props();

	function traceCount(items: unknown[] | undefined): number {
		return items?.length || 0;
	}

	function renderError(error: unknown): string {
		if (!error) return '';
		if (typeof error === 'string') return error;
		return JSON.stringify(error);
	}
</script>

<main class="space-y-6 p-4">
	<section class="card bg-white p-5 space-y-4">
		<div class="flex flex-col gap-2 md:flex-row md:items-start md:justify-between">
			<div>
				<div class="text-sm font-medium text-slate-500">{data.workflowCase.ref_id}</div>
				<h1 class="text-2xl font-semibold text-slate-900">{data.workflowCase.name}</h1>
				<p class="mt-1 text-sm text-slate-600">{data.workflowCase.description || 'No description provided.'}</p>
			</div>
			<div class="grid gap-2 text-sm text-slate-600 md:text-right">
				<div>Status: <span class="font-medium text-slate-900">{data.workflowCase.status}</span></div>
				<div>Approval: <span class="font-medium text-slate-900">{data.workflowCase.approval_state}</span></div>
				<div>Remediation: <span class="font-medium text-slate-900">{data.workflowCase.remediation_completion}%</span></div>
			</div>
		</div>

		{#if form?.error}
			<div class="rounded border border-rose-200 bg-rose-50 px-3 py-2 text-sm text-rose-700">
				{renderError(form.error)}
			</div>
		{/if}

		<div class="grid gap-3 md:grid-cols-3">
			<div class="rounded border border-slate-200 p-4">
				<div class="text-xs uppercase tracking-wide text-slate-500">Closure readiness</div>
				<div class="mt-2 text-2xl font-semibold text-slate-900">
					{data.closureReadiness.can_close ? 'Ready' : 'Blocked'}
				</div>
				{#if !data.closureReadiness.can_close}
					<ul class="mt-3 list-disc pl-5 text-sm text-slate-600">
						{#each data.closureReadiness.missing || [] as missing}
							<li>{missing}</li>
						{/each}
					</ul>
				{/if}
			</div>

			<div class="rounded border border-slate-200 p-4">
				<div class="text-xs uppercase tracking-wide text-slate-500">Review</div>
				<form method="POST" action="?/submitReview" class="mt-3">
					<button type="submit" class="rounded bg-slate-900 px-4 py-2 text-sm font-medium text-white">
						Submit for review
					</button>
				</form>
			</div>

			<div class="rounded border border-slate-200 p-4">
				<div class="text-xs uppercase tracking-wide text-slate-500">Residual risk reassessment</div>
				<form method="POST" action="?/reassess" class="mt-3 space-y-3">
					<textarea
						name="summary"
						rows="4"
						placeholder="Summarize residual risk after remediation."
						class="w-full rounded border border-slate-300 px-3 py-2 text-sm"
					></textarea>
					<button type="submit" class="rounded border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700">
						Record reassessment
					</button>
				</form>
			</div>
		</div>
	</section>

	<section class="grid gap-6 lg:grid-cols-[1.1fr,0.9fr]">
		<div class="card bg-white p-5 space-y-4">
			<div>
				<h2 class="text-xl font-semibold text-slate-900">Approval steps</h2>
				<p class="text-sm text-slate-500">Act on assigned workflow-case approval steps from this page.</p>
			</div>

			{#if data.workflowCase.approval_steps?.length}
				<div class="space-y-4">
					{#each data.workflowCase.approval_steps as step}
						<div class="rounded border border-slate-200 p-4 space-y-3">
							<div class="flex items-center justify-between">
								<div>
									<div class="text-sm font-medium text-slate-900">Step {step.sequence}</div>
									<div class="text-xs text-slate-500">{step.approver?.email || 'Unassigned approver'}</div>
								</div>
								<div class="text-sm text-slate-600">{step.status}</div>
							</div>

							<div class="grid gap-3 md:grid-cols-3">
								<form method="POST" action="?/approve" class="space-y-2">
									<input type="hidden" name="step_id" value={step.id} />
									<textarea name="notes" rows="3" class="w-full rounded border border-slate-300 px-3 py-2 text-sm" placeholder="Approval notes"></textarea>
									<button type="submit" class="w-full rounded bg-emerald-600 px-3 py-2 text-sm font-medium text-white">Approve</button>
								</form>

								<form method="POST" action="?/requestChanges" class="space-y-2">
									<input type="hidden" name="step_id" value={step.id} />
									<textarea name="notes" rows="3" class="w-full rounded border border-slate-300 px-3 py-2 text-sm" placeholder="Requested changes"></textarea>
									<button type="submit" class="w-full rounded bg-amber-500 px-3 py-2 text-sm font-medium text-white">Request changes</button>
								</form>

								<form method="POST" action="?/reject" class="space-y-2">
									<input type="hidden" name="step_id" value={step.id} />
									<textarea name="notes" rows="3" class="w-full rounded border border-slate-300 px-3 py-2 text-sm" placeholder="Rejection reason"></textarea>
									<button type="submit" class="w-full rounded bg-rose-600 px-3 py-2 text-sm font-medium text-white">Reject</button>
								</form>
							</div>
						</div>
					{/each}
				</div>
			{:else}
				<div class="rounded border border-dashed border-slate-300 px-4 py-6 text-sm text-slate-500">
					No approval steps are linked to this workflow case yet.
				</div>
			{/if}
		</div>

		<div class="card bg-white p-5 space-y-4">
			<div>
				<h2 class="text-xl font-semibold text-slate-900">Traceability</h2>
				<p class="text-sm text-slate-500">Linked records that support auditability and remediation tracking.</p>
			</div>

			<div class="grid gap-3 sm:grid-cols-2">
				<div class="rounded border border-slate-200 p-4">
					<div class="text-xs uppercase tracking-wide text-slate-500">Requirements</div>
					<div class="mt-2 text-2xl font-semibold text-slate-900">{traceCount(data.traceability.requirements)}</div>
				</div>
				<div class="rounded border border-slate-200 p-4">
					<div class="text-xs uppercase tracking-wide text-slate-500">Findings</div>
					<div class="mt-2 text-2xl font-semibold text-slate-900">{traceCount(data.traceability.findings)}</div>
				</div>
				<div class="rounded border border-slate-200 p-4">
					<div class="text-xs uppercase tracking-wide text-slate-500">Controls</div>
					<div class="mt-2 text-2xl font-semibold text-slate-900">{traceCount(data.traceability.applied_controls)}</div>
				</div>
				<div class="rounded border border-slate-200 p-4">
					<div class="text-xs uppercase tracking-wide text-slate-500">Tasks</div>
					<div class="mt-2 text-2xl font-semibold text-slate-900">{traceCount(data.traceability.tasks)}</div>
				</div>
				<div class="rounded border border-slate-200 p-4">
					<div class="text-xs uppercase tracking-wide text-slate-500">Evidence</div>
					<div class="mt-2 text-2xl font-semibold text-slate-900">{traceCount(data.traceability.evidences)}</div>
				</div>
				<div class="rounded border border-slate-200 p-4">
					<div class="text-xs uppercase tracking-wide text-slate-500">Risk scenarios</div>
					<div class="mt-2 text-2xl font-semibold text-slate-900">{traceCount(data.traceability.risk_scenarios)}</div>
				</div>
			</div>

			<div>
				<h3 class="text-sm font-semibold uppercase tracking-wide text-slate-500">Recent events</h3>
				<div class="mt-3 space-y-3">
					{#each data.workflowCase.events || [] as event}
						<div class="rounded border border-slate-200 px-3 py-2 text-sm text-slate-700">
							<div class="font-medium text-slate-900">{event.event_type}</div>
							<div>{event.event_notes || 'No notes recorded.'}</div>
							<div class="text-xs text-slate-500">{event.created_at}</div>
						</div>
					{/each}
				</div>
			</div>
		</div>
	</section>
</main>