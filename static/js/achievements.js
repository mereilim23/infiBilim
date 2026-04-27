// static/js/achievements.js
// ─────────────────────────────────────────────────────────────
//  Барлық сыныптарға (7, 8, 9) арналған жетістіктер жүйесі
// ─────────────────────────────────────────────────────────────

// ── Сынып бойынша бөлім конфигурациясы ──────────────────────
const SECTION_CONFIG = {
    7: { 1: 4, 2: 3, 3: 7, 4: 4, 5: 4 },
    8: { 1: 5, 2: 2, 3: 5, 4: 7, 5: 5 },
    9: { 1: 4, 2: 3, 3: 5, 4: 8 }
};

// ── Жетістіктер тізімі ───────────────────────────────────────
const ACHIEVEMENTS_LIST = [

    // ════════════════════════════════
    //  БАСТАУЫШ — алғашқы қадамдар
    // ════════════════════════════════
    {
        id: 'first_test',
        name: 'Алғашқы қадам',
        description: 'Бірінші тестіңізді тапсырдыңыз!',
        icon: '🎯',
        category: 'beginner',
        check: (s) => s.totalTests >= 1
    },
    {
        id: 'first_70',
        name: 'Жақсы бастама',
        description: 'Бірінші рет 70%+ жинадыңыз!',
        icon: '📈',
        category: 'beginner',
        check: (s) => s.highTests >= 1
    },
    {
        id: 'first_100',
        name: 'Мінсіз нәтиже!',
        description: 'Бірінші рет 100% жинадыңыз!',
        icon: '💯',
        category: 'beginner',
        check: (s) => s.perfectTests >= 1
    },
    {
        id: 'five_tests',
        name: 'Табанды оқушы',
        description: '5 тест тапсырдыңыз',
        icon: '📝',
        category: 'beginner',
        check: (s) => s.totalTests >= 5
    },
    {
        id: 'ten_tests',
        name: 'Тест батыры',
        description: '10 тест тапсырдыңыз',
        icon: '🏋️',
        category: 'beginner',
        check: (s) => s.totalTests >= 10
    },

    // ════════════════════════════════
    //  100% ЖЕТІСТІКТЕР
    // ════════════════════════════════
    {
        id: 'three_perfect',
        name: 'Үш жұлдыз',
        description: '3 тақырыптан 100% жинадыңыз',
        icon: '⭐',
        category: 'perfect',
        check: (s) => s.perfectTests >= 3
    },
    {
        id: 'five_perfect',
        name: 'Бес жұлдыз',
        description: '5 тақырыптан 100% жинадыңыз',
        icon: '🌟',
        category: 'perfect',
        check: (s) => s.perfectTests >= 5
    },
    {
        id: 'section_perfect',
        name: 'Мінсіз бөлім',
        description: 'Бір бөлімнің барлық тақырыптарынан 100% жинадыңыз',
        icon: '✨',
        category: 'perfect',
        check: (s) => s.perfectSections >= 1
    },
    {
        id: 'all_perfect',
        name: 'Абсолют шебер',
        description: 'Барлық тапсырған тесттерден 100% жинадыңыз (кем дегенде 5)',
        icon: '🏆',
        category: 'perfect',
        check: (s) => s.totalTests >= 5 && s.perfectTests === s.totalTests
    },

    // ════════════════════════════════
    //  7-СЫНЫП БӨЛІМДЕРІ
    // ════════════════════════════════
    {
        id: 'g7_master_1',
        name: 'Жад шебері',
        description: '7-сынып: 1-бөлімнің барлық тақырыптарын 70%+ аяқтадыңыз',
        icon: '💾',
        category: 'grade7',
        check: (s) => s.grade === 7 && s.sectionComplete[1] === true
    },
    {
        id: 'g7_master_2',
        name: 'Желі маманы',
        description: '7-сынып: 2-бөлімнің барлық тақырыптарын 70%+ аяқтадыңыз',
        icon: '🌐',
        category: 'grade7',
        check: (s) => s.grade === 7 && s.sectionComplete[2] === true
    },
    {
        id: 'g7_master_3',
        name: 'Кесте шебері',
        description: '7-сынып: 3-бөлімнің барлық тақырыптарын 70%+ аяқтадыңыз',
        icon: '📊',
        category: 'grade7',
        check: (s) => s.grade === 7 && s.sectionComplete[3] === true
    },
    {
        id: 'g7_master_4',
        name: 'Python гуру',
        description: '7-сынып: 4-бөлімнің барлық тақырыптарын 70%+ аяқтадыңыз',
        icon: '🐍',
        category: 'grade7',
        check: (s) => s.grade === 7 && s.sectionComplete[4] === true
    },
    {
        id: 'g7_master_5',
        name: 'Практика шебері',
        description: '7-сынып: 5-бөлімнің барлық тақырыптарын 70%+ аяқтадыңыз',
        icon: '💻',
        category: 'grade7',
        check: (s) => s.grade === 7 && s.sectionComplete[5] === true
    },
    {
        id: 'g7_champion',
        name: '7-сынып чемпионы',
        description: '7-сыныптың барлық 5 бөлімін аяқтадыңыз!',
        icon: '👑',
        category: 'grade7',
        check: (s) => s.grade === 7 && s.completedSections >= 5
    },

    // ════════════════════════════════
    //  8-СЫНЫП БӨЛІМДЕРІ
    // ════════════════════════════════
    {
        id: 'g8_master_1',
        name: 'Техника маманы',
        description: '8-сынып: 1-бөлімнің барлық тақырыптарын 70%+ аяқтадыңыз',
        icon: '🖥️',
        category: 'grade8',
        check: (s) => s.grade === 8 && s.sectionComplete[1] === true
    },
    {
        id: 'g8_master_2',
        name: 'Денсаулық сақшысы',
        description: '8-сынып: 2-бөлімнің барлық тақырыптарын 70%+ аяқтадыңыз',
        icon: '🛡️',
        category: 'grade8',
        check: (s) => s.grade === 8 && s.sectionComplete[2] === true
    },
    {
        id: 'g8_master_3',
        name: 'Кесте сарапшысы',
        description: '8-сынып: 3-бөлімнің барлық тақырыптарын 70%+ аяқтадыңыз',
        icon: '📋',
        category: 'grade8',
        check: (s) => s.grade === 8 && s.sectionComplete[3] === true
    },
    {
        id: 'g8_master_4',
        name: 'Python шебері',
        description: '8-сынып: 4-бөлімнің барлық тақырыптарын 70%+ аяқтадыңыз',
        icon: '🐍',
        category: 'grade8',
        check: (s) => s.grade === 8 && s.sectionComplete[4] === true
    },
    {
        id: 'g8_master_5',
        name: 'Практика сарапшысы',
        description: '8-сынып: 5-бөлімнің барлық тақырыптарын 70%+ аяқтадыңыз',
        icon: '⚙️',
        category: 'grade8',
        check: (s) => s.grade === 8 && s.sectionComplete[5] === true
    },
    {
        id: 'g8_champion',
        name: '8-сынып чемпионы',
        description: '8-сыныптың барлық 5 бөлімін аяқтадыңыз!',
        icon: '👑',
        category: 'grade8',
        check: (s) => s.grade === 8 && s.completedSections >= 5
    },

    // ════════════════════════════════
    //  9-СЫНЫП БӨЛІМДЕРІ
    // ════════════════════════════════
    {
        id: 'g9_master_1',
        name: 'Ақпарат шебері',
        description: '9-сынып: 1-бөлімнің барлық тақырыптарын 70%+ аяқтадыңыз',
        icon: '📡',
        category: 'grade9',
        check: (s) => s.grade === 9 && s.sectionComplete[1] === true
    },
    {
        id: 'g9_master_2',
        name: 'Техника таңдаушы',
        description: '9-сынып: 2-бөлімнің барлық тақырыптарын 70%+ аяқтадыңыз',
        icon: '🔧',
        category: 'grade9',
        check: (s) => s.grade === 9 && s.sectionComplete[2] === true
    },
    {
        id: 'g9_master_3',
        name: 'Деректер базасы шебері',
        description: '9-сынып: 3-бөлімнің барлық тақырыптарын 70%+ аяқтадыңыз',
        icon: '🗄️',
        category: 'grade9',
        check: (s) => s.grade === 9 && s.sectionComplete[3] === true
    },
    {
        id: 'g9_master_4',
        name: 'Алгоритм гуру',
        description: '9-сынып: 4-бөлімнің барлық тақырыптарын 70%+ аяқтадыңыз',
        icon: '🧠',
        category: 'grade9',
        check: (s) => s.grade === 9 && s.sectionComplete[4] === true
    },
    {
        id: 'g9_champion',
        name: '9-сынып чемпионы',
        description: '9-сыныптың барлық 4 бөлімін аяқтадыңыз!',
        icon: '👑',
        category: 'grade9',
        check: (s) => s.grade === 9 && s.completedSections >= 4
    },

    // ════════════════════════════════
    //  АРНАЙЫ ЖЕТІСТІКТЕР
    // ════════════════════════════════
    {
        id: 'streak_3',
        name: 'Үш жеңіс қатарынан',
        description: '3 тест қатарынан 70%+ жинадыңыз',
        icon: '🔥',
        category: 'special',
        check: (s) => s.bestStreak >= 3
    },
    {
        id: 'streak_5',
        name: 'Тоқтамас жеңімпаз',
        description: '5 тест қатарынан 70%+ жинадыңыз',
        icon: '🚀',
        category: 'special',
        check: (s) => s.bestStreak >= 5
    },
    {
        id: 'high_avg',
        name: 'Жоғары үлгерім',
        description: 'Жалпы орташа балыңыз 80%+ (кем дегенде 3 тест)',
        icon: '📐',
        category: 'special',
        check: (s) => s.totalTests >= 3 && s.overallAvg >= 80
    },
    {
        id: 'top_avg',
        name: 'Озат оқушы',
        description: 'Жалпы орташа балыңыз 90%+ (кем дегенде 3 тест)',
        icon: '🎖️',
        category: 'special',
        check: (s) => s.totalTests >= 3 && s.overallAvg >= 90
    },
    {
        id: 'three_sections',
        name: 'Үздік үштік',
        description: '3 бөлімді 70%+ аяқтадыңыз',
        icon: '🏅',
        category: 'special',
        check: (s) => s.completedSections >= 3
    },
];

