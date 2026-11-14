// DompetVibe AI - 6-Step Progressive User Flow Logic

let gaugeChart = null;
let categoryDonutChart = null;
let modelComparisonChart = null;
let elbowChart = null;

let currentUploadedData = null;
let allTransactions = [];
let monthlyBreakdown = [];
let multiMonthSummary = null;
let currentSelectedMonth = 'all';
let isTxExpanded = false;
const INITIAL_TX_LIMIT = 5;

document.addEventListener('DOMContentLoaded', () => {
    initSidebarState();
    if (window.lucide) {
        lucide.createIcons();
    }
    setupDropzone();
    initGaugeChart();
    recalculateSavings();
});

// ==========================================
// 1. SIDEBAR & MULTI-VIEW NAVIGATION
// ==========================================
let currentNavMenu = 'home';

function switchNavigation(menu) {
    currentNavMenu = menu;
    const views = {
        'home': document.getElementById('section-home-view'),
        'analysis': document.getElementById('section-main-flow'),
        'personas': document.getElementById('section-personas-view'),
        'about': document.getElementById('section-about-view'),
        'contact': document.getElementById('section-contact-view')
    };

    const navBtns = {
        'home': document.getElementById('nav-menu-home'),
        'analysis': document.getElementById('nav-menu-analysis'),
        'personas': document.getElementById('nav-menu-personas'),
        'about': document.getElementById('nav-menu-about'),
        'contact': document.getElementById('nav-menu-contact')
    };

    // Toggle Section Views
    Object.keys(views).forEach(key => {
        if (views[key]) {
            if (key === menu) {
                views[key].classList.remove('hidden');
            } else {
                views[key].classList.add('hidden');
            }
        }
    });

    // Update Sidebar Navigation Active Styling (Pastel Friendly)
    const activeClass = "bg-brand-50 text-brand-700 font-bold border-l-4 border-brand-600 shadow-2xs";
    const inactiveClass = "text-slate-600 hover:text-slate-900 hover:bg-slate-50 font-medium border-l-4 border-transparent";

    Object.keys(navBtns).forEach(key => {
        if (navBtns[key]) {
            if (key === menu) {
                navBtns[key].className = `w-full text-left px-3.5 py-3 rounded-2xl transition-all flex items-center justify-between group cursor-pointer ${activeClass}`;
            } else {
                navBtns[key].className = `w-full text-left px-3.5 py-3 rounded-2xl transition-all flex items-center justify-between group cursor-pointer ${inactiveClass}`;
            }
        }
    });

    // Close Mobile Drawer if open
    toggleMobileSidebar(false);
    if (typeof closePersonaModal === 'function') closePersonaModal();

    // Resize Chart.js canvases when analysis tab becomes visible
    setTimeout(() => {
        if (menu === 'analysis') {
            if (gaugeChart) gaugeChart.resize();
            if (categoryDonutChart) categoryDonutChart.resize();
        }
    }, 80);

    // Smooth Scroll to Top
    window.scrollTo({ top: 0, behavior: 'smooth' });

    if (window.lucide) lucide.createIcons();
}

// ==========================================
// COLLAPSIBLE SIDEBAR (HIDE & UNHIDE)
// ==========================================
function isDesktopScreen() {
    return window.innerWidth >= 1024;
}

function updateSidebarToggleUI(isCollapsed) {
    const icon = document.getElementById('sidebar-toggle-icon');
    const btn = document.getElementById('sidebar-toggle-btn');
    if (!icon || !btn) return;

    if (isDesktopScreen()) {
        if (isCollapsed) {
            icon.setAttribute('data-lucide', 'panel-left-open');
            btn.setAttribute('title', 'Tampilkan Menu Navigasi (Ctrl + B)');
            btn.classList.add('bg-purple-50', 'text-purple-700', 'border-purple-300');
            btn.classList.remove('text-slate-600');
        } else {
            icon.setAttribute('data-lucide', 'panel-left-close');
            btn.setAttribute('title', 'Sembunyikan Menu Navigasi (Ctrl + B)');
            btn.classList.remove('bg-purple-50', 'text-purple-700', 'border-purple-300');
            btn.classList.add('text-slate-600');
        }
    } else {
        const sidebar = document.getElementById('main-sidebar');
        const isOpen = sidebar && !sidebar.classList.contains('-translate-x-full');
        if (isOpen) {
            icon.setAttribute('data-lucide', 'x');
            btn.setAttribute('title', 'Tutup Menu Navigasi');
            btn.classList.add('bg-purple-50', 'text-purple-700', 'border-purple-300');
            btn.classList.remove('text-slate-600');
        } else {
            icon.setAttribute('data-lucide', 'menu');
            btn.setAttribute('title', 'Buka Menu Navigasi');
            btn.classList.remove('bg-purple-50', 'text-purple-700', 'border-purple-300');
            btn.classList.add('text-slate-600');
        }
    }
    if (window.lucide) lucide.createIcons();
}

function toggleSidebar() {
    if (isDesktopScreen()) {
        const isCollapsed = document.body.classList.toggle('sidebar-collapsed');
        localStorage.setItem('dompetvibe_sidebar_collapsed', isCollapsed ? 'true' : 'false');
        updateSidebarToggleUI(isCollapsed);

        // Resize Chart.js jika ada grafik yang sedang aktif
        setTimeout(() => {
            window.dispatchEvent(new Event('resize'));
        }, 320);
    } else {
        const sidebar = document.getElementById('main-sidebar');
        const isClosed = !sidebar || sidebar.classList.contains('-translate-x-full');
        toggleMobileSidebar(isClosed);
    }
}

function toggleMobileSidebar(open) {
    const sidebar = document.getElementById('main-sidebar');
    const overlay = document.getElementById('sidebar-overlay');
    if (!sidebar || !overlay) return;

    if (open) {
        sidebar.classList.remove('-translate-x-full');
        sidebar.classList.add('translate-x-0');
        overlay.classList.remove('hidden');
    } else {
        sidebar.classList.add('-translate-x-full');
        sidebar.classList.remove('translate-x-0');
        overlay.classList.add('hidden');
    }
    updateSidebarToggleUI(!open);
}

function initSidebarState() {
    if (isDesktopScreen()) {
        const savedState = localStorage.getItem('dompetvibe_sidebar_collapsed');
        if (savedState === 'true') {
            document.body.classList.add('sidebar-collapsed');
            updateSidebarToggleUI(true);
        } else {
            document.body.classList.remove('sidebar-collapsed');
            updateSidebarToggleUI(false);
        }
    } else {
        document.body.classList.remove('sidebar-collapsed');
        updateSidebarToggleUI(true);
    }
}

// Listener perubahan ukuran layar (responsive)
window.addEventListener('resize', () => {
    if (isDesktopScreen()) {
        const overlay = document.getElementById('sidebar-overlay');
        if (overlay) overlay.classList.add('hidden');
        const isCollapsed = document.body.classList.contains('sidebar-collapsed');
        updateSidebarToggleUI(isCollapsed);
    } else {
        const sidebar = document.getElementById('main-sidebar');
        const isClosed = !sidebar || sidebar.classList.contains('-translate-x-full');
        updateSidebarToggleUI(isClosed);
    }
});

// Shortcut keyboard Ctrl + B / Cmd + B untuk Hide & Unhide Sidebar
document.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'b') {
        e.preventDefault();
        toggleSidebar();
    }
});

// Interaktif FAQ Accordion
function toggleFaq(index) {
    const answer = document.getElementById(`faq-content-${index}`) || document.getElementById(`faq-ans-${index}`);
    const icon = document.getElementById(`faq-chevron-${index}`) || document.getElementById(`faq-icon-${index}`);
    if (!answer) return;

    if (answer.classList.contains('hidden')) {
        answer.classList.remove('hidden');
        if (icon) icon.classList.add('rotate-180');
    } else {
        answer.classList.add('hidden');
        if (icon) icon.classList.remove('rotate-180');
    }
}

// Handler Form Kontak Kami
function handleContactSubmit(e) {
    e.preventDefault();
    alert('Terima kasih atas pesan dan masukan Anda! Kami akan terus menyempurnakan DompetVibe untuk Anda.');
    const form = e.target;
    if (form) form.reset();
}

function startMutationFlow() {
    switchNavigation('analysis');
    setTimeout(() => {
        const dropzone = document.getElementById('dropzone');
        if (dropzone) dropzone.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }, 120);
}

