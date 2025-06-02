const themeToggleBtns = document.querySelectorAll('.theme-toggle-btn');
const themeIcons = document.querySelectorAll('.theme-toggle-icon');
const htmlTag = document.documentElement;

function updateIcons(theme) {
    themeIcons.forEach(icon => {
        if (theme === 'dark') {
            icon.classList.remove('bi-moon-fill');
            icon.classList.add('bi-sun-fill');
        } else {
            icon.classList.remove('bi-sun-fill');
            icon.classList.add('bi-moon-fill');
        }
    });
}

// Проверяем системную тему
const prefersDarkScheme = window.matchMedia('(prefers-color-scheme: dark)').matches;
const defaultTheme = prefersDarkScheme ? 'dark' : 'light';

// Загружаем сохранённую тему или используем системную
const savedTheme = localStorage.getItem('bs-theme');
const initialTheme = savedTheme || defaultTheme;
htmlTag.setAttribute('data-bs-theme', initialTheme);
updateIcons(initialTheme);

themeToggleBtns.forEach(button => {
    button.addEventListener('click', () => {
        let currentTheme = htmlTag.getAttribute('data-bs-theme');
        let newTheme = currentTheme === 'light' ? 'dark' : 'light';
        htmlTag.setAttribute('data-bs-theme', newTheme);
        localStorage.setItem('bs-theme', newTheme);
        updateIcons(newTheme);
    });
});