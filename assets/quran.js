/* Shared helpers for every Quran app (owner, 2026-10-30): load the verified mushaf text from data/quran.json (never type
   ayat by hand), Arabic-Indic digits, and the light/dark toggle remembered on the device.
   Usage: <script src="../../assets/quran.js"></script> then  const q = await Quran.load();  q.ayah(2, 255); q.surah(1).name */
(function () {
  var cache = null;
  var base = (document.currentScript && document.currentScript.src) ? new URL('../', document.currentScript.src).href : '../../';

  function digits(n) { return String(n).replace(/\d/g, function (d) { return '٠١٢٣٤٥٦٧٨٩'[d]; }); }

  function load() {
    if (cache) return cache;
    cache = fetch(base + 'data/quran.json').then(function (r) {
      if (!r.ok) throw new Error('quran.json: ' + r.status);
      return r.json();
    }).then(function (list) {
      return {
        surahs: list,                                     // [{id, name, translit, type, ayat: [...]}] × 114
        surah: function (s) { return list[s - 1]; },
        ayah: function (s, a) { var x = list[s - 1]; return x ? x.ayat[a - 1] : undefined; },
        count: function (s) { return list[s - 1].ayat.length; }
      };
    });
    return cache;
  }

  var Theme = {
    key: 'quran-theme',
    init: function (button) {
      var root = document.documentElement;
      try { var saved = localStorage.getItem(Theme.key); if (saved) root.dataset.theme = saved; } catch (e) {}
      if (!button) return;
      button.addEventListener('click', function () {
        var dark = root.dataset.theme ? root.dataset.theme === 'dark' : matchMedia('(prefers-color-scheme: dark)').matches;
        root.dataset.theme = dark ? 'light' : 'dark';
        try { localStorage.setItem(Theme.key, root.dataset.theme); } catch (e) {}
      });
    }
  };

  window.Quran = { load: load, digits: digits, Theme: Theme, base: base };
})();