async function exploreDemoPersona(sampleFilename, label) {
    switchNavigation('analysis');
    await loadSampleFile(sampleFilename, label);
}

// ==========================================
// POPUP MODAL KARAKTER FINANSIAL (BERANDA)
// ==========================================
function openPersonaModal(key) {
    const modal = document.getElementById('persona-detail-modal');
    if (!modal) return;

    // Sembunyikan semua item kartu modal persona
    document.querySelectorAll('.persona-modal-item').forEach(el => el.classList.add('hidden'));

    // Tampilkan kartu persona yang dipilih
    const targetCard = document.getElementById(`modal-card-${key}`);
    if (targetCard) {
        targetCard.classList.remove('hidden');
    }

    modal.classList.remove('hidden');
    document.body.classList.add('overflow-hidden');
    if (window.lucide) lucide.createIcons();
}

function closePersonaModal() {
    const modal = document.getElementById('persona-detail-modal');
    if (!modal) return;
    modal.classList.add('hidden');
    document.body.classList.remove('overflow-hidden');
}

function handlePersonaModalBackdrop(event) {
    if (event.target.id === 'persona-detail-modal') {
        closePersonaModal();
    }
}

function startPersonaFromModal(sampleFilename, label) {
    closePersonaModal();
    exploreDemoPersona(sampleFilename, label);
}

// Tutup popup modal saat menekan tombol Escape keyboard
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        closePersonaModal();
    }
});

// Backwards-compatibility helper for any legacy caller
function switchMainTab(tab) {
    if (tab === 'main') {
        switchNavigation('analysis');
    } else if (tab === 'research') {
        switchNavigation('research');
    } else if (tab === 'home') {
        switchNavigation('home');
    }
}

// ==========================================
// 2. SETUP DROPZONE & FILE SELECTION
// ==========================================
function setupDropzone() {
    const dropzone = document.getElementById('dropzone');
    const fileInput = document.getElementById('file-input');
    if (!dropzone || !fileInput) return;

    dropzone.addEventListener('click', () => fileInput.click());

    dropzone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropzone.classList.add('border-brand-500', 'bg-brand-100/50');
    });

    dropzone.addEventListener('dragleave', () => {
        dropzone.classList.remove('border-brand-500', 'bg-brand-100/50');
    });

    dropzone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropzone.classList.remove('border-brand-500', 'bg-brand-100/50');
        if (e.dataTransfer.files.length > 0) {
            handleUploadFiles(e.dataTransfer.files);
        }
    });

    fileInput.addEventListener('change', () => {
        if (fileInput.files.length > 0) {
            handleUploadFiles(fileInput.files);
            fileInput.value = ''; // reset value agar file yang sama bisa dipilih ulang jika diperlukan
        }
    });
}

async function loadSampleFile(filename, label) {
    try {
        showLoading(true, "Sedang memuat berkas sampel mutasi...");
        const res = await fetch(`/api/demo-samples/${filename}`);
        const blob = await res.blob();
        const file = new File([blob], filename, { type: blob.type });
        await handleUploadFiles([file]);
    } catch (err) {
        showLoading(false);
        alert("Gagal memuat berkas sampel: " + err);
    }
}

function showLoading(show, customMsg = null) {
    const spinner = document.getElementById('upload-loading-spinner');
    if (spinner) {
        if (show) {
            spinner.classList.remove('hidden');
            const txt = spinner.querySelector('span');
            if (txt) {
                txt.textContent = customMsg || "Sedang membaca dan mengklasifikasi transaksi mutasi Anda dengan NLP AI...";
            }
        } else {
            spinner.classList.add('hidden');
        }
    }
}

// ==========================================
// 3. STEP 1 & 2: PROSES & TAMPILKAN MUTASI (SINGLE / MULTI-FILE)
// ==========================================
async function handleUploadFiles(fileListOrSingle) {
    const files = Array.isArray(fileListOrSingle) ? fileListOrSingle : Array.from(fileListOrSingle);
    if (!files || files.length === 0) return;

    // Validasi format
    for (const file of files) {
        const ext = file.name.split('.').pop().toLowerCase();
        if (['jpg', 'jpeg', 'png', 'webp'].includes(ext)) {
            alert(`Format gambar (${file.name}) tidak didukung! Unggah berkas dokumen mutasi digital (.csv, .xlsx, atau .pdf).`);
            return;
        }
    }

    const loadMsg = files.length > 1 ? 
        `Sedang membaca dan menggabungkan ${files.length} berkas mutasi Anda dengan NLP AI...` :
        "Sedang membaca dan mengklasifikasi transaksi mutasi Anda dengan NLP AI...";
    showLoading(true, loadMsg);

    const formData = new FormData();
    for (let i = 0; i < files.length; i++) {
        formData.append('files', files[i]);
    }
    formData.append('file', files[0]); // fallback legacy backend

    try {
        const res = await fetch('/api/upload-mutation', {
            method: 'POST',
            body: formData
        });
        const data = await res.json();
        showLoading(false);

        if (data.success) {
            currentUploadedData = data;
            allTransactions = data.transactions || [];
            monthlyBreakdown = data.monthly_breakdown || [];
            multiMonthSummary = data.multi_month_summary || { is_multi_month: false, num_months: 1 };
            currentSelectedMonth = 'all';
            isTxExpanded = false;

            if (currentNavMenu !== 'analysis') {
                switchNavigation('analysis');
            }

            if (document.getElementById('tx-search-box')) {
                document.getElementById('tx-search-box').value = '';
            }

            // Tampilkan Step 2: Rincian Mutasi
            const step2Section = document.getElementById('section-step-2');
            step2Section.classList.remove('hidden');

            document.getElementById('tx-file-status-label').textContent = `Berkas: ${data.filename}`;
            document.getElementById('tx-badge-count').textContent = `${allTransactions.length} Transaksi Terverifikasi`;

            // Render Kontrol Multi-Bulan, Kartu Statistik & Banner Arus Kas
            renderMonthlyBreakdownUI();
            updateStatCards();
            renderCashflowBanner();

            // Render Tabel Transaksi Awal (Semua Bulan)
            const initialList = getActiveFilteredTransactions();
            renderTransactionTable(initialList);

            // Sembunyikan hasil analisis lama jika ada sampai tombol analisis diklik
            document.getElementById('section-analysis-results').classList.add('hidden');

            // Scroll otomatis halus ke Step 2
            step2Section.scrollIntoView({ behavior: 'smooth', block: 'start' });
            if (window.lucide) lucide.createIcons();
        } else {
            alert("Gagal membaca berkas: " + data.message);
        }
    } catch (err) {
        showLoading(false);
        alert("Terjadi kesalahan jaringan atau server.");
    }
}

// ==========================================
// PENGELOLA TREN & FILTER MULTI-BULAN
// ==========================================
function getActiveFilteredTransactions() {
    let txs = allTransactions;
    if (currentSelectedMonth !== 'all') {
        txs = txs.filter(t => t.month_key === currentSelectedMonth);
    }
    const q = (document.getElementById('tx-search-box')?.value || '').toLowerCase().trim();
    if (q) {
        txs = txs.filter(tx => 
            (tx.deskripsi && tx.deskripsi.toLowerCase().includes(q)) || 
            (tx.kategori && tx.kategori.toLowerCase().includes(q)) ||
            (tx.category_group && tx.category_group.toLowerCase().includes(q)) ||
            (tx.tanggal && tx.tanggal.includes(q))
        );
    }
    return txs;
}