// ── Категория атаулары ───────────────────────────────────────
const CATEGORY_LABELS = {
    beginner: '🌱 Бастауыш',
    perfect:  '💯 Мінсіз нәтиже',
    grade7:   '📚 7-сынып',
    grade8:   '📘 8-сынып',
    grade9:   '📗 9-сынып',
    special:  '⚡ Арнайы',
};

const EARNED_KEY = 'my_achievements';
const LATEST_KEY = 'my_latest_achievement';

// ────────────────────────────────────────────────────────────
class AchievementsSystem {
    constructor() {
        this.earned = this.loadEarned();
        this.latest = this.loadLatest();
    }

    loadEarned() {
        try { return JSON.parse(localStorage.getItem(EARNED_KEY)) || []; }
        catch(e) { return []; }
    }
    saveEarned() { localStorage.setItem(EARNED_KEY, JSON.stringify(this.earned)); }

    loadLatest() {
        try { return JSON.parse(localStorage.getItem(LATEST_KEY)); }
        catch(e) { return null; }
    }
    saveLatest(ach) {
        if (ach) { localStorage.setItem(LATEST_KEY, JSON.stringify(ach)); this.latest = ach; }
    }

    // ── Сынып деңгейін анықтау ──────────────────────────────
    detectGrade() {
        const fromSession = parseInt(sessionStorage.getItem('classLevel'));
        if (fromSession && [7, 8, 9].includes(fromSession)) return fromSession;
        const fromLocal = parseInt(localStorage.getItem('selectedClass'));
        if (fromLocal && [7, 8, 9].includes(fromLocal)) return fromLocal;
        return 7;
    }

