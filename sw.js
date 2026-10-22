/**
 * Opportunities Portal — Service Worker (sw.js)
 * Enables offline access to app shell, opportunity catalog, and saved favorites.
 * Pure Vanilla JavaScript • Zero External Dependencies • Mobile-First PWA
 */

const CACHE_NAME = 'opportunities-portal-v10';

// App shell assets required for the complete offline experience
const PRECACHE_ASSETS = [
  './',
  'index.html',
  'css/style.css',
  'js/app.js',
  'js/ui-preferences.js',
  'data/opportunities.json'
];

// ============================================================================
// LIFECYCLE: INSTALL
// Pre-caches the application shell and forces the waiting service worker
// to become the active service worker.
// ============================================================================
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        return cache.addAll(PRECACHE_ASSETS);
      })
      .then(() => {
        return self.skipWaiting();
      })
      .catch((error) => {
        console.error('[SW] Pre-caching failed during install:', error);
      })
  );
});

// ============================================================================
// LIFECYCLE: ACTIVATE
// Cleans up outdated cache generations and immediately takes control
// of all uncontrolled clients.
// ============================================================================
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys()
      .then((cacheNames) => {
        return Promise.all(
          cacheNames.map((name) => {
            if (name.startsWith('opportunities-portal-') && name !== CACHE_NAME) {
              console.log('[SW] Removing old cache generation:', name);
              return caches.delete(name);
            }
            return null;
          })
        );
      })
      .then(() => {
        return self.clients.claim();
      })
  );
});

// ============================================================================
// FETCH STRATEGIES
// 1. Navigation requests: Network-First with Cache Fallback to index.html
// 2. Data requests (data/opportunities.json): Network-First with Cache Fallback
// 3. Static assets (CSS, JS, Fonts): Stale-While-Revalidate
// ============================================================================
self.addEventListener('fetch', (event) => {
  const request = event.request;

  // Intercept only HTTP and HTTPS GET requests (ignore chrome-extension://, etc.)
  if (request.method !== 'GET' || !request.url.startsWith('http')) {
    return;
  }

  const url = new URL(request.url);

  // Do not proxy/cache third-party pages or APIs through this site's worker.
  if (url.origin !== self.location.origin) return;

  // Strategy 1: HTML Navigation Requests (Network-First, fallback to cached index.html)
  if (request.mode === 'navigate' || request.destination === 'document') {
    event.respondWith(
      fetch(request)
        .then((networkResponse) => {
          if (networkResponse && networkResponse.status === 200) {
            const copy = networkResponse.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(request, copy));
          }
          return networkResponse;
        })
        .catch(() => {
          return caches.match(request)
            .then((cachedResponse) => {
              if (cachedResponse) {
                return cachedResponse;
              }
              return caches.match('index.html')
                .then((fallback) => fallback || caches.match('./'));
            });
        })
    );
    return;
  }

  // Strategy 2: Opportunity Catalog / Data JSON (Network-First with Cache Fallback)
  // Ensures students receive the latest opportunities when online,
  // while falling back seamlessly to cached opportunities when offline.
  if (url.pathname.endsWith('.json') || url.pathname.includes('/data/')) {
    event.respondWith(
      fetch(request)
        .then((networkResponse) => {
          if (networkResponse && networkResponse.status === 200) {
            const copy = networkResponse.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(request, copy));
          }
          return networkResponse;
        })
        .catch(() => {
          return caches.match(request)
            .then((cachedResponse) => {
              if (cachedResponse) {
                return cachedResponse;
              }
              // If specific JSON is not found, fallback to cached opportunities.json
              return caches.match('data/opportunities.json');
            });
        })
    );
    return;
  }

  // Network-first for UI scripts/styles ensures language fixes are received online.
  // Cached assets still allow offline usage.
  event.respondWith(
    fetch(request).then((response) => {
      if (response && response.ok) {
        const copy = response.clone();
        event.waitUntil(caches.open(CACHE_NAME).then(cache => cache.put(request, copy)));
      }
      return response;
    }).catch(() => caches.match(request))
  );
});
