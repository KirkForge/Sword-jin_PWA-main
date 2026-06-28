// Swordjin PWA Service Worker — managed by patch_pwa.sh, do not edit directly
const CACHE_NAME = 'swordjin-v0-70';
const ASSETS_TO_CACHE = [
  '/',
  '/index.html',
  '/Swordjin.js',
  '/Swordjin.wasm',
  '/Swordjin.pck',
  '/Swordjin.audio.worklet.js',
  '/manifest.json',
  '/icon-192.png',
  '/icon-512.png',
];

// Install — cache core assets
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(ASSETS_TO_CACHE);
    }).then(() => self.skipWaiting())
  );
});

// Activate — clean old caches
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key))
      );
    }).then(() => self.clients.claim())
  );
});

// Fetch — network first, then cache, with offline fallback
self.addEventListener('fetch', (event) => {
  if (event.request.method !== 'GET') return;

  event.respondWith(
    fetch(event.request)
      .then((response) => {
        if (response.status === 200) {
          const clone = response.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(event.request, clone);
          });
        }
        return response;
      })
      .catch(() => {
        return caches.match(event.request).then((r) => {
          if (r) return r;
          if (event.request.mode === 'navigate') {
            return caches.match('/offline.html');
          }
          return Response.error();
        });
      })
  );
});
