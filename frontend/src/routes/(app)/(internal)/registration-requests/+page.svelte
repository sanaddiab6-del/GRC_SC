<script lang="ts">
	import type { PageData } from './$types';
	import { m } from '$paraglide/messages';
	import { enhance } from '$app/forms';
	import { invalidateAll } from '$app/navigation';

	interface Props {
		data: PageData;
	}

	let { data }: Props = $props();

	let activeTab: 'pending' | 'all' = $state('pending');
	let reviewingRequest: any = $state(null);
	let reviewAction: 'approve' | 'reject' | null = $state(null);
	let reviewNotes: string = $state('');
	let selectedUserGroups: string[] = $state([]);
	let selectedFolder: string = $state('');
	let submitting: boolean = $state(false);
	let errorMessage: string = $state('');

	function getStatusClasses(status: string): string {
		switch (status) {
			case 'pending':
				return 'bg-amber-100 text-amber-800 border-amber-200';
			case 'approved':
				return 'bg-green-100 text-green-800 border-green-200';
			case 'rejected':
				return 'bg-red-100 text-red-800 border-red-200';
			default:
				return 'bg-gray-100 text-gray-800 border-gray-200';
		}
	}

	function formatDate(dateStr: string): string {
		if (!dateStr) return '—';
		return new Date(dateStr).toLocaleString(undefined, {
			year: 'numeric',
			month: 'short',
			day: 'numeric',
			hour: '2-digit',
			minute: '2-digit'
		});
	}

	function openReview(request: any, action: 'approve' | 'reject') {
		reviewingRequest = request;
		reviewAction = action;
		reviewNotes = '';
		selectedUserGroups = [];
		selectedFolder = '';
		errorMessage = '';
	}

	function cancelReview() {
		reviewingRequest = null;
		reviewAction = null;
		reviewNotes = '';
		selectedUserGroups = [];
		selectedFolder = '';
		errorMessage = '';
	}

	let displayedRequests = $derived(
		activeTab === 'pending' ? data.pendingRequests : data.allRequests
	);
</script>

