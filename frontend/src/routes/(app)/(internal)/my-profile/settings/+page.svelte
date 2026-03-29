<script lang="ts">
	import { run } from 'svelte/legacy';

	import { Tabs } from '@skeletonlabs/skeleton-svelte';
	import type { ActionData, PageData } from './$types';
	import ActivateTOTPModal from './mfa/components/ActivateTOTPModal.svelte';

	import ConfirmModal from '$lib/components/Modals/ConfirmModal.svelte';
	import { m } from '$paraglide/messages';
	import { getLocale } from '$paraglide/runtime';
	import { defaults } from 'sveltekit-superforms';
	import { zod } from 'sveltekit-superforms/adapters';
	import { z } from 'zod';
	import ListRecoveryCodesModal from './mfa/components/ListRecoveryCodesModal.svelte';
	import { recoveryCodes } from './mfa/utils/stores';
	import {
		getModalStore,
		type ModalComponent,
		type ModalSettings,
		type ModalStore
	} from '$lib/components/Modals/stores';
	import CreatePatModal from './pat/components/CreatePATModal.svelte';

	// ---- Notification preferences ----
	type NotifPrefs = {
		in_app_enabled: boolean;
		email_enabled: boolean;
		slack_enabled: boolean;
		slack_webhook_url: string;
		teams_enabled: boolean;
		teams_webhook_url: string;
	};

	let notifPrefs = $state<NotifPrefs>(
		(data as any).notificationPreferences ?? {
			in_app_enabled: true,
			email_enabled: false,
			slack_enabled: false,
			slack_webhook_url: '',
			teams_enabled: false,
			teams_webhook_url: ''
		}
	);
	let notifSaving = $state(false);
	let notifSaved = $state(false);
	let notifError = $state('');

	async function saveNotifPrefs() {
		notifSaving = true;
		notifSaved = false;
		notifError = '';
		try {
			const res = await fetch('/fe-api/notifications/preferences', {
				method: 'PATCH',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({
					in_app_enabled: notifPrefs.in_app_enabled,
					email_enabled: notifPrefs.email_enabled,
					slack_enabled: notifPrefs.slack_enabled,
					slack_webhook_url: notifPrefs.slack_webhook_url || '',
					teams_enabled: notifPrefs.teams_enabled,
					teams_webhook_url: notifPrefs.teams_webhook_url || ''
				})
			});
			if (res.ok) {
				notifSaved = true;
				setTimeout(() => (notifSaved = false), 3000);
			} else {
				const err = await res.json().catch(() => ({}));
				notifError = Object.values(err).flat().join(' ');
			}
		} catch (e: any) {
			notifError = e?.message ?? 'Network error';
		} finally {
			notifSaving = false;
		}
	}

	interface Props {
		data: PageData;
		form: ActionData;
	}

	let { data, form }: Props = $props();

	const modalStore: ModalStore = getModalStore();

	function modalActivateTOTP(totp: Record<string, any>): void {
		const modalComponent: ModalComponent = {
			ref: ActivateTOTPModal,
			props: {
				_form: data.activateTOTPForm,
				formAction: '?/activateTOTP',
				totp
			}
		};
		const modal: ModalSettings = {
			type: 'component',
			component: modalComponent,
			// Data
			title: m.activateTOTPTitle(),
			body: m.activateTOTPMessage()
		};
		modalStore.trigger(modal);
	}

	function modalConfirm(action: string): void {
		const modalComponent: ModalComponent = {
			ref: ConfirmModal,
			props: {
				debug: false,
				formAction: action
			}
		};
		const modal: ModalSettings = {
			type: 'component',
			component: modalComponent,
			// Data
			title: m.confirmModalTitle(),
			body: m.disableTOTPConfirm()
		};
		modalStore.trigger(modal);
	}

	function modalListRecoveryCodes(): void {
		const recoveryCodesModalComponent: ModalComponent = {
			ref: ListRecoveryCodesModal
		};
		const recoveryCodesModal: ModalSettings = {
			type: 'component',
			component: recoveryCodesModalComponent,
			// Data
			title: m.recoveryCodes(),
			body: m.listRecoveryCodesHelpText()
		};
		modalStore.trigger(recoveryCodesModal);
	}

	let group = $state('security');
	function modalPATCreateForm(): void {
		const modalComponent: ModalComponent = {
			ref: CreatePatModal,
			props: {
				form: data.personalAccessTokenCreateForm
			}
		};
		const modal: ModalSettings = {
			type: 'component',
			component: modalComponent,
			// Data
			title: m.generateNewPersonalAccessToken()
		};
		modalStore.trigger(modal);
	}

	function modalConfirmPATDelete(id: string): void {
		const modalComponent: ModalComponent = {
			ref: ConfirmModal,
			props: {
				_form: defaults({ id }, zod(z.object({ id: z.string() }))),
				schema: zod(z.object({ id: z.string() })),
				id: id,
				debug: false,
				formAction: '?/deletePAT'
			}
		};
		const modal: ModalSettings = {
			type: 'component',
			component: modalComponent,
			// Data
			title: m.confirmModalTitle(),
			body: m.personalAccessTokenDeleteConfirm()
		};
		modalStore.trigger(modal);
	}

	let hasTOTP = $derived(data.authenticators.some((auth) => auth.type === 'totp'));
	run(() => {
		$recoveryCodes =
			form && Object.hasOwn(form, 'recoveryCodes') ? form.recoveryCodes : data.recoveryCodes;
	});
