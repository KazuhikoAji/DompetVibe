import os
import io
from datetime import datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Wedge, Circle
import numpy as np

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm, cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, KeepTogether, PageBreak, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

IMG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static', 'img')

ALL_PERSONAS = [
    {
        "id": 0,
        "name": "Si Mindful Planner",
        "tagline": "Disiplin & Kebal Diskon",
        "badge_desc": "Paling Sehat & Terencana",
        "image": os.path.join(IMG_DIR, "persona_mindful.png"),
        "color": "#059669",
        "bg_color": "#ECFDF5",
        "border_color": "#A7F3D0",
        "trait": "Kontrol diri tinggi, rasio tabungan > 30%, bebas cicilan konsumtif."
    },
    {
        "id": 1,
        "name": "Anak Kopi & Kafe",
        "tagline": "Kopi & Jajan Santai",
        "badge_desc": "Pecinta Kuliner & Kafe",
        "image": os.path.join(IMG_DIR, "persona_kopi.png"),
        "color": "#D97706",
        "bg_color": "#FFFBEB",
        "border_color": "#FDE68A",
        "trait": "Kebocoran halus pos kuliner, delivery daring, & nongkrong santai."
    },
    {
        "id": 2,
        "name": "Promo & FOMO Hunter",
        "tagline": "Tanggal Kembar & Sale",
        "badge_desc": "Pemburu Diskon & Promo",
        "image": os.path.join(IMG_DIR, "persona_promo.png"),
        "color": "#7C3AED",
        "bg_color": "#FAF5FF",
        "border_color": "#E9D5FF",
        "trait": "Sering checkout impulsif promo marketplace & tren barang viral."
    },
    {
        "id": 3,
        "name": "Sahabat Paylater",
        "tagline": "Cicilan & Belanja Malam",
        "badge_desc": "Perlu Rem Cicilan",
        "image": os.path.join(IMG_DIR, "persona_paylater.png"),
        "color": "#DC2626",
        "bg_color": "#FEF2F2",
        "border_color": "#FECACA",
        "trait": "Kerap pakai cicilan paylater & belanja impulsif larut malam > 21.00."
    }
]

def generate_gauge_chart(score_pct, risk_label):
    """
    Menghasilkan grafik visual Speedometer Gauge (Risk Meter) semi-lingkaran
    dengan 4 zona risiko (Aman, Waspada, Impulsif, Kritis) dan jarum penunjuk presisi.
    """
    fig, ax = plt.subplots(figsize=(4.0, 2.2))
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#FFFFFF')
    
    # 4 Wedges (Aman: 135-180, Waspada: 90-135, Impulsif: 45-90, Kritis: 0-45)
    w_aman = Wedge((0, 0), 1.0, 135, 180, width=0.35, facecolor='#10B981', edgecolor='white', linewidth=2)
    w_wasp = Wedge((0, 0), 1.0, 90, 135, width=0.35, facecolor='#F59E0B', edgecolor='white', linewidth=2)
    w_imp = Wedge((0, 0), 1.0, 45, 90, width=0.35, facecolor='#8B5CF6', edgecolor='white', linewidth=2)
    w_krit = Wedge((0, 0), 1.0, 0, 45, width=0.35, facecolor='#EF4444', edgecolor='white', linewidth=2)
    
    ax.add_patch(w_aman)
    ax.add_patch(w_wasp)
    ax.add_patch(w_imp)
    ax.add_patch(w_krit)
    
    # Labels
    ax.text(-0.95, -0.05, 'Aman', fontsize=7, fontweight='bold', color='#059669', ha='center')
    ax.text(-0.65, 0.90, 'Waspada', fontsize=7, fontweight='bold', color='#D97706', ha='center')
    ax.text(0.65, 0.90, 'Impulsif', fontsize=7, fontweight='bold', color='#7C3AED', ha='center')
    ax.text(0.95, -0.05, 'Kritis', fontsize=7, fontweight='bold', color='#DC2626', ha='center')
    
    # Needle
    score_clamped = max(0.0, min(100.0, float(score_pct)))
    deg = 180.0 - (score_clamped / 100.0) * 180.0
    rad = np.radians(deg)
    
    needle_len = 0.85
    nx = needle_len * np.cos(rad)
    ny = needle_len * np.sin(rad)
    
    ax.plot([0, nx], [0, ny], color='#1E293B', linewidth=3.5, solid_capstyle='round')
    ax.add_patch(Circle((0, 0), 0.12, facecolor='#1E293B', edgecolor='white', linewidth=2))
    
    # Center text
    ax.text(0, 0.28, f"{score_pct:.1f}%", fontsize=17, fontweight='black', color='#1E293B', ha='center', va='center')
    ax.text(0, 0.14, f"SKOR RISIKO", fontsize=7, fontweight='bold', color='#94A3B8', ha='center', va='center')
    
    status_colors = {
        'Aman': '#059669',
        'Waspada': '#D97706',
        'Impulsif': '#7C3AED',
        'Kritis': '#DC2626'
    }
    st_col = status_colors.get(risk_label, '#1E293B')
    ax.text(0, -0.15, f"{risk_label.upper()}", fontsize=11, fontweight='black', color=st_col, ha='center', va='center')
    
    ax.set_xlim(-1.25, 1.25)
    ax.set_ylim(-0.28, 1.15)
    ax.axis('off')
    
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=200, bbox_inches='tight', facecolor='#FFFFFF', transparent=False)
    plt.close(fig)
    buf.seek(0)
    return buf

