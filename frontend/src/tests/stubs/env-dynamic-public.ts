/**
 * Test stub for SvelteKit's `$env/dynamic/public` virtual module.
 *
 * `vitest.config.ts` runs without the SvelteKit Vite plugin, so the virtual module does not
 * exist during unit tests. Any module that reaches `$lib/utils/constants` (every AI onboarding
 * proxy does, for `BASE_API_URL`) fails to resolve without this stub.
 *
 * The object is intentionally empty: `constants.ts` falls back to the default backend URL when
 * `PUBLIC_BACKEND_API_URL` is absent, which is what the proxy tests assert against.
 */
export const env: Record<string, string> = {};
