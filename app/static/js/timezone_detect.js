// 📅 Автоматическое определение часового пояса
    document.addEventListener('DOMContentLoaded', function() {
        // Получаем часовой пояс пользователя и устанавливаем его в скрытое поле формы
        const userTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
        const timezoneField = document.getElementById('user_timezone_input')

        if (timezoneField) {
        timezoneField.value = userTimezone;
    }

    });
