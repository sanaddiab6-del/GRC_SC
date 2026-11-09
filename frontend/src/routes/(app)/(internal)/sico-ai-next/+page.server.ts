/**
 * SICO AI Next â€” one-request advisory workflow.
 *
 * This route deliberately reuses the existing authenticated intake and
 * read-only discovery handlers. It does not expose the legacy commit actions,
 * introduce its own authorization, or write GRC business records.
 */
import { fail } from '@sveltejs/kit';
import type { Actions } from './$types';
import { actions as existingActions } from '../sico-ai/+page.server';

type RecordValue = Record<string, unknown>;

function isRecord(value: unknown): value is RecordValue {
    return typeof value === 'object' && value !== null && !Array.isArray(value);
}

function isFailure(value: unknown): value is { status: number; data: unknown } {
    return isRecord(value) && typeof value.status === 'number' &&
        value.status >= 400 && 'data' in value;
}

function failureMessage(value: { status: number; data: unknown }, fallback: string): string {
    const content = isRecord(value.data) ? value.data : {};
    const message = content.error ?? content.detail ?? content.message;
    return typeof message === 'string' && message.trim() ? message.slice(0, 600) : fallback;
}

export const actions = {
    run: async (event) => {
        // Clone before any handler reads the body. These requests are handled
        // by the existing SICO auth/RBAC logic; never elevate permissions.
        const checkRequest = event.request.clone();
        const discoverRequest = event.request.clone();
        const intakeRequest = event.request.clone();
        const body = await checkRequest.formData();
        const instruction = String(body.get('scenario_text') ?? '').trim();

        if (instruction.length < 20 || instruction.length > 12000) {
            return fail(400, {
                error: 'Describe your GRC assignment in 20â€“12,000 characters.'
            });
        }

        // Both handlers are already used by the existing SICO AI screen.
        // They are read-only discovery and advisory intake, NOT commit APIs.
        const discoveryResponse = await existingActions.discover({
            ...event,
            request: discoverRequest
        } as Parameters<typeof existingActions.discover>[0]);

        if (isFailure(discoveryResponse) && [401, 403].includes(discoveryResponse.status)) {
            return fail(discoveryResponse.status, {
                error: 'You do not have permission to investigate these GRC records.'
            });
        }

        const intakeResponse = await existingActions.intake({
            ...event,
            request: intakeRequest
        } as Parameters<typeof existingActions.intake>[0]);

        if (isFailure(intakeResponse) && [401, 403].includes(intakeResponse.status)) {
            return fail(intakeResponse.status, {
                error: 'You do not have permission to generate this GRC intake.'
            });
        }

        const discoveryOk = !isFailure(discoveryResponse) && isRecord(discoveryResponse);
        const intakeOk = !isFailure(intakeResponse) && isRecord(intakeResponse);

        if (!discoveryOk && !intakeOk) {
            return fail(422, {
                error: 'Both the GRC record lookup and advisory intake failed.',
                discovery_error: isFailure(discoveryResponse)
                    ? failureMessage(discoveryResponse, 'Record lookup failed') : 'Record lookup unavailable',
                intake_error: isFailure(intakeResponse)
                    ? failureMessage(intakeResponse, 'Advisory intake failed') : 'Advisory intake unavailable'
            });
        }

        // Keep returned source objects unchanged. Don't manufacture findings,
        // evidence, compliance verdicts, approval, or records.
        return {
            ...(discoveryOk ? discoveryResponse : {}),
            ...(intakeOk ? intakeResponse : {}),
            sico_run: {
                discovery: discoveryOk ? 'completed' : 'unavailable',
                intake: intakeOk ? 'completed' : 'unavailable',
                advisory_only: true,
                grc_business_records_written: false
            },
            ...(isFailure(discoveryResponse) ? {
                discovery_error: failureMessage(discoveryResponse, 'Record lookup failed')
            } : {}),
            ...(isFailure(intakeResponse) ? {
                intake_error: failureMessage(intakeResponse, 'Advisory intake failed')
            } : {})
        };
    }
} satisfies Actions;