    // ── API-дан прогрес алып, жетістіктерді тексеру ─────────
    async fetchAndUpdate() {
        const grade = this.detectGrade();
        try {
            const res  = await fetch(`/api/user-progress?class_level=${grade}`);
            const data = await res.json();
            const stats = this.calculateStats(data.progress || {}, grade);

            const newAchievements = [];
            for (const ach of ACHIEVEMENTS_LIST) {
                if (!this.earned.includes(ach.id) && ach.check(stats)) {
                    this.earned.push(ach.id);
                    newAchievements.push(ach);
                }
            }
            if (newAchievements.length > 0) {
                this.saveEarned();
                this.saveLatest(newAchievements[newAchievements.length - 1]);
                newAchievements.forEach(a => this._showToast(a));
            }
            this.updateUI();
            return newAchievements;
        } catch(e) {
            console.error('Achievements fetch error:', e);
            this.updateUI();
            return [];
        }
    }

    // ── Статистиканы есептеу ─────────────────────────────────
    calculateStats(progress, grade) {
        const config = SECTION_CONFIG[grade] || SECTION_CONFIG[7];

        let totalTests     = 0;
        let highTests      = 0;
        let perfectTests   = 0;
        let totalScore     = 0;
        let sectionComplete  = {};
        let perfectSections  = 0;
        let completedSections = 0;
        const allScores    = [];

        for (const [secIdStr, section] of Object.entries(progress)) {
            const secId   = parseInt(secIdStr);
            const required = config[secId] || 5;
            if (!section || !section.topics) continue;

            let topicsHigh    = 0;
            let topicsPerfect = 0;

            for (const topic of section.topics) {
                if (topic.percentage > 0) {
                    totalTests++;
                    totalScore += topic.percentage;
                    allScores.push(topic.percentage);
                    if (topic.percentage >= 70)  { highTests++;    topicsHigh++;   }
                    if (topic.percentage === 100) { perfectTests++; topicsPerfect++; }
                }
            }

            const isDone    = topicsHigh    >= required;
            const isPerfect = topicsPerfect >= required;
            sectionComplete[secId] = isDone;
            if (isDone)    completedSections++;
            if (isPerfect) perfectSections++;
        }

        const overallAvg = totalTests > 0 ? Math.round(totalScore / totalTests) : 0;

        // Серия (streak) есептеу
        let curStreak = 0, bestStreak = 0;
        for (const sc of allScores) {
            if (sc >= 70) { curStreak++; bestStreak = Math.max(bestStreak, curStreak); }
            else          { curStreak = 0; }
        }

        return {
            grade,
            totalTests,
            highTests,
            perfectTests,
            perfectSections,
            completedSections,
            sectionComplete,
            overallAvg,
            bestStreak,
        };
    }

