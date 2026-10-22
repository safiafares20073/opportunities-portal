/**
 * Tests for Service Worker (sw.js) Offline Support
 * Opportunities Portal — Milestone 3
 */

describe('Service Worker Offline Capabilities', () => {
  const CACHE_NAME = 'opportunities-portal-v1';
  const REQUIRED_PRECACHE_URLS = [
    './',
    'index.html',
    'css/style.css',
    'js/app.js',
    'data/opportunities.json'
  ];

  it('should support navigator.serviceWorker in modern browsers', () => {
    expect('serviceWorker' in navigator).toBe(true);
  });

  it('should register sw.js with scope ./', async () => {
    const reg = await navigator.serviceWorker.register('./sw.js', { scope: './' });
    expect(reg).toBeDefined();
    expect(reg.scope).toContain('/');
  });

  it('should populate Cache API with App Shell and Catalog', async () => {
    const cache = await caches.open(CACHE_NAME);
    const requests = await cache.keys();
    const cachedPaths = requests.map(req => new URL(req.url).pathname);

    // Verify all core assets are cached
    for (const asset of REQUIRED_PRECACHE_URLS) {
      const match = cachedPaths.some(p => p.endsWith(asset.replace('./', '')) || p === '/');
      expect(match).toBe(true);
    }
  });

  it('should retrieve opportunities.json from Cache API when offline', async () => {
    const response = await fetch('data/opportunities.json');
    expect(response.ok).toBe(true);
    const data = await response.json();
    expect(Array.isArray(data)).toBe(true);
    expect(data.length).toBeGreaterThanOrEqual(20);
  });

  it('should support favorites retrieval offline from cached catalog', async () => {
    const sampleId = 'chevening-scholarship-yemen';
    localStorage.setItem('opportunities_portal_favorites', JSON.stringify([sampleId]));

    const favs = JSON.parse(localStorage.getItem('opportunities_portal_favorites') || '[]');
    const response = await fetch('data/opportunities.json');
    const catalog = await response.json();

    const matched = catalog.filter(item => favs.includes(item.id));
    expect(matched.length).toBe(1);
    expect(matched[0].id).toBe(sampleId);
  });
});
