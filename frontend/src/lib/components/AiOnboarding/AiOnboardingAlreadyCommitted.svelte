<script lang="ts">
	/**
	 * Shown once a commit step has an approved-commit result, while its commit button is disabled.
	 *
	 * The workflow now survives navigation between the step pages, so a finished commit step is
	 * still on screen when the user comes back to it — with its selection and its approval
	 * checkbox exactly as they were left. Leaving the button live there would make a second
	 * approved write one stray click away, and each commit sends a fresh idempotency key, so that
	 * second click would create a second set of records.
	 *
	 * Re-running the step's own suggestion step clears the result and re-arms the commit; for the
	 * steps whose dry-run also clears it, a fresh dry-run is enough.
	 */
	interface Props {
		/** Commit step id, e.g. `6B`. */
		step: string;
		/** Suggestion step that re-arms this commit, e.g. `6A`. */
		rerun: string;
		/** Whether this step's dry-run also clears the result and re-arms the commit. */
		dryRunReArms?: boolean;
	}

	let { step, rerun, dryRunReArms = false }: Props = $props();
</script>

<p
	class="mt-2 rounded border border-slate-300 bg-slate-50 p-2 text-xs text-slate-700"
	data-testid="ai-onboarding-committed-{step}"
>
	Step {step} has already written its approved records for this case, so the commit button is disabled
	to keep a second click from writing them twice. Re-run Step {rerun}
	{#if dryRunReArms}or the Step {step} dry-run{/if}
	to commit again.
</p>
