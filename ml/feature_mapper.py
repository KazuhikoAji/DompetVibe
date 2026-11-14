import os
import re
import joblib
import pandas as pd
import numpy as np
from datetime import datetime

class BehavioralFeatureMapper:
    def __init__(self, models_dir='models'):
        self.models_dir = models_dir
        self.tfidf_pipeline = None
        self._load_nlp_model()

    def _load_nlp_model(self):
        pipeline_path = os.path.join(self.models_dir, 'tfidf_transaction_pipeline.pkl')
        if os.path.exists(pipeline_path):
            try:
                self.tfidf_pipeline = joblib.load(pipeline_path)
            except:
                self.tfidf_pipeline = None

    def parse_file(self, file_path, original_filename):
        """Membaca berkas mutasi digital (.csv, .xlsx, .pdf)."""
        ext = os.path.splitext(original_filename)[1].lower()
        if ext in ['.jpg', '.jpeg', '.png', '.webp', '.bmp']:
            raise ValueError(
                "Format berkas gambar (.jpg/.png) tidak didukung. "
                "Silakan unggah dokumen mutasi digital asli (.csv, .xlsx, atau .pdf e-Statement) tanpa OCR."
            )
        
        if ext not in ['.csv', '.xlsx', '.xls', '.pdf']:
            raise ValueError(
                f"Format berkas '{ext}' tidak dikenali. "
                "Sistem hanya menerima berkas .csv, .xlsx, atau .pdf e-Statement."
            )

        if ext == '.csv':
            return self._parse_csv(file_path)
        elif ext in ['.xlsx', '.xls']:
            return self._parse_excel(file_path)
        elif ext == '.pdf':
            return self._parse_pdf(file_path)

    MONTH_NAMES_ID = {
        1: 'Januari', 2: 'Februari', 3: 'Maret', 4: 'April', 5: 'Mei', 6: 'Juni',
        7: 'Juli', 8: 'Agustus', 9: 'September', 10: 'Oktober', 11: 'November', 12: 'Desember'
    }

    def _get_month_info(self, tgl_str):
        """Mengekstrak kunci bulan (YYYY-MM) dan label bahasa Indonesia (e.g. Juli 2026)."""
        try:
            parts = str(tgl_str).strip().split('-')
            if len(parts) >= 2:
                year = int(parts[0])
                month = int(parts[1])
                month_key = f"{year:04d}-{month:02d}"
                month_label = f"{self.MONTH_NAMES_ID.get(month, f'Bulan {month}')} {year}"
                return month_key, month_label
        except:
            pass
        return "Lainnya", "Periode Lainnya"

    def _clean_amount(self, val):
        """Membersihkan format string Rupiah / angka seperti Rp 50.000,00 ke float positif."""
        if pd.isna(val):
            return 0.0
        if isinstance(val, (int, float)):
            return abs(float(val))
        s = str(val).strip().replace('Rp', '').replace('IDR', '').replace(' ', '')
        s = s.replace('CR', '').replace('DB', '').replace('Cr', '').replace('Db', '').strip()
        if '.' in s and ',' in s:
            if s.rfind('.') < s.rfind(','):
                s = s.replace('.', '').replace(',', '.')
            else:
                s = s.replace(',', '')
        elif '.' in s and len(s.split('.')[-1]) == 3:
            s = s.replace('.', '')
        elif ',' in s and len(s.split(',')[-1]) == 3:
            s = s.replace(',', '')
        elif ',' in s:
            s = s.replace(',', '.')
        try:
            return abs(float(s))
        except:
            return 0.0

    def _normalize_date(self, tgl_str, default_year='2026'):
        """Menstandarisasi tanggal dari format DD/MM, DD/MM/YY, DD/MM/YYYY, atau YYYY-MM-DD ke YYYY-MM-DD."""
        if not tgl_str:
            return datetime.today().strftime('%Y-%m-%d')
        s = str(tgl_str).strip().replace('-', '/')
        parts = s.split('/')
        try:
            if len(parts) == 2:
                d, m = parts
                return f"{default_year}-{int(m):02d}-{int(d):02d}"
            elif len(parts) == 3:
                if len(parts[0]) == 4:
                    y, m, d = parts[0], parts[1], parts[2]
                else:
                    d, m, y = parts[0], parts[1], parts[2]
                    if len(y) == 2:
                        y = '20' + y
                return f"{int(y):04d}-{int(m):02d}-{int(d):02d}"
        except:
            pass
        return str(tgl_str).strip()

    def _is_income_description(self, desc):
        """Mendeteksi apakah deskripsi transaksi adalah pemasukan (gaji PT, payroll, transfer masuk, bunga, dll)."""
        d = str(desc).lower()
        # Jika transaksi eksplisit keluar (TRF KE, TRANSFER KE, BAYAR), bukan pemasukan meskipun ada nama PT bank penerima
        if any(out in d for out in ['transfer ke', 'trf ke', 'trf bifast ke', 'trsf ke', 'kirim ke', 'bayar ke', 'trf bifast']):
            if not any(inc in d for inc in ['incoming', 'dari', 'dr ']):
                return False

        income_patterns = [
            r'\bpb dari\b', r'\bdari pt[\.\s]', r'\bgaji\b', r'\bpayroll\b', r'\bsalary\b',
            r'\bhonor\b', r'\bhonorarium\b', r'\bbonus\b', r'\bthr\b', r'\bdividen\b',
            r'\binsentif\b', r'\breimburse\b', r'\breimbursement\b', r'\bupah\b',
            r'\bsetor tunai\b', r'\bsetoran tunai\b', r'\btransfer masuk\b', r'\btrsf masuk\b',
            r'\bdana masuk\b', r'\buang saku\b', r'\bkiriman masuk\b', r'\bdari rek\b',
            r'\bterima dari\b', r'\btrsf e-banking cr\b', r'\bbif-in\b', r'\bbifast in\b',
            r'\bswitch cr\b', r'\bkliring cr\b', r'\bbunga\b', r'\bbunga bank\b',
            r'\btransfer dr\b', r'\btrsf dr\b', r'\bbi-fast cr\b', r'\btrf incoming\b', r'\bincoming bifast\b'
        ]
        return any(re.search(pat, d, re.IGNORECASE) for pat in income_patterns)

    def _normalize_columns(self, df):
        """Menemukan kolom tanggal, waktu, nominal, deskripsi, dan tipe (mendukung Debit/Kredit bank asli)."""
        col_map = {}
        debit_col = None
        kredit_col = None

        for col in df.columns:
            clean_col = str(col).strip().lower().replace('_', ' ').replace('-', ' ')
            if any(k in clean_col for k in ['tanggal', 'date', 'tgl', 'waktu', 'valuta']):
                if 'tanggal' not in col_map:
                    col_map['tanggal'] = col
            elif any(k in clean_col for k in ['jam', 'time', 'pukul']):
                if 'jam' not in col_map:
                    col_map['jam'] = col
            elif any(k in clean_col for k in ['deskripsi', 'description', 'keterangan', 'rincian', 'nama transaksi', 'uraian', 'detail', 'transaksi']):
                if 'deskripsi' not in col_map:
                    col_map['deskripsi'] = col
            elif 'debit' in clean_col or 'debet' in clean_col or 'keluar' in clean_col:
                debit_col = col
            elif 'kredit' in clean_col or 'credit' in clean_col or 'masuk' in clean_col:
                kredit_col = col
            elif any(k in clean_col for k in ['nominal', 'amount', 'jumlah', 'mutasi', 'saldo']):
                if 'nominal' not in col_map:
                    col_map['nominal'] = col
            elif any(k in clean_col for k in ['tipe', 'type', 'kategori', 'jenis', 'status', 'd/k', 'db/cr']):
                if 'tipe' not in col_map:
                    col_map['tipe'] = col

        standardized = pd.DataFrame()
        
        # Tanggal
        if 'tanggal' in col_map:
            standardized['tanggal'] = df[col_map['tanggal']].apply(self._normalize_date)
        else:
            standardized['tanggal'] = datetime.today().strftime('%Y-%m-%d')

        # Jam
        if 'jam' in col_map:
            standardized['jam'] = df[col_map['jam']].astype(str).str.strip()
        else:
            standardized['jam'] = '12:00:00'

        # Deskripsi
        if 'deskripsi' in col_map:
            standardized['deskripsi'] = df[col_map['deskripsi']].fillna('Transaksi').astype(str).str.strip()
        else:
            str_cols = df.select_dtypes(include=['object']).columns
            standardized['deskripsi'] = df[str_cols[0]].astype(str) if len(str_cols) > 0 else 'Transaksi'

        # Penanganan Kasus Bank: Kolom Debit dan Kredit Terpisah
        if debit_col and kredit_col:
            nominals = []
            tipes = []
            for _, r in df.iterrows():
                deb_val = self._clean_amount(r[debit_col])
                kred_val = self._clean_amount(r[kredit_col])
                if deb_val > 0:
                    nominals.append(deb_val)
                    tipes.append('expense')
                elif kred_val > 0:
                    nominals.append(kred_val)
                    tipes.append('income')
                else:
                    nominals.append(0.0)
                    tipes.append('expense')
            standardized['nominal'] = nominals
            standardized['tipe'] = tipes
        else:
            # Kolom Nominal Tunggal (misal BCA kolom MUTASI)
            raw_nom_series = df[col_map['nominal']] if 'nominal' in col_map else df.iloc[:, -1]
            standardized['nominal'] = raw_nom_series.apply(self._clean_amount)

            tipes = []
            has_tipe_col = 'tipe' in col_map
            for idx, r in df.iterrows():
                raw_nom_str = str(raw_nom_series.iloc[idx]).strip().upper()
                desc_str = standardized['deskripsi'].iloc[idx]

                # 1. Cek indikator CR (Credit) di kolom nominal / mutasi BCA
                if 'CR' in raw_nom_str or 'KREDIT' in raw_nom_str or raw_nom_str.endswith('CR'):
                    tipes.append('income')
                # 2. Cek indikator DB (Debit) di kolom nominal
                elif 'DB' in raw_nom_str or 'DEBET' in raw_nom_str or 'DEBIT' in raw_nom_str:
                    tipes.append('expense')
                # 3. Cek kolom tipe eksplisit jika ada
                elif has_tipe_col:
                    t_val = str(r[col_map['tipe']]).strip().lower()
                    if any(i in t_val for i in ['in', 'masuk', 'kredit', 'cr', 'c']):
                        tipes.append('income')
                    else:
                        tipes.append('expense')
                # 4. Cek teks deskripsi (PT, CV, Payroll, Gaji, dll)
                elif self._is_income_description(desc_str):
                    tipes.append('income')
                else:
                    tipes.append('expense')

            standardized['tipe'] = tipes

        standardized = standardized[standardized['nominal'] > 0].reset_index(drop=True)
        # Saring baris non-transaksi (saldo awal/akhir, header rekapitulasi)
        skip_patterns = r'saldo awal|saldo akhir|beginning balance|ending balance|saldo per|total mutasi|rekapitulasi'
        standardized = standardized[~standardized['deskripsi'].str.lower().str.contains(skip_patterns, na=False)].reset_index(drop=True)
        return standardized

    def _parse_csv(self, file_path):
        for sep in [',', ';', '\t']:
            try:
                df = pd.read_csv(file_path, sep=sep)
                if df.shape[1] >= 2:
                    norm = self._normalize_columns(df)
                    if len(norm) > 0:
                        return norm
            except:
                continue
        df = pd.read_csv(file_path)
        return self._normalize_columns(df)

    def _parse_excel(self, file_path):
        df = pd.read_excel(file_path)
        return self._normalize_columns(df)

    def _parse_pdf(self, file_path):
        """
        Mesin Ekstraksi PDF Mutasi Perbankan Indonesia:
        Mendukung e-Statement m-BCA, KlikBCA, BCA Mobile, Mandiri Livin, BRImo, BNI.
        Menerapkan 3 strategi bertingkat dengan seleksi hasil terlengkap.
        """
        import pdfplumber

        skip_patterns = r'saldo awal|saldo akhir|beginning balance|ending balance|saldo per|total mutasi|rekapitulasi'

        # -------------------------------------------------------------
        # STRATEGI 1: Ekstraksi Tabel Bersih (Jika PDF memiliki grid tabel)
        # -------------------------------------------------------------
        df_table = None
        table_rows = []
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                if tables:
                    for t in tables:
                        if not t or len(t) < 2:
                            continue
                        header_idx = -1
                        for idx, row in enumerate(t[:5]):
                            clean_r = [str(c).lower() for c in row if c]
                            row_txt = ' '.join(clean_r)
                            if any(k in row_txt for k in ['tgl', 'date', 'tanggal']) and any(k in row_txt for k in ['keterangan', 'deskripsi', 'mutasi', 'debit', 'jumlah', 'nominal']):
                                header_idx = idx
                                break
                        
                        if header_idx != -1:
                            raw_header = [str(c).replace('\n', ' ').strip() if c else f'col_{i}' for i, c in enumerate(t[header_idx])]
                            for data_row in t[header_idx + 1:]:
                                if data_row and any(data_row):
                                    clean_data = [str(c).replace('\n', ' ').strip() if c else '' for c in data_row]
                                    if len(clean_data) == len(raw_header):
                                        table_rows.append(dict(zip(raw_header, clean_data)))

        if table_rows:
            try:
                df_table_raw = pd.DataFrame(table_rows)
                df_table = self._normalize_columns(df_table_raw)
            except:
                df_table = None

        # -------------------------------------------------------------
        # STRATEGI 2: Ekstraksi Halaman & Pemisahan Header/Footer Ketat Multi-Bank
        # Mendukung e-Statement m-BCA, Permata Bank, Mandiri, BRI, BNI multi-halaman.
        # Menjamin header dan footer tiap halaman tidak pernah masuk ke rincian transaksi.
        # -------------------------------------------------------------
        def is_table_header(l):
            low = l.lower()
            has_date = bool(re.search(r'\b(tgl|tanggal|date|trx\.?\s*date)\b', low))
            has_cols = any(k in low for k in ['uraian', 'keterangan', 'description', 'mutasi', 'debet', 'kredit', 'saldo', 'cbg', 'cb', 'balance', 'transaksi'])
            return (has_date and has_cols) or ('tanggal keterangan' in low) or ('uraian trx' in low)

        def is_sub_header(l):
            low = l.lower()
            return any(k in low for k in ['trx. date', 'val. date', 'trx. description', 'debit credit balance', '(dd/mm)', 'dd/mm'])

        def is_footer(l):
            low = l.lower()
            footer_kws = [
                'bersambung ke halaman', 'halaman/page', 'halaman ', 'page ',
                'berizin dan diawasi oleh otoritas jasa keuangan', 'lembaga penjamin simpanan',
                'catatan:', 'disclaimer', 'laporan transaksi ini sah', 'saldo awal :', 'saldo akhir :',
                'mutasi cr :', 'mutasi db :', 'total mutasi', 'rekapitulasi', 'realisasi bagi hasil',
                'file estatement', 'jika dalam waktu 7 (tujuh)'
            ]
            if any(m in low for m in footer_kws):
                return True
            if low.startswith('total ') and any(c.isdigit() for c in low):
                return True
            return False

        def is_metadata_noise(l):
            low = l.lower()
            noise = [
                'rekening koran', 'account statement', 'unit usaha syariah', 'rekening tahapan',
                'kcu ', 'statement period', 'statement date', 'cif no', 'account no',
                'product name', 'currency', 'mata uang', 'periode laporan', 'tanggal laporan',
                'no.cif', 'no. rekening', 'nama produk', 'cabang', 'branch',
                'ringkasan rekening', 'ekuivalen saldo rupiah', 'rekening simpanan',
                'dengan telah berlakunya pojk', 'terkait penutupan', 'secara otomatis atas rekening',
                'selama 6 bulan berturut-turut', 'penutupan rekening otomatis', 'segera tambahkan saldo',
                'auto close', 'penyesuaianstatusrekening', 'apabila nasabah tidak melakukan',
                'telah menyetujui segala data', 'bca berhak setiap saat', 'kramat halaman',
                'rt001 rw003', 'kemuning', 'tegal 52181'
            ]
            return any(n in low for n in noise)

        def is_income_indicator(text):
            low = text.lower()
            if re.search(r'\b(cr|kredit|income|masuk|setor|setoran|pemasukan|gaji|payroll|bunga|bagi\s*hasil|pb\s*dari|cashback|refund)\b', low):
                return True
            return False

        date_re = re.compile(r'(\b\d{2}[/-]\d{2}(?:[/-]\d{2,4})?)\b')
        amt_db_cr_re = re.compile(r'([0-9]{1,3}(?:[.,][0-9]{3})+(?:[.,][0-9]{2})?|[0-9]+[.,][0-9]{2})\s*(CR|DB)', re.IGNORECASE)
        plain_amt_re = re.compile(r'([0-9]{1,3}(?:[.,][0-9]{3})*(?:[.,][0-9]{2}))')

        all_pages_lines = []
        with pdfplumber.open(file_path) as pdf:
            for p_idx, page in enumerate(pdf.pages):
                text = page.extract_text() or ""
                raw_lines = [l.strip() for l in text.split('\n') if l.strip()]

                has_hdr = any(is_table_header(l) for l in raw_lines)
                if not has_hdr and p_idx == 0:
                    continue

                in_table = not has_hdr
                page_clean = []

                for l in raw_lines:
                    if has_hdr and not in_table:
                        if is_table_header(l):
                            in_table = True
                        continue

                    if is_sub_header(l):
                        continue

                    if is_footer(l):
                        if has_hdr:
                            break
                        else:
                            continue

                    if is_metadata_noise(l):
                        continue

                    page_clean.append(l)

                all_pages_lines.append(page_clean)

        transactions = []
        current_tx = None
        running_balance = None

        for page_lines in all_pages_lines:
            for line in page_lines:
                clean_l = line.strip()
                if not clean_l or is_metadata_noise(clean_l) or is_footer(clean_l):
                    continue

                d_matches = list(date_re.finditer(clean_l))
                is_date_line = bool(d_matches and d_matches[0].start() <= 6)

                if 'saldo awal' in clean_l.lower():
                    amts = plain_amt_re.findall(clean_l)
                    if amts:
                        running_balance = self._clean_amount(amts[-1])
                    continue

                if is_date_line:
                    if current_tx and current_tx.get('nominal') is not None:
                        transactions.append(current_tx)
                        current_tx = None

                    tgl = d_matches[0].group(1)
                    rem = clean_l[d_matches[0].end():].strip()

                    d_val = date_re.match(rem)
                    if d_val:
                        rem = rem[d_val.end():].strip()

                    db_cr_m = amt_db_cr_re.search(rem)
                    plain_amts = list(plain_amt_re.finditer(rem))

                    if db_cr_m:
                        nom_str = db_cr_m.group(1)
                        db_cr = db_cr_m.group(2).upper()
                        desc = rem[:db_cr_m.start()].strip()
                        desc = re.sub(r'\s+\d{4}$', '', desc)
                        nom_val = self._clean_amount(nom_str)

                        if running_balance is not None:
                            if db_cr == 'CR':
                                running_balance += nom_val
                            else:
                                running_balance -= nom_val

                        current_tx = {
                            'tanggal': tgl,
                            'desc_parts': [desc] if desc else [],
                            'nominal': nom_val,
                            'tipe': 'income' if db_cr == 'CR' else 'expense',
                            'saldo': None
                        }
                    elif plain_amts:
                        if len(plain_amts) >= 2:
                            mutasi_str = plain_amts[0].group(1)
                            saldo_str = plain_amts[1].group(1)
                            desc = rem[:plain_amts[0].start()].strip()
                            mutasi_val = self._clean_amount(mutasi_str)
                            saldo_val = self._clean_amount(saldo_str)

                            tx_type = 'expense'
                            if is_income_indicator(desc) or is_income_indicator(clean_l):
                                tx_type = 'income'
                            elif running_balance is not None:
                                if abs((running_balance + mutasi_val) - saldo_val) < 1.0:
                                    tx_type = 'income'
                                elif abs((running_balance - mutasi_val) - saldo_val) < 1.0:
                                    tx_type = 'expense'
                                elif saldo_val > running_balance:
                                    tx_type = 'income'
                                else:
                                    tx_type = 'expense'
                            else:
                                tx_type = 'income' if is_income_indicator(desc) else 'expense'

                            running_balance = saldo_val
                            current_tx = {
                                'tanggal': tgl,
                                'desc_parts': [desc] if desc else [],
                                'nominal': mutasi_val,
                                'tipe': tx_type,
                                'saldo': saldo_val
                            }
                        else:
                            mutasi_str = plain_amts[0].group(1)
                            desc = rem[:plain_amts[0].start()].strip()
                            mutasi_val = self._clean_amount(mutasi_str)
                            is_inc = is_income_indicator(desc) or is_income_indicator(clean_l)
                            current_tx = {
                                'tanggal': tgl,
                                'desc_parts': [desc] if desc else [],
                                'nominal': mutasi_val,
                                'tipe': 'income' if is_inc else 'expense',
                                'saldo': None
                            }
                    else:
                        current_tx = {
                            'tanggal': tgl,
                            'desc_parts': [rem] if rem else [],
                            'nominal': None,
                            'tipe': None,
                            'saldo': None
                        }
                elif current_tx:
                    if current_tx.get('nominal') is None:
                        db_cr_m = amt_db_cr_re.search(clean_l)
                        plain_amts = list(plain_amt_re.finditer(clean_l))
                        if db_cr_m:
                            nom_str = db_cr_m.group(1)
                            db_cr = db_cr_m.group(2).upper()
                            pre = clean_l[:db_cr_m.start()].strip()
                            if pre:
                                current_tx['desc_parts'].append(pre)
                            current_tx['nominal'] = self._clean_amount(nom_str)
                            current_tx['tipe'] = 'income' if db_cr == 'CR' else 'expense'
                        elif plain_amts:
                            mut_str = plain_amts[0].group(1)
                            pre = clean_l[:plain_amts[0].start()].strip()
                            if pre:
                                current_tx['desc_parts'].append(pre)
                            current_tx['nominal'] = self._clean_amount(mut_str)
                            d_full = ' '.join(current_tx['desc_parts'])
                            current_tx['tipe'] = 'income' if is_income_indicator(d_full) else 'expense'
                        else:
                            current_tx['desc_parts'].append(clean_l)
                    else:
                        p_m = plain_amt_re.search(clean_l)
                        end_p = p_m.start() if p_m else len(clean_l)
                        extra = clean_l[:end_p].strip()
                        extra = re.sub(r'^(WS ID \d+|0000|\d{4})\s*', '', extra)
                        if extra and extra != '0000' and not is_metadata_noise(extra) and not is_footer(extra):
                            current_tx['desc_parts'].append(extra)

            if current_tx and current_tx.get('nominal') is not None:
                transactions.append(current_tx)
                current_tx = None

        if current_tx and current_tx.get('nominal') is not None:
            transactions.append(current_tx)

        bca_records = []
        for t in transactions:
            full_desc = ' '.join(t['desc_parts']).strip()
            nom = t['nominal']
            if nom is not None and nom > 0:
                bca_records.append({
                    'tanggal': self._normalize_date(t['tanggal']),
                    'jam': '12:00:00',
                    'deskripsi': full_desc if full_desc else 'Transaksi Bank Digital',
                    'nominal': nom,
                    'tipe': t['tipe']
                })

        df_bca = None
        if bca_records:
            df_bca_raw = pd.DataFrame(bca_records)
            df_bca_raw = df_bca_raw[df_bca_raw['nominal'] > 0].reset_index(drop=True)
            df_bca = df_bca_raw[~df_bca_raw['deskripsi'].str.lower().str.contains(skip_patterns, na=False)].reset_index(drop=True)

        # -------------------------------------------------------------
        # STRATEGI 3: Ekstraksi Teks Generik (Mandiri, BRI, BNI)
        # -------------------------------------------------------------
        df_gen = None
        generic_records = []
        gen_date_pattern = re.compile(r'(\b\d{2}[/-]\d{2}(?:[/-]\d{2,4})?\b|\b\d{4}[/-]\d{2}[/-]\d{2}\b)')
        gen_amount_pattern = re.compile(r'([0-9]{1,3}(?:[.,][0-9]{3})+(?:[.,][0-9]{2})?)')

        for page_lines in all_pages_lines:
            for line in page_lines:
                d_m = gen_date_pattern.search(line)
                amounts = gen_amount_pattern.findall(line)
                if d_m and amounts:
                    tgl = d_m.group(1)
                    nom = amounts[0]
                    desc = line.replace(tgl, '').replace(nom, '').strip()
                    if any(k in desc.lower() for k in ['saldo awal', 'saldo akhir', 'beginning', 'ending']):
                        continue
                    is_income = any(w in line.lower() for w in ['cr', 'kredit', 'masuk', 'transfer masuk', 'gaji']) or self._is_income_description(desc)
                    generic_records.append({
                        'tanggal': self._normalize_date(tgl),
                        'jam': '12:00:00',
                        'deskripsi': desc if desc else 'Transaksi Mutasi Bank',
                        'nominal': self._clean_amount(nom),
                        'tipe': 'income' if is_income else 'expense'
                    })

        if generic_records:
            df_gen_raw = pd.DataFrame(generic_records)
            df_gen_raw = df_gen_raw[df_gen_raw['nominal'] > 0].reset_index(drop=True)
            df_gen = df_gen_raw[~df_gen_raw['deskripsi'].str.lower().str.contains(skip_patterns, na=False)].reset_index(drop=True)

        # -------------------------------------------------------------
        # SELEKSI STRATEGI PRESISI TINGGI
        # Prioritas 1: State-machine m-BCA (Akurasi tinggi, tanpa duplikasi saldo)
        # Prioritas 2: Ekstraksi Tabel Bersih
        # Prioritas 3: Ekstraksi Baris Generik
        # -------------------------------------------------------------
        if df_bca is not None and len(df_bca) > 0:
            return df_bca
        elif df_table is not None and len(df_table) > 0:
            return df_table
        elif df_gen is not None and len(df_gen) > 0:
            return df_gen

        raise ValueError(
            "Tidak dapat mengekstrak daftar transaksi dari berkas PDF ini. "
            "Pastikan berkas adalah mutasi digital resmi m-BCA, KlikBCA, atau bank nasional lainnya."
        )

    def _classify_transaction_details(self, desc, tipe):
        """
        Taksonomi Perbankan Indonesia:
        Mengelompokkan transaksi ke dalam kategori finansial anggaran (Needs, Wants, Cicilan, Adm Bank, dll)
        dan kategori visual pengeluaran.
        """
        d = str(desc).lower().strip()

        # 1. Pemasukan (Income)
        if tipe == 'income' or self._is_income_description(desc):
            return {
                'tipe': 'income',
                'kategori': 'Pemasukan',
                'category_group': 'Pemasukan',
                'is_impulse': False,
                'is_debt': False
            }

        # 2. Biaya Administrasi & Tagihan Bank Resmi
        bank_adm_kw = [
            'biaya adm', 'adm bulanan', 'biaya administrasi', 'biaya kartu', 
            'biaya pemeliharaan', 'biaya transaksi', 'biaya txn', 'biaya trsf',
            'biaya transfer', 'biaya bi-fast', 'biaya bifast', 'biaya kliring',
            'pajak bunga', 'materai', 'fee transfer', 'biaya buku', 'kartu atm',
            'biaya sms', 'sms notifikasi', 'biaya notifikasi', 'sms banking', 'adm.'
        ]
        if any(k in d for k in bank_adm_kw):
            return {
                'tipe': 'expense',
                'kategori': 'Kebutuhan (Needs)',
                'category_group': 'Biaya Adm & Tagihan Bank',
                'is_impulse': False,
                'is_debt': False
            }

        # 3. Pinjaman, Cicilan & E-Paylater (Debt Obligations)
        debt_kw = [
            'spinjam', 'spaylater', 'kopkar', 'koperasi', 'kredivo', 'akulaku',
            'gopaylater', 'indodana', 'ada kami', 'easycash', 'julo', 'cicilan',
            'angsuran', 'pinjaman', 'pembiayaan', 'leasing', 'fif', 'oto finance', 'baf'
        ]
        if any(k in d for k in debt_kw):
            return {
                'tipe': 'expense',
                'kategori': 'Cicilan / Pinjaman',
                'category_group': 'Cicilan & Pinjaman',
                'is_impulse': False,
                'is_debt': True  # Memicu Paylater_Status = 2
            }

        # 4. Kebutuhan Pokok, Rumah Tangga & Tagihan Utilitas
        utilities_kw = [
            'listrik', 'pln', 'air pam', 'pdam', 'bpjs', 'pbb', 'wifi', 'indihome',
            'biznet', 'first media', 'pulsa', 'paket data', 'kuota', 'telkomsel', 'mytelkomsel', 
            'indosat', 'xl axiata', 'tri', 'smartfren', 'sembako', 'beras', 'minyak goreng',
            'sayur', 'telur', 'pasar', 'supermarket', 'superindo', 'indomaret', 
            'alfamart', 'hypermart', 'lotte mart'
        ]
        if any(k in d for k in utilities_kw):
            return {
                'tipe': 'expense',
                'kategori': 'Kebutuhan (Needs)',
                'category_group': 'Kebutuhan Pokok & Tagihan',
                'is_impulse': False,
                'is_debt': False
            }

        # 5. Transportasi & Mobilitas Harian
        transport_kw = [
            'krl', 'commuter', 'mrt', 'lrt', 'transjakarta', 'busway', 'angkot',
            'bensin', 'pertalite', 'pertamax', 'spbu', 'shell', 'parkir', 'tol',
            'goride', 'grabcar', 'ojol', 'gojek', 'grab', 'maxim'
        ]
        if any(k in d for k in transport_kw):
            return {
                'tipe': 'expense',
                'kategori': 'Kebutuhan (Needs)',
                'category_group': 'Transportasi',
                'is_impulse': False,
                'is_debt': False
            }

        # 6. Kesehatan & Medis
        health_kw = [
            'apotek', 'kimia farma', 'k24', 'k-24', 'dokter', 'klinik', 'obat',
            'vitamin', 'rumah sakit', 'rsud', 'halodoc', 'alodokter'
        ]
        if any(k in d for k in health_kw):
            return {
                'tipe': 'expense',
                'kategori': 'Kebutuhan (Needs)',
                'category_group': 'Kesehatan',
                'is_impulse': False,
                'is_debt': False
            }

        # 7. Makanan Pokok Harian Non-Impulsif (Warteg, Makan Siang Murah)
        daily_food_kw = [
            'warteg', 'makan siang', 'sarapan', 'makan malam', 'catering', 'nasi rames',
            'ketoprak', 'nasi uduk', 'pecel', 'sate', 'siomay', 'batagor', 'kantin'
        ]
        if any(k in d for k in daily_food_kw) and not any(h in d for h in ['kopi', 'cafe', 'boba', 'warkop']):
            return {
                'tipe': 'expense',
                'kategori': 'Kebutuhan (Needs)',
                'category_group': 'Kuliner & F&B',
                'is_impulse': False,
                'is_debt': False
            }

        # 8. Kuliner Santai, Cafe, Kopi & F&B Hedonis (Impulse / Wants)
        hedonic_fnb_kw = [
            'warkop', 'kopi', 'cafe', 'kafe', 'jajan', 'boba', 'starbucks', 'kenangan',
            'tuku', 'janji jiwa', 'fore', 'kulo', 'chatime', 'mixue', 'gofood', 
            'grabfood', 'shopeefood', 'mcd', 'kfc', 'hokben', 'burger king', 'pizza',
            'bakso', 'soto', 'mie gacoan', 'geprek', 'resto', 'kuliner'
        ]
        if any(k in d for k in hedonic_fnb_kw):
            return {
                'tipe': 'expense',
                'kategori': 'Keinginan (Wants)',
                'category_group': 'Kuliner & F&B',
                'is_impulse': True,
                'is_debt': False
            }

        # 9. Belanja Daring, Marketplace & Gaya Hidup (Impulse / Wants)
        ecommerce_kw = [
            'shopee', 'tokopedia', 'tiktok shop', 'lazada', 'blibli', 'zalora',
            'baju', 'celana', 'sepatu', 'tas', 'outfit', 'fashion', 'zara', 'uniqlo',
            'h&m', 'skincare', 'makeup', 'kosmetik', 'gadget', 'iphone', 'samsung',
            'headset', 'tws', 'elektronik', 'aksesoris'
        ]
        if any(k in d for k in ecommerce_kw):
            return {
                'tipe': 'expense',
                'kategori': 'Keinginan (Wants)',
                'category_group': 'Belanja & E-Commerce',
                'is_impulse': True,
                'is_debt': False
            }

        # 10. Hiburan, Media & Game (Impulse / Wants)
        entertainment_kw = [
            'game', 'steam', 'playstation', 'mobile legends', 'topup diamond', 'spotify',
            'netflix', 'disney', 'youtube premium', 'bioskop', 'xxi', 'cgv', 'cinepolis',
            'karaoke', 'billiard', 'konser', 'tiket nonton'
        ]
        if any(k in d for k in entertainment_kw):
            return {
                'tipe': 'expense',
                'kategori': 'Keinginan (Wants)',
                'category_group': 'Hiburan & Gaya Hidup',
                'is_impulse': True,
                'is_debt': False
            }

        # 11. Top Up E-Wallet
        topup_kw = ['topup', 'top up', 'gopay', 'shopeepay', 'ovo', 'dana', 'linkaja']
        if any(k in d for k in topup_kw):
            return {
                'tipe': 'expense',
                'kategori': 'Top-Up E-Wallet',
                'category_group': 'Top-Up & E-Wallet',
                'is_impulse': False,
                'is_debt': False
            }

        # 12. Virtual Account (VA)
        if 'virtual account' in d or ' va ' in f" {d} ":
            # Cek jika VA untuk marketplace
            if any(m in d for m in ['tokopedia', 'shopee', 'tiktok', 'lazada']):
                return {
                    'tipe': 'expense',
                    'kategori': 'Keinginan (Wants)',
                    'category_group': 'Belanja & E-Commerce',
                    'is_impulse': True,
                    'is_debt': False
                }
            elif any(u in d for u in ['pln', 'bpjs', 'pdam', 'kampus', 'sekolah']):
                return {
                    'tipe': 'expense',
                    'kategori': 'Kebutuhan (Needs)',
                    'category_group': 'Kebutuhan Pokok & Tagihan',
                    'is_impulse': False,
                    'is_debt': False
                }
            else:
                return {
                    'tipe': 'expense',
                    'kategori': 'Tagihan / VA',
                    'category_group': 'Virtual Account & Tagihan',
                    'is_impulse': False,
                    'is_debt': False
                }

        # 13. Transfer Dana & Penarikan Tunai
        transfer_kw = [
            'transfer ke', 'trsf e-banking db', 'tarik tunai', 'crm atm', 
            'kirim uang', 'kliring db', 'bi-fast db', 'm-transfer', 'switching db', 
            'transfer', 'trf bifast', 'trf ke', 'trf ', 'trsf '
        ]
        if any(k in d for k in transfer_kw):
            return {
                'tipe': 'expense',
                'kategori': 'Transfer / Tarik Tunai',
                'category_group': 'Transfer & Tarik Tunai',
                'is_impulse': False,
                'is_debt': False
            }

        # 14. Pembayaran Merchant & QRIS UMKM
        if 'qris' in d or 'qr ' in f" {d} ":
            return {
                'tipe': 'expense',
                'kategori': 'Kebutuhan (Needs)',
                'category_group': 'Belanja Ritel & QRIS',
                'is_impulse': False,
                'is_debt': False
            }

        # 15. Fallback: Klasifikasi Pos Umum / Lain-lain
        is_impulse = False
        if self.tfidf_pipeline:
            try:
                hedonic_cues = ['belanja', 'store', 'mall', 'boutique', 'cafe', 'resto', 'jajan', 'game', 'hobby', 'optik', 'salon', 'bar']
                if any(c in d for c in hedonic_cues):
                    pred = self.tfidf_pipeline.predict([desc])[0]
                    is_impulse = bool(pred == 1)
                else:
                    is_impulse = False
            except:
                is_impulse = False

        cat_label = 'Keinginan (Wants)' if is_impulse else 'Kebutuhan (Needs)'
        return {
            'tipe': 'expense',
            'kategori': cat_label,
            'category_group': 'Lain-lain',
            'is_impulse': is_impulse,
            'is_debt': False
        }

    def classify_and_map(self, df_transactions, user_declared_income=None):
        """
        1. Menandai tiap transaksi ke dalam taksonomi finansial perbankan Indonesia.
        2. Mengelompokkan transaksi per bulan (Juli 2026, Agustus 2026, dll.) untuk analisis multi-bulan.
        3. Menghitung ringkasan likuiditas arus kas (Pemasukan, Pengeluaran, Sisa Tabungan, Beban Kas).
        4. Menghitung 7 fitur perilaku belanja (Mendeley Data) dengan normalisasi rata-rata bulanan.
        5. Menyusun rekomendasi finansial personal & analisis tren multi-bulan berbasis data.
        """
        if df_transactions.empty:
            raise ValueError("Data transaksi kosong.")

        records = []
        has_paylater = False

        for _, row in df_transactions.iterrows():
            desc = str(row['deskripsi']).strip()
            raw_tipe = str(row.get('tipe', 'expense')).lower()
            nom = float(row['nominal'])
            tgl = str(row['tanggal'])
            jam = str(row.get('jam', '12:00:00'))

            # Klasifikasi detail menggunakan taksonomi perbankan
            detail = self._classify_transaction_details(desc, raw_tipe)
            
            if detail['is_debt']:
                has_paylater = True

            m_key, m_label = self._get_month_info(tgl)

            records.append({
                'tanggal': tgl,
                'jam': jam,
                'deskripsi': desc,
                'nominal': nom,
                'nominal_fmt': f"Rp {int(nom):,}".replace(',', '.'),
                'tipe': detail['tipe'],
                'kategori': detail['kategori'],
                'category_group': detail['category_group'],
                'is_impulse': detail['is_impulse'],
                'is_debt': detail['is_debt'],
                'month_key': m_key,
                'month_label': m_label
            })

        df_processed = pd.DataFrame(records)
        df_expense = df_processed[df_processed['tipe'] == 'expense']
        df_income = df_processed[df_processed['tipe'] == 'income']

        total_income = df_income['nominal'].sum()
        total_expense = df_expense['nominal'].sum()
        total_wants = df_expense[df_expense['is_impulse']]['nominal'].sum()
        total_needs = df_expense[~df_expense['is_impulse'] & ~df_expense['is_debt']]['nominal'].sum()
        total_debt = df_expense[df_expense['is_debt']]['nominal'].sum()

        # =============================================================
        # PENGELOMPOKAN DATA BERDASARKAN BULAN (MONTHLY BREAKDOWN)
        # =============================================================
        month_groups = {}
        for rec in records:
            mk = rec['month_key']
            ml = rec['month_label']
            if mk not in month_groups:
                month_groups[mk] = {
                    'month_key': mk,
                    'month_label': ml,
                    'records': []
                }
            month_groups[mk]['records'].append(rec)

        # Urutkan bulan secara kronologis
        sorted_keys = sorted([k for k in month_groups.keys() if k != "Lainnya"])
        if "Lainnya" in month_groups:
            sorted_keys.append("Lainnya")

        monthly_breakdown = []
        for mk in sorted_keys:
            mg = month_groups[mk]
            m_recs = mg['records']
            m_inc = sum(r['nominal'] for r in m_recs if r['tipe'] == 'income')
            m_exp = sum(r['nominal'] for r in m_recs if r['tipe'] == 'expense')
            m_needs = sum(r['nominal'] for r in m_recs if r['tipe'] == 'expense' and not r['is_impulse'] and not r['is_debt'])
            m_wants = sum(r['nominal'] for r in m_recs if r['tipe'] == 'expense' and r['is_impulse'])
            m_debt = sum(r['nominal'] for r in m_recs if r['tipe'] == 'expense' and r['is_debt'])
            m_net = m_inc - m_exp
            m_sav_pct = (m_net / m_inc * 100) if m_inc > 0 else (0.0 if m_exp == 0 else -100.0)

            # Pos dominan bulan ini
            m_cats = {}
            for r in m_recs:
                if r['tipe'] == 'expense':
                    c_grp = r['category_group']
                    m_cats[c_grp] = m_cats.get(c_grp, 0.0) + r['nominal']
            m_top_cat = max(m_cats.items(), key=lambda x: x[1])[0] if m_cats else 'Lain-lain'

            if m_net < 0:
                m_status = "Defisit"
            elif m_sav_pct < 15:
                m_status = "Rentan"
            else:
                m_status = "Sehat"

            monthly_breakdown.append({
                'month_key': mk,
                'month_label': mg['month_label'],
                'total_income': float(m_inc),
                'total_income_fmt': f"Rp {int(m_inc):,}".replace(',', '.'),
                'total_expense': float(m_exp),
                'total_expense_fmt': f"Rp {int(m_exp):,}".replace(',', '.'),
                'net_cashflow': float(m_net),
                'net_cashflow_fmt': f"Rp {int(m_net):,}".replace(',', '.'),
                'savings_ratio_pct': round(float(m_sav_pct), 1),
                'total_needs': float(m_needs),
                'total_needs_fmt': f"Rp {int(m_needs):,}".replace(',', '.'),
                'total_wants': float(m_wants),
                'total_wants_fmt': f"Rp {int(m_wants):,}".replace(',', '.'),
                'total_debt': float(m_debt),
                'total_debt_fmt': f"Rp {int(m_debt):,}".replace(',', '.'),
                'tx_count': len(m_recs),
                'top_category': m_top_cat,
                'status': m_status
            })

        valid_months = [m for m in monthly_breakdown if m['month_key'] != "Lainnya"]
        num_months = len(valid_months) if valid_months else 1
        is_multi_month = bool(num_months >= 2)

        if is_multi_month:
            avg_monthly_income = total_income / num_months
            avg_monthly_expense = total_expense / num_months
            avg_monthly_net_cashflow = (total_income - total_expense) / num_months
            avg_monthly_savings_ratio = (avg_monthly_net_cashflow / avg_monthly_income * 100) if avg_monthly_income > 0 else 0.0
            avg_monthly_needs = total_needs / num_months
            avg_monthly_wants = total_wants / num_months
            avg_monthly_debt = total_debt / num_months

            highest_exp_month = max(valid_months, key=lambda x: x['total_expense'])

            # Tren perubahan pengeluaran dari bulan awal ke bulan akhir
            first_m = valid_months[0]
            last_m = valid_months[-1]
            if first_m['total_expense'] > 0 and len(valid_months) >= 2:
                diff_exp = last_m['total_expense'] - first_m['total_expense']
                diff_pct = (diff_exp / first_m['total_expense']) * 100
                if diff_pct > 10:
                    trend_dir = f"Tren belanja meningkat (+{abs(round(diff_pct, 1))}%) dari {first_m['month_label']} ke {last_m['month_label']}."
                elif diff_pct < -10:
                    trend_dir = f"Tren belanja menurun hemat (-{abs(round(diff_pct, 1))}%) dari {first_m['month_label']} ke {last_m['month_label']}."
                else:
                    trend_dir = f"Tren belanja relatif stabil antara {first_m['month_label']} dan {last_m['month_label']}."
            else:
                trend_dir = ""

            avg_exp_fmt = f"Rp {int(avg_monthly_expense):,}".replace(',', '.')
            avg_inc_fmt = f"Rp {int(avg_monthly_income):,}".replace(',', '.')
            avg_net_fmt = f"Rp {int(avg_monthly_net_cashflow):,}".replace(',', '.')

            trend_narrative = (
                f"Berdasarkan tren {num_months} bulan terakhir, rata-rata pengeluaran bulanan Anda adalah {avg_exp_fmt} "
                f"dengan rata-rata pemasukan {avg_inc_fmt} (rata-rata sisa kas {avg_net_fmt} atau {round(avg_monthly_savings_ratio, 1)}% per bulan). "
                f"Puncak pengeluaran tertinggi terjadi pada {highest_exp_month['month_label']} sebesar {highest_exp_month['total_expense_fmt']}. {trend_dir}"
            ).strip()

            multi_month_summary = {
                'is_multi_month': True,
                'num_months': num_months,
                'avg_monthly_income': float(avg_monthly_income),
                'avg_monthly_income_fmt': f"Rp {int(avg_monthly_income):,}".replace(',', '.'),
                'avg_monthly_expense': float(avg_monthly_expense),
                'avg_monthly_expense_fmt': f"Rp {int(avg_monthly_expense):,}".replace(',', '.'),
                'avg_monthly_net_cashflow': float(avg_monthly_net_cashflow),
                'avg_monthly_net_cashflow_fmt': f"Rp {int(avg_monthly_net_cashflow):,}".replace(',', '.'),
                'avg_monthly_savings_ratio_pct': round(float(avg_monthly_savings_ratio), 1),
                'avg_monthly_needs': float(avg_monthly_needs),
                'avg_monthly_needs_fmt': f"Rp {int(avg_monthly_needs):,}".replace(',', '.'),
                'avg_monthly_wants': float(avg_monthly_wants),
                'avg_monthly_wants_fmt': f"Rp {int(avg_monthly_wants):,}".replace(',', '.'),
                'avg_monthly_debt': float(avg_monthly_debt),
                'avg_monthly_debt_fmt': f"Rp {int(avg_monthly_debt):,}".replace(',', '.'),
                'highest_expense_month': highest_exp_month['month_label'],
                'highest_expense_amount_fmt': highest_exp_month['total_expense_fmt'],
                'trend_narrative': trend_narrative
            }
        else:
            highest_m = monthly_breakdown[0] if monthly_breakdown else None
            multi_month_summary = {
                'is_multi_month': False,
                'num_months': 1,
                'avg_monthly_income': float(total_income),
                'avg_monthly_income_fmt': f"Rp {int(total_income):,}".replace(',', '.'),
                'avg_monthly_expense': float(total_expense),
                'avg_monthly_expense_fmt': f"Rp {int(total_expense):,}".replace(',', '.'),
                'avg_monthly_net_cashflow': float(total_income - total_expense),
                'avg_monthly_net_cashflow_fmt': f"Rp {int(total_income - total_expense):,}".replace(',', '.'),
                'avg_monthly_savings_ratio_pct': round(float((total_income - total_expense) / total_income * 100) if total_income > 0 else 0.0, 1),
                'avg_monthly_needs': float(total_needs),
                'avg_monthly_needs_fmt': f"Rp {int(total_needs):,}".replace(',', '.'),
                'avg_monthly_wants': float(total_wants),
                'avg_monthly_wants_fmt': f"Rp {int(total_wants):,}".replace(',', '.'),
                'avg_monthly_debt': float(total_debt),
                'avg_monthly_debt_fmt': f"Rp {int(total_debt):,}".replace(',', '.'),
                'highest_expense_month': highest_m['month_label'] if highest_m else '-',
                'highest_expense_amount_fmt': highest_m['total_expense_fmt'] if highest_m else 'Rp 0',
                'trend_narrative': None
            }

        # Penentuan Nilai Efektif untuk Normalisasi Model ML
        if user_declared_income and user_declared_income > 0:
            effective_income = user_declared_income
            calc_monthly_income = user_declared_income
        elif is_multi_month:
            effective_income = total_income
            calc_monthly_income = avg_monthly_income if avg_monthly_income > 0 else max(avg_monthly_expense, 3000000.0)
        elif total_income > 0:
            effective_income = total_income
            calc_monthly_income = total_income
        else:
            effective_income = max(total_expense, 3000000.0)
            calc_monthly_income = effective_income

        calc_monthly_expense = avg_monthly_expense if is_multi_month else total_expense
        calc_monthly_wants = avg_monthly_wants if is_multi_month else total_wants

        # Likuiditas Arus Kas (Cashflow Health)
        net_cashflow = effective_income - total_expense
        savings_ratio = (net_cashflow / effective_income * 100) if effective_income > 0 else 0.0
        expense_ratio = (calc_monthly_expense / calc_monthly_income * 100) if calc_monthly_income > 0 else 100.0
        wants_ratio = (calc_monthly_wants / calc_monthly_income * 100) if calc_monthly_income > 0 else 0.0

        if is_multi_month:
            avg_net = avg_monthly_net_cashflow
            avg_sav = avg_monthly_savings_ratio
            if avg_net < 0:
                cashflow_status = f"Defisit Arus Kas (Tren {num_months} Bulan: Pengeluaran Melebihi Pemasukan)"
            elif avg_sav < 15:
                cashflow_status = f"Arus Kas Tren {num_months} Bulan Ketat (Rata-rata Sisa Tabungan < 15%)"
            elif avg_sav < 30:
                cashflow_status = f"Arus Kas Tren {num_months} Bulan Cukup (Rata-rata Sisa Tabungan 15% - 30%)"
            else:
                cashflow_status = f"Arus Kas Tren {num_months} Bulan Sehat & Surplus (Rata-rata Sisa Tabungan >= 30%)"
        else:
            if net_cashflow < 0:
                cashflow_status = "Defisit Arus Kas (Pengeluaran Melebihi Pemasukan)"
            elif savings_ratio < 15:
                cashflow_status = "Arus Kas Rentan / Ketat (Sisa Tabungan < 15%)"
            elif savings_ratio < 30:
                cashflow_status = "Arus Kas Cukup (Sisa Tabungan 15% - 30%)"
            else:
                cashflow_status = "Arus Kas Sehat & Surplus (Sisa Tabungan >= 30%)"

        # Kategori Pengeluaran Terbesar untuk Grafik (Langkah 5)
        category_breakdown = []
        if not df_expense.empty:
            cat_summary = df_expense.groupby('category_group')['nominal'].agg(['sum', 'count']).reset_index()
            cat_summary = cat_summary.sort_values(by='sum', ascending=False)
            
            for _, r in cat_summary.iterrows():
                pct = (r['sum'] / total_expense) * 100 if total_expense > 0 else 0
                category_breakdown.append({
                    'category': r['category_group'],
                    'total': float(r['sum']),
                    'total_fmt': f"Rp {int(r['sum']):,}".replace(',', '.'),
                    'count': int(r['count']),
                    'percentage': round(float(pct), 1)
                })

        # =============================================================
        # REKAYASA 7 FITUR BEHAVIORAL FEATURE MAPPING (MENDELEY DATA)
        # Menggunakan Nilai Rata-rata Bulanan Agar Skala Fitur Tetap Presisi
        # =============================================================
        # Fitur 1: Income_Code (1 - 6) berdasarkan pendapatan bulanan riil
        if calc_monthly_income < 1000000: income_code = 1
        elif calc_monthly_income <= 2500000: income_code = 2
        elif calc_monthly_income <= 5000000: income_code = 3
        elif calc_monthly_income <= 7500000: income_code = 4
        elif calc_monthly_income <= 10000000: income_code = 5
        else: income_code = 6

        # Fitur 2: Exp_Ratio_Code (1 - 6)
        # Mengintegrasikan beban kas bulanan riil & rasio belanja konsumtif
        if expense_ratio >= 100: exp_by_total = 6      # Defisit penuh
        elif expense_ratio >= 85: exp_by_total = 5     # Sisa kas < 15%
        elif expense_ratio >= 70: exp_by_total = 4     # Sisa kas < 30%
        elif expense_ratio >= 50: exp_by_total = 3
        elif expense_ratio >= 30: exp_by_total = 2
        else: exp_by_total = 1

        if wants_ratio >= 50: exp_by_wants = 6
        elif wants_ratio >= 40: exp_by_wants = 5
        elif wants_ratio >= 30: exp_by_wants = 4
        elif wants_ratio >= 20: exp_by_wants = 3
        elif wants_ratio >= 10: exp_by_wants = 2
        else: exp_by_wants = 1

        exp_ratio_code = max(exp_by_total, exp_by_wants)

        # Fitur 3: Paylater_Status (1 = Bebas Pinjaman, 2 = Pengguna Aktif)
        paylater_status = 2 if has_paylater else 1

        # Fitur 4: P_Score (Sensitivitas Promo & Diskon, Likert 1.0 - 5.0)
        twin_days_dates = [(i, i) for i in range(1, 13)]
        promo_kw = ['promo', 'diskon', 'discount', 'voucher', 'cashback', 'flash sale', 'paylater']
        p_count = 0
        total_tx = max(len(df_expense), 1)
        for _, r in df_expense.iterrows():
            is_p = any(pk in str(r['deskripsi']).lower() for pk in promo_kw)
            try:
                dt = pd.to_datetime(r['tanggal'])
                if (dt.month, dt.day) in twin_days_dates or (25 <= dt.day <= 28):
                    is_p = True
            except: pass
            if is_p: p_count += 1
        p_pct = (p_count / total_tx) * 100
        p_score = round(float(1.8 + (p_pct / 100.0) * 2.2 + (0.5 if has_paylater else 0.0)), 2)
        p_score = min(max(p_score, 1.0), 5.0)

        # Fitur 5: SI_Score (Pengaruh Sosial & E-Commerce, Likert 1.0 - 5.0)
        si_kw = ['shopee', 'tokopedia', 'tiktok shop', 'lazada', 'blibli', 'sepatu', 'baju', 'elektronik', 'gadget', 'skincare', 'fashion']
        si_wants_sum = sum(float(r['nominal']) for _, r in df_expense.iterrows() if any(sk in str(r['deskripsi']).lower() for sk in si_kw))
        si_pct = (si_wants_sum / max(total_expense, 1.0)) * 100
        si_score = round(float(1.8 + (si_pct / 100.0) * 2.4), 2)
        si_score = min(max(si_score, 1.0), 5.0)

        # Fitur 6: H_Score (Motivasi Belanja Hedonis, Likert 1.0 - 5.0)
        hedonic_kw = ['warkop', 'kopi', 'jajan', 'cafe', 'kafe', 'gofood', 'grabfood', 'shopeefood', 'game', 'spotify', 'netflix', 'bioskop', 'boba']
        h_count = sum(1 for _, r in df_expense.iterrows() if any(hk in str(r['deskripsi']).lower() for hk in hedonic_kw))
        h_pct = (h_count / total_tx) * 100
        h_score = round(float(2.6 + (h_pct / 100.0) * 2.2), 2)
        h_score = min(max(h_score, 1.0), 5.0)

        # Fitur 7: SC_Lack_Score (Defisit Kontrol Diri, Likert 1.0 - 5.0)
        night_wants_count = 0
        date_tx_counts = {}
        for _, r in df_expense[df_expense['is_impulse']].iterrows():
            tgl_str = str(r['tanggal'])
            date_tx_counts[tgl_str] = date_tx_counts.get(tgl_str, 0) + 1
            try:
                h = int(str(r['jam']).split(':')[0])
                if h >= 21 or h < 3: night_wants_count += 1
            except: pass
        consecutive_days = sum(1 for d, c in date_tx_counts.items() if c >= 2)
        sc_lack_metric = (night_wants_count + consecutive_days * 1.5) / max(len(df_expense[df_expense['is_impulse']]), 1) * 100
        sc_lack_score = round(float(2.0 + (min(sc_lack_metric, 100) / 100.0) * 2.4), 2)
        sc_lack_score = min(max(sc_lack_score, 1.0), 5.0)

        mendeley_features = {
            'Income_Code': int(income_code),
            'Exp_Ratio_Code': int(exp_ratio_code),
            'Paylater_Status': int(paylater_status),
            'P_Score': float(p_score),
            'SI_Score': float(si_score),
            'H_Score': float(h_score),
            'SC_Lack_Score': float(sc_lack_score)
        }

        # =============================================================
        # REKOMENDASI & TIPS FINANSIAL PERSONAL (LANGKAH 6)
        # =============================================================
        financial_tips = []

        # 1. Peringatan Likuiditas Arus Kas (Disesuaikan Multi-Bulan vs Bulan Tunggal)
        if is_multi_month:
            if avg_monthly_net_cashflow < 0:
                financial_tips.append({
                    "icon": "🚨",
                    "title": f"Tren Arus Kas Defisit (Rata-rata Minus Rp {abs(int(avg_monthly_net_cashflow)):,}/bln)".replace(',', '.'),
                    "text": f"Berdasarkan tren {num_months} bulan terakhir, rata-rata pengeluaran bulanan Anda ({multi_month_summary['avg_monthly_expense_fmt']}) melampaui pemasukan ({multi_month_summary['avg_monthly_income_fmt']})! Segera rem belanja non-pokok dan evaluasi pos pengeluaran berulang agar arus kas kembali seimbang."
                })
            elif avg_monthly_savings_ratio < 15:
                financial_tips.append({
                    "icon": "⚠️",
                    "title": f"Tren Arus Kas Ketat: Rata-rata Sisa Kas {avg_monthly_savings_ratio:.1f}%/bln",
                    "text": f"Berdasarkan tren {num_months} bulan terakhir, rata-rata pengeluaran bulanan Anda adalah {multi_month_summary['avg_monthly_expense_fmt']} dari pemasukan {multi_month_summary['avg_monthly_income_fmt']}. Sisa dana bulanan rata-rata hanya {multi_month_summary['avg_monthly_net_cashflow_fmt']} (di bawah batas aman 20%). Sisihkan tabungan di awal gajian sebelum dialokasikan ke pos lainnya."
                })
            else:
                financial_tips.append({
                    "icon": "🎯",
                    "title": f"Tren Arus Kas Sehat: Rata-rata Surplus {avg_monthly_savings_ratio:.1f}%/bln",
                    "text": f"Berdasarkan tren {num_months} bulan terakhir, rata-rata pengeluaran bulanan Anda terkontrol baik di {multi_month_summary['avg_monthly_expense_fmt']} dengan pemasukan {multi_month_summary['avg_monthly_income_fmt']}. Anda rata-rata mampu menyisihkan surplus kas {multi_month_summary['avg_monthly_net_cashflow_fmt']} per bulan."
                })

            if multi_month_summary.get('highest_expense_month'):
                financial_tips.append({
                    "icon": "📊",
                    "title": f"Puncak Pengeluaran: {multi_month_summary['highest_expense_month']}",
                    "text": f"Pengeluaran tertinggi selama periode pemantauan tercatat pada {multi_month_summary['highest_expense_month']} sebesar {multi_month_summary['highest_expense_amount_fmt']}. Evaluasi transaksi pada periode tersebut untuk mengantisipasi potensi kebocoran serupa."
                })
        else:
            if net_cashflow < 0:
                financial_tips.append({
                    "icon": "🚨",
                    "title": f"Arus Kas Defisit (Minus Rp {abs(int(net_cashflow)):,})".replace(',', '.'),
                    "text": "Total pengeluaranmu bulan ini telah melampaui pemasukan! Segera rem belanja non-pokok dan hindari menambah cicilan baru agar tidak terjerat gali lubang tutup lubang."
                })
            elif savings_ratio < 15:
                financial_tips.append({
                    "icon": "⚠️",
                    "title": f"Arus Kas Ketat: Sisa Tabungan Hanya {savings_ratio:.1f}%",
                    "text": f"Sisa dana bulananmu hanya Rp {int(net_cashflow):,}. Angka ini di bawah ambang aman (minimal 20%). Sisihkan uang tabungan/dana darurat di awal gajian sebelum dipakai jajan.".replace(',', '.')
                })
            else:
                financial_tips.append({
                    "icon": "🎯",
                    "title": f"Arus Kas Sehat: Sisa Tabungan {savings_ratio:.1f}%",
                    "text": f"Kamu berhasil menyisihkan surplus kas Rp {int(net_cashflow):,}. Pertahankan disiplin ini dan alokasikan ke instrumen investasi aman seperti reksa dana pasar uang.".replace(',', '.')
                })

        # 2. Peringatan Pinjaman & Paylater
        if has_paylater:
            financial_tips.append({
                "icon": "💳",
                "title": "Waspada Beban Cicilan Pinjaman / Paylater",
                "text": "Terdeteksi transaksi cicilan pinjaman digital (SPinjam / Kopkar / Paylater). Prioritaskan pelunasan pokok utang dan jangan mengambil pinjaman baru untuk kebutuhan konsumtif."
            })
        else:
            financial_tips.append({
                "icon": "🌱",
                "title": "Bebas dari Beban Utang Konsumtif",
                "text": "Kamu tidak memiliki catatan cicilan pinjaman konsumtif. Ini pondasi keuangan yang sangat baik untuk menjaga skor kredit dan ketenangan finansialmu."
            })

        # 3. Analisis Kategori Pengeluaran Terbesar
        if category_breakdown:
            top_cat = category_breakdown[0]
            if top_cat['category'] == 'Kuliner & F&B' and top_cat['percentage'] >= 20:
                financial_tips.append({
                    "icon": "☕",
                    "title": f"Pos Kuliner & Kopi Terbesar ({top_cat['percentage']}%)",
                    "text": f"Pengeluaran untuk kopi, warkop, dan kuliner mencapai {top_cat['total_fmt']}. Terapkan batas jajan mingguan atau kurangi pesan antar makanan untuk menghemat pos ini."
                })
            elif top_cat['category'] == 'Belanja & E-Commerce' and top_cat['percentage'] >= 20:
                financial_tips.append({
                    "icon": "🛍️",
                    "title": f"Belanja E-Commerce Mendominasi ({top_cat['percentage']}%)",
                    "text": f"Pengeluaran marketplace mencapai {top_cat['total_fmt']}. Terapkan 'Aturan Tunggu 48 Jam' sebelum checkout barang agar tidak terjebak impulse buying sesaat."
                })

        if night_wants_count > 0:
            financial_tips.append({
                "icon": "🌙",
                "title": f"Terdeteksi {night_wants_count} Transaksi Larut Malam",
                "text": "Belanja di atas jam 21.00 sering kali dipicu rasa jenuh atau lelah. Hapus aplikasi belanja dari layar utama ponsel di malam hari."
            })

        financial_summary = {
            'total_income': float(effective_income),
            'total_income_fmt': f"Rp {int(effective_income):,}".replace(',', '.'),
            'total_expense': float(total_expense),
            'total_expense_fmt': f"Rp {int(total_expense):,}".replace(',', '.'),
            'net_cashflow': float(net_cashflow),
            'net_cashflow_fmt': f"Rp {int(net_cashflow):,}".replace(',', '.'),
            'savings_ratio_pct': round(float(savings_ratio), 1),
            'cashflow_status': cashflow_status,
            'has_paylater': bool(has_paylater),
            'total_needs': float(total_needs),
            'total_needs_fmt': f"Rp {int(total_needs):,}".replace(',', '.'),
            'total_wants': float(total_wants),
            'total_wants_fmt': f"Rp {int(total_wants):,}".replace(',', '.'),
            'total_debt': float(total_debt),
            'total_debt_fmt': f"Rp {int(total_debt):,}".replace(',', '.'),
            'ratio_wants_pct': round(float(wants_ratio), 1),
            'total_transactions': int(len(df_processed)),
            'needs_count': int(sum(~df_expense['is_impulse'] & ~df_expense['is_debt'])),
            'wants_count': int(sum(df_expense['is_impulse'])),
            'debt_count': int(sum(df_expense['is_debt'])),
            'is_multi_month': is_multi_month,
            'num_months': num_months,
            'trend_narrative': multi_month_summary.get('trend_narrative')
        }

        return {
            'transactions': records,
            'features': mendeley_features,
            'summary': financial_summary,
            'category_breakdown': category_breakdown,
            'financial_tips': financial_tips,
            'monthly_breakdown': monthly_breakdown,
            'multi_month_summary': multi_month_summary
        }

feature_mapper = BehavioralFeatureMapper()