function renderMonthlyBreakdownUI() {
    const filterContainer = document.getElementById('monthly-filter-container');
    const trendCard = document.getElementById('multi-month-trend-card');
    const filterBadge = document.getElementById('monthly-filter-badge');
    const trendBadge = document.getElementById('multi-month-active-badge');
    const narrativeText = document.getElementById('multi-month-narrative-text');
    const microCards = document.getElementById('monthly-micro-cards');

    if (!filterContainer || !trendCard) return;

    if (!monthlyBreakdown || monthlyBreakdown.length <= 1) {
        filterContainer.classList.add('hidden');
        trendCard.classList.add('hidden');
        return;
    }

    // Tampilkan Filter & Kartu Tren Multi-Bulan
    filterContainer.classList.remove('hidden');
    trendCard.classList.remove('hidden');

    if (filterBadge) filterBadge.textContent = `${monthlyBreakdown.length} Bulan`;
    if (trendBadge) trendBadge.textContent = `${monthlyBreakdown.length} Bulan Terpantau`;
    if (narrativeText && multiMonthSummary) {
        narrativeText.textContent = multiMonthSummary.trend_narrative || 
            `Berdasarkan tren ${monthlyBreakdown.length} bulan terakhir, rata-rata pengeluaran bulanan Anda adalah ${multiMonthSummary.avg_monthly_expense_fmt} dengan rata-rata pemasukan ${multiMonthSummary.avg_monthly_income_fmt}.`;
    }

    // Render Pills Pilihan Bulan
    renderMonthPills();

    // Render Micro Cards Perbandingan Bulan
    if (microCards) {
        microCards.innerHTML = monthlyBreakdown.map(m => {
            let statusBadge = "bg-emerald-100 text-emerald-800 border-emerald-200";
            if (m.status === 'Defisit') statusBadge = "bg-rose-100 text-rose-800 border-rose-200";
            else if (m.status === 'Rentan') statusBadge = "bg-amber-100 text-amber-800 border-amber-200";

            return `
                <div onclick="selectMonthFilter('${m.month_key}')" class="cursor-pointer p-3 rounded-2xl bg-white/95 hover:bg-white border border-brand-100/80 hover:border-brand-400 shadow-2xs transition-all hover:scale-[1.02] space-y-1.5">
                    <div class="flex items-center justify-between">
                        <span class="font-bold text-slate-900 text-xs">${m.month_label}</span>
                        <span class="px-2 py-0.5 rounded-full text-[9px] font-black border ${statusBadge}">${m.status}</span>
                    </div>
                    <div class="text-[11px] text-slate-500 space-y-0.5">
                        <div class="flex justify-between">
                            <span>Masuk:</span>
                            <span class="font-bold text-blue-600">${m.total_income_fmt}</span>
                        </div>
                        <div class="flex justify-between">
                            <span>Keluar:</span>
                            <span class="font-bold text-slate-800">${m.total_expense_fmt}</span>
                        </div>
                        <div class="flex justify-between pt-1 border-t border-slate-100">
                            <span>Sisa Kas:</span>
                            <span class="font-black ${m.net_cashflow < 0 ? 'text-rose-600' : 'text-emerald-600'}">${m.net_cashflow_fmt}</span>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    }

    if (window.lucide) lucide.createIcons();
}

function renderMonthPills() {
    const pillsList = document.getElementById('month-pills-list');
    if (!pillsList) return;

    const isAll = currentSelectedMonth === 'all';
    const allPillClass = isAll ?
        "bg-brand-600 text-white font-bold shadow-xs border-brand-600" :
        "bg-white text-slate-600 hover:bg-slate-100 border-slate-200 font-medium";

    let pillsHtml = `
        <button onclick="selectMonthFilter('all')" class="px-3 py-1.5 rounded-xl text-xs border transition-all cursor-pointer flex items-center gap-1.5 ${allPillClass}">
            <span>Semua Periode (${allTransactions.length})</span>
        </button>
    `;

    pillsHtml += monthlyBreakdown.map(m => {
        const isSelected = currentSelectedMonth === m.month_key;
        const pillClass = isSelected ?
            "bg-brand-600 text-white font-bold shadow-xs border-brand-600" :
            "bg-white text-slate-700 hover:bg-slate-100 border-slate-200 font-medium";

        let dotColor = "bg-emerald-500";
        if (m.status === 'Defisit') dotColor = "bg-rose-500";
        else if (m.status === 'Rentan') dotColor = "bg-amber-500";

        return `
            <button onclick="selectMonthFilter('${m.month_key}')" class="px-3 py-1.5 rounded-xl text-xs border transition-all cursor-pointer flex items-center gap-1.5 ${pillClass}">
                <span class="w-2 h-2 rounded-full ${dotColor}"></span>
                <span>${m.month_label} (${m.tx_count})</span>
            </button>
        `;
    }).join('');

    pillsList.innerHTML = pillsHtml;
}

function selectMonthFilter(monthKey) {
    currentSelectedMonth = monthKey;
    isTxExpanded = false;

    renderMonthPills();
    updateStatCards();
    renderCashflowBanner();

    const txs = getActiveFilteredTransactions();
    renderTransactionTable(txs);
}

function updateStatCards() {
    if (!currentUploadedData) return;
    const sum = currentUploadedData.summary;
    const isMulti = multiMonthSummary && multiMonthSummary.is_multi_month;
    const modeIndicator = document.getElementById('monthly-mode-indicator');

    const incVal = document.getElementById('stat-income-val');
    const incSub = document.getElementById('stat-income-sub');
    const expVal = document.getElementById('stat-expense-val');
    const expSub = document.getElementById('stat-expense-sub');
    const cashVal = document.getElementById('stat-cashflow-val');
    const cashSub = document.getElementById('stat-cashflow-sub');
    const needsVal = document.getElementById('stat-needs-val');
    const needsSub = document.getElementById('stat-needs-sub');
    const wantsVal = document.getElementById('stat-wants-val');
    const wantsSub = document.getElementById('stat-wants-sub');

    if (currentSelectedMonth === 'all') {
        if (modeIndicator) {
            modeIndicator.textContent = isMulti ?
                `Menampilkan Rata-rata ${multiMonthSummary.num_months} Bulan & Akumulasi` :
                `Menampilkan Semua Transaksi`;
        }

        incVal.textContent = sum.total_income_fmt;
        expVal.textContent = sum.total_expense_fmt;
        cashVal.textContent = `${sum.net_cashflow_fmt} (${sum.savings_ratio_pct}%)`;
        needsVal.textContent = sum.total_needs_fmt;
        wantsVal.textContent = sum.total_wants_fmt;

        if (isMulti) {
            if (incSub) { incSub.textContent = `Rata-rata: ${multiMonthSummary.avg_monthly_income_fmt}/bln`; incSub.classList.remove('hidden'); }
            if (expSub) { expSub.textContent = `Rata-rata: ${multiMonthSummary.avg_monthly_expense_fmt}/bln`; expSub.classList.remove('hidden'); }
            if (cashSub) { cashSub.textContent = `Rata-rata: ${multiMonthSummary.avg_monthly_net_cashflow_fmt}/bln`; cashSub.classList.remove('hidden'); }
            if (needsSub) { needsSub.textContent = `Rata-rata: ${multiMonthSummary.avg_monthly_needs_fmt}/bln`; needsSub.classList.remove('hidden'); }
            if (wantsSub) { wantsSub.textContent = `Rata-rata: ${multiMonthSummary.avg_monthly_wants_fmt}/bln`; wantsSub.classList.remove('hidden'); }
        } else {
            [incSub, expSub, cashSub, needsSub, wantsSub].forEach(el => el && el.classList.add('hidden'));
        }
    } else {
        const m = monthlyBreakdown.find(x => x.month_key === currentSelectedMonth);
        if (!m) return;

        if (modeIndicator) {
            modeIndicator.textContent = `Menampilkan Periode ${m.month_label}`;
        }

        incVal.textContent = m.total_income_fmt;
        expVal.textContent = m.total_expense_fmt;
        cashVal.textContent = `${m.net_cashflow_fmt} (${m.savings_ratio_pct}%)`;
        needsVal.textContent = m.total_needs_fmt;
        wantsVal.textContent = m.total_wants_fmt;

        const subText = `Khusus ${m.month_label}`;
        if (incSub) { incSub.textContent = subText; incSub.classList.remove('hidden'); }
        if (expSub) { expSub.textContent = subText; expSub.classList.remove('hidden'); }
        if (cashSub) { cashSub.textContent = subText; cashSub.classList.remove('hidden'); }
        if (needsSub) { needsSub.textContent = subText; needsSub.classList.remove('hidden'); }
        if (wantsSub) { wantsSub.textContent = subText; wantsSub.classList.remove('hidden'); }
    }
}

function renderCashflowBanner() {
    const banner = document.getElementById('cashflow-health-banner');
    if (!banner || !currentUploadedData) return;

    banner.classList.remove('hidden');
    let title = "";
    let desc = "";
    let badgeText = "Arus Kas Sehat";
    let badgeColor = "bg-emerald-100 text-emerald-800 border-emerald-300";
    let bannerClass = "bg-emerald-50 border-emerald-200 text-emerald-800";
    let bannerIcon = "✅";

    if (currentSelectedMonth === 'all') {
        const sum = currentUploadedData.summary;
        const isMulti = multiMonthSummary && multiMonthSummary.is_multi_month;
        title = sum.cashflow_status;

        if (isMulti) {
            desc = `Berdasarkan tren ${multiMonthSummary.num_months} bulan terakhir: Rata-rata pengeluaran bulanan ${multiMonthSummary.avg_monthly_expense_fmt} vs pemasukan ${multiMonthSummary.avg_monthly_income_fmt} (rata-rata sisa kas ${multiMonthSummary.avg_monthly_net_cashflow_fmt}/bln). ${sum.has_paylater ? '• 💳 Terdeteksi cicilan pinjaman aktif: ' + sum.total_debt_fmt : '• Bebas pinjaman'}`;
            if (multiMonthSummary.avg_monthly_net_cashflow < 0) {
                bannerClass = "bg-rose-50 border-rose-200 text-rose-800";
                bannerIcon = "🚨";
                badgeText = "Defisit Multi-Bulan";
                badgeColor = "bg-rose-100 text-rose-800 border-rose-300";
            } else if (multiMonthSummary.avg_monthly_savings_ratio_pct < 15) {
                bannerClass = "bg-amber-50 border-amber-200 text-amber-800";
                bannerIcon = "⚠️";
                badgeText = "Arus Kas Rentan";
                badgeColor = "bg-amber-100 text-amber-800 border-amber-300";
            }
        } else {
            desc = `Sisa tabungan bulanan: ${sum.net_cashflow_fmt} (${sum.savings_ratio_pct}% dari pemasukan). ${sum.has_paylater ? '• 💳 Terdeteksi cicilan pinjaman aktif: ' + sum.total_debt_fmt : '• Bebas cicilan pinjaman'}`;
            if (sum.net_cashflow < 0) {
                bannerClass = "bg-rose-50 border-rose-200 text-rose-800";
                bannerIcon = "🚨";
                badgeText = "Defisit Kas";
                badgeColor = "bg-rose-100 text-rose-800 border-rose-300";
            } else if (sum.savings_ratio_pct < 15) {
                bannerClass = "bg-amber-50 border-amber-200 text-amber-800";
                bannerIcon = "⚠️";
                badgeText = "Arus Kas Rentan";
                badgeColor = "bg-amber-100 text-amber-800 border-amber-300";
            }
        }
    } else {
        const m = monthlyBreakdown.find(x => x.month_key === currentSelectedMonth);
        if (!m) return;
        title = `Status Arus Kas: ${m.month_label}`;
        desc = `Pemasukan: ${m.total_income_fmt} • Pengeluaran: ${m.total_expense_fmt} • Sisa Kas: ${m.net_cashflow_fmt} (${m.savings_ratio_pct}%). Pos dominan: ${m.top_category}.`;

        if (m.status === 'Defisit') {
            bannerClass = "bg-rose-50 border-rose-200 text-rose-800";
            bannerIcon = "🚨";
            badgeText = `Defisit ${m.month_label}`;
            badgeColor = "bg-rose-100 text-rose-800 border-rose-300";
        } else if (m.status === 'Rentan') {
            bannerClass = "bg-amber-50 border-amber-200 text-amber-800";
            bannerIcon = "⚠️";
            badgeText = `Rentan ${m.month_label}`;
            badgeColor = "bg-amber-100 text-amber-800 border-amber-300";
        } else {
            badgeText = `Sehat ${m.month_label}`;
        }
    }

    banner.className = `p-3.5 rounded-2xl border text-xs font-semibold flex flex-col sm:flex-row sm:items-center justify-between gap-2.5 ${bannerClass}`;
    banner.innerHTML = `
        <div class="flex items-center gap-2.5">
            <span class="text-xl">${bannerIcon}</span>
            <div>
                <span class="font-bold block text-sm">${title}</span>
                <span class="text-xs opacity-90 block mt-0.5">${desc}</span>
            </div>
        </div>
        <span class="px-3 py-1 rounded-xl text-xs font-black uppercase tracking-wider shadow-xs border ${badgeColor} w-fit">
            ${badgeText}
        </span>
    `;
}

function toggleTxExpanded() {
    isTxExpanded = !isTxExpanded;
    const txs = getActiveFilteredTransactions();
    renderTransactionTable(txs);
}

function filterTxTable() {
    const txs = getActiveFilteredTransactions();
    renderTransactionTable(txs);
}

function renderTransactionTable(txList) {
    const tbody = document.getElementById('tx-table-body');
    const expandContainer = document.getElementById('tx-expand-btn-container');
    const toggleText = document.getElementById('tx-toggle-text');
    const toggleIcon = document.getElementById('tx-toggle-icon');
    const counterLabel = document.getElementById('tx-display-counter');
    if (!tbody) return;

    if (!txList || txList.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" class="py-8 text-center text-slate-400">Tidak ada transaksi ditemukan pada periode ini.</td></tr>`;
        if (expandContainer) expandContainer.classList.add('hidden');
        if (counterLabel) counterLabel.textContent = '(0 transaksi)';
        return;
    }

    const totalCount = txList.length;
    const q = (document.getElementById('tx-search-box')?.value || '').trim();
    const isSearching = q.length > 0;

    let displayList = txList;
    if (!isSearching && !isTxExpanded && totalCount > INITIAL_TX_LIMIT) {
        displayList = txList.slice(0, INITIAL_TX_LIMIT);
    }

    // Update Counter Label
    if (counterLabel) {
        const periodNote = currentSelectedMonth === 'all' ? '' : ' pada bulan ini';
        if (isSearching) {
            counterLabel.textContent = `(Ditemukan ${totalCount} transaksi${periodNote})`;
        } else if (!isTxExpanded && totalCount > INITIAL_TX_LIMIT) {
            counterLabel.textContent = `(Menampilkan ${INITIAL_TX_LIMIT} dari ${totalCount} transaksi${periodNote})`;
        } else {
            counterLabel.textContent = `(Menampilkan semua ${totalCount} transaksi${periodNote})`;
        }
    }

    // Update Expand Button
    if (expandContainer && toggleText) {
        if (isSearching || totalCount <= INITIAL_TX_LIMIT) {
            expandContainer.classList.add('hidden');
        } else {
            expandContainer.classList.remove('hidden');
            if (isTxExpanded) {
                toggleText.textContent = "Ciutkan Transaksi";
                if (toggleIcon) toggleIcon.setAttribute('data-lucide', 'chevron-up');
            } else {
                const remaining = totalCount - INITIAL_TX_LIMIT;
                toggleText.textContent = `Lihat Selengkapnya (${remaining} transaksi lainnya)`;
                if (toggleIcon) toggleIcon.setAttribute('data-lucide', 'chevron-down');
            }
        }
    }

    tbody.innerHTML = displayList.map(tx => {
        let badgeColor = 'bg-slate-100 text-slate-700 border-slate-200';
        let tipeBadge = tx.tipe === 'income' ? 
            '<span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-blue-50 text-blue-700 border border-blue-200 whitespace-nowrap">Masuk (CR)</span>' :
            '<span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-slate-50 text-slate-600 border border-slate-200 whitespace-nowrap">Keluar (DB)</span>';

        if (tx.tipe === 'income') {
            badgeColor = 'bg-blue-50 text-blue-700 border-blue-200';
        } else if (tx.is_debt || tx.kategori.includes('Cicilan') || tx.category_group.includes('Pinjaman')) {
            badgeColor = 'bg-purple-50 text-purple-700 border-purple-200';
        } else if (tx.kategori.includes('Needs') || tx.category_group.includes('Biaya Adm')) {
            badgeColor = 'bg-emerald-50 text-emerald-700 border-emerald-200';
        } else if (tx.kategori.includes('Wants')) {
            badgeColor = 'bg-rose-50 text-rose-700 border-rose-200';
        } else if (tx.category_group.includes('Top-Up')) {
            badgeColor = 'bg-cyan-50 text-cyan-700 border-cyan-200';
        } else {
            badgeColor = 'bg-slate-100 text-slate-700 border-slate-200';
        }

        return `
            <tr class="hover:bg-slate-50/80 transition-colors">
                <td class="py-2.5 px-3.5 whitespace-nowrap text-slate-400 font-medium">${tx.tanggal}</td>
                <td class="py-2.5 px-3.5 font-bold text-slate-800">${tx.deskripsi}</td>
                <td class="py-2.5 px-3.5 whitespace-nowrap font-black ${tx.tipe === 'income' ? 'text-blue-600' : 'text-slate-900'}">${tx.nominal_fmt}</td>
                <td class="py-2.5 px-3.5 whitespace-nowrap">${tipeBadge}</td>
                <td class="py-2.5 px-3.5 whitespace-nowrap">
                    <span class="px-2.5 py-0.5 rounded-full text-[10px] font-bold border ${badgeColor}">
                        ${tx.kategori}
                    </span>
                </td>
                <td class="py-2.5 px-3.5 whitespace-nowrap">
                    <span class="px-2.5 py-0.5 rounded-xl text-[10px] font-semibold bg-slate-100 text-slate-600">
                        ${tx.category_group || 'Lain-lain'}
                    </span>
                </td>
            </tr>
        `;
    }).join('');

    if (window.lucide) lucide.createIcons();
}

// ==========================================
// 4. STEP 3 -> 4, 5, 6: EKSEKUSI ANALISIS AI
// ==========================================
function executeAIAnalysis() {
    if (!currentUploadedData) {
        alert("Silakan unggah berkas mutasi terlebih dahulu.");
        return;
    }

    const data = currentUploadedData;
    const risk = data.risk_assessment;
    const persona = data.persona_assessment.persona;
    const personaId = data.persona_assessment.persona_id;
    const categories = data.category_breakdown || [];
    const tips = data.financial_tips || [];

    // Tampilkan Section Hasil Analisis
    const resultSection = document.getElementById('section-analysis-results');
    resultSection.classList.remove('hidden');

    // ------------------------------------------
    // LANGKAH 4: TINGKAT RISIKO & SPENDING PERSONA
    // ------------------------------------------
    // A. Update Speedometer Gauge
    const gaugeScore = risk.risk_gauge_percentage;
    document.getElementById('gauge-score-result').textContent = `${gaugeScore}%`;
    document.getElementById('risk-badge-result').textContent = risk.risk_label;
    document.getElementById('risk-badge-result').className = `px-3 py-1 text-xs font-black rounded-full border ${risk.badge_class}`;
    document.getElementById('risk-desc-result').textContent = risk.description;

    const riskSubBadge = document.getElementById('monthly-risk-analysis-badge');
    if (riskSubBadge) {
        if (multiMonthSummary && multiMonthSummary.is_multi_month) {
            riskSubBadge.textContent = `Tren ${multiMonthSummary.num_months} Bulan`;
            riskSubBadge.classList.remove('hidden');
        } else {
            riskSubBadge.classList.add('hidden');
        }
    }

    let gaugeColor = '#10B981'; // Aman (Hijau)
    if (risk.risk_class === 1) gaugeColor = '#F59E0B'; // Waspada (Kuning)
    else if (risk.risk_class === 2) gaugeColor = '#8B5CF6'; // Impulsif (Ungu)
    else if (risk.risk_class === 3) gaugeColor = '#F43F5E'; // Kritis (Merah)

    if (gaugeChart) {
        gaugeChart.data.datasets[0].data = [gaugeScore, 100 - gaugeScore];
        gaugeChart.data.datasets[0].backgroundColor = [gaugeColor, '#F1F5F9'];
        gaugeChart.update();
    }

    // B. Update Persona Card
    const iconsMap = { 0: '🌱', 1: '☕', 2: '⚡', 3: '💳' };
    const personaBadges = {
        0: '🌱 Paling Sehat & Terencana',
        1: '☕ Pecinta Kuliner & Kafe',
        2: '⚡ Pemburu Promo & Diskon',
        3: '💳 Perlu Rem Cicilan'
    };
    const personaImages = {
        0: '/static/img/persona_mindful.png',
        1: '/static/img/persona_kopi.png',
        2: '/static/img/persona_promo.png',
        3: '/static/img/persona_paylater.png'
    };

    document.getElementById('persona-badge-result').textContent = personaBadges[personaId] || persona.name;
    const mainImgEl = document.getElementById('persona-main-img');
    if (mainImgEl) {
        mainImgEl.src = personaImages[personaId] || personaImages[0];
        mainImgEl.alt = persona.name;
    }
    document.getElementById('persona-title-result').textContent = persona.name;
    document.getElementById('persona-tagline-result').textContent = persona.tagline;
    document.getElementById('persona-desc-result').textContent = persona.description;

    // Chips Karakteristik
    const chipsContainer = document.getElementById('persona-chips-result');
    const chipTags = {
        0: ['Kontrol Diri Tinggi', 'Non-Paylater', 'Perencanaan Rapi'],
        1: ['Pecinta Kuliner', 'Nongkrong Kafe', 'Non-Paylater'],
        2: ['Pemburu Diskon', 'FOMO Tanggal Kembar', 'Belanja Online'],
        3: ['Pengguna Aktif Paylater', 'Belanja Malam', 'Rasio Belanja Tinggi']
    };
    const tags = chipTags[personaId] || ['Gaya Belanja'];
    chipsContainer.innerHTML = tags.map(t => `
        <span class="px-2.5 py-0.5 rounded-lg bg-slate-100 text-slate-700 text-[11px] font-bold">${t}</span>
    `).join('');

    // C. Update 4 Persona Comparison Grid with Highlights
    for (let i = 0; i < 4; i++) {
        const cardEl = document.getElementById(`comp-persona-card-${i}`);
        const badgeEl = document.getElementById(`comp-badge-${i}`);
        const pillEl = document.getElementById(`comp-pill-${i}`);
        if (!cardEl) continue;

        if (i === personaId) {
            cardEl.className = "p-3.5 rounded-2xl border-2 border-purple-500 bg-purple-50/80 shadow-md ring-2 ring-purple-300/60 scale-[1.02] flex flex-col justify-between space-y-2.5 transition-all";
            if (badgeEl) badgeEl.classList.remove('hidden');
            if (pillEl) {
                pillEl.textContent = "✨ Karakter Kamu!";
                pillEl.className = "py-1 px-2 rounded-xl text-center text-[10px] font-black bg-purple-600 text-white shadow-xs";
            }
        } else {
            cardEl.className = "p-3.5 rounded-2xl border border-slate-200 bg-slate-50/50 opacity-75 hover:opacity-100 flex flex-col justify-between space-y-2.5 transition-all";
            if (badgeEl) badgeEl.classList.add('hidden');
            if (pillEl) {
                pillEl.textContent = "Profil Lainnya";
                pillEl.className = "py-1 px-2 rounded-xl text-center text-[10px] font-medium bg-slate-100 text-slate-500";
            }
        }
    }

    // Render Display 7 Indikator Kebiasaan Finansial (Bahasa Manusia Bersahabat)
    const featsDisplay = document.getElementById('user-features-display');
    if (featsDisplay && data.features) {
        const featLabels = {
            'Income_Code': 'Pemasukan Bulanan',
            'Exp_Ratio_Code': 'Beban Pengeluaran',
            'Paylater_Status': 'Status Cicilan',
            'P_Score': 'Sensitivitas Diskon',
            'SI_Score': 'Belanja Online',
            'H_Score': 'Jajan & Kuliner',
            'SC_Lack_Score': 'Kontrol Diri'
        };
        const featValues = {
            'Income_Code': (v) => v >= 4 ? 'Terpenuhi Baik' : (v >= 2 ? 'Menengah' : 'Cukup'),
            'Exp_Ratio_Code': (v) => v >= 5 ? 'Ketat / Defisit' : (v >= 3 ? 'Cukup Seimbang' : 'Sangat Sehat'),
            'Paylater_Status': (v) => v === 2 ? 'Ada Cicilan Aktif' : 'Bebas Pinjaman',
            'P_Score': (v) => v >= 3.0 ? 'Gampang Tergoda' : (v >= 2.0 ? 'Wajar' : 'Jarang Tergoda'),
            'SI_Score': (v) => v >= 3.0 ? 'Sering Belanja' : (v >= 2.0 ? 'Sesekali' : 'Jarang'),
            'H_Score': (v) => v >= 3.5 ? 'Suka Nongkrong' : (v >= 2.5 ? 'Wajar' : 'Hemat'),
            'SC_Lack_Score': (v) => v >= 3.0 ? 'Perlu Ditingkatkan' : (v >= 2.2 ? 'Cukup Terkendali' : 'Sangat Kuat')
        };
        featsDisplay.innerHTML = Object.entries(data.features).map(([k, v]) => `
            <div class="p-2.5 rounded-2xl bg-white border border-brand-100/80 text-center shadow-xs">
                <span class="text-[9px] text-slate-400 font-bold block uppercase leading-tight">${featLabels[k] || k}</span>
                <span class="text-xs font-black text-brand-700 block mt-1">${(featValues[k] ? featValues[k](v) : v)}</span>
            </div>
        `).join('');
    }

    // ------------------------------------------
    // LANGKAH 5: GRAFIK PENGELUARAN TERBANYAK
    // ------------------------------------------
    renderCategoryBreakdown(categories);

    // ------------------------------------------
    // LANGKAH 6: SARAN & TIPS FINANSIAL PERSONAL
    // ------------------------------------------
    renderFinancialTips(tips);

    // Inisialisasi Simulator Cerdas & Rencana Penghematan
    initSavingsSimulator(data);

    // Scroll halus ke Hasil Analisis
    resultSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    if (window.lucide) lucide.createIcons();
}

function toggleExplanationDetails() {
    const content = document.getElementById('explanation-details-content');
    const text = document.getElementById('toggle-explanation-text');
    const icon = document.getElementById('toggle-explanation-icon');
    if (!content) return;

    if (content.classList.contains('hidden')) {
        content.classList.remove('hidden');
        if (text) text.textContent = 'Tutup Rincian';
        if (icon) icon.classList.add('rotate-180');
    } else {
        content.classList.add('hidden');
        if (text) text.textContent = 'Lihat Rincian';
        if (icon) icon.classList.remove('rotate-180');
    }
    if (window.lucide) lucide.createIcons();
}

// ==========================================
// 5. RENDER GRAFIK KATEGORI PENGELUARAN
// ==========================================
function renderCategoryBreakdown(categories) {
    if (!categories || categories.length === 0) return;

    const topCat = categories[0];
    document.getElementById('top-category-highlight').textContent = 
        `Kategori Terbanyak: ${topCat.category} (${topCat.percentage}%)`;

    // A. Donut Chart
    const ctx = document.getElementById('categoryDonutChart');
    if (ctx) {
        const catColors = ['#8B5CF6', '#F43F5E', '#10B981', '#F59E0B', '#3B82F6', '#EC4899', '#64748B'];
        if (categoryDonutChart) {
            categoryDonutChart.destroy();
        }
        categoryDonutChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: categories.map(c => c.category),
                datasets: [{
                    data: categories.map(c => c.total),
                    backgroundColor: catColors.slice(0, categories.length),
                    borderWidth: 0,
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '68%',
                plugins: {
                    legend: { display: false }
                }
            }
        });
    }

    // B. Breakdown List Items
    const listContainer = document.getElementById('category-breakdown-list');
    if (listContainer) {
        listContainer.innerHTML = categories.map((cat, idx) => {
            const colors = ['bg-brand-500', 'bg-rose-500', 'bg-emerald-500', 'bg-amber-500', 'bg-blue-500', 'bg-pink-500', 'bg-slate-400'];
            const barColor = colors[idx % colors.length];

            return `
                <div class="p-3 rounded-2xl bg-slate-50 border border-slate-100/80 space-y-1.5">
                    <div class="flex items-center justify-between font-bold text-slate-800">
                        <span class="flex items-center gap-2">
                            <span class="w-2.5 h-2.5 rounded-full ${barColor}"></span>
                            <span>${cat.category}</span>
                            <span class="text-[10px] text-slate-400 font-normal">(${cat.count} transaksi)</span>
                        </span>
                        <span>${cat.total_fmt} <span class="text-slate-400 font-normal">(${cat.percentage}%)</span></span>
                    </div>
                    <div class="w-full h-1.5 rounded-full bg-slate-200 overflow-hidden">
                        <div class="h-full ${barColor} rounded-full" style="width: ${cat.percentage}%"></div>
                    </div>
                </div>
            `;
        }).join('');
    }
}

// ==========================================
// 6. RENDER TIPS FINANSIAL PERSONAL
// ==========================================
function renderFinancialTips(tips) {
    const container = document.getElementById('financial-tips-container');
    if (!container) return;

    if (!tips || tips.length === 0) {
        container.innerHTML = `
            <div class="p-4 rounded-2xl bg-slate-50 border border-slate-100 text-xs text-slate-500 col-span-2">
                Tidak ada anomali belanja kritis. Pertahankan kebiasaan mencatat transaksi secara teratur!
            </div>
        `;
        return;
    }

    container.innerHTML = tips.map(t => `
        <div class="p-4 rounded-2xl bg-slate-50 border border-slate-100 flex items-start gap-3 shadow-xs">
            <span class="text-2xl flex-shrink-0 mt-0.5">${t.icon}</span>
            <div>
                <h4 class="font-bold text-slate-900 text-xs sm:text-sm">${t.title}</h4>
                <p class="text-xs text-slate-500 mt-1 leading-relaxed">${t.text}</p>
            </div>
        </div>
    `).join('');
}

// ==========================================
// 7. SIMULASI CERDAS & RENCANA PENGHEMATAN (WHAT-IF SMART SIMULATOR)
// ==========================================
let selectedSavingsCategories = new Set();
let currentSimulatorCategories = [];
let topSavingsCategory = null;

const CATEGORY_META = {
    'Kuliner & F&B': {
        icon: '☕',
        advice: 'Batasi jajan kopi kekinian dan kurangi delivery makanan siap saji dengan memasak makanan sendiri.',
        tip: '📌 Alokasikan jatah dompet mingguan khusus jajan di e-wallet terpisah. Jika saldo habis, tahan sampai minggu depan!'
    },
    'Belanja & E-Commerce': {
        icon: '🛍️',
        advice: 'Terapkan aturan jeda tunggu 48 jam sebelum checkout barang promo di marketplace agar terhindar dari FOMO.',
        tip: '📌 Hapus notifikasi promosi marketplace dari layar utama HP dan masukkan barang belanjaan ke wishlist terlebih dahulu.'
    },
    'Cicilan & Pinjaman': {
        icon: '💳',
        advice: 'Hentikan pemakaian paylater baru dan gunakan uang hasil penghematan ini untuk melunasi pokok pinjaman yang berbunga.',
        tip: '📌 Nonaktifkan metode pembayaran Paylater dari aplikasi belanja dan prioritaskan metode pembayaran debit langsung.'
    },
    'Hiburan & Gaya Hidup': {
        icon: '🎬',
        advice: 'Evaluasi langganan streaming film/musik yang jarang ditonton dan kurangi aktivitas rekreasi berbiaya tinggi.',
        tip: '📌 Lakukan audit langganan digital bulanan. Matikan langganan yang tidak terpakai lebih dari 2 minggu.'
    },
    'Top-Up & E-Wallet': {
        icon: '📱',
        advice: 'Top-up e-wallet sering menjadi sumber kebocoran halus karena uang digital terasa tidak nyata.',
        tip: '📌 Tetapkan jadwal top-up hanya 1x seminggu dengan batas nominal yang sudah dianggarkan sejak awal.'
    },
    'Biaya Adm & Tagihan Bank': {
        icon: '🏦',
        advice: 'Gunakan BI-FAST (Rp 2.500) atau aplikasi transfer bebas biaya untuk menghemat akumulasi biaya transfer bulanan.',
        tip: '📌 Manfaatkan fitur transfer gratis antarbank atau pilih rekening tabungan yang bebas biaya administrasi bulanan.'
    },
    'Kebutuhan Pokok & Tagihan': {
        icon: '🛒',
        advice: 'Belanja bulanan kebutuhan pokok dapat dihemat dengan membeli dalam kemasan grosir atau memanfaatkan promo supermarket.',
        tip: '📌 Buat daftar belanja kebutuhan pokok sebelum pergi ke supermarket dan hindari belanja saat perut lapar.'
    },
    'Transfer & Tarik Tunai': {
        icon: '💸',
        advice: 'Batasi transfer santai ke sesama teman atau penarikan uang tunai tanpa tujuan yang jelas.',
        tip: '📌 Catat setiap transfer pribadi dan hindari menaruh saldo kas berlebih di dompet tunai.'
    },
    'Lain-lain': {
        icon: '📦',
        advice: 'Pengeluaran lain-lain yang fleksibel dapat dipangkas dengan memperketat kriteria belanja non-mendesak.',
        tip: '📌 Evaluasi kembali setiap transaksi non-rutin apakah benar-benar mendesak atau sekadar keinginan sesaat.'
    }
};

function initSavingsSimulator(data) {
    if (!data) return;

    const categories = data.category_breakdown || [];
    currentSimulatorCategories = categories;
    selectedSavingsCategories.clear();

    if (categories.length > 0) {
        // Tentukan Prioritas AI: cari pos terboros non-kebutuhan pokok, jika semua kebutuhan pilih pos terbesar
        const nonNeeds = categories.filter(c => !c.category.toLowerCase().includes('kebutuhan pokok') && c.total > 0);
        topSavingsCategory = nonNeeds.length > 0 ? nonNeeds[0] : categories[0];

        // Otomatis pilih pos rekomendasi utama (dan pos kedua jika ada)
        if (topSavingsCategory) {
            selectedSavingsCategories.add(topSavingsCategory.category);
        }
        if (nonNeeds.length > 1 && nonNeeds[1].total > 0) {
            selectedSavingsCategories.add(nonNeeds[1].category);
        }
    }

    // Render Kartu Rekomendasi Prioritas AI
    renderAIRecommendationCard();

    // Render Chips Kategori Pilihan
    renderSavingsCategoryChips();

    // Jalankan kalkulasi penghematan
    recalculateSavings();
}

function renderAIRecommendationCard() {
    const card = document.getElementById('whatif-ai-recommendation-card');
    if (!card || !topSavingsCategory) return;

    const meta = CATEGORY_META[topSavingsCategory.category] || { 
        icon: '💡', 
        advice: 'Pos ini menjadi pengeluaran terbesar yang paling potensial untuk dihemat.' 
    };
    
    const iconEl = document.getElementById('whatif-top-cat-icon');
    const titleEl = document.getElementById('whatif-top-cat-title');
    const statEl = document.getElementById('whatif-top-cat-stat');
    const narrativeEl = document.getElementById('whatif-top-cat-narrative');

    if (iconEl) iconEl.textContent = meta.icon;
    if (titleEl) titleEl.textContent = topSavingsCategory.category;
    if (statEl) statEl.textContent = `Total: ${topSavingsCategory.total_fmt} (${topSavingsCategory.percentage}% dari pengeluaran)`;
    if (narrativeEl) {
        narrativeEl.innerHTML = `
            Pos <strong>${topSavingsCategory.category}</strong> menyerap <strong>${topSavingsCategory.total_fmt}</strong> (${topSavingsCategory.percentage}% dari total pengeluaranmu). 
            ${meta.advice} Memangkas pos ini memberi dampak paling nyata bagi kesehatan tabunganmu!
        `;
    }
}

function renderSavingsCategoryChips() {
    const container = document.getElementById('whatif-category-chips');
    if (!container) return;

    if (!currentSimulatorCategories || currentSimulatorCategories.length === 0) {
        container.innerHTML = '<span class="text-xs text-slate-400">Unggah berkas mutasi untuk memuat pos pengeluaran.</span>';
        return;
    }

    container.innerHTML = currentSimulatorCategories.filter(c => c.total > 0).map(cat => {
        const isSelected = selectedSavingsCategories.has(cat.category);
        const meta = CATEGORY_META[cat.category] || { icon: '📦' };
        
        const activeClass = isSelected ? 
            'bg-emerald-600 text-white border-emerald-600 shadow-2xs font-bold scale-[1.02]' : 
            'bg-white text-slate-700 border-slate-200/80 hover:bg-emerald-50/60 font-semibold';
        const checkIcon = isSelected ? '✓ ' : '+ ';

        return `
            <button type="button" onclick="toggleSavingsCategory('${cat.category.replace(/'/g, "\\'")}')" class="px-3 py-1.5 rounded-xl text-xs transition-all border flex items-center gap-1.5 cursor-pointer ${activeClass}">
                <span>${checkIcon}${meta.icon}</span>
                <span>${cat.category}</span>
                <span class="opacity-80 text-[10px]">(${cat.total_fmt})</span>
            </button>
        `;
    }).join('');
}

function toggleSavingsCategory(categoryName) {
    if (selectedSavingsCategories.has(categoryName)) {
        selectedSavingsCategories.delete(categoryName);
        // Jika semua tidak terpilih, kembalikan ke default top category agar tidak Rp 0
        if (selectedSavingsCategories.size === 0 && topSavingsCategory) {
            selectedSavingsCategories.add(topSavingsCategory.category);
        }
    } else {
        selectedSavingsCategories.add(categoryName);
    }
    renderSavingsCategoryChips();
    recalculateSavings();
}

function setSavingsPreset(pct) {
    const slider = document.getElementById('slider-whatif');
    if (slider) {
        slider.value = pct;
    }
    // Update active preset button styling
    [10, 20, 35, 50].forEach(p => {
        const btn = document.getElementById(`btn-preset-${p}`);
        if (btn) {
            if (p === pct) {
                btn.className = "px-3 py-1.5 rounded-xl text-xs font-bold transition-all border bg-emerald-600 text-white border-emerald-600 shadow-2xs cursor-pointer";
            } else {
                btn.className = "px-3 py-1.5 rounded-xl text-xs font-bold transition-all border bg-slate-50 text-slate-600 border-slate-200 hover:bg-emerald-50 cursor-pointer";
            }
        }
    });
    recalculateSavings();
}

function updateWhatIfFromSlider() {
    const slider = document.getElementById('slider-whatif');
    if (!slider) return;
    const pct = parseInt(slider.value);

    // Update preset button active states
    [10, 20, 35, 50].forEach(p => {
        const btn = document.getElementById(`btn-preset-${p}`);
        if (btn) {
            if (p === pct) {
                btn.className = "px-3 py-1.5 rounded-xl text-xs font-bold transition-all border bg-emerald-600 text-white border-emerald-600 shadow-2xs cursor-pointer";
            } else {
                btn.className = "px-3 py-1.5 rounded-xl text-xs font-bold transition-all border bg-slate-50 text-slate-600 border-slate-200 hover:bg-emerald-50 cursor-pointer";
            }
        }
    });

    recalculateSavings();
}

function recalculateSavings() {
    const slider = document.getElementById('slider-whatif');
    const pct = slider ? parseInt(slider.value) : 20;

    const labelBadge = document.getElementById('whatif-saving-label');
    if (labelBadge) labelBadge.textContent = `Hemat ${pct}%`;

    const pctText = document.getElementById('whatif-pct-text');
    if (pctText) pctText.textContent = `${pct}%`;

    // 1. Hitung Total Dana dari Kategori Terpilih
    let targetPool = 0;
    if (currentSimulatorCategories && currentSimulatorCategories.length > 0) {
        currentSimulatorCategories.forEach(c => {
            if (selectedSavingsCategories.has(c.category)) {
                targetPool += (c.total || 0);
            }
        });
    }

    // Fallback jika tidak ada data kategori: gunakan total_wants atau 30% dari total pengeluaran
    if (targetPool <= 0) {
        if (currentUploadedData && currentUploadedData.summary) {
            targetPool = currentUploadedData.summary.total_wants || 
                         (currentUploadedData.summary.total_expense * 0.3) || 500000;
        } else {
            targetPool = 500000;
        }
    }

    const fmt = n => `Rp ${Math.round(n).toLocaleString('id-ID')}`;

    const poolLabel = document.getElementById('whatif-target-pool-text');
    if (poolLabel) {
        poolLabel.textContent = `Total Dana Sasaran: ${fmt(targetPool)} / bln`;
    }

    // 2. Hitung Penghematan Bulanan & Tahunan
    const monthSave = Math.round(targetPool * (pct / 100));
    const yearSave = monthSave * 12;

    const monthEl = document.getElementById('whatif-month-val');
    const yearEl = document.getElementById('whatif-year-val');
    if (monthEl) monthEl.textContent = fmt(monthSave);
    if (yearEl) yearEl.textContent = fmt(yearSave);

    // 3. Proyeksi Peningkatan Arus Kas
    const sum = (currentUploadedData && currentUploadedData.summary) ? currentUploadedData.summary : {};
    const curNet = sum.net_cashflow !== undefined ? sum.net_cashflow : 0;
    const newNet = curNet + monthSave;
    const income = sum.total_income > 0 ? sum.total_income : ((sum.total_expense || 0) + Math.max(0, curNet)) || 3000000;
    const curRatio = income > 0 ? ((curNet / income) * 100).toFixed(1) : 0;
    const newRatio = income > 0 ? ((newNet / income) * 100).toFixed(1) : 0;

    const compText = document.getElementById('whatif-comparison-text');
    const compBadge = document.getElementById('whatif-comparison-badge');
    if (compText) {
        if (curNet < 0 && newNet >= 0) {
            compText.innerHTML = `Arus Kas Berbalik Positif: Dari <strong>${fmt(curNet)} (Defisit)</strong> menjadi <strong>${fmt(newNet)} (Surplus)</strong>!`;
            if (compBadge) {
                compBadge.textContent = "Bebas Defisit 🎉";
                compBadge.className = "px-2.5 py-1 rounded-xl bg-emerald-600 text-white text-[10px] font-black shadow-2xs w-fit";
            }
        } else {
            compText.innerHTML = `Sisa Tabungan Bulanan: Dari <strong>${fmt(curNet)} (${curRatio}%)</strong> naik menjadi <strong>${fmt(newNet)} (${newRatio}%)</strong> per bulan.`;
            if (compBadge) {
                compBadge.textContent = `+${fmt(monthSave)}/bln`;
                compBadge.className = "px-2.5 py-1 rounded-xl bg-white text-emerald-800 text-[10px] font-black shadow-2xs w-fit";
            }
        }
    }

    // 4. Milestone Ekuivalen Nyata
    const emergencyEl = document.getElementById('whatif-milestone-emergency');
    if (emergencyEl) {
        const curExp = sum.total_expense || 1500000;
        const monthsFund = (yearSave / (curExp || 1)).toFixed(1);
        emergencyEl.textContent = `Dalam 1 tahun, dana terkumpul ${fmt(yearSave)} (setara ${monthsFund} bulan biaya hidup darurat).`;
    }

    const goldEl = document.getElementById('whatif-milestone-gold');
    if (goldEl) {
        const grams = (yearSave / 1350000).toFixed(1);
        goldEl.textContent = `Setara membeli ~${grams} gram emas murni Antam atau modal investasi reksa dana per tahun.`;
    }

    const lifestyleEl = document.getElementById('whatif-milestone-lifestyle');
    if (lifestyleEl) {
        let hasCoffee = false;
        let hasShop = false;
        selectedSavingsCategories.forEach(c => {
            if (c.toLowerCase().includes('kuliner') || c.toLowerCase().includes('kopi')) hasCoffee = true;
            if (c.toLowerCase().includes('belanja') || c.toLowerCase().includes('commerce')) hasShop = true;
        });

        if (hasCoffee) {
            const cups = Math.max(1, Math.round(monthSave / 28000));
            lifestyleEl.textContent = `Cukup dengan mengurangi ~${cups} cup kopi/minuman manis per bulan (${Math.ceil(cups / 4)} cup/minggu).`;
        } else if (hasShop) {
            const orders = Math.max(1, Math.round(monthSave / 150000));
            lifestyleEl.textContent = `Cukup dengan menahan ~${orders} transaksi checkout marketplace per bulan.`;
        } else {
            const perDay = Math.round(monthSave / 30);
            lifestyleEl.textContent = `Setara menyisihkan uang jajan ${fmt(perDay)} setiap hari ke celengan khusus.`;
        }
    }

    // 5. Checklist Langkah Nyata (Action Tips)
    const tipsList = document.getElementById('whatif-action-tips');
    if (tipsList) {
        const tips = [];
        selectedSavingsCategories.forEach(c => {
            if (CATEGORY_META[c] && CATEGORY_META[c].tip) {
                tips.push(CATEGORY_META[c].tip);
            }
        });
        if (tips.length === 0) {
            tips.push('📌 Sisihkan nominal target penghematan di awal gajian sebelum mulai berbelanja.');
            tips.push('📌 Terapkan aturan tunggu 48 jam sebelum membeli barang non-pokok.');
        }
        tipsList.innerHTML = tips.slice(0, 3).map(t => `<li class="flex items-start gap-2 leading-relaxed">${t}</li>`).join('');
    }
}

// ==========================================
// 8. INISIALISASI SPEEDOMETER GAUGE
// ==========================================
function initGaugeChart() {
    const ctx = document.getElementById('gaugeChart');
    if (ctx && !gaugeChart) {
        gaugeChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                datasets: [{
                    data: [15, 85],
                    backgroundColor: ['#10B981', '#F1F5F9'],
                    borderWidth: 0,
                    circumference: 240,
                    rotation: 240,
                    borderRadius: 10
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '80%',
                plugins: {
                    legend: { display: false },
                    tooltip: { enabled: false }
                }
            }
        });
    }
}