    // ── UI жаңарту ───────────────────────────────────────────
    updateUI() {
        const iconEl = document.getElementById('latestIcon');
        const nameEl = document.getElementById('latestName');
        const descEl = document.getElementById('latestDesc');
        if (iconEl && nameEl && descEl) {
            if (this.latest) {
                iconEl.textContent = this.latest.icon;
                nameEl.textContent = this.latest.name;
                descEl.textContent = this.latest.description;
            } else {
                iconEl.textContent = '🎯';
                nameEl.textContent = 'Әлі жетістік жоқ';
                descEl.textContent = 'Бірінші тестіңізді тапсырыңыз';
            }
        }
        const countEl = document.getElementById('achievementsCount');
        if (countEl) countEl.textContent = this.earned.length;
    }

    // ── Барлық жетістіктер модалы ───────────────────────────
    showAllAchievementsModal() {
        const modalBody = document.getElementById('allAchievementsList');
        if (!modalBody) return;

        const grade = this.detectGrade();
        const relevant = ACHIEVEMENTS_LIST.filter(a =>
            !a.category.startsWith('grade') || a.category === `grade${grade}`
        );

        // Категория бойынша топтастыру
        const grouped = {};
        for (const ach of relevant) {
            if (!grouped[ach.category]) grouped[ach.category] = [];
            grouped[ach.category].push(ach);
        }

        modalBody.innerHTML = '';
        for (const [cat, list] of Object.entries(grouped)) {
            const header = document.createElement('div');
            header.className = 'ach-category-header';
            header.textContent = CATEGORY_LABELS[cat] || cat;
            modalBody.appendChild(header);

            for (const ach of list) {
                const earned = this.earned.includes(ach.id);
                const div = document.createElement('div');
                div.className = `modal-achievement ${earned ? 'earned-modal' : ''}`;
                div.innerHTML = `
                    <div class="modal-achievement-icon">${ach.icon}</div>
                    <div class="modal-achievement-info">
                        <div class="modal-achievement-name">${ach.name}</div>
                        <div class="modal-achievement-desc">${ach.description}</div>
                    </div>
                    ${earned
                        ? '<span class="modal-earned-badge">✔ Алынды</span>'
                        : '<span class="modal-locked-badge">🔒 Ашылмаған</span>'
                    }
                `;
                modalBody.appendChild(div);
            }
        }

        // Жалпы прогресс жолағы
        const total  = relevant.length;
        const done   = relevant.filter(a => this.earned.includes(a.id)).length;
        const pct    = total > 0 ? Math.round(done / total * 100) : 0;
        const progEl = document.getElementById('achProgressBar');
        const progTx = document.getElementById('achProgressText');
        if (progEl) progEl.style.width = pct + '%';
        if (progTx) progTx.textContent = `${done} / ${total} жетістік (${pct}%)`;
    }

