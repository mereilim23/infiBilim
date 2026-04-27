// Конфигурация курсов - тек 7 сынып
const courseData = {
    7: {
        1: { name: 'Компьютерлік жад және оның өлшем бірліктері', url: '/topic_7_1bolim', topics: 4 },
        2: { name: 'Желі және қауіпсіздік', url: '/topic_7_2bolim', topics: 3 },
        3: { name: 'Электрондық кесте арқылы есептер шығару', url: '/topic_7_3bolim', topics: 7 },
        4: { name: 'Python тіліндегі алгоритмдерді программалау', url: '/topic_7_4bolim', topics: 4 },
        5: { name: 'Практикалық программалау', url: '/topic_7_5bolim', topics: 4 }
    },
    8: {
        1: { name: 'Компьютер мен желілердің техникалық сипаттамалары', url: '/topic_8_1bolim', topics: 5 },
        2: { name: 'Денсаулық және қауіпсіздік', url: '/topic_8_2bolim', topics: 2 },
        3: { name: 'Ақпаратты электронды кестелерде өңдеу', url: '/topic_8_3bolim', topics: 5 },
        4: { name: 'Python тіліндегі алгоритмдерді программалау', url: '/topic_8_4bolim', topics: 7 },
        5: { name: 'Практикалық программалау', url: '/topic_8_5bolim', topics: 5 }
    },
    9: {
        1: { name: 'Ақпаратпен жұмыс жасау', url: '/topic_9_1bolim', topics: 4 },
        2: { name: 'Компьютер таңдаймыз', url: '/topic_9_2bolim', topics: 3 },
        3: { name: 'Деректер базасы', url: '/topic_9_3bolim', topics: 5 },
        4: { name: 'Python тіліндегі алгоритмдерді программалау', url: '/topic_9_4bolim', topics: 8 },

    }
};

let currentClass = null;
let userProgress = {};

function saveSelectedClass(classValue) {
    localStorage.setItem('selectedClass', classValue);
}

function loadSelectedClass() {
    const saved = localStorage.getItem('selectedClass');
    if (saved) {
        currentClass = parseInt(saved);
        const dropdownBtn = document.getElementById('classDropdownBtn');
        if (dropdownBtn) {
            dropdownBtn.querySelector('span').textContent = currentClass + ' сынып';
        }
        updateCourseCards();
    }
}

async function loadProgress() {
    if (!currentClass) return {};
    try {
        const res = await fetch(`/api/user-progress?class_level=${currentClass}`);
        const data = await res.json();
        if (data.progress) {
            userProgress = data.progress;
        }
        return userProgress;
    } catch(e) {
        console.error('Error loading progress:', e);
        return {};
    }
}

async function updateCourseCards() {
    const grid = document.getElementById('courseGrid');
    if (!grid) return;

    if (!currentClass) {
        grid.innerHTML = '<div style="text-align: center; padding: 40px; color: #64748b;">📚 Әуелі сыныпты таңдаңыз</div>';
        return;
    }

    grid.innerHTML = '';
    await loadProgress();

    const courses = courseData[currentClass];
    if (!courses) {
        grid.innerHTML = '<div style="text-align: center; padding: 40px; color: #64748b;">📚 Бұл сыныпқа арналған курстар жоқ</div>';
        return;
    }

    for (const [id, section] of Object.entries(courses)) {
        const totalTopicsInSection = section.topics; // Бөлімдегі барлық тақырыптар саны

        const progress = userProgress[id] || {
            avg_percentage: 0,
            is_completed: false,
            completed_topics: 0,
            total_topics: totalTopicsInSection
        };

        // Егер API-дан келген total_topics ескі болса, біздің мәнді қолданамыз
        const totalTopics = totalTopicsInSection;
        const completedTopics = progress.completed_topics || 0;
        const percent = progress.avg_percentage || 0;

        // Барлық тақырыптар өтілген бе?
        const allTopicsCompleted = completedTopics >= totalTopics;

        let btnClass = 'btn-start';
        let btnText = 'Бастау';
        let cardColor = '#3b82f6';
        let statusText = '';

        if (allTopicsCompleted) {
            btnClass = 'btn-completed';
            btnText = '✅ Барлық тесттер өтілді';
            if (percent >= 70) cardColor = '#10b981';
            else if (percent >= 40) cardColor = '#f59e0b';
            else cardColor = '#ef4444';
            statusText = 'Барлық тесттер өтілді';
        } else if (completedTopics > 0) {
            if (percent >= 70) cardColor = '#10b981';
            else if (percent >= 40) cardColor = '#f59e0b';
            else cardColor = '#ef4444';
            btnClass = 'btn-progress';
            btnText = '📚 Жалғастыру';
            statusText = `${completedTopics}/${totalTopics} тақырып`;
        } else {
            btnClass = 'btn-start';
            btnText = 'Бастау';
            cardColor = '#3b82f6';
            statusText = 'Басталмаған';
        }

        const card = document.createElement('div');
        card.className = 'course-card';
        card.style.borderLeft = `4px solid ${cardColor}`;
        card.innerHTML = `
            <div class="card-badge" style="background: ${cardColor}20; color: ${cardColor};">${id}-бөлім</div>
            <div class="card-body">
                <h3 class="card-title">${section.name}</h3>
                <div class="progress-bar-wrapper">
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${percent}%; background: linear-gradient(90deg, ${cardColor}, ${cardColor}80);"></div>
                    </div>
                    <span class="progress-percent" style="color: ${cardColor};">${percent}%</span>
                </div>
                <div class="card-stats">
                    <div class="stat-item">
                        <span class="stat-icon">📚</span>
                        <span class="stat-text"><strong>${completedTopics}/${totalTopics}</strong> тақырып</span>
                    </div>
                </div>
                <a href="${section.url}" class="card-btn ${btnClass}" style="background: ${cardColor};">
                    <span>${btnText}</span>
                </a>
            </div>
        `;
        grid.appendChild(card);
    }
}

function initDropdown() {
    const dropdownBtn = document.getElementById('classDropdownBtn');
    const dropdownMenu = document.getElementById('classDropdownMenu');

    if (!dropdownBtn || !dropdownMenu) return;

    dropdownBtn.addEventListener('click', function(e) {
        e.stopPropagation();
        dropdownMenu.classList.toggle('show');
    });

    dropdownMenu.querySelectorAll('li').forEach(item => {
        item.addEventListener('click', function(e) {
            const classValue = this.dataset.class;
            if (classValue) {
                currentClass = parseInt(classValue);
                saveSelectedClass(currentClass);
                dropdownBtn.querySelector('span').textContent = classValue + ' сынып';
                dropdownMenu.classList.remove('show');
                updateCourseCards();
            }
        });
    });

    document.addEventListener('click', function() {
        dropdownMenu.classList.remove('show');
    });
}

document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded');
    initDropdown();
    loadSelectedClass();

    if (!currentClass) {
        const grid = document.getElementById('courseGrid');
        if (grid) {
            grid.innerHTML = '<div style="text-align: center; padding: 40px; color: #64748b;">📚 Сыныпты таңдаңыз</div>';
        }
    }
});