</script>

<Tabs
	value={group}
	onValueChange={(e) => {
		group = e.value;
	}}
>
	<Tabs.List>
		<Tabs.Trigger value="security"
			><i class="fa-solid fa-shield-halved mr-2"></i>{m.securitySettings()}</Tabs.Trigger
		>
		<Tabs.Trigger value="notifications"
			><i class="fa-solid fa-bell mr-2"></i>Notifications</Tabs.Trigger
		>
		<Tabs.Indicator />
	</Tabs.List>
	<Tabs.Content value="security">
		<div class="p-4 flex flex-col space-y-4">
			<div class="flex flex-col">
				<h3 class="h3 font-medium">{m.securitySettings()}</h3>
				<p class="text-sm text-surface-800">{m.securitySettingsDescription()}</p>
			</div>
			<hr />
			<div class="flow-root">
				<dl class="-my-3 divide-y divide-surface-100 text-sm">
					<div class="grid grid-cols-1 gap-1 py-3 sm:grid-cols-3 sm:gap-4">
						<dt class="font-medium">{m.multiFactorAuthentication()}</dt>
						<dd class="text-surface-900 sm:col-span-2">
							<div class="card p-4 bg-inherit w-fit flex flex-col space-y-3">
								<div class="flex flex-col space-y-2">
									<span class="flex flex-row justify-between text-xl">
										<i class="fa-solid fa-mobile-screen-button"></i>
										{#if hasTOTP}
											<i class="fa-solid fa-circle-check text-success-600-400"></i>
										{/if}
									</span>
									<span class="flex flex-row space-x-2">
										<h6 class="h6 base-font-color">{m.authenticatorApp()}</h6>
										<p class="badge h-fit preset-tonal-secondary">{m.recommended()}</p>
									</span>
									<p class="text-sm text-surface-800 max-w-[50ch]">
										{m.authenticatorAppDescription()}
									</p>
								</div>
								<div class="flex flex-wrap justify-between gap-2">
									{#if hasTOTP}
										<button
											class="btn preset-outlined-surface-500 w-fit"
											onclick={(_) => modalConfirm('?/deactivateTOTP')}>{m.disableTOTP()}</button
										>
										{#if data.recoveryCodes}
											<button
												class="btn preset-outlined-surface-500 w-fit"
												onclick={(_) => modalListRecoveryCodes()}>{m.listRecoveryCodes()}</button
											>
										{/if}
									{:else}
										<button
											class="btn preset-outlined-surface-500 w-fit"
											onclick={(_) => modalActivateTOTP(data.totp)}>{m.enableTOTP()}</button
										>
									{/if}
								</div>
							</div>
						</dd>
					</div>
				</dl>
				<dl class="-my-3 divide-y divide-surface-100 text-sm">
					<div class="grid grid-cols-1 gap-1 py-3 sm:grid-cols-3 sm:gap-4">
						<dt class="font-medium">{m.personalAccessTokens()}</dt>
						<dd class="text-surface-900 sm:col-span-2">
							<div class="card p-4 bg-inherit w-fit flex flex-col space-y-3">
								<div class="flex flex-col space-y-2">
									<span class="flex flex-row justify-between text-xl">
										<i class="fa-solid fa-key"></i>
										{#if hasTOTP}
											<i class="fa-solid fa-circle-check text-success-500-400-token"></i>
										{/if}
									</span>
									<span class="flex flex-row space-x-2">
										<h6 class="h6 text-token">{m.personalAccessTokens()}</h6>
									</span>
									<p class="text-sm text-surface-800 max-w-[65ch]">
										{m.personalAccessTokensDescription()}
									</p>
									<div class="card p-4 preset-tonal-warning max-w-[65ch]">
										<i class="fa-solid fa-warning mr-2 text-warning-900"></i>
										{m.personalAccessTokenCreateWarning()}
									</div>
								</div>
								<div class="flex flex-col gap-2">
									<ul class="max-h-72 overflow-y-scroll">
										{#each data.personalAccessTokens as pat}
											<li class="flex flex-row justify-between card p-4 bg-inherit">
												<span class="grid grid-rows-1 grid-cols-2 w-full">
													<p>
														{pat.name}
													</p>
													<p>
														{m.expiresOn({
															date: new Date(pat.expiry).toLocaleDateString(getLocale())
														})}
													</p>
												</span>
												<button
													onclick={(_) => {
														modalConfirmPATDelete(pat.digest);
													}}
													onkeydown={() => modalConfirmPATDelete(pat.digest)}
													class="cursor-pointer hover:text-primary-500"
													data-testid="tablerow-delete-button"
													><i class="fa-solid fa-trash"></i></button
												>
											</li>
										{/each}
									</ul>
									<button class="btn preset-outlined w-fit" onclick={(_) => modalPATCreateForm()}
										>{m.generateNewPersonalAccessToken()}</button
									>
								</div>
							</div>
						</dd>
					</div>
				</dl>
			</div>
		</div>
	</Tabs.Content>

	<!-- ======================================================= -->
	<!-- Notifications tab                                       -->
	<!-- ======================================================= -->
	<Tabs.Content value="notifications">
		<div class="p-4 flex flex-col space-y-6">
			<div class="flex flex-col">
				<h3 class="h3 font-medium">Notification Settings</h3>
				<p class="text-sm text-surface-800">Control how and where you receive notifications.</p>
			</div>
			<hr />

			<!-- Channels -->
			<div class="flex flex-col space-y-4">
				<h4 class="font-semibold text-sm text-surface-700 uppercase tracking-wide">Delivery channels</h4>

				<!-- In-app -->
				<label class="flex items-center justify-between gap-4 p-4 card bg-surface-50 rounded-lg cursor-pointer">
					<div class="flex items-center gap-3">
						<span class="flex items-center justify-center w-8 h-8 rounded-full bg-blue-100 text-blue-600">
							<i class="fa-solid fa-bell text-sm"></i>
						</span>
						<div>
							<p class="font-medium text-sm">In-app notifications</p>
							<p class="text-xs text-surface-600">Bell icon in the top bar</p>
						</div>
					</div>
					<input type="checkbox" class="checkbox" bind:checked={notifPrefs.in_app_enabled} />
				</label>

				<!-- Email -->
				<label class="flex items-center justify-between gap-4 p-4 card bg-surface-50 rounded-lg cursor-pointer">
					<div class="flex items-center gap-3">
						<span class="flex items-center justify-center w-8 h-8 rounded-full bg-green-100 text-green-600">
							<i class="fa-solid fa-envelope text-sm"></i>
						</span>
						<div>
							<p class="font-medium text-sm">Email notifications</p>
							<p class="text-xs text-surface-600">Sent to your account email address</p>
						</div>
					</div>
					<input type="checkbox" class="checkbox" bind:checked={notifPrefs.email_enabled} />
				</label>

				<!-- Slack -->
				<div class="flex flex-col gap-2 p-4 card bg-surface-50 rounded-lg">
					<label class="flex items-center justify-between gap-4 cursor-pointer">
						<div class="flex items-center gap-3">
							<span class="flex items-center justify-center w-8 h-8 rounded-full bg-purple-100 text-purple-600">
								<i class="fa-brands fa-slack text-sm"></i>
							</span>
							<div>
								<p class="font-medium text-sm">Slack notifications</p>
								<p class="text-xs text-surface-600">Send to a Slack webhook</p>
							</div>
						</div>
						<input type="checkbox" class="checkbox" bind:checked={notifPrefs.slack_enabled} />
					</label>
					{#if notifPrefs.slack_enabled}
						<input
							type="url"
							class="input w-full text-sm"
							placeholder="https://hooks.slack.com/services/..."
							bind:value={notifPrefs.slack_webhook_url}
						/>
					{/if}
				</div>

				<!-- Teams -->
				<div class="flex flex-col gap-2 p-4 card bg-surface-50 rounded-lg">
					<label class="flex items-center justify-between gap-4 cursor-pointer">
						<div class="flex items-center gap-3">
							<span class="flex items-center justify-center w-8 h-8 rounded-full bg-sky-100 text-sky-600">
								<i class="fa-brands fa-microsoft text-sm"></i>
							</span>
							<div>
								<p class="font-medium text-sm">Microsoft Teams notifications</p>
								<p class="text-xs text-surface-600">Send to a Teams incoming webhook</p>
							</div>
						</div>
						<input type="checkbox" class="checkbox" bind:checked={notifPrefs.teams_enabled} />
					</label>
					{#if notifPrefs.teams_enabled}
						<input
							type="url"
							class="input w-full text-sm"
							placeholder="https://outlook.office.com/webhook/..."
							bind:value={notifPrefs.teams_webhook_url}
						/>
					{/if}
				</div>
			</div>

			<!-- Save button -->
			<div class="flex items-center gap-3">
				<button
					class="btn preset-filled-primary-500 w-fit"
					onclick={saveNotifPrefs}
					disabled={notifSaving}
				>
					{#if notifSaving}
						<i class="fa-solid fa-spinner fa-spin mr-2"></i>Saving...
					{:else}
						<i class="fa-solid fa-floppy-disk mr-2"></i>Save preferences
					{/if}
				</button>
				{#if notifSaved}
					<span class="text-sm text-success-600">
						<i class="fa-solid fa-circle-check mr-1"></i>Saved
					</span>
				{/if}
				{#if notifError}
					<span class="text-sm text-error-600">
						<i class="fa-solid fa-circle-exclamation mr-1"></i>{notifError}
					</span>
				{/if}
			</div>
		</div>
	</Tabs.Content>
</Tabs>