    // ── Жаңа жетістік toast хабарламасы ─────────────────────
    _showToast(ach) {
        this._injectStyles();
        const toast = document.createElement('div');
        toast.className = '_ach-toast';
        toast.innerHTML = `
            <div style="font-size:28px;line-height:1">${ach.icon}</div>
            <div>
                <div class="_ach-toast-title">🏅 Жаңа жетістік!</div>
                <div class="_ach-toast-name">${ach.name}</div>
                <div class="_ach-toast-desc">${ach.description}</div>
            </div>
        `;
        document.body.appendChild(toast);
        setTimeout(() => {
            toast.style.transition = 'opacity .4s, transform .4s';
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(120%)';
            setTimeout(() => toast.remove(), 400);
        }, 4000);
    }

    _injectStyles() {
        if (document.getElementById('_achCss')) return;
        const s = document.createElement('style');
        s.id = '_achCss';
        s.textContent = `
            ._ach-toast {
                position:fixed; bottom:30px; right:24px; z-index:9999;
                background:linear-gradient(135deg,#1a1d27,#222535);
                border:1px solid #6c63ff66; border-radius:14px;
                padding:14px 18px; display:flex; align-items:center; gap:12px;
                box-shadow:0 8px 32px rgba(108,99,255,.3);
                animation:_achIn .4s ease; max-width:320px;
            }
            ._ach-toast-title { font-family:'Sora',sans-serif; font-weight:700; font-size:13px; color:#e8eaf0; }
            ._ach-toast-name  { font-size:12px; color:#a89dff; font-weight:600; margin-top:2px; }
            ._ach-toast-desc  { font-size:11px; color:#7b7f9e; margin-top:2px; }
            @keyframes _achIn {
                from { transform:translateX(120%); opacity:0; }
                to   { transform:translateX(0);    opacity:1; }
            }
            .ach-category-header {
                font-family:'Sora',sans-serif; font-weight:700; font-size:11px;
                color:#7b7f9e; text-transform:uppercase; letter-spacing:.5px;
                padding:12px 0 6px; margin-top:8px; border-bottom:1px solid #2e3147;
            }
        `;
        document.head.appendChild(s);
    }

    // ── Сыртқы API ───────────────────────────────────────────
    async init()            { await this.fetchAndUpdate(); }
    async refresh()         { await this.fetchAndUpdate(); }
    async refreshAndCheck() { return await this.fetchAndUpdate(); }
}

window.AchievementsSystem = new AchievementsSystem();