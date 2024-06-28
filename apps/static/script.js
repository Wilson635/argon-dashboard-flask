document.addEventListener('DOMContentLoaded', (event) => {
    const submitBtn = document.getElementById('submit-btn');
    const usernameField = document.getElementById('username');
    const passwordField = document.getElementById('password');
    const emailField = document.getElementById('email');
    const roleField = document.getElementById('role');
    const initialPosition = { left: submitBtn.style.left, top: submitBtn.style.top };

    submitBtn.addEventListener('mouseover', () => {
        if (!usernameField.value || !passwordField.value || !emailField.value || !roleField.value) {
            moveButton();
        }
    });

    function moveButton() {
        const container = document.querySelector('.container');
        const containerRect = container.getBoundingClientRect();
        const btnRect = submitBtn.getBoundingClientRect();

        let newLeft = Math.random() * (containerRect.width - btnRect.width);
        let newTop = Math.random() * (containerRect.height - btnRect.height);

        submitBtn.style.position = 'absolute';
        submitBtn.style.left = `${newLeft}px`;
        submitBtn.style.top = `${newTop}px`;
    }

    function resetButtonPosition() {
        submitBtn.style.position = 'static';
    }

    usernameField.addEventListener('input', () => {
        if (usernameField.value && passwordField.value && emailField.value && roleField.value) {
            resetButtonPosition();
        }
    });

    passwordField.addEventListener('input', () => {
        if (usernameField.value && passwordField.value && emailField.value && roleField.value) {
            resetButtonPosition();
        }
    });

    emailField.addEventListener('input', () => {
        if (usernameField.value && passwordField.value && emailField.value && roleField.value) {
            resetButtonPosition();
        }
    });

    roleField.addEventListener('input', () => {
        if (usernameField.value && passwordField.value && emailField.value && roleField.value) {
            resetButtonPosition();
        }
    });
});
