// Tab Switching
const menuItems = document.querySelectorAll('.menu-item');
const tabContents = document.querySelectorAll('.tab-content');

menuItems.forEach(item => {
    item.addEventListener('click', function() {
        const tabName = this.getAttribute('data-tab');

        // Remove active class from all items
        menuItems.forEach(i => i.classList.remove('active'));
        tabContents.forEach(t => t.classList.remove('active'));

        // Add active class to clicked item
        this.classList.add('active');
        document.getElementById(tabName).classList.add('active');
    });
});

// Edit Profile
const editBtn = document.getElementById('editBtn');
const saveBtn = document.getElementById('saveBtn');
const cancelBtn = document.getElementById('cancelBtn');
const profileForm = document.getElementById('profileForm');
const formInputs = profileForm.querySelectorAll('input, select, textarea');

let originalValues = {};

editBtn.addEventListener('click', function() {
    // Save original values
    formInputs.forEach(input => {
        originalValues[input.id] = input.value;
        input.disabled = false;
    });

    // Toggle buttons
    editBtn.style.display = 'none';
    saveBtn.style.display = 'flex';
    cancelBtn.style.display = 'flex';
});

cancelBtn.addEventListener('click', function() {
    // Restore original values
    formInputs.forEach(input => {
        input.value = originalValues[input.id];
        input.disabled = true;
    });

    // Toggle buttons
    editBtn.style.display = 'flex';
    saveBtn.style.display = 'none';
    cancelBtn.style.display = 'none';
});

profileForm.addEventListener('submit', function(e) {
    e.preventDefault();

    // Get values
    const fullName = document.getElementById('fullName').value;
    const grade = document.getElementById('grade').value;
    const email = document.getElementById('email').value;
    const phone = document.getElementById('phone').value;
    const bio = document.getElementById('bio').value;

    // Disable inputs
    formInputs.forEach(input => input.disabled = true);

    // Show loading
    saveBtn.innerHTML = '<span>Сақталуда...</span>';
    saveBtn.disabled = true;

    // Simulate API call
    setTimeout(() => {
        console.log('Profile updated:', { fullName, grade, email, phone, bio });

        // Update avatar info
        document.querySelector('.avatar-info h3').textContent = fullName;

        showNotification('✅ Профиль сәтті жаңартылды!', 'success');

        // Toggle buttons
        editBtn.style.display = 'flex';
        saveBtn.style.display = 'none';
        cancelBtn.style.display = 'none';
        saveBtn.innerHTML = '<svg width="18" height="18" viewBox="0 0 18 18" fill="none"><path d="M15 5L7 13L3 9" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg><span>Сақтау</span>';
        saveBtn.disabled = false;
    }, 1500);
});

// Password Change
const passwordForm = document.getElementById('passwordForm');
const newPasswordInput = document.getElementById('newPassword');

if (newPasswordInput) {
    newPasswordInput.addEventListener('input', function() {
        const password = this.value;
        const strengthFill = document.getElementById('newPasswordStrength');
        const strengthText = document.getElementById('newPasswordText');

        let strength = 0;
        let strengthLabel = '';
        let color = '';

        if (password.length >= 6) strength++;
        if (password.length >= 10) strength++;
        if (/[a-z]/.test(password) && /[A-Z]/.test(password)) strength++;
        if (/[0-9]/.test(password)) strength++;
        if (/[^a-zA-Z0-9]/.test(password)) strength++;

        const percentage = (strength / 5) * 100;

        if (strength === 0) {
            strengthLabel = 'Кем дегенде 6 таңба';
            color = '#94a3b8';
        } else if (strength <= 2) {
            strengthLabel = 'Әлсіз құпия сөз';
            color = '#ef4444';
        } else if (strength <= 3) {
            strengthLabel = 'Орташа құпия сөз';
            color = '#f59e0b';
        } else if (strength <= 4) {
            strengthLabel = 'Жақсы құпия сөз';
            color = '#10b981';
        } else {
            strengthLabel = 'Өте күшті құпия сөз!';
            color = '#10b981';
        }

        strengthFill.style.width = percentage + '%';
        strengthFill.style.background = color;
        strengthText.textContent = strengthLabel;
        strengthText.style.color = color;
    });
}

if (passwordForm) {
    passwordForm.addEventListener('submit', function(e) {
        e.preventDefault();

        const currentPassword = document.getElementById('currentPassword').value;
        const newPassword = document.getElementById('newPassword').value;
        const confirmNewPassword = document.getElementById('confirmNewPassword').value;

        if (newPassword !== confirmNewPassword) {
            showNotification('❌ Құпия сөздер сәйкес келмейді!', 'error');
            return;
        }

        if (newPassword.length < 6) {
            showNotification('⚠️ Құпия сөз кем дегенде 6 таңбадан тұруы керек!', 'warning');
            return;
        }

        const submitBtn = this.querySelector('.btn-primary');
        submitBtn.innerHTML = '<span>Сақталуда...</span>';
        submitBtn.disabled = true;

        setTimeout(() => {
            console.log('Password changed');
            showNotification('✅ Құпия сөз сәтті өзгертілді!', 'success');

            // Clear form
            this.reset();

            submitBtn.innerHTML = '<svg width="18" height="18" viewBox="0 0 18 18" fill="none"><path d="M15 5L7 13L3 9" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg><span>Құпия сөзді өзгерту</span>';
            submitBtn.disabled = false;
        }, 1500);
    });
}

// Logout
document.querySelector('.logout-btn').addEventListener('click', function() {
    if (confirm('Шығуға сенімдісіз бе?')) {
        showNotification('👋 Сәтті шықтыңыз!', 'info');
        setTimeout(() => {
            window.location.href = 'login.html';
        }, 1500);
    }
});

// Notification System
function showNotification(message, type) {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 100px;
        right: 30px;
        padding: 18px 28px;
        border-radius: 14px;
        font-weight: 700;
        font-size: 15px;
        color: white;
        z-index: 10000;
        animation: slideIn 0.4s ease, fadeOut 0.4s ease 2.6s;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.25);
    `;

    if (type === 'success') {
        notification.style.background = 'linear-gradient(135deg, #10b981 0%, #059669 100%)';
    } else if (type === 'error') {
        notification.style.background = 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)';
    } else if (type === 'warning') {
        notification.style.background = 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)';
    } else {
        notification.style.background = 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)';
    }

    document.body.appendChild(notification);
    setTimeout(() => notification.remove(), 3000);
}

// Add animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }

    @keyframes fadeOut {
        from { opacity: 1; }
        to { opacity: 0; }
    }
`;
document.head.appendChild(style);