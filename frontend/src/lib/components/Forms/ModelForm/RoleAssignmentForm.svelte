<script lang="ts">
	import AutocompleteSelect from '../AutocompleteSelect.svelte';
	import Checkbox from '$lib/components/Forms/Checkbox.svelte';
	import type { SuperValidated } from 'sveltekit-superforms';
	import type { ModelInfo, CacheLock } from '$lib/utils/types';
	import { m } from '$paraglide/messages';

	interface Props {
		form: SuperValidated<any>;
		model: ModelInfo;
		cacheLocks?: Record<string, CacheLock>;
		formDataCache?: Record<string, any>;
		context?: string;
	}

	let {
		form,
		model,
		cacheLocks = {},
		formDataCache = $bindable({}),
		context = 'create'
	}: Props = $props();
</script>

<AutocompleteSelect
	{form}
	optionsEndpoint="folders?content_type=DO&content_type=GL"
	field="folder"
	pathField="path"
	cacheLock={cacheLocks['folder']}
	bind:cachedValue={formDataCache['folder']}
	label={m.folder()}
/>
<AutocompleteSelect
	{form}
	optionsEndpoint="users?is_third_party=false"
	optionsLabelField="email"
	field="user"
	cacheLock={cacheLocks['user']}
	bind:cachedValue={formDataCache['user']}
	label={m.user()}
	nullable={true}
/>
<AutocompleteSelect
	{form}
	optionsEndpoint="user-groups"
	field="user_group"
	pathField="path"
	cacheLock={cacheLocks['user_group']}
	bind:cachedValue={formDataCache['user_group']}
	label={m.userGroup()}
	nullable={true}
/>
<AutocompleteSelect
	{form}
	optionsEndpoint="roles"
	field="role"
	cacheLock={cacheLocks['role']}
	bind:cachedValue={formDataCache['role']}
	label={m.role()}
/>
<AutocompleteSelect
	{form}
	multiple
	optionsEndpoint="folders?content_type=DO&content_type=GL"
	field="perimeter_folders"
	pathField="path"
	cacheLock={cacheLocks['perimeter_folders']}
	bind:cachedValue={formDataCache['perimeter_folders']}
	label="Perimeter domains"
/>
<Checkbox {form} field="is_recursive" label="Apply recursively to sub-domains" />