<div class="flex flex-col space-y-6 p-6">
	<!-- Header -->
	<div class="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
		<div>
			<h1 class="text-2xl font-bold text-gray-900">
				<i class="fa-solid fa-user-check mr-2 text-primary-600"></i>
				{m.registrationRequests()}
			</h1>
			<p class="text-sm text-gray-500 mt-1">
				{m.registrationRequestsDescription()}
			</p>
		</div>
		{#if data.pendingRequests.length > 0}
			<div class="flex items-center gap-2">
				<span
					class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-amber-100 text-amber-800"
				>
					<i class="fa-solid fa-clock mr-1.5"></i>
					{data.pendingRequests.length}
					{m.pendingReview()}
				</span>
			</div>
		{/if}
	</div>

	<!-- Tabs -->
	<div class="flex gap-2 border-b border-gray-200">
		<button
			class="px-4 py-2 text-sm font-medium border-b-2 transition-colors {activeTab === 'pending'
				? 'border-primary-500 text-primary-700'
				: 'border-transparent text-gray-500 hover:text-gray-700'}"
			onclick={() => (activeTab = 'pending')}
		>
			{m.pending()}
			{#if data.pendingRequests.length > 0}
				<span
					class="ml-1.5 inline-flex items-center justify-center w-5 h-5 text-xs font-bold text-white bg-amber-500 rounded-full"
				>
					{data.pendingRequests.length}
				</span>
			{/if}
		</button>
		<button
			class="px-4 py-2 text-sm font-medium border-b-2 transition-colors {activeTab === 'all'
				? 'border-primary-500 text-primary-700'
				: 'border-transparent text-gray-500 hover:text-gray-700'}"
			onclick={() => (activeTab = 'all')}
		>
			{m.allRequests()}
		</button>
	</div>

	<!-- Table -->
	{#if displayedRequests.length === 0}
		<div class="flex flex-col items-center justify-center py-16 text-gray-400">
			<i class="fa-solid fa-inbox text-4xl mb-3"></i>
			<p class="text-lg font-medium">{m.noRegistrationRequests()}</p>
			<p class="text-sm">{m.noRegistrationRequestsHint()}</p>
		</div>
	{:else}
		<div class="overflow-x-auto rounded-lg border border-gray-200 shadow-sm">
			<table class="min-w-full divide-y divide-gray-200">
				<thead class="bg-gray-50">
					<tr>
						<th class="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase"
							>{m.name()}</th
						>
						<th class="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase"
							>{m.email()}</th
						>
						<th class="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase"
							>{m.companyOrganization()}</th
						>
						<th class="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase"
							>{m.jobTitle()}</th
						>
						<th class="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase"
							>{m.status()}</th
						>
						<th class="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase"
							>{m.submittedAt()}</th
						>
						<th class="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase"
							>{m.actions()}</th
						>
					</tr>
				</thead>
				<tbody class="bg-white divide-y divide-gray-200">
					{#each displayedRequests as req}
						<tr class="hover:bg-gray-50 transition-colors">
							<td class="px-4 py-3 whitespace-nowrap">
								<div class="font-medium text-gray-900">
									{req.first_name}
									{req.last_name}
								</div>
								{#if req.department}
									<div class="text-xs text-gray-500">{req.department}</div>
								{/if}
							</td>
							<td class="px-4 py-3 whitespace-nowrap text-sm text-gray-600">{req.email}</td>
							<td class="px-4 py-3 whitespace-nowrap text-sm text-gray-600">{req.company}</td>
							<td class="px-4 py-3 whitespace-nowrap text-sm text-gray-600">{req.job_title}</td>
							<td class="px-4 py-3 whitespace-nowrap">
								<span
									class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border {getStatusClasses(
										req.status
									)}"
								>
									{req.status}
								</span>
							</td>
							<td class="px-4 py-3 whitespace-nowrap text-sm text-gray-500">
								{formatDate(req.created_at)}
							</td>
							<td class="px-4 py-3 whitespace-nowrap">
								{#if req.status === 'pending'}
									<div class="flex gap-2">
										<button
											class="btn btn-sm preset-filled-success-500 text-xs"
											onclick={() => openReview(req, 'approve')}
										>
											<i class="fa-solid fa-check mr-1"></i>
											{m.approve()}
										</button>
										<button
											class="btn btn-sm preset-filled-error-500 text-xs"
											onclick={() => openReview(req, 'reject')}
										>
											<i class="fa-solid fa-xmark mr-1"></i>
											{m.reject()}
										</button>
									</div>
								{:else}
									<div class="text-xs text-gray-500">
										{#if req.reviewed_by}
											{m.reviewedBy()}: {req.reviewed_by.str || req.reviewed_by.email || '—'}
										{/if}
										{#if req.reviewed_at}
											<br />{formatDate(req.reviewed_at)}
										{/if}
									</div>
								{/if}
							</td>
						</tr>

						<!-- Expandable detail row -->
						{#if reviewingRequest?.id === req.id}
							<tr class="bg-gray-50">
								<td colspan="7" class="px-6 py-4">
									<div class="flex flex-col lg:flex-row gap-6">
										<!-- Request details -->
										<div class="flex-1">
											<h4 class="font-semibold text-gray-900 mb-2">
												<i class="fa-solid fa-file-lines mr-1"></i>
												{m.requestDetails()}
											</h4>
											<div class="grid grid-cols-2 gap-2 text-sm">
												<div>
													<span class="text-gray-500">{m.phoneNumber()}:</span>
													<span class="ml-1">{req.phone || '—'}</span>
												</div>
												<div>
													<span class="text-gray-500">{m.departmentDomain()}:</span>
													<span class="ml-1">{req.department || '—'}</span>
												</div>
											</div>
											<div class="mt-2">
												<span class="text-sm text-gray-500">{m.reasonForAccess()}:</span>
												<p class="text-sm mt-1 bg-white p-2 rounded border border-gray-200">
													{req.reason}
												</p>
											</div>
										</div>

										<!-- Review form -->
										<div class="flex-1 border-l border-gray-200 pl-6">
											<h4 class="font-semibold text-gray-900 mb-3">
												{#if reviewAction === 'approve'}
													<i class="fa-solid fa-check-circle text-green-600 mr-1"></i>
													{m.approveRegistration()}
												{:else}
													<i class="fa-solid fa-times-circle text-red-600 mr-1"></i>
													{m.rejectRegistration()}
												{/if}
											</h4>

											<form
												method="POST"
												action="?/review"
												use:enhance={() => {
													submitting = true;
													errorMessage = '';
													return async ({ result, update }) => {
														submitting = false;
														if (result.type === 'failure') {
															errorMessage = result.data?.error || 'An error occurred';
														} else {
															cancelReview();
															await update();
														}
													};
												}}
											>
												<input type="hidden" name="id" value={reviewingRequest.id} />
												<input type="hidden" name="action" value={reviewAction} />

												{#if reviewAction === 'approve'}
													<div class="space-y-3">
														<div>
															<label
																class="text-sm font-semibold block mb-1"
																for="review-user-groups"
															>
																{m.userGroups()}
															</label>
															<select
																id="review-user-groups"
																name="user_groups"
																class="select w-full"
																multiple
																bind:value={selectedUserGroups}
															>
																{#each data.userGroups as group}
																	<option value={group.id}>
																		{group.str || group.name}
																	</option>
																{/each}
															</select>
															<p class="text-xs text-gray-500 mt-1">
																{m.userGroupsApprovalHint()}
															</p>
														</div>

														<div>
															<label
																class="text-sm font-semibold block mb-1"
																for="review-folder"
															>
																{m.domain()}
															</label>
															<select
																id="review-folder"
																name="folder"
																class="select w-full"
																bind:value={selectedFolder}
															>
																<option value="">— {m.none()} —</option>
																{#each data.folders as folder}
																	<option value={folder.id}>
																		{folder.str || folder.name}
																	</option>
																{/each}
															</select>
														</div>
													</div>
												{/if}

												<div class="mt-3">
													<label class="text-sm font-semibold block mb-1" for="review-notes">
														{m.reviewNotes()}
													</label>
													<textarea
														id="review-notes"
														name="review_notes"
														class="input min-h-[60px]"
														rows="2"
														bind:value={reviewNotes}
														placeholder={m.reviewNotesPlaceholder()}
													></textarea>
												</div>

												{#if errorMessage}
													<p class="text-error-500 text-sm mt-2">
														<i class="fa-solid fa-exclamation-triangle mr-1"></i>
														{errorMessage}
													</p>
												{/if}

												<div class="flex gap-2 mt-4">
													<button
														type="submit"
														class="btn btn-sm {reviewAction === 'approve'
															? 'preset-filled-success-500'
															: 'preset-filled-error-500'}"
														disabled={submitting}
													>
														{#if submitting}
															<i class="fa-solid fa-spinner fa-spin mr-1"></i>
														{/if}
														{reviewAction === 'approve' ? m.approve() : m.reject()}
													</button>
													<button
														type="button"
														class="btn btn-sm preset-tonal"
														onclick={cancelReview}
													>
														{m.cancel()}
													</button>
												</div>
											</form>
										</div>
									</div>
								</td>
							</tr>
						{/if}
					{/each}
				</tbody>
			</table>
		</div>
	{/if}
</div>
