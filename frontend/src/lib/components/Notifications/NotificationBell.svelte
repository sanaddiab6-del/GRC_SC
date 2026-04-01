<script lang="ts">
	import { page } from '$app/stores';

	let notificationCount = $state(0);
	let showDropdown = $state(false);

	// Fetch pending count if user is admin
	async function fetchCount() {
		try {
			const res = await fetch('/api/iam/registration-requests/count/');
			if (res.ok) {
				const data = await res.json();
				notificationCount = data.pending_count || 0;
			}
		} catch {
			// Silently fail - notifications are non-critical
		}
	}

	$effect(() => {
		const user = $page.data?.user;
		if (user?.is_admin) {
			fetchCount();
			const interval = setInterval(fetchCount, 60000);
			return () => clearInterval(interval);
		}
	});
</script>

{#if notificationCount > 0}
	<a
		href="/registration-requests"
		class="relative inline-flex items-center p-2 text-gray-500 hover:text-gray-700 transition-colors"
		title="Pending registration requests"
	>
		<i class="fa-solid fa-bell text-lg"></i>
		<span
			class="absolute -top-0.5 -right-0.5 inline-flex items-center justify-center w-5 h-5 text-xs font-bold text-white bg-red-500 rounded-full"
		>
			{notificationCount}
		</span>
	</a>
{:else}
	<span class="inline-flex items-center p-2 text-gray-400">
		<i class="fa-solid fa-bell text-lg"></i>
	</span>
{/if}
