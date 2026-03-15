<script lang="ts">
	import { safeTranslate } from '$lib/utils/i18n';
	interface Props {
		item: any; // Specify the type of 'item' as a key of 'Sidebar'
	}

	let { item }: Props = $props();
</script>

<span
	class="flex-1 text-left whitespace-nowrap text-gray-400 font-semibold uppercase tracking-wider text-[10px]"
	data-testid={'accordion-item-' + item.name.toLowerCase().replace(' ', '-')}
>
	{safeTranslate(item.name)}
</span>
