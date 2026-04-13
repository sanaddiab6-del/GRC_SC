<script lang="ts">
	import type { ActionData, PageData } from './$types';

	let { data, form }: { data: PageData; form: ActionData } = $props();

	const statusOptions = [
		{ value: 'draft', label: 'Draft' },
		{ value: 'open', label: 'Open' },
		{ value: 'in_progress', label: 'In Progress' }
	];

	function renderError(error: unknown): string {
		if (!error) return '';
		if (typeof error === 'string') return error;
		return JSON.stringify(error);
	}
</script>

<main class="space-y-6 p-4">
	<section class="card bg-white p-5 space-y-4">
		<div>
			<h2 class="text-xl font-semibold text-slate-900">Create workflow case</h2>
			<p class="text-sm text-slate-500">
				Use this to open an orchestrated remediation case for a finding, risk, exception, or incident.
			</p>
		</div>

		{#if form?.action === 'create' && form?.error}
			<div class="rounded border border-rose-200 bg-rose-50 px-3 py-2 text-sm text-rose-700">
				{renderError(form.error)}
			</div>
		{/if}

		<form method="POST" action="?/create" class="grid gap-4 md:grid-cols-2">
			<label class="space-y-1 text-sm text-slate-700">
				<span>Name</span>
				<input
					name="name"
					required
					value={form?.values?.name || ''}
					class="w-full rounded border border-slate-300 px-3 py-2"
				/>
			</label>

			<label class="space-y-1 text-sm text-slate-700">
				<span>Folder</span>
				<select
					name="folder"
					required
					class="w-full rounded border border-slate-300 px-3 py-2"
				>
					<option value="">Select a folder</option>
					{#each data.folders as folder}
						<option value={folder.id} selected={form?.values?.folder === folder.id}>
							{folder.str || folder.name}
						</option>
					{/each}
				</select>
			</label>

			<label class="space-y-1 text-sm text-slate-700 md:col-span-2">
				<span>Description</span>
				<textarea
					name="description"
					rows="4"
					class="w-full rounded border border-slate-300 px-3 py-2"
				>{form?.values?.description || ''}</textarea>
			</label>

			<label class="space-y-1 text-sm text-slate-700">
				<span>Workflow type</span>
				<select name="workflow_type" class="w-full rounded border border-slate-300 px-3 py-2">
					{#each Object.entries(data.workflowTypeChoices) as [value, label]}
						<option value={value} selected={(form?.values?.workflow_type || 'finding') === value}>
							{label}
						</option>
					{/each}
				</select>
			</label>

			<label class="space-y-1 text-sm text-slate-700">
				<span>Classification</span>
				<select name="classification" class="w-full rounded border border-slate-300 px-3 py-2">
					{#each Object.entries(data.classificationChoices) as [value, label]}
						<option
							value={value}
							selected={(form?.values?.classification || 'control_deficiency') === value}
						>
							{label}
						</option>
					{/each}
				</select>
			</label>

			<label class="space-y-1 text-sm text-slate-700">
				<span>Initial status</span>
				<select name="status" class="w-full rounded border border-slate-300 px-3 py-2">
					{#each statusOptions as option}
						<option value={option.value} selected={(form?.values?.status || 'draft') === option.value}>
							{option.label}
						</option>
					{/each}
				</select>
			</label>

			<div class="md:col-span-2">
				<button
					type="submit"
					class="rounded bg-slate-900 px-4 py-2 text-sm font-medium text-white"
				>
					Create case
				</button>
			</div>
		</form>
	</section>

	<section class="card bg-white p-5">
		<div class="mb-4 flex items-center justify-between">
			<div>
				<h2 class="text-xl font-semibold text-slate-900">Open workflow cases</h2>
				<p class="text-sm text-slate-500">The latest 100 cases from the workflow orchestration API.</p>
			</div>
			<div class="text-sm text-slate-500">{data.cases.length} visible</div>
		</div>

		<div class="overflow-x-auto">
			<table class="min-w-full divide-y divide-slate-200 text-sm">
				<thead class="bg-slate-50 text-left text-slate-600">
					<tr>
						<th class="px-3 py-2 font-medium">Case</th>
						<th class="px-3 py-2 font-medium">Type</th>
						<th class="px-3 py-2 font-medium">Classification</th>
						<th class="px-3 py-2 font-medium">Status</th>
						<th class="px-3 py-2 font-medium">Approval</th>
						<th class="px-3 py-2 font-medium">Remediation</th>
					</tr>
				</thead>
				<tbody class="divide-y divide-slate-100">
					{#each data.cases as workflowCase}
						<tr class="hover:bg-slate-50">
							<td class="px-3 py-3 align-top">
								<a href={`/workflow-cases/${workflowCase.id}`} class="font-medium text-slate-900 hover:underline">
									{workflowCase.ref_id || 'Case'}: {workflowCase.name}
								</a>
								<div class="text-xs text-slate-500">{workflowCase.folder?.str}</div>
							</td>
							<td class="px-3 py-3 text-slate-700">{workflowCase.workflow_type}</td>
							<td class="px-3 py-3 text-slate-700">{workflowCase.classification}</td>
							<td class="px-3 py-3 text-slate-700">{workflowCase.status}</td>
							<td class="px-3 py-3 text-slate-700">{workflowCase.approval_state}</td>
							<td class="px-3 py-3 text-slate-700">{workflowCase.remediation_completion}%</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</div>
	</section>
</main>