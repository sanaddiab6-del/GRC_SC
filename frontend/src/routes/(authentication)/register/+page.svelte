<script lang="ts">
	import type { ActionData, PageData } from './$types';
	import Logo from '$lib/components/Logo/Logo.svelte';
	import RegisterForm from './RegisterForm.svelte';

	interface Props {
		data: PageData;
		form: ActionData;
	}

	let { data, form }: Props = $props();
</script>

<div class="lg:relative min-h-screen bg-slate-200">
	<div class="lg:absolute top-5 lg:left-5 flex justify-center">
		<div class="flex justify-center flex-row max-w-48 space-x-4 pb-3">
			<Logo />
		</div>
	</div>
	<div class="flex justify-center items-center min-h-screen py-10">
		<div class="w-full max-w-2xl px-4">
			<RegisterForm {data} {form} />
		</div>
	</div>
</div>
