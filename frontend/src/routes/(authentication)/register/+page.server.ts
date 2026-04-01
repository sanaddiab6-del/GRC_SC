import { BASE_API_URL } from '$lib/utils/constants';
import { registrationBaseSchema } from '$lib/utils/schemas';
import { fail, redirect, type Actions } from '@sveltejs/kit';
import { setError, superValidate, type SuperValidated } from 'sveltekit-superforms';
import { zod } from 'sveltekit-superforms/adapters';
import type { z } from 'zod';
import type { PageServerLoad } from './$types';

type RegistrationData = z.infer<typeof registrationBaseSchema>;
// Cast required: superforms' ZodObjectType constraint is too narrow for schemas with .default() fields
const schema = zod(registrationBaseSchema as any);

export const load: PageServerLoad = async ({ request, locals }) => {
if (locals.user) {
redirect(302, '/analytics');
}

const form = (await superValidate(request, schema)) as SuperValidated<RegistrationData>;
return { form };
};

export const actions: Actions = {
register: async ({ request, fetch }) => {
const form = (await superValidate(request, schema)) as SuperValidated<RegistrationData>;
if (!form.valid) {
return fail(400, { form });
}

if (form.data.password !== form.data.confirm_password) {
return setError(form, 'confirm_password', 'Passwords do not match');
}

const endpoint = `${BASE_API_URL}/iam/registration-requests/`;

const requestInitOptions: RequestInit = {
method: 'POST',
headers: { 'Content-Type': 'application/json' },
body: JSON.stringify(form.data)
};

const res = await fetch(endpoint, requestInitOptions);
const body = await res.json();

if (!res.ok) {
if (body && typeof body === 'object') {
for (const [field, errors] of Object.entries(body)) {
if (Array.isArray(errors)) {
for (const error of errors) {
setError(form as any, field as any, String(error));
}
} else if (typeof errors === 'string') {
setError(form as any, field as any, errors);
}
}
}
return fail(res.status, { form });
}

return { form, success: true };
}
};
