// Fills in the latest release, stars and forks under each repository link in
// the header (overrides/partials/source.html), the way Material does for its
// single one. Each repository is cached for the session under its own key.
(function () {
  "use strict";

  function count(n) {
    if (n < 1000) return String(n);
    return (n / 1000).toFixed(n < 10000 ? 1 : 0).replace(/\.0$/, "") + "k";
  }

  function getJSON(url) {
    return fetch(url).then(function (r) {
      return r.ok ? r.json() : null;
    }).catch(function () {
      return null;
    });
  }

  // The header and the mobile drawer both carry the links: fetch each once.
  var pending = {};

  function facts(repo) {
    return pending[repo] || (pending[repo] = load(repo));
  }

  function load(repo) {
    var key = "ntre-source:" + repo;
    try {
      var cached = sessionStorage.getItem(key);
      if (cached) return Promise.resolve(JSON.parse(cached));
    } catch (e) { /* storage blocked: fetch every time */ }
    var api = "https://api.github.com/repos/" + repo;
    return Promise.all([getJSON(api + "/releases/latest"), getJSON(api)]).then(function (r) {
      var f = {};
      if (r[0] && r[0].tag_name) f.version = r[0].tag_name;
      if (r[1]) {
        f.stars = count(r[1].stargazers_count);
        f.forks = count(r[1].forks_count);
        try { sessionStorage.setItem(key, JSON.stringify(f)); } catch (e) { /* ignore */ }
      }
      return f;
    });
  }

  function mount(link) {
    var target = link.querySelector(".md-source__repository");
    facts(link.dataset.ntreSource).then(function (f) {
      var names = Object.keys(f);
      if (!names.length) return;
      var list = document.createElement("ul");
      list.className = "md-source__facts";
      names.forEach(function (name) {
        var item = document.createElement("li");
        item.className = "md-source__fact md-source__fact--" + name;
        item.textContent = f[name];
        list.appendChild(item);
      });
      target.appendChild(list);
      target.classList.add("md-source__repository--active");
    });
  }

  document.querySelectorAll("[data-ntre-source]").forEach(mount);
})();
