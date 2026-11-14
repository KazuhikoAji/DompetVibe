import os
import json
import warnings
warnings.filterwarnings('ignore')
import joblib
import pandas as pd
import numpy as np
import shap
from flask import Flask, render_template, request, jsonify, send_from_directory, Response
from flask_cors import CORS
from werkzeug.utils import secure_filename

from ml.feature_mapper import feature_mapper
from ml.pdf_report import build_pdf_report

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Max 16 MB

MODELS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models')
scaler = joblib.load(os.path.join(MODELS_DIR, 'scaler.pkl'))
kmeans_bundle = joblib.load(os.path.join(MODELS_DIR, 'kmeans_model.pkl'))
xgboost_model = joblib.load(os.path.join(MODELS_DIR, 'xgboost_model.pkl'))
rf_model = joblib.load(os.path.join(MODELS_DIR, 'rf_model.pkl'))

# SHAP TreeExplainer langsung pada model XGBoost
shap_explainer = shap.TreeExplainer(xgboost_model)

with open(os.path.join(MODELS_DIR, 'evaluation_metrics.json'), 'r', encoding='utf-8') as f:
    evaluation_metrics = json.load(f)

FEATURE_NAMES = [
    'Income_Code', 
    'Exp_Ratio_Code', 
    'Paylater_Status', 
    'P_Score', 
    'SI_Score', 
    'H_Score', 
    'SC_Lack_Score'
]

RISK_METADATA = {
    0: {"name": "Aman", "badge": "bg-emerald-100 text-emerald-800 border-emerald-300", "desc": "Pola belanja kamu terkendali dengan sangat baik dan seimbang dengan pemasukan."},
    1: {"name": "Waspada", "badge": "bg-amber-100 text-amber-800 border-amber-300", "desc": "Ada tanda-tanda kebocoran pengeluaran di pos kuliner, jajan santai, atau hiburan."},
    2: {"name": "Impulsif", "badge": "bg-purple-100 text-purple-800 border-purple-300", "desc": "Kamu cukup sering tergoda promo tanggal kembar, flash sale, dan tren media sosial."},
    3: {"name": "Kritis", "badge": "bg-rose-100 text-rose-800 border-rose-300", "desc": "Pengeluaran melampaui kemampuan kas riil, didorong cicilan paylater & checkout larut malam."}
}

