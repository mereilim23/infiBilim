// static/js/achievements.js

const ACHIEVEMENTS_LIST = [
    {
        id: 'first_test',
        name: 'Алғашқы қадам',
        description: 'Бірінші тестіңізді тапсырдыңыз!',
        icon: '🎯',
        check: (stats) => stats.totalTests >= 1
    },
    {
        id: 'first_70',
        name: 'Жақсы бастама',
        description: 'Тесттен 70%+ жинадыңыз!',
        icon: '📈',
        check: (stats) => stats.highTests >= 1
    },
    {
        id: 'master_1',
        name: 'Жад шебері',
        description: '1-бөлімнің барлық тақырыптарын 70%+ аяқтадыңыз',
        icon: '💾',
        check: (stats) => stats.section1Complete === true
    },
    {
        id: 'master_2',
        name: 'Желі маманы',
        description: '2-бөлімнің барлық тақырыптарын 70%+ аяқтадыңыз',
        icon: '🌐',
        check: (stats) => stats.section2Complete === true
    },
    {
        id: 'master_3',
        name: 'Кесте шебері',
        description: '3-бөлімнің барлық тақырыптарын 70%+ аяқтадыңыз',
        icon: '📊',
        check: (stats) => stats.section3Complete === true
    },
    {
        id: 'master_4',
        name: 'Python гуру',
        description: '4-бөлімнің барлық тақырыптарын 70%+ аяқтадыңыз',
        icon: '🐍',
        check: (stats) => stats.section4Complete === true
    },
    {
        id: 'three_high',
        name: 'Үздік үштік',
        description: '3 бөлімнен 70%+ жинадыңыз',
        icon: '🏅',
        check: (stats) => stats.highSectionsCount >= 3
    },
    {
        id: 'all_sections',
        name: 'Абсолют чемпион',
        description: 'Барлық 4 бөлімді аяқтадыңыз!',
        icon: '👑',
        check: (stats) => stats.allSectionsComplete === true
    },
    {
        id: 'master_5',
        name: 'Практика шебері',
        description: '5-бөлімнің барлық тақырыптарын 70%+ аяқтадыңыз',
        icon: '💻',
        check: (stats) => stats.section5Complete === true
    },
];

const EARNED_KEY = 'my_achievements';
const LATEST_KEY = 'my_latest_achievement';

class AchievementsSystem {
    constructor() {
        this.earned = this.loadEarned();
        this.latest = this.loadLatest();
    }

    loadEarned() {
        try {
            const saved = localStorage.getItem(EARNED_KEY);
            return saved ? JSON.parse(saved) : [];
        } catch(e) {
            return [];
        }
    }

    saveEarned() {
        localStorage.setItem(EARNED_KEY, JSON.stringify(this.earned));
    }

    loadLatest() {
        try {
            const saved = localStorage.getItem(LATEST_KEY);
            return saved ? JSON.parse(saved) : null;
        } catch(e) {
            return null;
        }
    }

    saveLatest(ach) {
        if (ach) {
            localStorage.setItem(LATEST_KEY, JSON.stringify(ach));
            this.latest = ach;
        }
    }

    async fetchAndUpdate() {
        try {
            // Прогресті API-дан алу
            const res = await fetch('/api/user-progress?class_level=7');
            const data = await res.json();

            // Статистиканы есептеу
            const stats = this.calculateStats(data.progress || {});

            // Жаңа жетістіктерді тексеру
            const newAchievements = [];
            for (const ach of ACHIEVEMENTS_LIST) {
                if (!this.earned.includes(ach.id) && ach.check(stats)) {
                    this.earned.push(ach.id);
                    newAchievements.push(ach);
                }
            }

            // Егер жаңа жетістіктер болса, сақтау
            if (newAchievements.length > 0) {
                this.saveEarned();
                // Ең соңғысын сақтау
                const latest = newAchievements[newAchievements.length - 1];
                this.saveLatest(latest);
            }

            // UI жаңарту
            this.updateUI();

            return newAchievements;
        } catch(e) {
            console.error('Error:', e);
            this.updateUI();
            return [];
        }
    }

    calculateStats(progress) {
        let totalTests = 0;
        let highTests = 0;
        let section1Complete = false;
        let section2Complete = false;
        let section3Complete = false;
        let section4Complete = false;
        let section5Complete = false;
        let highSectionsCount = 0;

        const sectionTopicCounts = { 1: 4, 2: 3, 3: 7, 4: 4, 5: 4 };

    for (let s = 1; s <= 5; s++) {
        const section = progress[s];
        const requiredTopics = sectionTopicCounts[s];

        if (section && section.topics) {
            let topicsHigh = 0;

            for (const topic of section.topics) {
                if (topic.percentage > 0) {
                    totalTests++;
                    if (topic.percentage >= 70) {
                        highTests++;
                        topicsHigh++;
                    }
                }
            }

            const isComplete = (topicsHigh >= requiredTopics);

            if (s === 1) section1Complete = isComplete;
            if (s === 2) section2Complete = isComplete;
            if (s === 3) section3Complete = isComplete;
            if (s === 4) section4Complete = isComplete;
            if (s === 5) section5Complete = isComplete;  // жаңа

            if (isComplete) highSectionsCount++;
        }
    }

        return {
            totalTests: totalTests,
            highTests: highTests,
            section1Complete: section1Complete,
            section2Complete: section2Complete,
            section3Complete: section3Complete,
            section4Complete: section4Complete,
            section5Complete: section5Complete,
            highSectionsCount: highSectionsCount,
            allSectionsComplete: (section1Complete && section2Complete && section3Complete && section4Complete && section5Complete)
        };
    }

    updateUI() {
        const iconEl = document.getElementById('latestIcon');
        const nameEl = document.getElementById('latestName');
        const descEl = document.getElementById('latestDesc');

        if (!iconEl || !nameEl || !descEl) return;

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

    showAllAchievementsModal() {
        const modalBody = document.getElementById('allAchievementsList');
        if (!modalBody) return;

        modalBody.innerHTML = '';

        for (const ach of ACHIEVEMENTS_LIST) {
            const earned = this.earned.includes(ach.id);
            const div = document.createElement('div');
            div.className = `modal-achievement ${earned ? 'earned-modal' : ''}`;
            div.innerHTML = `
                <div class="modal-achievement-icon">${ach.icon}</div>
                <div class="modal-achievement-info">
                    <div class="modal-achievement-name">${ach.name}</div>
                    <div class="modal-achievement-desc">${ach.description}</div>
                </div>
                ${earned ? 
                    '<span class="modal-earned-badge">✔ Алынды</span>' : 
                    '<span class="modal-locked-badge">🔒 Ашылмаған</span>'
                }
            `;
            modalBody.appendChild(div);
        }
    }

    async init() {
        await this.fetchAndUpdate();
    }

    async refresh() {
        await this.fetchAndUpdate();
    }
}

window.AchievementsSystem = new AchievementsSystem();