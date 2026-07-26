document.querySelectorAll("[data-confirm-action]").forEach((button) => {
  button.addEventListener("click", (event) => {
    if (!window.confirm(button.dataset.confirmAction)) event.preventDefault();
  });
});
