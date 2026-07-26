(() => {
  const button = document.querySelector("[data-onboarding-menu]");
  const sidebar = document.querySelector("[data-onboarding-sidebar]");
  if (!button || !sidebar) return;
  button.addEventListener("click", () => {
    const open = sidebar.classList.toggle("is-open");
    button.setAttribute("aria-expanded", String(open));
  });
})();