def generate_donut_chart(categories):
    """
    Menghasilkan grafik Donut resolusi tinggi dengan palet warna pastel & kontras jelas.
    """
    fig, ax = plt.subplots(figsize=(4.0, 2.5))
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#FFFFFF')
    
    labels = [c.get('category', 'Lainnya') for c in categories[:5]]
    values = [float(c.get('total', 0.0)) for c in categories[:5]]
    if not values or sum(values) == 0:
        labels = ['Pengeluaran']
        values = [1.0]
        
    palette = ['#8B5CF6', '#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#EC4899', '#6366F1']
    colors_list = palette[:len(values)]
    
    total_val = sum(values)
    wedges, texts, autotexts = ax.pie(
        values, labels=None, autopct=lambda pct: f"{pct:.0f}%" if pct >= 5 else "",
        pctdistance=0.75, startangle=140, colors=colors_list,
        wedgeprops=dict(width=0.42, edgecolor='white', linewidth=2)
    )
    
    for at in autotexts:
        at.set_color('white')
        at.set_fontweight('bold')
        at.set_fontsize(8)
        
    legend_labels = [f"{lbl[:14]}.. ({val/total_val*100:.0f}%)" if len(lbl) > 16 else f"{lbl} ({val/total_val*100:.0f}%)" 
                     for lbl, val in zip(labels, values)]
    ax.legend(wedges, legend_labels, loc="center left", bbox_to_anchor=(0.92, 0.5),
              fontsize=7, frameon=False)
              
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=200, bbox_inches='tight', facecolor='#FFFFFF', transparent=False)
    plt.close(fig)
    buf.seek(0)
    return buf

