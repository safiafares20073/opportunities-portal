/* Bilingual presentation and theme settings. No network services or external libraries. */
(() => {
  'use strict';
  const LANG_KEY = 'opportunities_portal_language';
  const THEME_KEY = 'opportunities_portal_theme';
  const langButton = document.getElementById('language-toggle');
  const themeButton = document.getElementById('theme-toggle');
  if (!langButton || !themeButton) return;

  const arToEn = new Map(Object.entries({
    'بوابة الفرص':'Opportunities Portal',
    'استكشف المنح الدراسية والدورات والتدريب المهني':'Explore scholarships, courses and internships',
    'جميع الفرص':'All opportunities','المحفوظات':'Favorites',
    'نوع الفرصة':'Opportunity type','المجال والتخصص':'Field and major',
    'المستوى الدراسي':'Study level','الدولة / الوجهة':'Country / destination',
    'حالة التقديم':'Application status','جميع الأنواع':'All types',
    'ابحث بالاسم، المؤسسة، التخصص، أو الكلمات المفتاحية...':'Search by opportunity, organization, field or keyword...',
    'ابحث بالاسم أو التخصص أو الجهة...':'Search by title, field or provider...',
    'الوقت المتبقي':'Time remaining','الموعد النهائي':'Deadline',
    'تعلم مرن / تحقق من التسجيل':'Self-paced / check enrollment',
    'يختلف حسب دورة التقديم':'Depends on application cycle',
    'موعد غير محدد':'Deadline not specified','موعد غير صالح':'Invalid deadline',
    'تحقق من التقديم':'Check application period',
    'تاريخ مراجعة الصفحة الرسمية:':'Official source reviewed:',
    'تاريخ مراجعة الصفحة الرسمية':'Official source review date',
    'إعادة تعيين البحث والمرشحات':'Reset search and filters',
    'البرنامج غير مؤكد / معلّق':'Program suspended or unconfirmed',
    'يحتاج التحقق من التقديم':'Check current application status',
    'الانتقال إلى الموقع الرسمي لـ':'Visit the official website for ',
    'تفعيل الوضع الداكن':'Enable dark mode',
    'الوضع الداكن':'Dark mode','الوضع الفاتح':'Light mode',
    'إغلاق نافذة التفاصيل':'Close details',
    'جميع الأنواع':'All types',
    'جميع التخصصات':'All fields','جميع المستويات':'All levels',
    'جميع الوجهات':'All destinations','جميع الحالات':'All statuses',
    'بكالوريوس':'Bachelor’s','ماجستير':'Master’s','دكتوراه':'PhD',
    'منحة دراسية':'Scholarship','دورة تدريبية':'Course','تدريب عملي':'Internship',
    'متاحة':'Open','متاحة (مستمرة)':'Open (ongoing)',
    'تغلق قريبًا':'Closing soon','منتهية':'Closed','إعادة تعيين المرشحات':'Reset filters',
    'التفاصيل':'Details','المجال / التخصص':'Field / major','التخصص:':'Field:',
    'الدولة / الوجهة':'Country / destination','الوجهة:':'Destination:',
    'نطاق التمويل':'Funding','التمويل:':'Funding:',
    'آخر موعد للتقديم':'Application deadline','آخر موعد:':'Deadline:',
    'المستوى الدراسي':'Study level', 'الجهة':'Organization', 'تفاصيل المنحة':'Scholarship details',
    'شروط الأهلية':'Eligibility','حالة التحقق والتقديم':'Application information',
    'تفاصيل الفرصة':'Opportunity details','زيارة المصدر الرسمي':'Visit official source',
    'حفظ':'Save','محفوظة':'Saved','انتهى التقديم':'Applications closed',
    'تاريخ مراجعة الصفحة الرسمية:':'Official page review date:',
    'لا توجد فرص متاحة حالياً':'No opportunities available at the moment',
    'جاري تحميل الفرص...':'Loading opportunities...',
    'خطأ في تحميل البيانات':'Unable to load opportunities',
    'لا توجد فرص محفوظة':'No saved opportunities',
    'لا توجد فرص محفوظة بعد':'No favorites yet',
    'لم تقم بحفظ أي فرصة حتى الآن. اضغط على أيقونة القلب على أي بطاقة لحفظها هنا للرجوع إليها لاحقاً دون اتصال بالإنترنت.':'You have not saved any opportunities yet. Select the heart icon on an opportunity card to save it here and access its details offline.',
    'لم نتمكن من العثور على أي فرصة تطابق خيارات البحث الحالية. يرجى تجربة كلمات بحث أخرى أو إلغاء بعض المرشحات.':'No opportunities match your current search. Try different keywords or remove some filters.',
    'يجري حالياً التحقق اليدوي والمستقل من صحة المنح والفرص وفق أعلى معايير الموثوقية. سيتم إدراج الفرص المعتمدة فور اكتمال مراجعتها.':'Opportunities are being reviewed against their official sources. Verified listings will appear here after review.',
    'استعراض جميع الفرص':'Browse all opportunities',
    'لم يتم العثور على فرص مطابقة':'No matching opportunities found',
    'لا توجد فرص منشورة حالياً':'No opportunities published yet',
    'العلوم السياسية والاجتماعية':'Political and social sciences',
    'العلوم الاجتماعية والعلاقات الدولية':'Social sciences and international relations',
    'الذكاء الاصطناعي والروبوتات':'Artificial intelligence and robotics',
    'الفيزياء الفلكية والفلك':'Astrophysics and astronomy',
    'علم الفلك والفيزياء الكونية':'Astronomy and cosmological physics',
    'البرمجة':'Programming','الأمن السيبراني':'Cybersecurity',
    'تقنية المعلومات':'Information technology','تحليل البيانات':'Data analytics',
    'تطوير الويب':'Web development','قواعد البيانات':'Databases',
    'علوم الحاسوب':'Computer science',
    'تخصصات البكالوريوس المتاحة':'Undergraduate programs',
    'جميع التخصصات المتاحة للبكالوريوس':'Undergraduate programs',
    'التخصصات الجامعية المتاحة':'University undergraduate programs',
    'دراسات الصين متعددة التخصصات':'Interdisciplinary Chinese studies',
    'برامج جامعية متعددة التخصصات':'Multiple university degree programs',
    'الفلك والفيزياء الفلكية':'Astronomy and astrophysics',
    'العلوم السياسية والاجتماعية والعلاقات الدولية':'Politics, social sciences and international relations',
    'كندا':'Canada','فرنسا':'France','ألمانيا':'Germany',
    'الصين':'China','الولايات المتحدة':'United States',
    'المملكة المتحدة':'United Kingdom','عبر الإنترنت':'Online',
    'مجانية للتعلم عبر الإنترنت':'Free online learning',
    'التعلم والمشروعات والشهادة مجانًا':'Free lessons, projects and certification',
    'التعلم عبر OpenCourseWare مجاني؛ الشهادات لها شروط خاصة':'Free OpenCourseWare learning; separate certificate conditions apply',
    'إزالة من المحفوظات':'Remove from favorites','حفظ الفرصة':'Save opportunity',
    'إغلاق نافذة التفاصيل':'Close opportunity details',
    'تصفية حسب نوع الفرصة':'Filter by opportunity type',
    'تصفية حسب المجال':'Filter by field',
    'تصفية حسب المستوى الدراسي':'Filter by academic level',
    'تصفية حسب الدولة':'Filter by country',
    'تصفية حسب حالة التقديم':'Filter by application status',
    'البحث في الفرص':'Search opportunities',
    'ابحث بالاسم، المؤسسة، التخصص، أو الكلمات المفتاحية...':'Search by title, organization, field, or keywords...',
    'عرض الفرص':'Opportunity views','أدوات البحث والتصفية':'Search and filters',
    'تنبيه بشأن حالة الفرص':'Opportunity information',
    'عرض جميع الفرص':'Show all opportunities',
    'جميع الدول':'All countries','دورات مجانية':'Free courses',
    'المصدر الرسمي':'Official source',
    'التقديم الآن':'Apply now',
    'الجهة المقدمة':'Provider',
    'الدولة':'Country',
    'فرصة':'opportunity',
    'مسح حقل البحث':'Clear search',
    'بوابة الفرص © 2026 | فرص تعليمية ومنح دراسية للطلاب في اليمن':'Opportunities Portal © 2026 | Scholarships and courses for students in Yemen',
    'تضم البوابة 10 منح دراسية للبكالوريوس والماجستير والدكتوراه، و10 دورات تعليمية عبر منصات رسمية. تعرض المواعيد المعلنة لكل منحة، وتخضع أهلية المتقدمين لشروط الجهة المانحة وإجراءات القبول. راجع رابط المصدر الرسمي قبل التقديم.':'The portal lists 10 scholarships for bachelor’s, master’s and PhD applicants plus 10 courses from official providers. Deadlines and eligibility are defined by each institution. Check the official source before applying.'
  }));
  const records = new Map();
  const originalAttrs = new WeakMap();
  function lookup(value) {
    const raw = value.trim();
    if (!raw) return value;
    if (arToEn.has(raw)) return value.replace(raw, arToEn.get(raw));
    if (/^عرض\s+\d+\s+من\s+أصل\s+\d+\s+فرصة/.test(raw)) {
      const nums = raw.match(/\d+/g) || [];
      return `Showing ${nums[0]} of ${nums[1]} ${raw.includes('محفوظة') ? 'saved ' : ''}opportunities`;
    }
    let m = raw.match(/^عرض (\d+) من أصل (\d+) فرصة(?: محفوظة)?$/);
    if (m) return `Showing ${m[1]} of ${m[2]} ${raw.includes('محفوظة') ? 'saved ' : ''}opportunities`;
    m = raw.match(/^تغلق قريبًا \((?:باقي (\d+) يوم|اليوم)\)$/);
    if (m) return m[1] ? `Closing soon (${m[1]} days left)` : 'Closing today';
    // Dynamic labels inserted by the application after initial page load.
    m = raw.match(/^باقي (\d+) يوم(?:ًا)?$/);
    if (m) return `${m[1]} days left`;
    if (raw === 'اليوم') return 'Today';
    if (raw === 'غير محدد') return 'Not specified';
    if (raw.startsWith('الانتقال إلى الموقع الرسمي لـ')) return 'Visit official website for ' + (titleTranslation.get(raw.slice('الانتقال إلى الموقع الرسمي لـ'.length)) || raw.slice('الانتقال إلى الموقع الرسمي لـ'.length));
    if (raw.startsWith('عرض تفاصيل ')) return 'View details: ' + (titleTranslation.get(raw.slice('عرض تفاصيل '.length)) || raw.slice('عرض تفاصيل '.length));
    // Translation of scholarships and courses uses the official English title in the dataset.
    if (titleTranslation.has(raw)) return titleTranslation.get(raw);
    if (eligibilityTranslation.has(raw)) return eligibilityTranslation.get(raw);
    if (coverageTranslation.has(raw)) return coverageTranslation.get(raw);
    if (raw.startsWith('تاريخ مراجعة الصفحة الرسمية:')) return value.replace('تاريخ مراجعة الصفحة الرسمية:', 'Official page reviewed:');
    return value;
  }
  const titleTranslation = new Map();
  const eligibilityTranslation = new Map();
  const coverageTranslation = new Map();
  const perOpportunityCoverage = {
    'sciences-po-boutmy-bachelor-2027':'Full tuition waiver or approximately $10,673 annually (depending on award tier; approximate USD value).',
    'sciences-po-boutmy-master-2027':'Tuition waiver worth approximately $20,785 per year for two years (USD equivalent).',
    'ubc-international-scholars-2027':'Need- and merit-based support that may cover demonstrated financial need.',
    'vanderbilt-ingram-2027':'Full tuition, plus additional support under Ingram program conditions; USD value varies with tuition.',
    'vanderbilt-cornelius-2027':'Full tuition, with additional support for selected activities; USD value varies with tuition.',
    'yenching-academy-master-2027':'Tuition, accommodation, monthly stipend, airfare and field-study support; no single USD amount published.',
    'imprs-intelligent-systems-phd-2027':'Funded research employment; salary depends on the individual offer.',
    'imprs-astrophysics-munich-2027':'Funded doctoral research position; salary depends on the individual employment offer.',
    'imprs-astronomy-heidelberg-2027':'Funded doctoral research position; salary depends on project and employment offer.',
    'ubc-international-major-entrance-2027':'Partial merit scholarship of approximately $7,119–$17,797 per year (USD exchange-rate estimate as of 21 October 2026).'
  };
  const requestedLang = (() => { try { return localStorage.getItem(LANG_KEY) === 'en' ? 'en' : 'ar'; } catch { return 'ar'; } })();
  let currentLang = requestedLang;
  let currentTheme = (() => { try { return localStorage.getItem(THEME_KEY) === 'dark' ? 'dark' : 'light'; } catch { return 'light'; } })();
  let busy = false;
  function indexDataset(data) {
    if (!Array.isArray(data)) return;
    for (const item of data) {
      if (item.title_ar && item.title_en) titleTranslation.set(item.title_ar, item.title_en);
      if (item.eligibility_ar && item.eligibility_en) eligibilityTranslation.set(item.eligibility_ar, item.eligibility_en);
      if (item.coverage && perOpportunityCoverage[item.id]) coverageTranslation.set(item.coverage, perOpportunityCoverage[item.id]);
    }
  }
  // The app fetches this JSON to populate cards. Read a local copy solely for translations.
  fetch(document.body.getAttribute('data-source') || 'data/opportunities.json')
    .then(r => r.ok ? r.json() : [])
    .then(data => { indexDataset(data); if (currentLang === 'en') translateDocument(); })
    .catch(() => {});

  function translateDocument() {
    if (busy) return;
    busy = true;
    document.documentElement.lang = currentLang;
    document.documentElement.dir = currentLang === 'en' ? 'ltr' : 'rtl';
    const langCaptionTop = currentLang === 'en' ? 'العربية' : 'English';
    if (langButton.textContent !== langCaptionTop) langButton.textContent = langCaptionTop;
    langButton.setAttribute('aria-pressed', String(currentLang === 'en'));
    try {
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    let node;
    while ((node = walker.nextNode())) {
      if (node.parentElement && ['SCRIPT','STYLE','NOSCRIPT'].includes(node.parentElement.tagName)) continue;
      const now = node.nodeValue;
      const previous = records.get(node);
      const original = previous && (now === previous.en || now === previous.ar) ? previous.ar : now;
      const english = lookup(original);
      records.set(node, { ar: original, en: english });
      const desired = currentLang === 'en' ? english : original;
      if (now !== desired) node.nodeValue = desired;
    }
    for (const element of document.querySelectorAll('[placeholder],[aria-label]')) {
      for (const attr of ['placeholder','aria-label']) {
        if (!element.hasAttribute(attr)) continue;
        let saved = originalAttrs.get(element);
        if (!saved) { saved = {}; originalAttrs.set(element, saved); }
        if (!(attr in saved)) saved[attr] = element.getAttribute(attr);
        const original = saved[attr];
        const translated = currentLang === 'en' ? lookup(original) : original;
        if (element.getAttribute(attr) !== translated) element.setAttribute(attr, translated);
      }
    }
    // Explicitly synchronize fields that browsers / dynamic option rebuilds can leave stale.
    const searchField = document.getElementById('search-input');
    if (searchField) {
      searchField.placeholder = currentLang === 'en'
        ? 'Search by title, university, major or keywords...'
        : 'ابحث بالاسم، المؤسسة، التخصص، أو الكلمات المفتاحية...';
      searchField.setAttribute('aria-label', currentLang === 'en' ? 'Search opportunities' : 'البحث في الفرص');
    }
    const statusSelect = document.getElementById('filter-status');
    if (statusSelect) {
      for (const opt of statusSelect.options) {
        const labels = {
          '': ['جميع الحالات', 'All statuses'],
          'متاحة': ['متاحة', 'Open'],
          'تغلق قريبًا': ['تغلق قريبًا', 'Closing soon'],
          'منتهية': ['منتهية', 'Closed']
        };
        if (Object.prototype.hasOwnProperty.call(labels, opt.value)) {
          opt.textContent = labels[opt.value][currentLang === 'en' ? 1 : 0];
        }
      }
    }
    const statusTitle = document.querySelector('label[for="filter-status"]');
    if (statusTitle) statusTitle.textContent = currentLang === 'en' ? 'Application deadline' : 'حالة التقديم';
    document.documentElement.lang = currentLang;
    document.documentElement.dir = currentLang === 'en' ? 'ltr' : 'rtl';
    document.title = currentLang === 'en' ? 'Opportunities Portal — Yemen' : 'بوابة الفرص — للطلاب والشباب في اليمن';
    const languageCaption = currentLang === 'en' ? 'العربية' : 'English';
    if (langButton.textContent !== languageCaption) langButton.textContent = languageCaption;
    const langLabel = currentLang === 'en' ? 'Switch to Arabic' : 'Switch to English';
    if (langButton.getAttribute('aria-label') !== langLabel) langButton.setAttribute('aria-label', langLabel);
    if (langButton.getAttribute('aria-pressed') !== String(currentLang === 'en')) langButton.setAttribute('aria-pressed', String(currentLang === 'en'));
    const themeCaption = currentTheme === 'dark' ? (currentLang === 'en' ? '☀ Light mode' : '☀ الوضع الفاتح') : (currentLang === 'en' ? '☾ Dark mode' : '☾ الوضع الداكن');
    if (themeButton.textContent !== themeCaption) themeButton.textContent = themeCaption;
    const themeLabel = currentLang === 'en' ? 'Toggle dark mode' : 'تبديل الوضع الداكن';
    if (themeButton.getAttribute('aria-label') !== themeLabel) themeButton.setAttribute('aria-label',themeLabel);
    } finally { busy = false; }
  }
  function setTheme() {
    document.documentElement.dataset.theme = currentTheme;
    themeButton.setAttribute('aria-pressed', String(currentTheme === 'dark'));
    translateDocument();
  }
  langButton.addEventListener('click', () => {
    currentLang = currentLang === 'ar' ? 'en' : 'ar';
    try { localStorage.setItem(LANG_KEY,currentLang); } catch {}
    observer.disconnect();
    translateDocument();
    observer.observe(document.body, { childList: true, subtree: true, characterData: true });
  });
  themeButton.addEventListener('click', () => {
    currentTheme = currentTheme === 'light' ? 'dark' : 'light';
    try { localStorage.setItem(THEME_KEY,currentTheme); } catch {}
    setTheme();
  });
  let translationScheduled = false;
  const observer = new MutationObserver(() => {
    if (currentLang !== 'en' || busy || translationScheduled) return;
    translationScheduled = true;
    queueMicrotask(() => {
      translationScheduled = false;
      if (currentLang === 'en' && !busy) {
        observer.disconnect();
        translateDocument();
        observer.observe(document.body, { childList: true, subtree: true, characterData: true });
      }
    });
  });
  observer.observe(document.body, { childList: true, subtree: true, characterData: true });
  document.addEventListener('opportunities:updated', () => {
    if (currentLang !== 'en') return;
    observer.disconnect();
    translateDocument();
    observer.observe(document.body, {childList:true,subtree:true,characterData:true});
  });
  setTheme();
})();
