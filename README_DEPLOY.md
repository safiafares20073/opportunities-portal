# GitHub Pages Deployment | نشر بوابة الفرص

## 1. Publish project sources

Publish the contents of the project root (not the ZIP file itself) to the `opportunities-portal` GitHub repository, preserving the relative paths of `index.html`, `css/`, `js/`, `data/`, and `sw.js`.

In **Repository Settings → Pages → Build and deployment**, select **Deploy from a branch**, the branch holding the site files (such as `main`), and **/(root)**. Save and open the generated HTTPS URL.

## 2. Verify the public deployment

1. Confirm that the landing page loads the 20 opportunities and that filtering, search and modal details respond correctly.
2. Select Arabic and English, and light and dark themes; refresh to confirm preference persistence.
3. Save a favorite, close and reopen the page, and confirm that the item remains bookmarked.
4. Open the public page while online to populate the Service Worker cache. In browser developer tools set network to **Offline**, reload, then inspect the catalog and saved favorites.
5. Inspect the page at 360 CSS px and desktop widths for scrolling or clipped controls.
6. Check the browser console for errors and confirm that paths use the repository-relative base correctly.

## 3. Data and source checks

```bash
python scripts/validate_data.py
python scripts/test_release_smoke.py
```

Official programs can change deadlines or admissions policies. When updating `data/opportunities.json`, keep `DATA_AUDIT.md` aligned with the published records.
