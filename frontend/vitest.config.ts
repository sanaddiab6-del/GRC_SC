import { configDefaults, defineConfig } from 'vitest/config';
import { svelte } from '@sveltejs/vite-plugin-svelte';
import path from 'path';

export default defineConfig({
	plugins: [svelte({ hot: !process.env.VITEST })],
	test: {
		globals: true,
		environment: 'jsdom',
		setupFiles: ['./vitest-setup.ts'],
		exclude: [...configDefaults.exclude, '**/tests/**']
	},
	resolve: {
		alias: {
			$lib: path.resolve(__dirname, 'src/lib'),
			// The SvelteKit Vite plugin is not loaded here, so its virtual modules have to be
			// resolved explicitly. Without them any test that imports `$lib/utils/constants`
			// — which every AI onboarding proxy does — fails to collect.
			'$env/dynamic/public': path.resolve(__dirname, 'src/tests/stubs/env-dynamic-public.ts'),
			'$app/environment': path.resolve(__dirname, 'src/tests/stubs/app-environment.ts'),
			$paraglide: path.resolve(__dirname, 'src/paraglide')
		}
	}
});
