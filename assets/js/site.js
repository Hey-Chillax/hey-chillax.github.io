// Language switch, e-mail link and the table-of-contents highlight. The initial language is set by a small
// inline script in <head> (saved choice, otherwise the browser language), so the page never flashes the wrong one.
(function () {
  var root = document.documentElement;

  function save(key, value) {
    try { localStorage.setItem(key, value); } catch (e) { /* private mode: keep the choice for this page only */ }
  }

  function setLang(lang) {
    root.setAttribute('data-lang', lang);
    root.setAttribute('lang', lang === 'zh' ? 'zh-CN' : 'en');
    var title = root.getAttribute('data-title-' + lang);
    if (title) document.title = title;
    var buttons = document.querySelectorAll('.lang-toggle');
    for (var i = 0; i < buttons.length; i++) {
      buttons[i].setAttribute('aria-label', lang === 'zh' ? 'Switch to English' : '切换到中文');
    }
  }

  document.addEventListener('click', function (event) {
    var toggle = event.target.closest('.lang-toggle');
    if (toggle) {
      var next = root.getAttribute('data-lang') === 'zh' ? 'en' : 'zh';
      setLang(next);
      save('lang', next);
    }
  });

  // The page source holds the address in two parts ("name [at] domain" without JavaScript),
  // so simple scrapers do not find it; readers see and click a normal address.
  var mails = document.querySelectorAll('[data-mail-u]');
  for (var m = 0; m < mails.length; m++) {
    var el = mails[m];
    var addr = el.getAttribute('data-mail-u') + '@' + el.getAttribute('data-mail-d');
    if (el.tagName === 'A') el.setAttribute('href', 'mailto:' + addr);
    var text = el.querySelector('.addr');
    if (text) text.textContent = addr;
  }

  // Highlight the section being read in the side table of contents (project pages).
  var tocLinks = document.querySelectorAll('.toc-side a[href^="#"]');
  if (tocLinks.length && 'IntersectionObserver' in window) {
    var byId = {};
    for (var t = 0; t < tocLinks.length; t++) byId[tocLinks[t].getAttribute('href').slice(1)] = tocLinks[t];
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        for (var k in byId) byId[k].classList.remove('active');
        var link = byId[entry.target.id];
        if (link) link.classList.add('active');
      });
    }, { rootMargin: '-30% 0px -60% 0px' });
    for (var id in byId) {
      var section = document.getElementById(id);
      if (section) observer.observe(section);
    }
  }

  setLang(root.getAttribute('data-lang') === 'zh' ? 'zh' : 'en');
})();
