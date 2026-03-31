<script lang="ts">
	import { onMount } from 'svelte';

	let unreadCount = $state(0);
	let open = $state(false);
	let notifications: any[] = $state([]);
	let loading = $state(false);

	async function fetchUnreadCount() {
		try {
			const res = await fetch('/api/notifications/unread-count/');
			if (res.ok) {
				const data = await res.json();
				unreadCount = data.unread_count ?? 0;
			}
		} catch {
			// silently fail – bell stays at 0
		}
	}

	async function fetchNotifications() {
		loading = true;
		try {
			const res = await fetch('/api/notifications/?status=unread&page_size=10');
			if (res.ok) {
				const data = await res.json();
				notifications = data.results ?? [];
			}
		} catch {
			notifications = [];
		} finally {
			loading = false;
		}
	}

	async function markAllRead() {
		try {
			await fetch('/api/notifications/mark-read/', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ all: true })
			});
			unreadCount = 0;
			notifications = notifications.map((n) => ({ ...n, status: 'read' }));
		} catch {
			// ignore
		}
	}

	function toggle() {
		open = !open;
		if (open && notifications.length === 0) {
			fetchNotifications();
		}
	}

	function handleClickOutside(e: MouseEvent) {
		const target = e.target as HTMLElement;
		if (!target.closest('.notification-bell-wrapper')) {
			open = false;
		}
	}

	onMount(() => {
		fetchUnreadCount();
		const interval = setInterval(fetchUnreadCount, 60000);
		document.addEventListener('click', handleClickOutside);
		return () => {
			clearInterval(interval);
			document.removeEventListener('click', handleClickOutside);
		};
	});
</script>

<div class="notification-bell-wrapper relative">
	<button
		type="button"
		class="relative p-2 text-gray-500 hover:text-gray-700 focus:outline-none cursor-pointer"
		onclick={toggle}
		aria-label="Notifications"
	>
		<i class="fa-solid fa-bell text-lg"></i>
		{#if unreadCount > 0}
			<span
				class="absolute -top-0.5 -right-0.5 inline-flex items-center justify-center w-5 h-5
					text-xs font-bold text-white bg-red-500 rounded-full"
			>
				{unreadCount > 99 ? '99+' : unreadCount}
			</span>
		{/if}
	</button>

	{#if open}
		<div
			class="absolute right-0 mt-2 w-80 bg-white rounded-lg shadow-xl border border-gray-200 z-50 overflow-hidden"
		>
			<div class="flex items-center justify-between px-4 py-3 border-b border-gray-100">
				<span class="text-sm font-semibold text-gray-700">Notifications</span>
				{#if unreadCount > 0}
					<button
						type="button"
						class="text-xs text-indigo-600 hover:text-indigo-800 cursor-pointer"
						onclick={markAllRead}
					>
						Mark all read
					</button>
				{/if}
			</div>
			<div class="max-h-72 overflow-y-auto">
				{#if loading}
					<div class="p-4 text-center text-sm text-gray-400">Loading...</div>
				{:else if notifications.length === 0}
					<div class="p-4 text-center text-sm text-gray-400">No new notifications</div>
				{:else}
					{#each notifications as notif}
						<div
							class="px-4 py-3 border-b border-gray-50 hover:bg-gray-50 transition-colors
								{notif.status === 'unread' ? 'bg-indigo-50/30' : ''}"
						>
							<div class="text-sm text-gray-700">{notif.title ?? notif.message ?? ''}</div>
							{#if notif.created_at}
								<div class="text-xs text-gray-400 mt-1">
									{new Date(notif.created_at).toLocaleString()}
								</div>
							{/if}
						</div>
					{/each}
				{/if}
			</div>
		</div>
	{/if}
</div>
