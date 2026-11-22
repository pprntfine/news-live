"""Build worker.js from worker-template.js + index.html and upload it to Cloudflare Workers.
Usage: python3 deploy.py <account_id> [script_name]  (auth is injected by the environment)"""
import json, re, subprocess, sys, tempfile, os, base64
acct = sys.argv[1]; name = sys.argv[2] if len(sys.argv) > 2 else 'news-live'
html = open('index.html', encoding='utf-8').read()
chans = sorted(set(re.findall(r'data-ch="(UC[\w-]+)"', html)))
src = open('worker-template.js', encoding='utf-8').read()
def txt(p): return open(p, encoding='utf-8').read()
def bin_(p): return base64.b64encode(open(p, 'rb').read()).decode()
assets = {
  '/manifest.webmanifest': {'type': 'application/manifest+json', 'data': txt('manifest.webmanifest')},
  '/sw.js': {'type': 'application/javascript', 'data': txt('sw.js'), 'cache': 'no-cache'},
  '/icon.svg': {'type': 'image/svg+xml', 'data': txt('icons/icon.svg')},
  '/icon-192.png': {'type': 'image/png', 'b64': True, 'data': bin_('icons/icon-192.png')},
  '/icon-512.png': {'type': 'image/png', 'b64': True, 'data': bin_('icons/icon-512.png')},
  '/apple-touch-icon.png': {'type': 'image/png', 'b64': True, 'data': bin_('icons/icon-180.png')},
}
src = src.replace('__ASSETS__', json.dumps(assets, ensure_ascii=False))
src = src.replace('__HTML__', json.dumps(html, ensure_ascii=False)).replace('__CHANNELS__', json.dumps(chans))
d = tempfile.mkdtemp(); p = os.path.join(d, 'worker.js'); open(p, 'w', encoding='utf-8').write(src)
print(subprocess.run(['curl', '-s', '-X', 'PUT', f'https://api.cloudflare.com/client/v4/accounts/{acct}/workers/scripts/{name}',
  '-F', 'metadata={"main_module":"worker.js","compatibility_date":"2026-11-01"};type=application/json',
  '-F', f'worker.js=@{p};type=application/javascript+module'], capture_output=True, text=True).stdout[:200])
