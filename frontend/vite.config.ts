import { paraglideVitePlugin } from '@inlang/paraglide-js';
import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vitest/config';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
	plugins: [
		paraglideVitePlugin({
			project: './project.inlang',
			outdir: './src/paraglide',
			outputStructure: 'locale-modules',
			cookieName: 'LOCALE',
			strategy: ['custom-userPreference', 'cookie', 'custom-fallback', 'baseLocale'],
			// Lets svelte-check/tsc resolve $paraglide/* from generated .d.ts files instead of
			// inferring types from the multi-megabyte generated .js implementation on every
			// import (this was the pathological memory/time cost behind the static-check gate).
			emitTsDeclarations: true
		}),
		tailwindcss(),
		sveltekit()
	],
	build: {
		sourcemap: false
	},
	test: {
		include: ['{src}/**/*.{test,spec}.{js,ts}']
	}
});
