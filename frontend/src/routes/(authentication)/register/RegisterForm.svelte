<script lang="ts">
	import SuperForm from '$lib/components/Forms/Form.svelte';
	import TextArea from '$lib/components/Forms/TextArea.svelte';
	import TextField from '$lib/components/Forms/TextField.svelte';
	import { registrationSchema } from '$lib/utils/schemas';
	import { zod } from 'sveltekit-superforms/adapters';
	import { m } from '$paraglide/messages';

	interface Props {
		data: any;
		form: any;
	}

	let { data, form }: Props = $props();
</script>

<div class="flex flex-col p-8 lg:p-10 rounded-lg shadow-lg bg-white bg-opacity-[.90]">
	{#if form?.success}
		<!-- Success state -->
		<div class="flex flex-col items-center space-y-4 py-8">
			<div class="bg-green-100 px-6 py-5 rounded-full text-3xl text-green-600">
				<i class="fa-solid fa-check-circle"></i>
			</div>
			<h3
				class="font-bold leading-tight tracking-tight text-xl md:text-2xl bg-linear-to-r from-teal-500 to-cyan-600 bg-clip-text text-transparent text-center"
			>
				{m.registrationSubmitted()}
			</h3>
			<p class="text-center text-gray-600 text-sm max-w-md">
				{m.registrationPendingApproval()}
			</p>
			<a
				href="/login"
				class="btn preset-filled-primary-500 font-semibold mt-4"
				data-testid="back-to-login-btn"
			>
				<i class="fa-solid fa-arrow-left mr-2"></i>
				{m.goBackToLogin()}
			</a>
		</div>
	{:else}
		<!-- Registration form -->
		<div class="flex flex-col w-full items-center space-y-4">
			<div class="bg-primary-300 px-6 py-5 rounded-full text-3xl">
				<i class="fa-solid fa-user-plus"></i>
			</div>
			<h3
				class="font-bold leading-tight tracking-tight text-xl md:text-2xl bg-linear-to-r from-teal-500 to-cyan-600 bg-clip-text text-transparent"
			>
				{m.requestAccess()}
			</h3>
			<p class="text-center text-gray-600 text-sm">
				{m.registrationDescription()}
			</p>

			<div class="w-full">
				<SuperForm
					class="flex flex-col space-y-3"
					data={data?.form}
					dataType="form"
					validators={zod(registrationSchema)}
					action="?/register"
				>
					{#snippet children({ form, errors })}
						<!-- Personal info -->
						<div class="grid grid-cols-1 md:grid-cols-2 gap-3">
							<TextField
								type="email"
								{form}
								field="email"
								label={m.businessEmail()}
								required
							/>
							<TextField {form} field="first_name" label={m.firstName()} required />
							<TextField {form} field="last_name" label={m.lastName()} required />
							<TextField {form} field="company" label={m.companyOrganization()} required />
							<TextField {form} field="job_title" label={m.jobTitle()} required />
							<TextField {form} field="phone" label={m.phoneNumber()} />
						</div>

						<TextField {form} field="department" label={m.departmentDomain()} />

						<TextArea
							{form}
							field="reason"
							label={m.reasonForAccess()}
							rows={3}
						/>

						<!-- Password fields -->
						<div class="border-t border-gray-200 pt-3 mt-1">
							<p class="text-sm text-gray-500 mb-2">
								<i class="fa-solid fa-shield-halved mr-1"></i>
								{m.passwordRequirements()}
							</p>
							<div class="grid grid-cols-1 md:grid-cols-2 gap-3">
								<TextField
									type="password"
									{form}
									field="password"
									label={m.password()}
									required
								/>
								<TextField
									type="password"
									{form}
									field="confirm_password"
									label={m.confirmPassword()}
									required
								/>
							</div>
						</div>

						<button
							class="btn preset-filled-primary-500 font-semibold w-full mt-2"
							data-testid="register-btn"
							type="submit"
						>
							<i class="fa-solid fa-paper-plane mr-2"></i>
							{m.submitRegistration()}
						</button>
					{/snippet}
				</SuperForm>
			</div>

			<div class="flex items-center justify-center w-full space-x-2">
				<hr class="w-64 bg-gray-200 border-0" />
				<span class="text-gray-600 text-sm">{m.or()}</span>
				<hr class="w-64 bg-gray-200 border-0" />
			</div>

			<a
				href="/login"
				class="text-primary-800 hover:text-primary-600 font-semibold text-sm"
				data-testid="back-to-login-link"
			>
				<i class="fa-solid fa-arrow-left mr-1"></i>
				{m.alreadyHaveAccount()}
			</a>
		</div>
	{/if}
</div>
