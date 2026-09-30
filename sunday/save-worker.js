/**
 * SOJO Sunday — save endpoint
 *
 * Takes content.json from the editor at sojo.church/sunday-admin/ and commits
 * it to the website repo. The push triggers the Sunday page Action, which
 * rebuilds from Planning Center and publishes.
 *
 * Deploy at https://save.sojo.church
 *
 * Secrets (Cloudflare dashboard, never in this file):
 *   GITHUB_TOKEN     fine-grained token, Contents read/write, this repo only
 *   EDIT_PASSWORD    the password you give whoever writes the page
 *   REPO             coreyalley704/sojo-website
 *
 * What this is NOT: a login system. It is one shared password in front of one
 * file that is published on a public website anyway. The worst case if it
 * leaks is that somebody edits the church bulletin, which is annoying and
 * completely reversible from git history. It is deliberately not holding
 * anything that would matter more than that — no Planning Center token, no
 * donor data, no ability to touch any other file in the repo.
 */

const PATH = 'sunday/content.json';
const BRANCH = 'main';
const ALLOWED = ['https://sojo.church', 'https://www.sojo.church'];
const MAX_BYTES = 256 * 1024;

function cors(origin) {
  const ok = ALLOWED.includes(origin) ? origin : ALLOWED[0];
  return {
    'Access-Control-Allow-Origin': ok,
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, X-Sojo-Key',
    'Access-Control-Max-Age': '86400',
    'Vary': 'Origin',
  };
}

/** Constant-time compare, so the response time never leaks the password. */
function sameSecret(a, b) {
  const x = new TextEncoder().encode(a || '');
  const y = new TextEncoder().encode(b || '');
  if (x.length !== y.length) return false;
  let diff = 0;
  for (let i = 0; i < x.length; i++) diff |= x[i] ^ y[i];
  return diff === 0;
}

function gh(env, path, init = {}) {
  return fetch(`https://api.github.com/repos/${env.REPO}${path}`, {
    ...init,
    headers: {
      Authorization: `Bearer ${env.GITHUB_TOKEN}`,
      Accept: 'application/vnd.github+json',
      'X-GitHub-Api-Version': '2022-11-28',
      'User-Agent': 'sojo-sunday-save',
      ...(init.headers || {}),
    },
  });
}

/* btoa() is byte-oriented; the content is full of curly quotes and em dashes,
   so it has to be UTF-8 encoded before base64 or the file comes back mangled. */
function b64(text) {
  const bytes = new TextEncoder().encode(text);
  let bin = '';
  for (const b of bytes) bin += String.fromCharCode(b);
  return btoa(bin);
}

export default {
  async fetch(request, env) {
    const origin = request.headers.get('Origin') || '';
    const headers = { ...cors(origin), 'Content-Type': 'application/json' };
    const fail = (status, error) =>
      new Response(JSON.stringify({ ok: false, error }), { status, headers });

    if (request.method === 'OPTIONS') {
      return new Response(null, { status: 204, headers: cors(origin) });
    }
    if (request.method !== 'POST') return fail(405, 'POST only');
    if (origin && !ALLOWED.includes(origin)) return fail(403, 'origin');

    if (!sameSecret(request.headers.get('X-Sojo-Key'), env.EDIT_PASSWORD)) {
      return fail(401, 'wrong password');
    }

    const body = await request.text();
    if (body.length > MAX_BYTES) return fail(413, 'too large');

    // Must be valid JSON and must look like this file, not something else.
    // A malformed content.json would fail the build and leave the chairs
    // pointing at a stale page, so it is refused here instead.
    let parsed;
    try {
      parsed = JSON.parse(body);
    } catch {
      return fail(400, 'not valid JSON');
    }
    for (const key of ['label', 'hero', 'announcements']) {
      if (!(key in parsed)) return fail(400, `missing "${key}" — is this content.json?`);
    }

    // GitHub needs the blob SHA of the file being replaced.
    let sha;
    const current = await gh(env, `/contents/${PATH}?ref=${BRANCH}`);
    if (current.ok) {
      sha = (await current.json()).sha;
    } else if (current.status !== 404) {
      return fail(502, `could not read the current file (${current.status})`);
    }

    const put = await gh(env, `/contents/${PATH}`, {
      method: 'PUT',
      body: JSON.stringify({
        message: 'Sunday page: update content from the editor',
        content: b64(JSON.stringify(parsed, null, 2) + '\n'),
        branch: BRANCH,
        ...(sha ? { sha } : {}),
        committer: { name: 'sojo-sunday-editor', email: 'noreply@sojo.church' },
      }),
    });

    if (!put.ok) {
      const detail = await put.text();
      console.log('github refused', put.status, detail.slice(0, 300));
      // 409 means somebody else saved while this editor was open.
      if (put.status === 409) {
        return fail(409, 'somebody else saved while you were editing — reload and redo your change');
      }
      return fail(502, `GitHub refused the commit (${put.status})`);
    }

    return new Response(JSON.stringify({ ok: true }), { status: 200, headers });
  },
};
