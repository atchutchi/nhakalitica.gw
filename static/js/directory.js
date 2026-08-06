(() => {
  const menuButton = document.querySelector("[data-member-menu]");
  const mobileNav = document.querySelector("[data-member-mobile-nav]");
  if (menuButton && mobileNav) {
    menuButton.addEventListener("click", () => {
      const open = mobileNav.classList.toggle("is-open");
      menuButton.setAttribute("aria-expanded", String(open));
      menuButton.querySelector(".visually-hidden").textContent = open
        ? menuButton.dataset.closeLabel
        : menuButton.dataset.openLabel;
    });
  }
  const filterButton = document.querySelector("[data-filter-toggle]");
  const filters = document.querySelector("[data-directory-filters]");
  if (filterButton && filters) {
    filterButton.addEventListener("click", () => {
      const open = filters.classList.toggle("is-open");
      filterButton.setAttribute("aria-expanded", String(open));
    });
  }
})();
