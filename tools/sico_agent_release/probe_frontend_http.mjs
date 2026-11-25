import assert from 'node:assert/strict';
let result;
for (let attempt = 0; attempt < 40; attempt++) {
  try {
    const response = await fetch('http://127.0.0.1:3000/sico-ai-next', { redirect: 'manual', headers: { Cookie: 'csrftoken=sico-isolated-smoke' }, signal: AbortSignal.timeout(2000) });
    assert.ok([200, 302, 303, 307, 308].includes(response.status), `Unexpected status ${response.status}`);
    result = { frontend_started: true, existing_page_http_status: response.status, location: response.headers.get('location') };
    break;
  } catch (error) {
    if (attempt === 39) throw error;
    await new Promise((resolve) => setTimeout(resolve, 1000));
  }
}
console.log(JSON.stringify(result));
