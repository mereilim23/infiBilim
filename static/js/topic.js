// Animate progress circle on load
window.addEventListener('load', () => {
    const progressCircle = document.querySelector('.progress-ring-circle');
    const percentage = 45;
    const circumference = 2 * Math.PI * 90;
    const offset = circumference - (percentage / 100) * circumference;
    
    setTimeout(() => {
        if (progressCircle) progressCircle.style.strokeDashoffset = offset;
    }, 300);
});

// Animate numbers counting up
function animateNumber(element, start, end, duration) {
    let startTimestamp = null;
    const step = (timestamp) => {
        if (!startTimestamp) startTimestamp = timestamp;
        const progress = Math.min((timestamp - startTimestamp) / duration, 1);
        element.textContent = Math.floor(progress * (end - start) + start);
        if (progress < 1) {
            window.requestAnimationFrame(step);
        }
    };
    window.requestAnimationFrame(step);
}

// Animate statistics
window.addEventListener('load', () => {
    setTimeout(() => {
        const percentageEl = document.querySelector('.percentage');
        const detailNumbers = document.querySelectorAll('.detail-number');

        if (percentageEl) animateNumber(percentageEl, 0, 45, 2000);
        if (detailNumbers[0]) animateNumber(detailNumbers[0], 0, 20, 1500);
        if (detailNumbers[1]) animateNumber(detailNumbers[1], 0, 45, 1500);
    }, 500);
});

// Button click handlers with animations
document.querySelectorAll('.card-btn').forEach(btn => {
    btn.addEventListener('click', function(e) {
        const card = this.closest('.course-card');
        if (!card) return;
        const title = card.querySelector('.card-title')?.textContent || '';

        // Create ripple effect
        const ripple = document.createElement('span');
        ripple.style.cssText = `
            position: absolute;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.6);
            transform: translate(-50%, -50%);
            animation: ripple 0.6s ease-out;
            pointer-events: none;
        `;

        const rect = this.getBoundingClientRect();
        ripple.style.left = (e.clientX - rect.left) + 'px';
        ripple.style.top = (e.clientY - rect.top) + 'px';

        this.appendChild(ripple);
        setTimeout(() => ripple.remove(), 600);

        if (this.classList.contains('btn-locked')) {
            showNotification('🔒 Бұл курс әзірге қолжетімсіз', 'warning');
        } else if (this.classList.contains('btn-completed')) {
            showNotification(`✓ "${title}" курсы аяқталды!`, 'success');
        } else {
            showNotification(`🚀 "${title}" курсын бастау...`, 'info');
        }
    });
});

// Dropdown functionality
const dropdownBtn = document.querySelector('.dropdown-btn');
const dropdownMenu = document.getElementById('classDropdownMenu');

if (dropdownBtn && dropdownMenu) {
    dropdownBtn.addEventListener('click', function(e) {
        e.stopPropagation();
        dropdownMenu.classList.toggle('show');
        dropdownMenu.style.display = dropdownMenu.classList.contains('show') ? 'block' : 'none';
    });

    dropdownMenu.addEventListener('click', function(e) {
        const item = e.target.closest('li');
        if (item) {
            const cls = item.dataset.class;
            const span = dropdownBtn.querySelector('span');
            if (span) span.textContent = cls + ' сынып';
            dropdownMenu.classList.remove('show');
            dropdownMenu.style.display = 'none';
        }
    });

    document.addEventListener('click', function(e) {
        if (!dropdownBtn.contains(e.target) && !dropdownMenu.contains(e.target)) {
            dropdownMenu.classList.remove('show');
            dropdownMenu.style.display = 'none';
        }
    });
} else if (dropdownBtn) {
    dropdownBtn.addEventListener('click', function() {
        showNotification('📚 Сынып таңдау мәзірі', 'info');
    });
}

// User menu
const userMenu = document.querySelector('.user-menu');
if (userMenu) {
    userMenu.addEventListener('click', function() {
        showNotification('👤 Пайдаланушы профилі', 'info');
    });
}

// Notification system
function showNotification(message, type) {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 100px;
        right: 30px;
        padding: 16px 24px;
        border-radius: 12px;
        font-weight: 600;
        font-size: 14px;
        color: white;
        z-index: 1000;
        animation: slideInRight 0.4s ease, fadeOut 0.4s ease 2.6s;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
    `;

    if (type === 'success') {
        notification.style.background = 'linear-gradient(135deg, #11998e 0%, #38ef7d 100%)';
    } else if (type === 'warning') {
        notification.style.background = 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)';
    } else {
        notification.style.background = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
    }

    document.body.appendChild(notification);
    setTimeout(() => notification.remove(), 3000);
}

// Добавляем CSS анимации (ОДИН РАЗ!)
if (!document.getElementById('dynamic-styles')) {
    const style = document.createElement('style');
    style.id = 'dynamic-styles';
    style.textContent = `
        @keyframes ripple {
            to {
                width: 300px;
                height: 300px;
                opacity: 0;
            }
        }
        
        @keyframes slideInRight {
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
        
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .nav-link.active {
            color: var(--primary);
            font-weight: 700;
        }
    `;
    document.head.appendChild(style);
}

// Smooth scroll
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Button handlers
const contactBtn = document.querySelector('.contact-btn');
if (contactBtn) {
    contactBtn.addEventListener('click', () => {
        showNotification('📧 Байланысу формасы жүктелуде...', 'info');
    });
}

const applyBtn = document.querySelector('.apply-btn');
if (applyBtn) {
    applyBtn.addEventListener('click', () => {
        showNotification('🎓 Тіркеу бетіне өтуде...', 'success');
    });
}

const demoBtn = document.querySelector('.demo-btn');
if (demoBtn) {
    demoBtn.addEventListener('click', () => {
        showNotification('🎬 Демо видео жүктелуде...', 'info');
    });
}

// Feature cards
document.querySelectorAll('.feature-card').forEach(card => {
    card.addEventListener('click', function() {
        const title = this.querySelector('.feature-title')?.textContent || '';
        showNotification(`✨ ${title} туралы толығырақ...`, 'info');
    });
});

// Scroll animations
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -100px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.animation = 'fadeInUp 0.6s ease forwards';
        }
    });
}, observerOptions);

document.querySelectorAll('.feature-card, .stat-box').forEach(el => {
    observer.observe(el);
});

// Active nav on scroll
window.addEventListener('scroll', () => {
    const sections = document.querySelectorAll('section[id]');
    const scrollY = window.pageYOffset;

    sections.forEach(section => {
        const sectionHeight = section.offsetHeight;
        const sectionTop = section.offsetTop - 100;
        const sectionId = section.getAttribute('id');
        
        if (scrollY > sectionTop && scrollY <= sectionTop + sectionHeight) {
            document.querySelectorAll('.nav-link').forEach(link => {
                link.classList.remove('active');
                if (link.getAttribute('href') === `#${sectionId}`) {
                    link.classList.add('active');
                }
            });
        }
    });
});