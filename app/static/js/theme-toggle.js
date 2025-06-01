// Получаем все кнопки переключения темы по их общему классу
const themeToggleBtns = document.querySelectorAll('.theme-toggle-btn');
// Получаем все иконки темы по их общему классу
const themeIcons = document.querySelectorAll('.theme-toggle-icon');
const htmlTag = document.documentElement;

// Функция для обновления иконок на всех кнопках
function updateIcons(theme) {
  themeIcons.forEach(icon => { // Перебираем все найденные иконки
    if (theme === 'dark') {
      icon.classList.remove('bi-moon-fill');
      icon.classList.add('bi-sun-fill');
    } else {
      icon.classList.remove('bi-sun-fill');
      icon.classList.add('bi-moon-fill');
    }
  });
}

// Загружаем сохраненную тему при загрузке страницы
const savedTheme = localStorage.getItem('bs-theme');
if (savedTheme) {
  htmlTag.setAttribute('data-bs-theme', savedTheme);
  updateIcons(savedTheme); // Используем новую функцию updateIcons
} else {
  // Если тема не сохранена, устанавливаем тему по умолчанию (например, light)
  // и обновляем иконки соответственно
  // Это важно, чтобы иконка соответствовала начальной теме, если она не была сохранена
  updateIcons(htmlTag.getAttribute('data-bs-theme') || 'light');
}


// Добавляем обработчик события клика ко всем кнопкам переключения темы
themeToggleBtns.forEach(button => {
  button.addEventListener('click', () => {
    let currentTheme = htmlTag.getAttribute('data-bs-theme');
    let newTheme = currentTheme === 'light' ? 'dark' : 'light';
    htmlTag.setAttribute('data-bs-theme', newTheme);
    localStorage.setItem('bs-theme', newTheme);
    updateIcons(newTheme); // Используем новую функцию updateIcons
  });
});