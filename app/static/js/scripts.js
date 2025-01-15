// Пример простого скрипта для валидации формы регистрации
document.addEventListener('DOMContentLoaded', function() {
    const registerForm = document.querySelector('form[action="/register"]');
    if (registerForm) {
        registerForm.addEventListener('submit', function(event) {
            const username = registerForm.querySelector('input[name="username"]').value;
            const password = registerForm.querySelector('input[name="password"]').value;

            if (!username || !password) {
                alert('Username and password are required!');
                event.preventDefault(); // Предотвратить отправку формы
            }
        });
    }

    const loginForm = document.querySelector('form[action="/login"]');
    if (loginForm) {
        loginForm.addEventListener('submit', function(event) {
            const username = loginForm.querySelector('input[name="username"]').value;
            const password = loginForm.querySelector('input[name="password"]').value;

            if (!username || !password) {
                alert('Username and password are required!');
                event.preventDefault(); // Предотвратить отправку формы
            }
        });
    }
});