// ==========================================
// 9. METRIK EVALUASI RISET (TAB METRIK)
// ==========================================
async function loadEvaluationStats() {
    try {
        const res = await fetch('/api/evaluation-stats');
        const json = await res.json();
        if (json.success) {
            renderResearchTab(json.data);
        }
    } catch (err) {
        console.error("Gagal load evaluasi riset:", err);
    }
}

function renderResearchTab(data) {
    const comp = data.classification_evaluation;
    const km = data.kmeans_evaluation;

    // Bar Chart Komparasi Model
    const ctxComp = document.getElementById('modelComparisonChart');
    if (ctxComp && !modelComparisonChart) {
        modelComparisonChart = new Chart(ctxComp, {
            type: 'bar',
            data: {
                labels: ['Accuracy', 'Precision', 'Recall', 'F1-Score'],
                datasets: [
                    {
                        label: 'XGBoost (Model Utama)',
                        data: [
                            comp.xgboost.accuracy * 100,
                            comp.xgboost.precision_macro * 100,
                            comp.xgboost.recall_macro * 100,
                            comp.xgboost.f1_macro * 100
                        ],
                        backgroundColor: '#8B5CF6',
                        borderRadius: 6
                    },
                    {
                        label: 'Random Forest (Pembanding)',
                        data: [
                            comp.random_forest.accuracy * 100,
                            comp.random_forest.precision_macro * 100,
                            comp.random_forest.recall_macro * 100,
                            comp.random_forest.f1_macro * 100
                        ],
                        backgroundColor: '#F59E0B',
                        borderRadius: 6
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        ticks: { callback: v => v + '%' }
                    }
                },
                plugins: {
                    legend: { position: 'top' }
                }
            }
        });
    }

    // Elbow Curve K-Means
    const ctxElbow = document.getElementById('elbowChart');
    if (ctxElbow && !elbowChart) {
        const elbowList = km.elbow_data || [];
        elbowChart = new Chart(ctxElbow, {
            type: 'line',
            data: {
                labels: elbowList.map(d => `K=${d.k}`),
                datasets: [{
                    label: 'WCSS (Inertia)',
                    data: elbowList.map(d => d.wcss),
                    borderColor: '#10B981',
                    backgroundColor: 'rgba(16, 185, 129, 0.08)',
                    fill: true,
                    tension: 0.3,
                    pointRadius: 4,
                    pointBackgroundColor: '#10B981'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });
    }
}

// ==========================================
// 8. DOWNLOAD LAPORAN HASIL ANALISIS (PDF)
// ==========================================
async function downloadAnalysisPDF() {
    if (!currentUploadedData) {
        alert("Silakan unggah dan lakukan analisis berkas mutasi terlebih dahulu.");
        return;
    }

    const btn = document.getElementById('btn-download-pdf');
    const btnText = document.getElementById('btn-download-pdf-text');
    const originalText = btnText ? btnText.textContent : 'Download PDF Hasil Analisis';

    try {
        if (btnText) btnText.textContent = 'Menyiapkan PDF... ⏳';
        if (btn) {
            btn.disabled = true;
            btn.classList.add('opacity-75', 'cursor-wait');
        }

        const response = await fetch('/api/download-report-pdf', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(currentUploadedData)
        });

        if (!response.ok) {
            const errData = await response.json().catch(() => ({}));
            throw new Error(errData.message || `Server merespon dengan status ${response.status}`);
        }

        const blob = await response.blob();
        const downloadUrl = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.style.display = 'none';
        link.href = downloadUrl;

        // Tentukan nama file yang rapi
        const rawFilename = currentUploadedData.filename || 'Mutasi_Keuangan';
        const cleanBase = rawFilename.replace(/\.[^/.]+$/, "").replace(/[^a-zA-Z0-9_\-]/g, "_");
        link.download = `Analisis_${cleanBase}.pdf`;

        document.body.appendChild(link);
        link.click();
        
        // Bersihkan memori URL object
        setTimeout(() => {
            window.URL.revokeObjectURL(downloadUrl);
            document.body.removeChild(link);
        }, 200);

    } catch (err) {
        console.error("Gagal mengunduh PDF:", err);
        alert(`Terjadi kendala saat membuat dokumen PDF: ${err.message}`);
    } finally {
        if (btnText) btnText.textContent = originalText;
        if (btn) {
            btn.disabled = false;
            btn.classList.remove('opacity-75', 'cursor-wait');
        }
    }
}
