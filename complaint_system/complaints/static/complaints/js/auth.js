// Password visibility toggle
document.addEventListener('DOMContentLoaded', function () {
    // Password toggle buttons
    const passwordToggles = document.querySelectorAll('.password-toggle');

    passwordToggles.forEach(toggle => {
        toggle.addEventListener('click', function () {
            const input = this.parentElement.querySelector('input');
            if (!input) return;

            const isPassword = input.type === 'password';
            input.type = isPassword ? 'text' : 'password';

            // Update icon
            const icon = this.querySelector('svg');
            if (icon) {
                if (isPassword) {
                    // Show eye-off icon
                    icon.innerHTML = '<path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/>';
                } else {
                    // Show eye icon
                    icon.innerHTML = '<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle>';
                }
            }
        });
    });

    // Real-time password validation
    const passwordInputs = document.querySelectorAll('input[type="password"], input.password-input');

    passwordInputs.forEach(input => {
        if (input.name === 'password1' || input.name === 'password') {
            input.addEventListener('input', function () {
                validatePassword(this);
            });
        }

        if (input.name === 'password2' || input.name === 'confirmPassword') {
            input.addEventListener('input', function () {
                validatePasswordMatch(this);
            });
        }
    });

    // Form validation on blur
    const formInputs = document.querySelectorAll('.auth-form input, .auth-form textarea');
    formInputs.forEach(input => {
        input.addEventListener('blur', function () {
            validateField(this);
        });
    });
});

function validatePassword(input) {
    const password = input.value;
    const minLength = 8;
    const hasUpperCase = /[A-Z]/.test(password);
    const hasNumber = /[0-9]/.test(password);
    const hasSymbol = /[!@#$%^&*(),.?":{}|<>]/.test(password);

    // Remove existing error/success classes
    input.classList.remove('error', 'success');

    if (password.length === 0) {
        return;
    }

    if (password.length >= minLength && hasUpperCase && hasNumber && hasSymbol) {
        input.classList.add('success');
    } else {
        input.classList.add('error');
    }
}

function validatePasswordMatch(input) {
    const passwordInput = document.querySelector('input[name="password1"], input[name="password"]');
    if (!passwordInput) return;

    const password = passwordInput.value;
    const confirmPassword = input.value;

    input.classList.remove('error', 'success');

    if (confirmPassword.length === 0) {
        return;
    }

    if (password === confirmPassword && password.length > 0) {
        input.classList.add('success');
    } else {
        input.classList.add('error');
    }
}

function validateField(input) {
    const value = input.value.trim();
    const name = input.name;

    input.classList.remove('error', 'success');

    if (value.length === 0) {
        return;
    }

    // Basic validation
    if (name === 'username' && value.length < 3) {
        input.classList.add('error');
        return;
    }

    if (name === 'contact' || name === 'contactNumber') {
        const contactRegex = /^\+?[\d\s-()]+$/;
        if (!contactRegex.test(value) || value.length < 10) {
            input.classList.add('error');
            return;
        }
    }

    input.classList.add('success');
}

