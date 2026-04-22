// Toggle password visibility
function togglePassword(inputId) {
    const input = document.getElementById(inputId);
    const icon = input.parentElement.querySelector('.eye-icon');
    if (input.type === 'password') {
        input.type = 'text';
        if (icon) icon.style.opacity = '0.4';
    } else {
        input.type = 'password';
        if (icon) icon.style.opacity = '1';
    }
}

// Password strength checker (register page only)
const passwordInput = document.getElementById('password');
if (passwordInput && document.getElementById('strengthFill')) {
    passwordInput.addEventListener('input', function() {
        const password = this.value;
        const strengthFill = document.getElementById('strengthFill');
        const strengthText = document.getElementById('strengthText');

        let strength = 0;
        if (password.length >= 6) strength++;
        if (password.length >= 10) strength++;
        if (/[a-z]/.test(password) && /[A-Z]/.test(password)) strength++;
        if (/[0-9]/.test(password)) strength++;
        if (/[^a-zA-Z0-9]/.test(password)) strength++;

        const percentage = (strength / 5) * 100;
        let label = '', color = '';

        if (strength === 0)      { label = 'Кем дегенде 6 таңба'; color = '#94a3b8'; }
        else if (strength <= 2)  { label = 'Әлсіз құпия сөз';     color = '#ef4444'; }
        else if (strength <= 3)  { label = 'Орташа құпия сөз';    color = '#f59e0b'; }
        else                     { label = 'Күшті құпия сөз';      color = '#10b981'; }

        strengthFill.style.width = percentage + '%';
        strengthFill.style.background = color;
        strengthText.textContent = label;
        strengthText.style.color = color;
    });
}

// Confirm password validation (register page only)
const confirmInput = document.getElementById('confirmPassword');
if (confirmInput) {
    confirmInput.addEventListener('input', function() {
        const password = document.getElementById('password').value;
        if (this.value && this.value !== password) {
            this.style.borderColor = '#ef4444';
        } else {
            this.style.borderColor = '';
        }
    });
}