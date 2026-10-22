/**
 * Opportunities Portal — Client-Side Application Engine
 * Mobile-First Arabic RTL • Instant Search • Multi-Criteria Filtering
 * Milestone 2: Details Modal (US3) • Favorites / localStorage (US5)
 * Zero External Dependencies (Vanilla ES6+)
 */

(function () {
  'use strict';

  // ── Storage Key ─────────────────────────────────────────────────────────────
  const FAVORITES_KEY = 'opportunities_portal_favorites';

  // ── Application State ────────────────────────────────────────────────────────
  const state = {
    allOpportunities: [],
    filteredOpportunities: [],
    favorites: new Set(),          // Set of opportunity IDs stored in localStorage
    viewMode: 'all',               // 'all' | 'favorites'
    activeFilters: {
      query: '',
      category: '',
      field: '',
      country: '',
      level: '',
      status: ''
    },
    dataSource: 'data/opportunities.json',
    isTestHarness: false
  };

  // ── Category Arabic Labels ───────────────────────────────────────────────────
  const CATEGORY_MAP = {
    Scholarship: { label: 'منحة دراسية', className: 'scholarship' },
    Course:      { label: 'دورة تدريبية', className: 'course' },
    Internship:  { label: 'تدريب عملي',  className: 'internship' }
  };

  // ── DOM Elements Cache ───────────────────────────────────────────────────────
  const elements = {};

  // ============================================================================
  // FAVORITES — localStorage persistence
  // ============================================================================

  function loadFavorites() {
    try {
      const raw = localStorage.getItem(FAVORITES_KEY);
      if (raw) {
        const arr = JSON.parse(raw);
        if (Array.isArray(arr)) {
          state.favorites = new Set(arr.map(String));
        }
      }
    } catch (e) {
      // localStorage may be blocked in private browsing; fail gracefully
      state.favorites = new Set();
    }
  }

  function saveFavorites() {
    try {
      localStorage.setItem(FAVORITES_KEY, JSON.stringify(Array.from(state.favorites)));
    } catch (e) {
      // Quota exceeded or blocked — silently ignore
    }
  }

  function isFavorite(id) {
    return state.favorites.has(String(id));
  }

  function toggleFavorite(id) {
    const sid = String(id);
    if (state.favorites.has(sid)) {
      state.favorites.delete(sid);
    } else {
      state.favorites.add(sid);
    }
    saveFavorites();
    updateFavoritesBadge();

    // Update the bookmark button's aria-pressed and visual state on the live card
    const btn = document.querySelector(`.btn-bookmark[data-id="${CSS.escape(sid)}"]`);
    if (btn) {
      btn.setAttribute('aria-pressed', String(state.favorites.has(sid)));
      btn.classList.toggle('bookmarked', state.favorites.has(sid));
    }

    // If we are in favorites view and the item was just removed, re-render
    if (state.viewMode === 'favorites') {
      filterOpportunities();
    }
  }

  function updateFavoritesBadge() {
    const count = state.favorites.size;
    if (elements.favoritesCountBadge) {
      elements.favoritesCountBadge.textContent = count;
      elements.favoritesCountBadge.style.display = count > 0 ? 'inline-flex' : 'none';
    }
  }

  // ============================================================================
  // DETAILS MODAL — US3
  // ============================================================================

  /**
   * Build the modal body HTML for a single opportunity.
   * All user-supplied strings go through escapeHtml().
   */
  function buildModalHTML(item) {
    const deadlineInfo = calculateDeadlineStatus(item.deadline, item.category);
    if (item.review_status === 'programme_suspended_or_unconfirmed') {
      Object.assign(deadlineInfo, { status: 'تحقق من التقديم', badgeClass: 'status-unknown', label: 'البرنامج غير مؤكد / معلّق', isExpired: false });
    } else if (item.review_status === 'needs_manual_verification') {
      Object.assign(deadlineInfo, { status: 'تحقق من التقديم', badgeClass: 'status-unknown', label: 'يحتاج التحقق من التقديم', isExpired: false });
    }
    const categoryInfo = CATEGORY_MAP[item.category] || {
      label: item.category || 'أخرى',
      className: 'default'
    };
    const deadlineFormatted =
      item.deadline === 'Rolling'
        ? (item.category === 'Course' ? 'تعلم مرن / تحقق من التسجيل' : 'يختلف حسب دورة التقديم')
        : escapeHtml(item.deadline) || '—';

    const favored = isFavorite(item.id);

    return `
      <!-- Category + Status row -->
      <div class="modal-meta-row">
        <span class="category-pill ${categoryInfo.className}">${escapeHtml(categoryInfo.label)}</span>
        <span class="status-badge ${deadlineInfo.badgeClass}" role="status">${escapeHtml(deadlineInfo.label)}</span>
      </div>

      <!-- Arabic Title -->
      <h3 class="modal-opportunity-title">${escapeHtml(item.title_ar)}</h3>

      <!-- English Title (bilingual) -->
      ${item.title_en ? `<p class="modal-title-en" dir="ltr"><bdi>${escapeHtml(item.title_en)}</bdi></p>` : ''}

      <!-- Organization -->
      <div class="modal-org">
        <svg class="org-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
          <rect x="4" y="2" width="16" height="20" rx="2" ry="2"></rect>
          <path d="M9 22v-4h6v4"></path>
          <path d="M8 6h.01"></path><path d="M16 6h.01"></path><path d="M12 6h.01"></path>
          <path d="M12 10h.01"></path><path d="M12 14h.01"></path>
          <path d="M16 10h.01"></path><path d="M16 14h.01"></path>
          <path d="M8 10h.01"></path><path d="M8 14h.01"></path>
        </svg>
        <span><bdi>${escapeHtml(item.organization)}</bdi></span>
      </div>

      <!-- Key Facts Table -->
      <dl class="modal-facts">
        <div class="modal-fact-row">
          <dt>المجال / التخصص</dt>
          <dd>${escapeHtml(item.field) || '—'}</dd>
        </div>
        <div class="modal-fact-row">
          <dt>الدولة / الوجهة</dt>
          <dd><bdi>${escapeHtml(countryLabel(item.country)) || '—'}</bdi></dd>
        </div>
        <div class="modal-fact-row">
          <dt>نطاق التمويل</dt>
          <dd>${escapeHtml(item.coverage) || '—'}</dd>
        </div>
        <div class="modal-fact-row">
          <dt>آخر موعد للتقديم</dt>
          <dd dir="ltr">${deadlineFormatted}</dd>
        </div>
      </dl>

      <!-- Eligibility (Arabic — primary language) -->
      ${item.eligibility_ar ? `
      <div class="modal-section">
        <h4 class="modal-section-heading">شروط الأهلية</h4>
        <p class="modal-section-text">${escapeHtml(item.eligibility_ar)}</p>
      </div>` : ''}

      ${item.review_note_ar ? `<div class="modal-section"><h4 class="modal-section-heading">حالة التحقق والتقديم</h4><p class="modal-section-text">${escapeHtml(item.review_note_ar)}</p></div>` : ''}
      <!-- Verification Badge -->
      <div class="modal-verification">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
          <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
          <polyline points="22 4 12 14.01 9 11.01"></polyline>
        </svg>
        <span>تاريخ مراجعة الصفحة الرسمية:
          <time datetime="${escapeHtml(item.verification_date || '')}">
            <bdi>${escapeHtml(item.verification_date) || 'غير محدد'}</bdi>
          </time>
        </span>
      </div>

      <!-- Action Buttons -->
      <div class="modal-actions">
        <a href="${escapeHtml(safeOfficialUrl(item.official_url))}"
           target="_blank"
           rel="noopener noreferrer"
           class="btn-apply modal-btn-apply ${deadlineInfo.isExpired ? 'disabled' : ''}"
           aria-label="الانتقال إلى الموقع الرسمي لـ${escapeHtml(item.title_ar)}">
          <span>${deadlineInfo.isExpired ? 'انتهى التقديم' : 'زيارة المصدر الرسمي'}</span>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path>
            <polyline points="15 3 21 3 21 9"></polyline>
            <line x1="10" y1="14" x2="21" y2="3"></line>
          </svg>
        </a>

        <button type="button"
                class="btn-bookmark-modal ${favored ? 'bookmarked' : ''}"
                data-id="${escapeHtml(String(item.id))}"
                aria-pressed="${favored}"
                aria-label="${favored ? 'إزالة من المحفوظات' : 'حفظ الفرصة'}">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="${favored ? 'currentColor' : 'none'}" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path>
          </svg>
          <span>${favored ? 'محفوظة' : 'حفظ'}</span>
        </button>
      </div>
    `;
  }

  function openModal(item) {
    if (!elements.modal || !elements.modalBody || !elements.modalTitle) return;

    elements.modalBody.innerHTML = buildModalHTML(item);

    // Wire the in-modal bookmark button
    const modalBookmarkBtn = elements.modalBody.querySelector('.btn-bookmark-modal');
    if (modalBookmarkBtn) {
      modalBookmarkBtn.addEventListener('click', () => {
        toggleFavorite(item.id);
        // Rebuild modal button state without closing modal
        const favored = isFavorite(item.id);
        modalBookmarkBtn.setAttribute('aria-pressed', String(favored));
        modalBookmarkBtn.classList.toggle('bookmarked', favored);
        modalBookmarkBtn.setAttribute(
          'aria-label', favored ? 'إزالة من المحفوظات' : 'حفظ الفرصة'
        );
        const svgPath = modalBookmarkBtn.querySelector('svg');
        if (svgPath) svgPath.setAttribute('fill', favored ? 'currentColor' : 'none');
        const span = modalBookmarkBtn.querySelector('span');
        if (span) span.textContent = favored ? 'محفوظة' : 'حفظ';
      });
    }

    // Show modal
    elements.modal.style.display = 'flex';
    elements.modal.setAttribute('aria-hidden', 'false');
    document.body.classList.add('modal-open');

    // Focus close button for keyboard accessibility
    requestAnimationFrame(() => {
      if (elements.modalCloseBtn) elements.modalCloseBtn.focus();
    });
  }

  function closeModal() {
    if (!elements.modal) return;
    elements.modal.style.display = 'none';
    elements.modal.setAttribute('aria-hidden', 'true');
    document.body.classList.remove('modal-open');

    // Return focus to last-focused card's details button
    if (state._lastFocusedCardBtn) {
      state._lastFocusedCardBtn.focus();
      state._lastFocusedCardBtn = null;
    }
  }

  function setupModalEventListeners() {
    // Close button
    if (elements.modalCloseBtn) {
      elements.modalCloseBtn.addEventListener('click', closeModal);
    }

    // Click outside panel
    if (elements.modal) {
      elements.modal.addEventListener('click', (e) => {
        if (e.target === elements.modal) closeModal();
      });
    }

    // Escape key
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && elements.modal &&
          elements.modal.getAttribute('aria-hidden') === 'false') {
        closeModal();
      }
    });
  }

  // ============================================================================
  // UTILITY FUNCTIONS
  // ============================================================================

  /**
   * Normalize Arabic text for forgiving keyword search
   */
  function normalizeArabic(text) {
    if (!text) return '';
    return text
      .toString()
      .toLowerCase()
      // Remove Arabic diacritics (tashkeel)
      .replace(/[\u064B-\u0652\u0670]/g, '')
      // Unify Alef forms
      .replace(/[إأآا]/g, 'ا')
      // Unify Yeh and Alef Maksura
      .replace(/[يى]/g, 'ي')
      // Unify Teh Marbuta and Heh
      .replace(/[ةه]/g, 'ه')
      .trim();
  }

  /**
   * Calculate Deadline Status
   * Returns: { status, badgeClass, label, isExpired }
   * Strict Arabic badges: "متاحة", "تغلق قريبًا", "منتهية"
   */
  function calculateDeadlineStatus(deadlineStr, category) {
    // A seasonal scholarship or internship has an application cycle, not a
    // guaranteed year-round open call. Never infer availability from "Rolling".
    if (deadlineStr === 'Rolling' && category && category !== 'Course') {
      return {
        status: 'تحقق من التقديم',
        badgeClass: 'status-unknown',
        label: 'تحقق من فترة التقديم',
        isExpired: false
      };
    }
    if (!deadlineStr) {
      return { status: 'تحقق من التقديم', badgeClass: 'status-unknown', label: 'موعد غير محدد', isExpired: false };
    }
    if (deadlineStr === 'Rolling') {
      return {
        status: 'متاحة',
        badgeClass: 'status-active',
        label: 'متاحة (مستمرة)',
        isExpired: false
      };
    }

    const today = new Date();
    today.setHours(0, 0, 0, 0);

    const deadlineDate = new Date(deadlineStr);
    deadlineDate.setHours(0, 0, 0, 0);

    if (isNaN(deadlineDate.getTime())) {
      return { status: 'تحقق من التقديم', badgeClass: 'status-unknown', label: 'موعد غير صالح', isExpired: false };
    }

    const diffTime = deadlineDate.getTime() - today.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

    if (diffDays < 0) {
      return {
        status: 'منتهية',
        badgeClass: 'status-expired',
        label: 'منتهية',
        isExpired: true
      };
    } else if (diffDays <= 14) {
      const daysText = diffDays === 0 ? 'اليوم' : `باقي ${diffDays} يوم`;
      return {
        status: 'تغلق قريبًا',
        badgeClass: 'status-closing',
        label: `تغلق قريبًا (${daysText})`,
        isExpired: false
      };
    } else {
      return {
        status: 'متاحة',
        badgeClass: 'status-active',
        label: 'متاحة',
        isExpired: false
      };
    }
  }

  /**
   * Escape HTML to prevent injection
   */
  function escapeHtml(str) {
    if (!str) return '';
    return str
      .toString()
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  /** Accept absolute public HTTPS links only; reject embedded credentials and malformed URLs. */
  function safeOfficialUrl(value) {
    if (typeof value !== 'string' || /[\x00-\x1f\x7f]/.test(value)) return '#';
    try {
      const url = new URL(value);
      if (url.protocol !== 'https:' || !url.hostname || url.username || url.password) return '#';
      return url.href;
    } catch (_) { return '#'; }
  }

  // ============================================================================
  // FILTER DROPDOWNS
  // ============================================================================

  const COUNTRY_AR = {
    'France': 'فرنسا', 'Canada': 'كندا', 'United States': 'الولايات المتحدة',
    'China': 'الصين', 'Germany': 'ألمانيا', 'Online': 'عبر الإنترنت',
    'United Kingdom': 'المملكة المتحدة', 'Japan': 'اليابان'
  };

  function countryLabel(country) { return COUNTRY_AR[country] || country; }

  // Consistent filter groups. Keep the source field in each opportunity's details.
  // Broad fields are grouped only for discovery, not as claims that every major is eligible.
  function fieldGroup(field) {
    const normalized = normalizeArabic(String(field || '')).trim();
    const broad = [
      'تخصصات البكالوريوس المتاحة', 'جميع التخصصات المتاحة للبكالوريوس',
      'التخصصات الجامعية المتاحة', 'جميع تخصصات الجامعة',
      'جميع التخصصات المتاحة في الجامعة', 'دراسات الصين متعددة التخصصات'
    ];
    if (broad.some(v => normalizeArabic(v) === normalized)) return 'برامج جامعية متعددة التخصصات';
    if (/الفلك|الفيزياء الفلكيه|الفيزياء الكونيه/.test(normalized)) return 'الفلك والفيزياء الفلكية';
    if (/العلوم السياسيه|العلوم الاجتماعيه|العلاقات الدوليه/.test(normalized)) return 'العلوم السياسية والاجتماعية والعلاقات الدولية';
    return field || '';
  }

  function getStudyLevel(item) {
    if (item.category !== 'Scholarship') return '';
    const name = normalizeArabic(`${item.title_ar || ''} ${item.title_en || ''}`).toLowerCase();
    if (/دكتوراه|phd|doctoral|doktor/.test(name)) return 'phd';
    if (/ماجستير|master|graduate|yenching/.test(name)) return 'master';
    if (/بكالوريوس|undergraduate|bachelor|ingram|vanderbilt|ubc/.test(name)) return 'bachelor';
    return '';
  }

  function populateFilterDropdowns(opportunities) {
    const categories = new Set();
    const fields = new Set();
    const countries = new Set();

    opportunities.forEach((item) => {
      if (item.category) categories.add(item.category);
      if (item.field) fields.add(fieldGroup(item.field));
      if (item.country) countries.add(item.country);
    });

    populateSelect(elements.filterCategory, Array.from(categories), (cat) => {
      return (CATEGORY_MAP[cat] && CATEGORY_MAP[cat].label) || cat;
    });
    populateSelect(elements.filterField, Array.from(fields).sort((a, b) => a.localeCompare(b, 'ar')));
    populateSelect(elements.filterCountry, Array.from(countries).sort(), (country) => COUNTRY_AR[country] || country);
  }

  function populateSelect(selectElem, items, labelFn) {
    if (!selectElem) return;
    const currentVal = selectElem.value;
    const firstOption = selectElem.options[0];
    selectElem.innerHTML = '';
    if (firstOption) selectElem.appendChild(firstOption);

    items.forEach((item) => {
      const option = document.createElement('option');
      option.value = item;
      option.textContent = labelFn ? labelFn(item) : item;
      selectElem.appendChild(option);
    });

    if (currentVal && items.includes(currentVal)) {
      selectElem.value = currentVal;
    }
  }

  // ============================================================================
  // FILTER & SEARCH ENGINE
  // ============================================================================

  function filterOpportunities() {
    const { query, category, field, country, level, status } = state.activeFilters;
    const normalizedQuery = normalizeArabic(query);

    let pool = state.allOpportunities;

    // In favorites view, restrict pool to saved items only
    if (state.viewMode === 'favorites') {
      pool = pool.filter((item) => isFavorite(item.id));
    }

    state.filteredOpportunities = pool.filter((item) => {
      if (category && item.category !== category) return false;
      if (field && fieldGroup(item.field) !== field) return false;
      if (country && item.country !== country) return false;
      if (level && getStudyLevel(item) !== level) return false;

      if (status) {
        const deadlineInfo = calculateDeadlineStatus(item.deadline, item.category);
    if (item.review_status === 'programme_suspended_or_unconfirmed') {
      Object.assign(deadlineInfo, { status: 'تحقق من التقديم', badgeClass: 'status-unknown', label: 'البرنامج غير مؤكد / معلّق', isExpired: false });
    } else if (item.review_status === 'needs_manual_verification') {
      Object.assign(deadlineInfo, { status: 'تحقق من التقديم', badgeClass: 'status-unknown', label: 'يحتاج التحقق من التقديم', isExpired: false });
    }
        if (deadlineInfo.status !== status) return false;
      }

      if (normalizedQuery) {
        const searchableText = normalizeArabic(
          [
            item.title_ar,
            item.title_en,
            item.organization,
            item.field,
            item.country,
            item.coverage,
            item.eligibility_ar,
            item.eligibility_en
          ].join(' ')
        );
        if (!searchableText.includes(normalizedQuery)) return false;
      }

      return true;
    });

    renderUI();
  }

  // ============================================================================
  // CARD RENDERER
  // ============================================================================

  function createCardElement(item) {
    const deadlineInfo = calculateDeadlineStatus(item.deadline, item.category);
    if (item.review_status === 'programme_suspended_or_unconfirmed') {
      Object.assign(deadlineInfo, { status: 'تحقق من التقديم', badgeClass: 'status-unknown', label: 'البرنامج غير مؤكد / معلّق', isExpired: false });
    } else if (item.review_status === 'needs_manual_verification') {
      Object.assign(deadlineInfo, { status: 'تحقق من التقديم', badgeClass: 'status-unknown', label: 'يحتاج التحقق من التقديم', isExpired: false });
    }
    const categoryInfo = CATEGORY_MAP[item.category] || {
      label: item.category || 'أخرى',
      className: 'default'
    };
    const favored = isFavorite(item.id);

    const card = document.createElement('article');
    card.className = 'opportunity-card';
    card.setAttribute('data-id', item.id || '');

    const deadlineFormatted =
      item.deadline === 'Rolling'
        ? (item.category === 'Course' ? 'تعلم مرن / تحقق من التسجيل' : 'يختلف حسب دورة التقديم')
        : escapeHtml(item.deadline);

    card.innerHTML = `
      <div>
        <div class="card-header">
          <span class="category-pill ${categoryInfo.className}">
            ${escapeHtml(categoryInfo.label)}
          </span>
          <span class="status-badge ${deadlineInfo.badgeClass}" role="status">
            ${escapeHtml(deadlineInfo.label)}
          </span>
        </div>

        <h3 class="card-title">
          ${escapeHtml(item.title_ar)}
        </h3>

        <div class="card-organization">
          <svg class="org-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <rect x="4" y="2" width="16" height="20" rx="2" ry="2"></rect>
            <path d="M9 22v-4h6v4"></path>
            <path d="M8 6h.01"></path><path d="M16 6h.01"></path><path d="M12 6h.01"></path>
            <path d="M12 10h.01"></path><path d="M12 14h.01"></path>
            <path d="M16 10h.01"></path><path d="M16 14h.01"></path>
            <path d="M8 10h.01"></path><path d="M8 14h.01"></path>
          </svg>
          <span><bdi>${escapeHtml(item.organization)}</bdi></span>
        </div>

        <ul class="card-meta-list">
          <li class="card-meta-item">
            <span class="meta-label">التخصص:</span>
            <span class="meta-value" title="${escapeHtml(item.field)}">${escapeHtml(item.field)}</span>
          </li>
          <li class="card-meta-item">
            <span class="meta-label">الوجهة:</span>
            <span class="meta-value" title="${escapeHtml(countryLabel(item.country))}"><bdi>${escapeHtml(countryLabel(item.country))}</bdi></span>
          </li>
          <li class="card-meta-item">
            <span class="meta-label">التمويل:</span>
            <span class="meta-value">${escapeHtml(item.coverage)}</span>
          </li>
          <li class="card-meta-item">
            <span class="meta-label">آخر موعد:</span>
            <span class="meta-value" dir="ltr">${deadlineFormatted}</span>
          </li>
        </ul>
      </div>

      <div class="card-footer">
        <!-- Details button opens modal -->
        <button type="button"
                class="btn-details"
                data-id="${escapeHtml(String(item.id))}"
                aria-label="عرض تفاصيل ${escapeHtml(item.title_ar)}">
          التفاصيل
        </button>

        <!-- Bookmark / Favorite button -->
        <button type="button"
                class="btn-bookmark ${favored ? 'bookmarked' : ''}"
                data-id="${escapeHtml(String(item.id))}"
                aria-pressed="${favored}"
                aria-label="${favored ? 'إزالة من المحفوظات' : 'حفظ الفرصة'}">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="${favored ? 'currentColor' : 'none'}" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path>
          </svg>
          <span class="sr-only">${favored ? 'محفوظة' : 'حفظ'}</span>
        </button>
      </div>
    `;

    // Wire details button
    const detailsBtn = card.querySelector('.btn-details');
    if (detailsBtn) {
      detailsBtn.addEventListener('click', () => {
        state._lastFocusedCardBtn = detailsBtn;
        openModal(item);
      });
    }

    // Wire bookmark button
    const bookmarkBtn = card.querySelector('.btn-bookmark');
    if (bookmarkBtn) {
      bookmarkBtn.addEventListener('click', () => {
        toggleFavorite(item.id);
      });
    }

    return card;
  }

  // ============================================================================
  // EMPTY STATE
  // ============================================================================

  function renderEmptyState(isInitialZero) {
    if (state.viewMode === 'favorites') {
      elements.emptyStateContainer.innerHTML = `
        <div class="empty-state-wrapper">
          <svg class="empty-state-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path>
          </svg>
          <h2 class="empty-state-title">لا توجد فرص محفوظة بعد</h2>
          <p class="empty-state-desc">
            لم تقم بحفظ أي فرصة حتى الآن. اضغط على أيقونة القلب على أي بطاقة لحفظها هنا للرجوع إليها لاحقاً دون اتصال بالإنترنت.
          </p>
          <button type="button" class="reset-filters-btn" id="show-all-btn">
            استعراض جميع الفرص
          </button>
        </div>
      `;
      elements.emptyStateContainer.style.display = 'block';
      const showAllBtn = document.getElementById('show-all-btn');
      if (showAllBtn) {
        showAllBtn.addEventListener('click', () => switchView('all'));
      }
      return;
    }

    if (isInitialZero) {
      elements.emptyStateContainer.innerHTML = `
        <div class="empty-state-wrapper">
          <svg class="empty-state-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
            <polyline points="14 2 14 8 20 8"></polyline>
            <line x1="16" y1="13" x2="8" y2="13"></line>
            <line x1="16" y1="17" x2="8" y2="17"></line>
            <polyline points="10 9 9 9 8 9"></polyline>
          </svg>
          <h2 class="empty-state-title">لا توجد فرص منشورة حالياً</h2>
          <p class="empty-state-desc">
            يجري حالياً التحقق اليدوي والمستقل من صحة المنح والفرص وفق أعلى معايير الموثوقية. سيتم إدراج الفرص المعتمدة فور اكتمال مراجعتها.
          </p>
        </div>
      `;
    } else {
      elements.emptyStateContainer.innerHTML = `
        <div class="empty-state-wrapper">
          <svg class="empty-state-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <circle cx="11" cy="11" r="8"></circle>
            <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
            <line x1="8" y1="11" x2="14" y2="11"></line>
          </svg>
          <h2 class="empty-state-title">لم يتم العثور على فرص مطابقة</h2>
          <p class="empty-state-desc">
            لم نتمكن من العثور على أي فرصة تطابق خيارات البحث الحالية. يرجى تجربة كلمات بحث أخرى أو إلغاء بعض المرشحات.
          </p>
          <button type="button" class="reset-filters-btn" id="empty-state-reset-btn">
            إعادة تعيين البحث والمرشحات
          </button>
        </div>
      `;
      const resetBtn = document.getElementById('empty-state-reset-btn');
      if (resetBtn) {
        resetBtn.addEventListener('click', resetFilters);
      }
    }
    elements.emptyStateContainer.style.display = 'block';
  }

  // ============================================================================
  // RENDER UI
  // ============================================================================

  function renderUI() {
    const totalAll = state.allOpportunities.length;
    const totalFiltered = state.filteredOpportunities.length;

    if (totalAll === 0) {
      elements.resultsCount.textContent = 'لا توجد فرص متاحة حالياً';
      elements.resetFiltersBtn.style.display = 'none';
      elements.gridContainer.innerHTML = '';
      renderEmptyState(true);
      return;
    }

    // Customize count text for favorites view
    if (state.viewMode === 'favorites') {
      const totalFaved = state.favorites.size;
      elements.resultsCount.textContent =
        totalFaved === 0
          ? 'لا توجد فرص محفوظة'
          : `عرض ${totalFiltered} من أصل ${totalFaved} فرصة محفوظة`;
    } else {
      elements.resultsCount.textContent = `عرض ${totalFiltered} من أصل ${totalAll} فرصة`;
    }

    const isFilterActive =
      state.activeFilters.query !== '' ||
      state.activeFilters.category !== '' ||
      state.activeFilters.field !== '' ||
      state.activeFilters.country !== '' ||
      state.activeFilters.level !== '' ||
      state.activeFilters.status !== '';

    elements.resetFiltersBtn.style.display = isFilterActive ? 'inline-flex' : 'none';

    if (totalFiltered === 0) {
      elements.gridContainer.innerHTML = '';
      renderEmptyState(false);
    } else {
      elements.emptyStateContainer.style.display = 'none';
      elements.gridContainer.innerHTML = '';
      const fragment = document.createDocumentFragment();
      state.filteredOpportunities.forEach((item) => {
        fragment.appendChild(createCardElement(item));
      });
      elements.gridContainer.appendChild(fragment);
    }
  }

  // ============================================================================
  // VIEW SWITCHING (All / Favorites)
  // ============================================================================

  function switchView(mode) {
    state.viewMode = mode;

    if (elements.tabAll) {
      elements.tabAll.classList.toggle('active', mode === 'all');
      elements.tabAll.setAttribute('aria-selected', String(mode === 'all'));
    }
    if (elements.tabFavorites) {
      elements.tabFavorites.classList.toggle('active', mode === 'favorites');
      elements.tabFavorites.setAttribute('aria-selected', String(mode === 'favorites'));
    }

    filterOpportunities();
  }

  // ============================================================================
  // RESET FILTERS
  // ============================================================================

  function resetFilters() {
    state.activeFilters = {
      query: '',
      category: '',
      field: '',
      country: '',
      level: '',
      status: ''
    };

    if (elements.searchInput) elements.searchInput.value = '';
    if (elements.searchClearBtn) elements.searchClearBtn.style.display = 'none';
    if (elements.filterCategory) elements.filterCategory.value = '';
    if (elements.filterField) elements.filterField.value = '';
    if (elements.filterCountry) elements.filterCountry.value = '';
    if (elements.filterLevel) elements.filterLevel.value = '';
    if (elements.filterStatus) elements.filterStatus.value = '';

    filterOpportunities();
  }

  // ============================================================================
  // DATA LOADING
  // ============================================================================

  async function loadOpportunities() {
    try {
      elements.resultsCount.textContent = 'جاري تحميل الفرص...';
      const response = await fetch(state.dataSource);
      if (!response.ok) {
        throw new Error(`HTTP Error ${response.status}`);
      }
      const data = await response.json();
      if (!Array.isArray(data)) {
        throw new Error('Invalid data format: Expected JSON array');
      }

      state.allOpportunities = data;
      populateFilterDropdowns(data);
      filterOpportunities();
    } catch (err) {
      console.error('Failed to load opportunities:', err);
      elements.resultsCount.textContent = 'خطأ في تحميل البيانات';
      elements.gridContainer.innerHTML = '';
      elements.emptyStateContainer.innerHTML = `
        <div class="empty-state-wrapper">
          <h2 class="empty-state-title">تعذر تحميل بيانات الفرص</h2>
          <p class="empty-state-desc">${escapeHtml(err.message)}</p>
        </div>
      `;
      elements.emptyStateContainer.style.display = 'block';
    }
  }

  // ============================================================================
  // EVENT LISTENERS
  // ============================================================================

  function setupEventListeners() {
    // Search input
    elements.searchInput.addEventListener('input', (e) => {
      state.activeFilters.query = e.target.value;
      elements.searchClearBtn.style.display = e.target.value ? 'flex' : 'none';
      filterOpportunities();
    });

    // Clear search
    elements.searchClearBtn.addEventListener('click', () => {
      elements.searchInput.value = '';
      elements.searchClearBtn.style.display = 'none';
      state.activeFilters.query = '';
      elements.searchInput.focus();
      filterOpportunities();
    });

    // Category filter
    elements.filterCategory.addEventListener('change', (e) => {
      state.activeFilters.category = e.target.value;
      filterOpportunities();
    });

    // Field filter
    elements.filterField.addEventListener('change', (e) => {
      state.activeFilters.field = e.target.value;
      filterOpportunities();
    });

    // Academic degree filter
    if (elements.filterLevel) elements.filterLevel.addEventListener('change', (e) => {
      state.activeFilters.level = e.target.value;
      filterOpportunities();
    });

    // Country filter
    elements.filterCountry.addEventListener('change', (e) => {
      state.activeFilters.country = e.target.value;
      filterOpportunities();
    });

    // Status filter
    elements.filterStatus.addEventListener('change', (e) => {
      state.activeFilters.status = e.target.value;
      filterOpportunities();
    });

    // Reset button
    elements.resetFiltersBtn.addEventListener('click', resetFilters);

    // View tabs
    if (elements.tabAll) {
      elements.tabAll.addEventListener('click', () => switchView('all'));
    }
    if (elements.tabFavorites) {
      elements.tabFavorites.addEventListener('click', () => switchView('favorites'));
    }

    // Modal
    setupModalEventListeners();
  }

  // ============================================================================
  // INITIALIZATION
  // ============================================================================

  function initApp(options = {}) {
    // Load persisted favorites before rendering anything
    loadFavorites();

    // Cache DOM elements
    elements.searchInput          = document.getElementById('search-input');
    elements.searchClearBtn       = document.getElementById('search-clear-btn');
    elements.filterCategory       = document.getElementById('filter-category');
    elements.filterField          = document.getElementById('filter-field');
    elements.filterCountry        = document.getElementById('filter-country');
    elements.filterLevel          = document.getElementById('filter-level');
    elements.filterStatus         = document.getElementById('filter-status');
    elements.resultsCount         = document.getElementById('results-count');
    elements.resetFiltersBtn      = document.getElementById('reset-filters-btn');
    elements.gridContainer        = document.getElementById('opportunities-grid');
    elements.emptyStateContainer  = document.getElementById('empty-state-container');
    elements.tabAll               = document.getElementById('tab-all');
    elements.tabFavorites         = document.getElementById('tab-favorites');
    elements.favoritesCountBadge  = document.getElementById('favorites-count-badge');
    elements.modal                = document.getElementById('details-modal');
    elements.modalBody            = document.getElementById('modal-body');
    elements.modalTitle           = document.getElementById('modal-title');
    elements.modalCloseBtn        = document.getElementById('modal-close-btn');

    // Determine data source
    const urlParams = new URLSearchParams(window.location.search);
    const dataParam = urlParams.get('data');
    if (dataParam) {
      state.dataSource = dataParam;
    } else if (options.dataSource) {
      state.dataSource = options.dataSource;
    }

    state.isTestHarness = Boolean(options.isTestHarness || urlParams.get('test'));

    // Sync badge count from restored localStorage
    updateFavoritesBadge();

    setupEventListeners();
    loadOpportunities();
  }

  // ── Public API ───────────────────────────────────────────────────────────────
  window.OpportunitiesApp = {
    init: initApp,
    calculateDeadlineStatus: calculateDeadlineStatus,
    normalizeArabic: normalizeArabic
  };

  // Register the offline cache only on a secure origin (HTTPS or localhost).
  if ('serviceWorker' in navigator &&
      (window.location.protocol === 'https:' ||
       ['localhost', '127.0.0.1'].includes(window.location.hostname))) {
    window.addEventListener('load', () => {
      navigator.serviceWorker.register('./sw.js', { scope: './' })
        .catch((error) => console.warn('Offline support is unavailable:', error));
    });
  }

  // Auto-init on DOMContentLoaded
  document.addEventListener('DOMContentLoaded', () => {
    const dataSourceAttr = document.body.getAttribute('data-source');
    const isTestHarness  = document.body.getAttribute('data-test-harness') === 'true';
    initApp({
      dataSource:    dataSourceAttr || undefined,
      isTestHarness: isTestHarness
    });
  });
})();
