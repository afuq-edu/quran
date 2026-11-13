/* وِرد — يعمل بلا إنترنت. مولَّد من build/ios/build.py */
const CACHE = 'wird-80c840b00f';
const FILES = ["./", "fonts/amiri-arabic-400-normal.woff2", "fonts/amiri-arabic-700-normal.woff2", "fonts/amiri-latin-400-normal.woff2", "fonts/amiri-latin-700-normal.woff2", "fonts/ibm-plex-sans-arabic-arabic-400-normal.woff2", "fonts/ibm-plex-sans-arabic-arabic-500-normal.woff2", "fonts/ibm-plex-sans-arabic-arabic-600-normal.woff2", "fonts/ibm-plex-sans-arabic-arabic-700-normal.woff2", "fonts/ibm-plex-sans-arabic-latin-400-normal.woff2", "fonts/ibm-plex-sans-arabic-latin-500-normal.woff2", "fonts/ibm-plex-sans-arabic-latin-600-normal.woff2", "fonts/ibm-plex-sans-arabic-latin-700-normal.woff2", "fonts/tajawal-arabic-400-normal.woff2", "fonts/tajawal-arabic-500-normal.woff2", "fonts/tajawal-arabic-700-normal.woff2", "fonts/tajawal-latin-400-normal.woff2", "fonts/tajawal-latin-500-normal.woff2", "fonts/tajawal-latin-700-normal.woff2", "icon-180.png", "icon-192.png", "icon-512.png", "manifest.webmanifest"];
self.addEventListener('install', e => e.waitUntil(caches.open(CACHE).then(c => c.addAll(FILES)).then(() => self.skipWaiting())));
self.addEventListener('activate', e => e.waitUntil(caches.keys().then(ks => Promise.all(
  ks.filter(k => k.startsWith('wird-') && k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim())));
self.addEventListener('message', e => { if (e.data === 'skip') self.skipWaiting(); });
// the page itself: network first (so a new version shows on the next open), cache when offline
// everything else: cache first (the cache name changes with every build, so new files arrive with it)
self.addEventListener('fetch', e => {
  const r = e.request, u = new URL(r.url);
  if (r.method !== 'GET' || u.origin !== location.origin) return;
  const page = r.mode === 'navigate' || u.pathname.endsWith('/') || u.pathname.endsWith('/index.html');
  if (page) {
    const net = fetch(r, {cache: 'no-store'}).then(res => {
      if (res.ok) { const c = res.clone(); caches.open(CACHE).then(k => k.put('./', c)); }
      return res;
    });
    // slow network: after 4 s show the saved copy (the fresh one is still saved for next time)
    const slow = new Promise(ok => setTimeout(ok, 4000)).then(() => caches.match('./')).then(c => c || net);
    e.respondWith(Promise.race([net.catch(() => caches.match('./')), slow]));
    return;
  }
  e.respondWith(caches.match(r, {ignoreSearch: true}).then(hit => hit || fetch(r)));
});
