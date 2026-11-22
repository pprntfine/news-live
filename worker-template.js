// Cloudflare Worker: serves the page and resolves each channel's current live video ID.
// deploy.py replaces __HTML__ with the contents of index.html.
const HTML = __HTML__;
const CHANNELS = __CHANNELS__;
const H = { 'user-agent': 'Mozilla/5.0', cookie: 'CONSENT=YES+1; SOCS=CAI', 'accept-language': 'ja' };

async function resolve(ch) {
  try {
    const r = await fetch(`https://www.youtube.com/channel/${ch}/live`, { headers: H, cf: { cacheTtl: 60, cacheEverything: true } });
    const t = await r.text();
    if (!t.includes('"isLive":true')) return null;
    const m = t.match(/"currentVideoEndpoint":\{.*?"url":"\/watch\?v=([\w-]{11})"/);
    if (!m) return null;
    const o = await fetch(`https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v=${m[1]}&format=json`, { headers: H });
    return { id: m[1], embeddable: o.status === 200 };
  } catch (e) { return null; }
}

export default {
  async fetch(req) {
    const u = new URL(req.url);
    if (u.pathname === '/api/live') {
      const out = {};
      await Promise.all(CHANNELS.map(async (c) => { out[c] = await resolve(c); }));
      return new Response(JSON.stringify(out), { headers: { 'content-type': 'application/json', 'cache-control': 'public,max-age=60' } });
    }
    return new Response(HTML, { headers: { 'content-type': 'text/html;charset=utf-8', 'cache-control': 'no-cache' } });
  },
};
