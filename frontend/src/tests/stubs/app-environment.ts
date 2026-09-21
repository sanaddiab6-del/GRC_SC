/**
 * Stub for SvelteKit's `$app/environment` virtual module.
 *
 * The SvelteKit Vite plugin is not loaded under vitest, so the AI onboarding workflow state —
 * which guards its `localStorage` access with `browser` — cannot resolve it. The tests run in
 * jsdom, which is the browser case.
 */
export const browser = true;
export const building = false;
export const dev = true;
export const version = 'test';
