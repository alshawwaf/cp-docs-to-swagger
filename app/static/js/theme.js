/**
 * Theme Management Logic
 * Handles toggling between light and dark modes and persisting preference.
 */

// Apply theme IMMEDIATELY to prevent flash (before DOM loads)
(function() {
  const savedTheme = localStorage.getItem("theme");
  // Default to dark mode if no preference is saved
  if (savedTheme === "light") {
    // Only set light mode if explicitly chosen
    document.documentElement.removeAttribute("data-theme");
  } else {
    // Default to dark mode (savedTheme is null or "dark")
    document.documentElement.setAttribute("data-theme", "dark");
  }
})();

document.addEventListener("DOMContentLoaded", () => {
  const themeToggle = document.getElementById("theme-toggle");
  const htmlElement = document.documentElement;

  // Check for saved preference and sync toggle state
  // Default to dark mode if no saved preference
  const savedTheme = localStorage.getItem("theme");
  
  if (savedTheme === "light") {
    if (themeToggle) themeToggle.checked = false;
  } else {
    // Default to dark (savedTheme is null or "dark")
    if (themeToggle) themeToggle.checked = true;
  }

  // Toggle event listener
  if (themeToggle) {
    themeToggle.addEventListener("change", (e) => {
      if (e.target.checked) {
        htmlElement.setAttribute("data-theme", "dark");
        localStorage.setItem("theme", "dark");
      } else {
        htmlElement.removeAttribute("data-theme");
        localStorage.setItem("theme", "light");
      }
    });
  }
});

