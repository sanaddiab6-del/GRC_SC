<script lang="ts">
	import sicoLogo from '$lib/assets/sico-logo.svg';

	interface Props {
		height?: number;
		width?: number;
		showText?: boolean;
	}

	let { height = 60, width = 60, showText = true }: Props = $props();
</script>

<div class="flex flex-col items-center gap-2">
	<img class="c" {height} {width} src={sicoLogo} alt="SICO GRC Platform icon" data-testid="logo-image" />
	{#if showText}
		<div class="text-center">
			<span class="text-xl font-bold bg-linear-to-r from-teal-500 to-cyan-500 bg-clip-text text-transparent">SICO</span>
			<span class="text-sm font-medium text-gray-300 block">GRC Platform</span>
		</div>
	{/if}
</div>
