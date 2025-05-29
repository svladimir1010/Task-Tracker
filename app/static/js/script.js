// Код выполняется после полной загрузки DOM
document.addEventListener('DOMContentLoaded', () => {

    // 🔒 ВАЛИДАЦИЯ ФОРМЫ РЕГИСТРАЦИИ
    const registerForm = document.querySelector('#register-form');
    if (registerForm) {
        registerForm.addEventListener('submit', (e) => {
            const username = document.querySelector('#username').value;
            const email = document.querySelector('#email').value;
            const password = document.querySelector('#password').value;
            let errors = [];

            // Проверка: имя пользователя должно быть не короче 3 символов
            if (username.length < 3) {
                errors.push('Username must be at least 3 characters long');
            }

            // Простая проверка email на наличие "@" и ограничение длины
            if (!email.includes('@') || email.length > 120) {
                errors.push('Please enter a valid email');
            }

            // Пароль не должен быть короче 6 символов
            if (password.length < 6) {
                errors.push('Password must be at least 6 characters long');
            }

            // Если есть ошибки — отменяем отправку формы и показываем alert
            if (errors.length > 0) {
                e.preventDefault(); // Остановка отправки формы
                alert(errors.join('\n')); // Показываем ошибки
            }
        });
    }

    // 🔑 ВАЛИДАЦИЯ ФОРМЫ ВХОДА
    const loginForm = document.querySelector('#login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', (e) => {
            const username = document.querySelector('#username').value;
            const password = document.querySelector('#password').value;
            let errors = [];

            // Проверка имени пользователя
            if (username.length < 3) {
                errors.push('Username must be at least 3 characters long');
            }

            // Проверка длины пароля
            if (password.length < 6) {
                errors.push('Password must be at least 6 characters long');
            }

            // Отмена отправки формы, если есть ошибки
            if (errors.length > 0) {
                e.preventDefault();
                alert(errors.join('\n'));
            }
        });
    }

    // ✅ ВАЛИДАЦИЯ ФОРМЫ ДОБАВЛЕНИЯ ЗАДАЧИ
    const taskForm = document.querySelector('#task-form');
    if (taskForm) {
        taskForm.addEventListener('submit', (e) => {
            const title = document.querySelector('#title').value;

            // Заголовок задачи обязателен
            if (title.length === 0) {
                e.preventDefault();
                alert('Title is required');
            }
        });
    }

});
