// certificates.js
const certificatesGrid = document.getElementById('certificatesGrid');
let currentCertificateHtml = '';

async function loadCertificates() {
    try {
        const response = await fetch('/api/user-certificates');
        const data = await response.json();

        if (data.certificates && data.certificates.length > 0) {
            displayCertificates(data.certificates);
        } else {
            showEmptyState();
        }
    } catch (error) {
        console.error('Error loading certificates:', error);
        showEmptyState();
    }
}

function displayCertificates(certificates) {
    certificatesGrid.innerHTML = '';

    certificates.forEach(cert => {
        const card = document.createElement('div');
        card.className = 'certificate-card';
        card.onclick = () => showCertificatePreview(cert);

        card.innerHTML = `
            <div class="certificate-icon">🏅</div>
            <div class="certificate-info">
                <h3 class="certificate-title">${cert.section_name || 'Сертификат'}</h3>
                <p class="certificate-meta">${new Date(cert.issued_at).toLocaleDateString('kk-KZ')}</p>
                <div class="certificate-badge">
                    <span>${cert.score}%</span>
                </div>
            </div>
            <div class="certificate-arrow">→</div>
        `;
        certificatesGrid.appendChild(card);
    });
}

function showEmptyState() {
    certificatesGrid.innerHTML = `
        <div class="empty-state">
            <div class="empty-icon">📜</div>
            <h3>Әлі сертификат жоқ</h3>
            <p>Курстарды аяқтап, алғашқы сертификатыңызды алыңыз!</p>
            <a href="/glav" class="empty-btn">Курстарды бастау</a>
        </div>
    `;
}

function showCertificatePreview(cert) {
    currentCertificateHtml = generateCertificateHtml(cert);
    const previewDiv = document.getElementById('certificatePreview');
    if (previewDiv) {
        previewDiv.innerHTML = currentCertificateHtml;
    }
    const modal = document.getElementById('certificateModal');
    if (modal) {
        modal.classList.add('active');
    }
}

function generateCertificateHtml(cert) {
    const date = new Date(cert.issued_at).toLocaleDateString('kk-KZ', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });

    return `
        <div style="
            background: linear-gradient(135deg, #fff9e6 0%, #fff5d9 100%);
            padding: 32px;
            border-radius: 24px;
            text-align: center;
            border: 2px solid #fbbf24;
            box-shadow: 0 8px 24px rgba(0,0,0,0.1);
        ">
            <div style="font-size: 48px; margin-bottom: 16px;">🏆</div>
            <h2 style="color: #b45309; margin-bottom: 8px;">СЕРТИФИКАТ</h2>
            <p style="color: #78350f; margin-bottom: 24px;">Мақтанышпен тапсырылады</p>
            <div style="width: 60px; height: 2px; background: #fbbf24; margin: 0 auto 24px;"></div>
            <p style="color: #451a03; margin-bottom: 8px;">Мына сертификат беріледі</p>
            <h3 style="font-size: 24px; color: #6366f1; margin-bottom: 16px;">${cert.student_name || 'Пайдаланушы'}</h3>
            <p style="color: #451a03; margin-bottom: 16px;">${cert.section_name || 'Бөлім'}</p>
            <p style="color: #78350f; margin-bottom: 24px;">${cert.score}% нәтижемен аяқтағаны үшін</p>
            <div style="width: 60px; height: 2px; background: #fbbf24; margin: 0 auto 24px;"></div>
            <p style="color: #451a03; font-size: 12px;">Код: ${cert.certificate_code}</p>
            <p style="color: #78350f; font-size: 12px;">${date}</p>
        </div>
    `;
}

function downloadCurrentCertificate() {
    if (!currentCertificateHtml) return;

    const element = document.createElement('div');
    element.innerHTML = currentCertificateHtml;

    const opt = {
        margin: [0.5, 0.5, 0.5, 0.5],
        filename: 'certificate.pdf',
        image: { type: 'jpeg', quality: 0.98 },
        html2canvas: { scale: 2, letterRendering: true },
        jsPDF: { unit: 'in', format: 'a4', orientation: 'landscape' }
    };

    html2pdf().set(opt).from(element).save();
}

document.addEventListener('DOMContentLoaded', () => {
    loadCertificates();

    // Download button
    const downloadBtn = document.getElementById('downloadCertBtn');
    if (downloadBtn) {
        downloadBtn.addEventListener('click', downloadCurrentCertificate);
    }
});