def build_pdf_report(data):
    """
    Menghasilkan dokumen PDF Laporan Analisis Keuangan DompetVibe.ai (2 Halaman Eksekutif)
    berisi:
    - HALAMAN 1: Ringkasan Arus Kas, Diagnosis Skor Risiko & Speedometer, Profil Karakter Terpilih,
      dan Perbandingan 4 Gaya Karakter Finansial Lengkap dengan Gambarnya.
    - HALAMAN 2: Alokasi Pengeluaran Donut Chart & Tabel Kategori, Saran & Tips Personal,
      Simulasi Cerdas Penghematan Nyata (What-If), dan Prinsip Emas Keuangan DompetVibe.
    """
    pdf_buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        pdf_buffer,
        pagesize=A4,
        leftMargin=14 * mm,
        rightMargin=14 * mm,
        topMargin=10 * mm,
        bottomMargin=10 * mm
    )

    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=17,
        leading=21,
        textColor=colors.HexColor('#6B21A8')
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor('#64748B')
    )
    meta_style = ParagraphStyle(
        'DocMeta',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=10.5,
        alignment=TA_RIGHT,
        textColor=colors.HexColor('#475569')
    )
    sec_title = ParagraphStyle(
        'SecTitle',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=12.5,
        textColor=colors.HexColor('#1E293B')
    )
    card_title = ParagraphStyle(
        'CardTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor('#64748B')
    )
    card_val = ParagraphStyle(
        'CardVal',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=colors.HexColor('#1E293B')
    )
    card_sub = ParagraphStyle(
        'CardSub',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=6.5,
        leading=8.5,
        textColor=colors.HexColor('#475569')
    )
    body_style = ParagraphStyle(
        'BodyTxt',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=10.5,
        textColor=colors.HexColor('#334155')
    )
    body_bold = ParagraphStyle(
        'BodyTxtBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor('#1E293B')
    )
    footer_style = ParagraphStyle(
        'FooterTxt',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=6.5,
        leading=8.5,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#94A3B8')
    )
    center_bold = ParagraphStyle(
        'CenterBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=9.5,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#1E293B')
    )
    center_sub = ParagraphStyle(
        'CenterSub',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=6.5,
        leading=8.5,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#64748B')
    )

    story = []

    # Ekstraksi Data
    sum_data = data.get('summary', {})
    risk_data = data.get('risk_assessment', {})
    persona_assessment = data.get('persona_assessment', {})
    persona_data = persona_assessment.get('persona', {})
    categories = data.get('category_breakdown', [])
    tips = data.get('financial_tips', [])
    filename = data.get('filename', 'Mutasi Rekening')
    
    total_income = float(sum_data.get('total_income', 0.0))
    total_expense = float(sum_data.get('total_expense', 0.0))
    net_cashflow = float(sum_data.get('net_cashflow', 0.0))
    savings_ratio = float(sum_data.get('savings_ratio_pct', 0.0))
    risk_score = float(risk_data.get('risk_gauge_percentage', 15.0))
    risk_label = risk_data.get('risk_label', 'Aman')
    risk_desc = risk_data.get('description', '')

    # Identifikasi Persona ID pengguna (0: Mindful, 1: Kopi, 2: Promo, 3: Paylater)
    user_pid = persona_assessment.get('persona_id')
    if user_pid is None:
        user_pid = persona_assessment.get('raw_cluster', 0)
    user_pid = int(user_pid) % 4
    
    user_persona_meta = ALL_PERSONAS[user_pid]
    persona_name = persona_data.get('name', user_persona_meta['name'])
    persona_tagline = persona_data.get('tagline', user_persona_meta['tagline'])
    persona_desc = persona_data.get('description', user_persona_meta['trait'])
    persona_rec = persona_data.get('recommendation', 'Pertahankan kontrol diri dan konsistensi pos tabungan.')

    now_str = datetime.now().strftime("%d %B %Y • %H:%M WIB")

    # =========================================================================
    # HALAMAN 1: HEADER & IDENTITAS
    # =========================================================================
    header_content = [
        [
            Paragraph("<b>DompetVibe.ai</b>", title_style),
            Paragraph(f"Tanggal Analisis: {now_str}<br/>Berkas: <b>{filename}</b>", meta_style)
        ],
        [
            Paragraph("Platform Cerdas Pengatur Keuangan &amp; Gaya Belanjamu", subtitle_style),
            Paragraph("Behavioral Finance &amp; Financial Health Report", meta_style)
        ]
    ]
    t_header = Table(header_content, colWidths=[105 * mm, 77 * mm])
    t_header.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(t_header)
    story.append(Spacer(1, 1.5 * mm))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#E9D5FF'), spaceAfter=2.5 * mm))

    # =========================================================================
    # BAGIAN 1: RINGKASAN ARUS KAS (4 KARTU STATISTIK VISUAL)
    # =========================================================================
    story.append(Paragraph("1. Ringkasan Arus Kas Finansial (Cashflow Overview)", sec_title))
    story.append(Spacer(1, 1.2 * mm))

    income_fmt = f"Rp {total_income:,.0f}".replace(',', '.')
    expense_fmt = f"Rp {total_expense:,.0f}".replace(',', '.')
    net_fmt = f"Rp {net_cashflow:,.0f}".replace(',', '.')
    save_status = sum_data.get('cashflow_status', 'Arus Kas Sehat')

    c1 = [
        Paragraph("TOTAL PEMASUKAN", card_title),
        Paragraph(f"<font color='#059669'>{income_fmt}</font>", card_val),
        Paragraph("Gaji &amp; Transfer Masuk", card_sub)
    ]
    c2 = [
        Paragraph("TOTAL PENGELUARAN", card_title),
        Paragraph(f"<font color='#DC2626'>{expense_fmt}</font>", card_val),
        Paragraph(f"{sum_data.get('total_transactions', 0)} transaksi tercatat", card_sub)
    ]
    c3 = [
        Paragraph("SISA KAS / TABUNGAN", card_title),
        Paragraph(f"<font color='#2563EB'>{net_fmt}</font>", card_val),
        Paragraph("Surplus dana akhir periode" if net_cashflow >= 0 else "Peringatan: Defisit kas", card_sub)
    ]
    c4 = [
        Paragraph("RASIO TABUNGAN", card_title),
        Paragraph(f"<font color='#7C3AED'>{savings_ratio:.1f}%</font>", card_val),
        Paragraph(f"Status: {save_status[:22]}..", card_sub)
    ]

    stat_cards = Table(
        [[c1, c2, c3, c4]],
        colWidths=[45.5 * mm, 45.5 * mm, 45.5 * mm, 45.5 * mm]
    )
    stat_cards.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,0), colors.HexColor('#ECFDF5')),
        ('BACKGROUND', (1,0), (1,0), colors.HexColor('#FEF2F2')),
        ('BACKGROUND', (2,0), (2,0), colors.HexColor('#EFF6FF')),
        ('BACKGROUND', (3,0), (3,0), colors.HexColor('#FAF5FF')),
        ('BOX', (0,0), (0,0), 1, colors.HexColor('#A7F3D0')),
        ('BOX', (1,0), (1,0), 1, colors.HexColor('#FECACA')),
        ('BOX', (2,0), (2,0), 1, colors.HexColor('#BFDBFE')),
        ('BOX', (3,0), (3,0), 1, colors.HexColor('#E9D5FF')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(stat_cards)
    story.append(Spacer(1, 2.5 * mm))

    # =========================================================================
    # BAGIAN 2: HASIL DIAGNOSIS AI & PROFIL KARAKTER TERDETEKSI (2 KARTU)
    # =========================================================================
    story.append(Paragraph("2. Diagnosis AI: Tingkat Kendali Belanja &amp; Profil Karakter", sec_title))
    story.append(Spacer(1, 1.2 * mm))

    # Generate Gauge Chart
    buf_gauge = generate_gauge_chart(risk_score, risk_label)
    img_gauge = RLImage(buf_gauge, width=80 * mm, height=44 * mm)

    risk_badge_colors = {
        'Aman': ('#ECFDF5', '#065F46', '#A7F3D0'),
        'Waspada': ('#FFFBEB', '#92400E', '#FDE68A'),
        'Impulsif': ('#FAF5FF', '#581C87', '#E9D5FF'),
        'Kritis': ('#FEF2F2', '#991B1B', '#FECACA')
    }
    rb_bg, rb_tx, rb_bd = risk_badge_colors.get(risk_label, ('#ECFDF5', '#065F46', '#A7F3D0'))

    risk_cell = [
        Paragraph(f"<b>TINGKAT KENDALI:</b> <font color='{rb_tx}'><b>{risk_label.upper()}</b></font>", body_bold),
        Spacer(1, 0.5 * mm),
        img_gauge,
        Spacer(1, 0.5 * mm),
        Paragraph(f"<b>Analisis AI:</b> {risk_desc}", body_style)
    ]

    # Kartu Profil Karakter Terpilih dengan Gambar Karakter
    user_img_flowable = RLImage(user_persona_meta['image'], width=27 * mm, height=27 * mm)
    persona_header_inner = Table([
        [
            user_img_flowable,
            [
                Paragraph("<b>PROFIL KARAKTER KAMU:</b>", card_title),
                Paragraph(f"<font color='#6B21A8' size='11'><b>{persona_name}</b></font>", body_bold),
                Paragraph(f"<i>'{persona_tagline}'</i>", card_sub),
                Spacer(1, 1 * mm),
                Paragraph(f"<font color='{user_persona_meta['color']}'><b>[ TERDIAGNOSIS SESUAI ARUS KAS ]</b></font>", card_sub)
            ]
        ]
    ], colWidths=[29 * mm, 55 * mm])
    persona_header_inner.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
    ]))

    persona_cell = [
        persona_header_inner,
        Spacer(1, 1.5 * mm),
        Paragraph(f"<b>Pola Kebiasaan:</b> {persona_desc}", body_style),
        Spacer(1, 1.2 * mm),
        Paragraph(f"<b>Rekomendasi Utama:</b> <font color='#047857'>{persona_rec}</font>", body_style)
    ]

    diagnosis_table = Table([[risk_cell, persona_cell]], colWidths=[91 * mm, 91 * mm])
    diagnosis_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,0), colors.HexColor('#F8FAFC')),
        ('BACKGROUND', (1,0), (1,0), colors.HexColor(user_persona_meta['bg_color'])),
        ('BOX', (0,0), (0,0), 1, colors.HexColor('#E2E8F0')),
        ('BOX', (1,0), (1,0), 1.5, colors.HexColor(user_persona_meta['color'])),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(diagnosis_table)
    story.append(Spacer(1, 2.5 * mm))

    # =========================================================================
    # BAGIAN 3: PERBANDINGAN 4 GAYA KARAKTER FINANSIAL (4 KOLOM DENGAN GAMBAR)
    # =========================================================================
    story.append(Paragraph("3. Peta 4 Gaya Karakter Finansial (Financial Personas Comparison)", sec_title))
    story.append(Spacer(1, 1.2 * mm))

    comp_cells = []
    for p in ALL_PERSONAS:
        is_me = (p['id'] == user_pid)
        p_img = RLImage(p['image'], width=23 * mm, height=23 * mm)
        badge_html = f"<font color='{p['color']}'><b>★ KARAKTER KAMU ★</b></font>" if is_me else "<font color='#94A3B8'>Profil Lainnya</font>"
        
        cell_items = [
            p_img,
            Spacer(1, 0.8 * mm),
            Paragraph(f"<b>{p['name']}</b>", center_bold),
            Paragraph(f"<i>{p['tagline']}</i>", center_sub),
            Spacer(1, 0.5 * mm),
            Paragraph(f"<font size='6'>{p['trait']}</font>", center_sub),
            Spacer(1, 0.8 * mm),
            Paragraph(badge_html, center_bold)
        ]
        comp_cells.append(cell_items)

    t_comp = Table([comp_cells], colWidths=[45.5 * mm, 45.5 * mm, 45.5 * mm, 45.5 * mm])
    t_comp_styles = [
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 3),
        ('RIGHTPADDING', (0,0), (-1,-1), 3),
    ]
    for idx, p in enumerate(ALL_PERSONAS):
        if p['id'] == user_pid:
            t_comp_styles.extend([
                ('BACKGROUND', (idx, 0), (idx, 0), colors.HexColor(p['bg_color'])),
                ('BOX', (idx, 0), (idx, 0), 1.5, colors.HexColor(p['color'])),
            ])
        else:
            t_comp_styles.extend([
                ('BACKGROUND', (idx, 0), (idx, 0), colors.HexColor('#F8FAFC')),
                ('BOX', (idx, 0), (idx, 0), 0.5, colors.HexColor('#E2E8F0')),
            ])
    t_comp.setStyle(TableStyle(t_comp_styles))
    story.append(t_comp)
    story.append(Spacer(1, 2.5 * mm))

    # FOOTER HALAMAN 1
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#CBD5E1'), spaceAfter=1.5 * mm))
    story.append(Paragraph(
        "Halaman 1 dari 2 • DompetVibe.ai Behavioral Finance Report • 100% Aman &amp; Menjaga Kerahasiaan Berkas",
        footer_style
    ))

    # BREAK KE HALAMAN 2
    story.append(PageBreak())

    # =========================================================================
    # HALAMAN 2: HEADER RINGKAS
    # =========================================================================
    header_p2 = [
        [
            Paragraph("<b>DompetVibe.ai</b> • Rencana Aksi &amp; Alokasi Belanja", title_style),
            Paragraph(f"Tanggal: {now_str}<br/>Berkas: <b>{filename}</b>", meta_style)
        ],
        [
            Paragraph("Rangkuman Alokasi Pengeluaran, Tips Personalisasi &amp; Simulasi Penghematan", subtitle_style),
            Paragraph("Financial Action Plan &amp; Smart Savings", meta_style)
        ]
    ]
    t_head_p2 = Table(header_p2, colWidths=[115 * mm, 67 * mm])
    t_head_p2.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(t_head_p2)
    story.append(Spacer(1, 1.5 * mm))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#E9D5FF'), spaceAfter=2.5 * mm))

    # =========================================================================
    # BAGIAN 4: ALOKASI PENGELUARAN (GRAFIK DONUT & TABEL POS KATEGORI)
    # =========================================================================
    story.append(Paragraph("4. Alokasi Pengeluaran Terbesar (Expense Breakdown)", sec_title))
    story.append(Spacer(1, 1.2 * mm))

    buf_donut = generate_donut_chart(categories)
    img_donut = RLImage(buf_donut, width=88 * mm, height=50 * mm)

    cat_rows = [
        [
            Paragraph("<b>Kategori Pengeluaran</b>", card_title),
            Paragraph("<b>Total (Rp)</b>", card_title),
            Paragraph("<b>Porsi</b>", card_title)
        ]
    ]
    for c in categories[:5]:
        cat_rows.append([
            Paragraph(str(c.get('category', '-')), body_style),
            Paragraph(f"Rp {float(c.get('total', 0.0)):,.0f}".replace(',', '.'), body_style),
            Paragraph(f"{float(c.get('percentage', 0.0)):.1f}%", body_bold)
        ])

    t_cat = Table(cat_rows, colWidths=[42 * mm, 30 * mm, 18 * mm])
    t_cat.setStyle(TableStyle([
        ('LINEBELOW', (0,0), (-1,0), 1, colors.HexColor('#CBD5E1')),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('LEFTPADDING', (0,0), (-1,-1), 2),
        ('RIGHTPADDING', (0,0), (-1,-1), 2),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#FFFFFF'), colors.HexColor('#F8FAFC')]),
    ]))

    alloc_table = Table([[img_donut, t_cat]], colWidths=[92 * mm, 90 * mm])
    alloc_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(alloc_table)
    story.append(Spacer(1, 2.5 * mm))

    # =========================================================================
    # BAGIAN 5: SARAN & TIPS PRAKTIS UNTUK DOMPETMU (ACTIONABLE CARDS)
    # =========================================================================
    story.append(Paragraph("5. Saran &amp; Tips Praktis Berdasarkan Mutasimu", sec_title))
    story.append(Spacer(1, 1.2 * mm))

    tip_items = tips[:3] if tips else [
        {
            "title": "Evaluasi Belanja Non-Esensial",
            "text": "Terapkan aturan jeda 48 jam sebelum membeli barang keinginan di marketplace daring."
        },
        {
            "title": "Bangun Pos Dana Darurat",
            "text": "Sisihkan minimal 10-20% dari setiap pemasukan begitu gaji masuk ke rekening khusus."
        },
        {
            "title": "Waspadai Bocor Halus Jajan Harian",
            "text": "Biaya delivery makanan dan kopi kekinian kerap menumpuk tanpa disadari."
        }
    ]

    tip_cells = []
    for idx, t in enumerate(tip_items):
        t_title = t.get('title', f'Langkah Finansial #{idx+1}')
        t_desc = t.get('text', '') or t.get('desc', '')
        tip_cells.append([
            Paragraph(f"<b>{t_title}</b>", body_bold),
            Spacer(1, 1 * mm),
            Paragraph(t_desc, body_style)
        ])

    while len(tip_cells) < 3:
        tip_cells.append([Paragraph("Langkah Finansial", body_bold), Paragraph("Jaga konsistensi pencatatan arus kas bulananmu.", body_style)])

    tips_table = Table([[tip_cells[0], tip_cells[1], tip_cells[2]]], colWidths=[60.5 * mm, 60.5 * mm, 61 * mm])
    tips_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('BOX', (0,0), (0,0), 1, colors.HexColor('#E2E8F0')),
        ('BOX', (1,0), (1,0), 1, colors.HexColor('#E2E8F0')),
        ('BOX', (2,0), (2,0), 1, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(tips_table)
    story.append(Spacer(1, 2.5 * mm))

    # =========================================================================
    # BAGIAN 6: SIMULASI PENGHEMATAN (WHAT-IF SMART SIMULATION)
    # =========================================================================
    story.append(Paragraph("6. Simulasi Cerdas Penghematan Nyata (What-If Savings)", sec_title))
    story.append(Spacer(1, 1.2 * mm))

    wants_total = float(sum_data.get('total_wants', 0.0))
    if wants_total <= 0:
        wants_total = total_expense * 0.35 if total_expense > 0 else 1000000.0

    save_20_month = wants_total * 0.20
    save_20_year = save_20_month * 12

    save_month_fmt = f"Rp {save_20_month:,.0f}".replace(',', '.')
    save_year_fmt = f"Rp {save_20_year:,.0f}".replace(',', '.')

    sim_content = [
        [
            Paragraph("<b>TARGET PEMANGKASAN 20% POS KEINGINAN:</b>", body_bold),
            Paragraph(f"Estimasi Tabungan Tahunan: <b><font color='#059669'>+{save_year_fmt}</font></b>", meta_style)
        ],
        [
            Paragraph(
                f"Dengan memangkas <b>20%</b> dari belanja keinginan/lifestyle, kamu dapat menyelamatkan "
                f"<b><font color='#059669'>{save_month_fmt} / bulan</font></b> "
                f"atau akumulasi <b><font color='#059669'>+{save_year_fmt} / tahun</font></b>.<br/>"
                f"<i>Dana ini setara dengan cadangan Dana Darurat 3 bulan atau investasi emas fisik murni.</i>",
                body_style
            ),
            Paragraph(f"Potensi Per Bulan:<br/><font size='10' color='#059669'><b>+{save_month_fmt}</b></font>", meta_style)
        ]
    ]
    t_sim = Table(sim_content, colWidths=[127 * mm, 55 * mm])
    t_sim.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#ECFDF5')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#A7F3D0')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t_sim)
    story.append(Spacer(1, 2.5 * mm))

    # =========================================================================
    # BAGIAN 7: 3 PRINSIP EMAS KEUANGAN DOMPETVIBE
    # =========================================================================
    rules_content = [
        [
            Paragraph("<b>PRINSIP FINANSIAL DOMPETVIBE:</b>", body_bold),
            Paragraph("<b>Aturan Emas Pengendalian Belanja</b>", meta_style)
        ],
        [
            Paragraph(
                "• <b>Aturan Jeda 48 Jam:</b> Tunda checkout keinginan non-esensial selama 2 hari untuk meredakan emosi FOMO.<br/>"
                "• <b>Bayar Tabungan Pertama:</b> Sisihkan minimal 20% penghasilan di awal sebelum membagi anggaran belanja harian.<br/>"
                "• <b>Rem Cicilan:</b> Pastikan total cicilan paylater / utang produktif maksimal 15% dari pendapatan bersih bulanan.",
                body_style
            ),
            Paragraph("Kunci Sukses:<br/><b>Disiplin &amp; Konsisten</b>", meta_style)
        ]
    ]
    t_rules = Table(rules_content, colWidths=[127 * mm, 55 * mm])
    t_rules.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t_rules)
    story.append(Spacer(1, 2 * mm))

    # =========================================================================
    # FOOTER HALAMAN 2
    # =========================================================================
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#CBD5E1'), spaceAfter=1.5 * mm))
    story.append(Paragraph(
        "Halaman 2 dari 2 • Laporan dihasilkan otomatis oleh <b>DompetVibe.ai</b> • 100% Aman &amp; Menjaga Kerahasiaan Berkas Tanpa OCR • 2026",
        footer_style
    ))

    # Build PDF
    doc.build(story)
    pdf_buffer.seek(0)
    return pdf_buffer.getvalue()
