/* وِرد — يعمل بلا إنترنت. مولَّد من build/ios/build.py */
const CACHE = 'wird-01ca1c2913';
const FILES = ["./", "fonts/amiri-arabic-400-normal.woff2", "fonts/amiri-arabic-700-normal.woff2", "fonts/amiri-latin-400-normal.woff2", "fonts/amiri-latin-700-normal.woff2", "fonts/ibm-plex-sans-arabic-arabic-400-normal.woff2", "fonts/ibm-plex-sans-arabic-arabic-500-normal.woff2", "fonts/ibm-plex-sans-arabic-arabic-600-normal.woff2", "fonts/ibm-plex-sans-arabic-arabic-700-normal.woff2", "fonts/ibm-plex-sans-arabic-latin-400-normal.woff2", "fonts/ibm-plex-sans-arabic-latin-500-normal.woff2", "fonts/ibm-plex-sans-arabic-latin-600-normal.woff2", "fonts/ibm-plex-sans-arabic-latin-700-normal.woff2", "fonts/tajawal-arabic-400-normal.woff2", "fonts/tajawal-arabic-500-normal.woff2", "fonts/tajawal-arabic-700-normal.woff2", "fonts/tajawal-latin-400-normal.woff2", "fonts/tajawal-latin-500-normal.woff2", "fonts/tajawal-latin-700-normal.woff2", "icon-180.png", "icon-192.png", "icon-512.png", "manifest.webmanifest"];
self.addEventListener('install', e => e.waitUntil(caches.open(CACHE).then(c => c.addAll(FILES)).then(() => self.skipWaiting())));
self.addEventListener('activate', e => e.waitUntil(caches.keys().then(ks => Promise.all(
  ks.filter(k => k.startsWith('wird-') && k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim())));
self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET' || new URL(e.request.url).origin !== location.origin) return;
  e.respondWith(caches.match(e.request, {ignoreSearch: true}).then(hit => hit || fetch(e.request)));
});
