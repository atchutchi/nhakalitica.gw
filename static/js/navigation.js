document.querySelectorAll("[data-public-menu-toggle]").forEach((button) => {
  const menu = document.querySelector("[data-public-menu]");
  if (!menu) return;
  const close = () => {
    button.setAttribute("aria-expanded", "false");
    menu.classList.remove("is-open");
    button.querySelector(".visually-hidden").textContent = button.dataset.openLabel;
  };
  button.addEventListener("click", () => {
    const willOpen = button.getAttribute("aria-expanded") !== "true";
    button.setAttribute("aria-expanded", String(willOpen));
    menu.classList.toggle("is-open", willOpen);
    button.querySelector(".visually-hidden").textContent = willOpen
      ? button.dataset.closeLabel
      : button.dataset.openLabel;
    if (willOpen) menu.querySelector("a")?.focus();
  });
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      close();
      button.focus();
    }
  });
});