PRESET_PROFILES = {
    "mindful": {
        "id": "mindful",
        "name": "Si Mindful",
        "subtitle": "Rasional & Bebas Utang",
        "avatar": "🌱",
        "features": {'Income_Code': 3, 'Exp_Ratio_Code': 1, 'Paylater_Status': 1, 'P_Score': 1.8, 'SI_Score': 1.7, 'H_Score': 3.0, 'SC_Lack_Score': 2.3}
    },
    "kopi": {
        "id": "kopi",
        "name": "Anak Kopi",
        "subtitle": "Kuliner & Nongkrong",
        "avatar": "☕",
        "features": {'Income_Code': 2, 'Exp_Ratio_Code': 1, 'Paylater_Status': 1, 'P_Score': 2.1, 'SI_Score': 2.3, 'H_Score': 3.6, 'SC_Lack_Score': 2.7}
    },
    "promo": {
        "id": "promo",
        "name": "Pejuang Promo",
        "subtitle": "Flash Sale & FOMO",
        "avatar": "⚡",
        "features": {'Income_Code': 2, 'Exp_Ratio_Code': 2, 'Paylater_Status': 1, 'P_Score': 3.1, 'SI_Score': 3.0, 'H_Score': 3.7, 'SC_Lack_Score': 2.9}
    },
    "paylater": {
        "id": "paylater",
        "name": "Raja Paylater",
        "subtitle": "Cicilan & Midnight Shopping",
        "avatar": "💳",
        "features": {'Income_Code': 3, 'Exp_Ratio_Code': 3, 'Paylater_Status': 2, 'P_Score': 3.5, 'SI_Score': 3.5, 'H_Score': 4.0, 'SC_Lack_Score': 3.4}
    }
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/upload-mutation', methods=['POST'])
def upload_mutation():
    """
    Step 1 & 2: Membaca berkas mutasi pengguna (mendukung satu atau banyak berkas sekaligus),
    mengembalikan daftar transaksi terlabeli TF-IDF, menghitung ringkasan kategori
    untuk grafik alokasi, dan menyiapkan hasil analisis AI.
    """
    raw_files = request.files.getlist('files')
    if not raw_files or len(raw_files) == 0:
        if 'file' in request.files:
            raw_files = [request.files['file']]
        else:
            return jsonify({"success": False, "message": "Pilih setidaknya satu berkas mutasi terlebih dahulu."}), 400

    valid_files = [f for f in raw_files if f.filename and f.filename.strip() != '']
    if not valid_files:
        return jsonify({"success": False, "message": "Nama berkas tidak boleh kosong."}), 400

    saved_paths = []
    parsed_dfs = []
    file_names = []

    try:
        user_income = request.form.get('declared_income', type=float)

        for idx, f in enumerate(valid_files):
            fname = secure_filename(f.filename)
            file_names.append(fname)
            spath = os.path.join(app.config['UPLOAD_FOLDER'], f"{idx}_{fname}")
            f.save(spath)
            saved_paths.append(spath)

            # 1. Parsing file dengan pandas / pdfplumber
            df_part = feature_mapper.parse_file(spath, fname)
            if df_part is not None and not df_part.empty:
                parsed_dfs.append(df_part)

        if not parsed_dfs:
            return jsonify({"success": False, "message": "Tidak ada data transaksi yang dapat diekstrak dari berkas yang diunggah."}), 400

        # Gabungkan seluruh transaksi dari semua berkas
        df_parsed = pd.concat(parsed_dfs, ignore_index=True)
        # Saring transaksi yang identik (misal berkas mutasi bulan yang saling tumpang tindih)
        df_parsed = df_parsed.drop_duplicates(subset=['tanggal', 'deskripsi', 'nominal', 'tipe']).reset_index(drop=True)
        # Urutkan berdasarkan tanggal kronologis
        try:
            df_parsed['temp_dt'] = pd.to_datetime(df_parsed['tanggal'], errors='coerce')
            df_parsed = df_parsed.sort_values(by=['temp_dt']).drop(columns=['temp_dt']).reset_index(drop=True)
        except:
            pass

        # 2. Klasifikasi TF-IDF, Kategori Breakdown, & Behavioral Mapping
        result = feature_mapper.classify_and_map(df_parsed, user_declared_income=user_income)

        # 3. Inferensi AI langsung pada 7 fitur yang dihasilkan
        features_dict = result['features']
        x_raw = pd.DataFrame([[features_dict[f] for f in FEATURE_NAMES]], columns=FEATURE_NAMES)
        x_scaled = scaler.transform(x_raw)

        # Prediksi XGBoost
        pred_risk = int(xgboost_model.predict(x_scaled)[0])
        prob_all = xgboost_model.predict_proba(x_scaled)[0].tolist()

        # Kalibrasi Likuiditas Finansial Riil (Financial Reality Calibration)
        sum_data = result['summary']
        multi_sum = result.get('multi_month_summary', {})
        is_multi = multi_sum.get('is_multi_month', False)
        num_m = multi_sum.get('num_months', 1)

        if is_multi:
            net_cashflow = multi_sum.get('avg_monthly_net_cashflow', 0.0)
            savings_ratio = multi_sum.get('avg_monthly_savings_ratio_pct', 0.0)
        else:
            net_cashflow = sum_data.get('net_cashflow', 0.0)
            savings_ratio = sum_data.get('savings_ratio_pct', 0.0)
        has_paylater = sum_data.get('has_paylater', False)

        risk_override_reason = None
        if net_cashflow < 0:
            if has_paylater:
                pred_risk = max(pred_risk, 2)  # Impulsif / Kritis karena defisit & ada utang
                risk_override_reason = f"Tren {num_m} bulan terakhir menunjukkan rata-rata defisit arus kas dan memiliki beban pinjaman/paylater aktif." if is_multi else "Pengeluaran melebihi pemasukan (defisit arus kas) dan memiliki beban pinjaman/paylater aktif."
            else:
                pred_risk = max(pred_risk, 1)  # Minimal Waspada
                risk_override_reason = f"Tren {num_m} bulan terakhir menunjukkan rata-rata pengeluaran bulanan melebihi pemasukan (defisit arus kas)." if is_multi else "Pengeluaran melebihi pemasukan bulanan (defisit arus kas)."
        elif savings_ratio < 15 and has_paylater:
            pred_risk = max(pred_risk, 1)  # Minimal Waspada
            risk_override_reason = f"Tren {num_m} bulan terakhir menunjukkan arus kas ketat (rata-rata sisa tabungan hanya {savings_ratio:.1f}%) dan terdapat cicilan pinjaman aktif." if is_multi else f"Arus kas ketat (sisa tabungan hanya {savings_ratio:.1f}%) dan terdapat cicilan pinjaman aktif (SPinjam / Kopkar)."
        elif savings_ratio < 5:
            pred_risk = max(pred_risk, 1)  # Minimal Waspada
            risk_override_reason = f"Tren {num_m} bulan terakhir menunjukkan arus kas sangat rentan (rata-rata sisa tabungan hanya {savings_ratio:.1f}%)." if is_multi else f"Arus kas sangat rentan (sisa tabungan hanya {savings_ratio:.1f}%)."

        # Ekspektasi matematis skor risiko kontinu (0% - 100%)
        expected_level = max(float(pred_risk), sum(k * prob_all[k] for k in range(4)))
        risk_gauge = round(float((expected_level / 3.0) * 100), 1)

        risk_desc = RISK_METADATA[pred_risk]['desc']
        if is_multi:
            risk_desc = f"Berdasarkan tren {num_m} bulan terakhir: {risk_desc}"
        if risk_override_reason:
            risk_desc = f"{risk_desc} Perhatian Finansial: {risk_override_reason}"

        # Prediksi K-Means Persona
        raw_cluster = int(kmeans_bundle['model'].predict(x_scaled)[0])
        persona_id = kmeans_bundle['cluster_mapping'][raw_cluster]
        persona_info = kmeans_bundle['persona_definitions'][persona_id]

        # Kontribusi SHAP TreeExplainer
        shap_values = shap_explainer.shap_values(x_scaled)
        pred_shap = shap_values[0, :, pred_risk]

        feature_labels = {
            'Income_Code': 'Tingkat Pendapatan',
            'Exp_Ratio_Code': 'Porsi Belanja / Kas',
            'Paylater_Status': 'Penggunaan Paylater',
            'P_Score': 'Sensitivitas Promo',
            'SI_Score': 'Pengaruh FOMO Medsos',
            'H_Score': 'Motivasi Hedonis',
            'SC_Lack_Score': 'Defisit Kontrol Diri'
        }

        user_xai = []
        for feat, sv in zip(FEATURE_NAMES, pred_shap):
            user_xai.append({
                "feature": feat,
                "label": feature_labels.get(feat, feat),
                "shap_value": round(float(abs(sv)), 3),
                "contribution_pct": round(float(abs(sv) * 100), 1)
            })
        user_xai.sort(key=lambda x: x['shap_value'], reverse=True)

        if len(file_names) == 1:
            display_filename = file_names[0]
        else:
            display_filename = f"{len(file_names)} Berkas ({', '.join(file_names[:2])}{'...' if len(file_names) > 2 else ''})"

        return jsonify({
            "success": True,
            "filename": display_filename,
            "filenames": file_names,
            "summary": result['summary'],
            "transactions": result['transactions'],
            "category_breakdown": result['category_breakdown'],
            "financial_tips": result['financial_tips'],
            "monthly_breakdown": result.get('monthly_breakdown', []),
            "multi_month_summary": result.get('multi_month_summary', {}),
            "features": features_dict,
            "risk_assessment": {
                "risk_class": pred_risk,
                "risk_label": RISK_METADATA[pred_risk]['name'],
                "risk_gauge_percentage": risk_gauge,
                "risk_probabilities": [round(float(p * 100), 1) for p in prob_all],
                "badge_class": RISK_METADATA[pred_risk]['badge'],
                "description": risk_desc
            },
            "persona_assessment": {
                "persona_id": persona_id,
                "raw_cluster": raw_cluster,
                "persona": persona_info
            },
            "xai_contributions": user_xai[:5]
        })
    except ValueError as ve:
        return jsonify({"success": False, "message": str(ve)}), 400
    except Exception as e:
        return jsonify({"success": False, "message": f"Gagal membaca berkas: {str(e)}"}), 500
    finally:
        for sp in saved_paths:
            if os.path.exists(sp):
                try: os.remove(sp)
                except: pass

@app.route('/api/predict-risk', methods=['POST'])
def predict_risk():
    """Inferensi interaktif jika pengguna mengubah slider parameter."""
    data = request.get_json() or {}
    try:
        input_features = {
            'Income_Code': int(data.get('Income_Code', 3)),
            'Exp_Ratio_Code': int(data.get('Exp_Ratio_Code', 2)),
            'Paylater_Status': int(data.get('Paylater_Status', 1)),
            'P_Score': float(data.get('P_Score', 2.5)),
            'SI_Score': float(data.get('SI_Score', 2.5)),
            'H_Score': float(data.get('H_Score', 3.0)),
            'SC_Lack_Score': float(data.get('SC_Lack_Score', 2.5))
        }

        input_features['Income_Code'] = max(1, min(6, input_features['Income_Code']))
        input_features['Exp_Ratio_Code'] = max(1, min(6, input_features['Exp_Ratio_Code']))
        input_features['Paylater_Status'] = 2 if input_features['Paylater_Status'] == 2 else 1
        for k in ['P_Score', 'SI_Score', 'H_Score', 'SC_Lack_Score']:
            input_features[k] = max(1.0, min(5.0, float(input_features[k])))

        x_raw = pd.DataFrame([[input_features[f] for f in FEATURE_NAMES]], columns=FEATURE_NAMES)
        x_scaled = scaler.transform(x_raw)

        pred_risk = int(xgboost_model.predict(x_scaled)[0])
        prob_all = xgboost_model.predict_proba(x_scaled)[0].tolist()

        # Kalibrasi parameter: Rasio belanja sangat tinggi & ada paylater
        if input_features['Exp_Ratio_Code'] >= 5 and input_features['Paylater_Status'] == 2:
            pred_risk = max(pred_risk, 1)
        elif input_features['Exp_Ratio_Code'] == 6:
            pred_risk = max(pred_risk, 1)

        expected_level = max(float(pred_risk), sum(k * prob_all[k] for k in range(4)))
        risk_gauge = round(float((expected_level / 3.0) * 100), 1)

        raw_cluster = int(kmeans_bundle['model'].predict(x_scaled)[0])
        persona_id = kmeans_bundle['cluster_mapping'][raw_cluster]
        persona_info = kmeans_bundle['persona_definitions'][persona_id]

        shap_values = shap_explainer.shap_values(x_scaled)
        pred_shap = shap_values[0, :, pred_risk]

        feature_labels = {
            'Income_Code': 'Tingkat Pendapatan',
            'Exp_Ratio_Code': 'Porsi Belanja / Kas',
            'Paylater_Status': 'Penggunaan Paylater',
            'P_Score': 'Sensitivitas Promo',
            'SI_Score': 'Pengaruh FOMO Medsos',
            'H_Score': 'Motivasi Hedonis',
            'SC_Lack_Score': 'Defisit Kontrol Diri'
        }

        user_xai = []
        for feat, sv in zip(FEATURE_NAMES, pred_shap):
            user_xai.append({
                "feature": feat,
                "label": feature_labels.get(feat, feat),
                "shap_value": round(float(abs(sv)), 3),
                "contribution_pct": round(float(abs(sv) * 100), 1)
            })
        user_xai.sort(key=lambda x: x['shap_value'], reverse=True)

        return jsonify({
            "success": True,
            "inputs": input_features,
            "risk_assessment": {
                "risk_class": pred_risk,
                "risk_label": RISK_METADATA[pred_risk]['name'],
                "risk_gauge_percentage": risk_gauge,
                "risk_probabilities": [round(float(p * 100), 1) for p in prob_all],
                "badge_class": RISK_METADATA[pred_risk]['badge'],
                "description": RISK_METADATA[pred_risk]['desc']
            },
            "persona_assessment": {
                "persona_id": persona_id,
                "raw_cluster": raw_cluster,
                "persona": persona_info
            },
            "xai_contributions": user_xai[:5]
        })
    except Exception as e:
        return jsonify({"success": False, "message": f"Kesalahan inferensi: {str(e)}"}), 500

@app.route('/api/presets', methods=['GET'])
def get_presets():
    return jsonify({"success": True, "presets": PRESET_PROFILES})

@app.route('/api/evaluation-stats', methods=['GET'])
def get_evaluation_stats():
    return jsonify({"success": True, "data": evaluation_metrics})

@app.route('/api/demo-samples', methods=['GET'])
def list_demo_samples():
    sample_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sample_demo')
    samples = []
    if os.path.exists(sample_dir):
        files_map = {
            'sample_estatement_mbca.pdf': {'title': 'Dokumen Asli m-BCA (.PDF)', 'badge': 'Format m-BCA'},
            'real_mutasi_user_6d68.csv': {'title': 'Pengguna Riil #1 (Harian & Sembako)', 'badge': 'Dataset Asli'},
            'real_mutasi_user_0929.xlsx': {'title': 'Pengguna Riil #2 (Excel - Kuliner & Kafe)', 'badge': 'Dataset Asli'},
            'real_mutasi_user_14c9.csv': {'title': 'Pengguna Riil #3 (E-Commerce & Belanja)', 'badge': 'Dataset Asli'},
            'real_mutasi_user_e4fa.csv': {'title': 'Pengguna Riil #4 (Promo & Diskon)', 'badge': 'Dataset Asli'},
            'mutasi_raja_paylater.csv': {'title': 'Uji Ekstrem: Paylater & Transaksi Malam', 'badge': 'Simulasi Kasus'}
        }
        for f, meta in files_map.items():
            path = os.path.join(sample_dir, f)
            if os.path.exists(path):
                samples.append({
                    "filename": f,
                    "title": meta['title'],
                    "badge": meta['badge'],
                    "size": os.path.getsize(path)
                })
    return jsonify({"success": True, "samples": samples})

@app.route('/api/demo-samples/<filename>', methods=['GET'])
def download_demo_sample(filename):
    sample_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sample_demo')
    safe_name = secure_filename(filename)
    return send_from_directory(sample_dir, safe_name, as_attachment=True)

@app.route('/api/download-report-pdf', methods=['POST'])
def download_report_pdf():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "Data analisis tidak ditemukan."}), 400

        pdf_bytes = build_pdf_report(data)

        raw_filename = data.get('filename', 'Laporan_Keuangan_DompetVibe')
        base_name = os.path.splitext(os.path.basename(raw_filename))[0]
        safe_name = f"Analisis_{base_name}.pdf"

        response = Response(pdf_bytes, mimetype='application/pdf')
        response.headers['Content-Disposition'] = f'attachment; filename="{safe_name}"'
        return response
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "message": f"Gagal membuat PDF: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
