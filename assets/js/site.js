// Language switch and e-mail link. The initial language is set by a small inline script in <head>
// (saved choice, otherwise the browser language) so the page never flashes the wrong language.
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
      return;
    }
    // The address is written as "name [at] domain" in the page; it is assembled only on click.
    var mail = event.target.closest('[data-mail-u]');
    if (mail) {
      event.preventDefault();
      window.location.href = 'mailto:' + mail.getAttribute('data-mail-u') + '@' + mail.getAttribute('data-mail-d');
    }
  });

  setLang(root.getAttribute('data-lang') === 'zh' ? 'zh' : 'en');
})();
