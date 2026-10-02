// Site navigation with a Products drop-down, shared by every page.
// To add a platform or app, edit PLATFORMS below; every page picks it up.
(function () {
  const PLATFORMS = [
    {
      name: "iPhone & iPad",
      apps: [
        { name: "Meduo", blurb: "Family health records", href: "/meduo/", icon: "/assets/images/icons/meduo.png" },
        { name: "BudgetXP+", blurb: "Personal finance", href: "/budgetxp/", icon: "/assets/images/icons/budgetxp-personal-finance.jpg" },
        { name: "MealBound", blurb: "Meal planning and grocery lists", href: "/mealbound/", icon: "/assets/images/icons/mealbound.jpg" },
      ],
    },
    {
      name: "Mac",
      apps: [
        { name: "BudgetXP+ Desktop", blurb: "Personal finance for macOS", href: "/budgetxp/desktop/", icon: "/assets/images/icons/budgetxp-personal-finance.jpg" },
        { name: "Scumble", blurb: "Painting app, coming soon", href: null, icon: null },
      ],
    },
    {
      name: "Games",
      apps: [
        { name: "Fox Dash", blurb: "Endless runner for iPhone and iPad", href: "/foxdash/", icon: "/assets/images/icons/fox-dash.jpg" },
      ],
    },
    // {
    //   name: "Windows",
    //   apps: [
    //     { name: "App name", blurb: "Short description", href: "https://apps.microsoft.com/…", icon: "/assets/images/icons/….png" },
    //   ],
    // },
    // {
    //   name: "Android",
    //   apps: [
    //     { name: "App name", blurb: "Short description", href: "https://play.google.com/store/apps/details?id=…", icon: "/assets/images/icons/….png" },
    //   ],
    // },
  ];

  const LINKS = [
    { name: "Meduo", href: "/meduo/" },
    { name: "Support", href: "/support/" },
  ];

  const nav = document.getElementById("site-nav");
  if (!nav) return;

  const path = location.pathname;
  const current = (href) => (href === "/" ? path === "/" : path.startsWith(href)) ? ' aria-current="page"' : "";
  const esc = (s) => s.replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);

  const appItem = (app) => {
    const icon = app.icon
      ? `<img class="nav-app-icon" src="${app.icon}" alt="" width="32" height="32">`
      : `<span class="nav-app-icon blank" aria-hidden="true">${esc(app.name[0])}</span>`;
    const body = `${icon}<span class="nav-app-text"><span class="nav-app-name">${esc(app.name)}</span><span class="nav-app-blurb">${esc(app.blurb)}</span></span>`;
    return app.href
      ? `<li><a class="nav-app" href="${app.href}"${current(app.href)}>${body}</a></li>`
      : `<li><span class="nav-app disabled">${body}</span></li>`;
  };

  nav.innerHTML = `
    <div class="wrap nav-bar">
      <a class="brand" href="/">Rohr Software</a>
      <ul class="nav-links">
        <li><button class="nav-products" type="button" aria-expanded="false" aria-controls="nav-panel">Products<span class="chev" aria-hidden="true"></span></button></li>
        ${LINKS.map((l) => `<li><a href="${l.href}"${current(l.href)}>${l.name}</a></li>`).join("")}
      </ul>
      <button class="nav-menu" type="button" aria-expanded="false" aria-controls="nav-panel" aria-label="Menu"><span></span><span></span></button>
    </div>
    <div class="nav-panel" id="nav-panel" hidden>
      <div class="wrap nav-panel-inner">
        ${PLATFORMS.map((p) => `
          <section class="nav-col">
            <h2 class="nav-col-title">${esc(p.name)}</h2>
            <ul>${p.apps.map(appItem).join("")}</ul>
          </section>`).join("")}
        <section class="nav-col nav-col-links">
          <h2 class="nav-col-title">More</h2>
          <ul class="nav-plain">
            <li><a href="/#apps">All apps</a></li>
            ${LINKS.map((l) => `<li><a href="${l.href}">${l.name}</a></li>`).join("")}
          </ul>
        </section>
      </div>
    </div>`;

  const scrim = document.createElement("div");
  scrim.className = "nav-scrim";
  scrim.hidden = true;
  nav.after(scrim);

  const panel = nav.querySelector(".nav-panel");
  const toggles = nav.querySelectorAll(".nav-products, .nav-menu");
  const productsBtn = nav.querySelector(".nav-products");
  const hoverCapable = window.matchMedia("(hover: hover) and (pointer: fine)");
  let closeTimer;
  let openedAt = 0;

  const setOpen = (open) => {
    clearTimeout(closeTimer);
    if (open && panel.hidden) openedAt = Date.now();
    panel.hidden = !open;
    scrim.hidden = !open;
    nav.classList.toggle("open", open);
    toggles.forEach((t) => t.setAttribute("aria-expanded", String(open)));
  };
  const isOpen = () => !panel.hidden;

  // A click that lands right after hover opened the menu shouldn't close it again.
  toggles.forEach((t) => t.addEventListener("click", () => {
    if (isOpen() && Date.now() - openedAt < 400) return;
    setOpen(!isOpen());
  }));
  scrim.addEventListener("click", () => setOpen(false));
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && isOpen()) { setOpen(false); productsBtn.focus(); }
  });

  // Desktop: open on hover like apple.com, with a short delay before closing.
  const hoverOpen = () => { if (hoverCapable.matches) setOpen(true); };
  const hoverClose = () => { if (hoverCapable.matches) closeTimer = setTimeout(() => setOpen(false), 180); };
  productsBtn.parentElement.addEventListener("mouseenter", hoverOpen);
  productsBtn.parentElement.addEventListener("mouseleave", hoverClose);
  panel.addEventListener("mouseenter", () => clearTimeout(closeTimer));
  panel.addEventListener("mouseleave", hoverClose);
})();
