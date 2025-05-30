const themeToggleBtn = document.getElementById('btn-theme-toggle');
const themeIcon = document.getElementById('theme-icon');
const htmlTag = document.documentElement;

const savedTheme = localStorage.getItem('bs-theme');
if (savedTheme) {
  htmlTag.setAttribute('data-bs-theme', savedTheme);
  updateIcon(savedTheme);
}

themeToggleBtn.addEventListener('click', () => {
  let currentTheme = htmlTag.getAttribute('data-bs-theme');
  let newTheme = currentTheme === 'light' ? 'dark' : 'light';
  htmlTag.setAttribute('data-bs-theme', newTheme);
  localStorage.setItem('bs-theme', newTheme);
  updateIcon(newTheme);
});

function updateIcon(theme) {
  if (theme === 'dark') {
    themeIcon.classList.remove('bi-moon-fill');
    themeIcon.classList.add('bi-sun-fill');
  } else {
    themeIcon.classList.remove('bi-sun-fill');
    themeIcon.classList.add('bi-moon-fill');
  }
}
