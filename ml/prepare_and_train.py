import os
import json
import joblib
import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, confusion_matrix, accuracy_score, precision_score, recall_score, f1_score
from xgboost import XGBClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

def run_training():
    print("=" * 60)
    print("DOMPETVIBE AI - ETL & MODEL TRAINING PIPELINE")
    print("Prodi Informatika UNM - Outline 01 (Kecerdasan Artifisial)")
    print("=" * 60)

    # 1. Pastikan folder models/ tersedia
    os.makedirs('models', exist_ok=True)

    # 2. Muat Dataset Utama (Mendeley Data)
    excel_path = os.path.join('Dataset', 'CodebookData_SEMPLS_IBB.xlsx')
    print(f"\n[1/6] Membaca Dataset Utama dari: {excel_path}")
    df_mendeley = pd.read_excel(excel_path, sheet_name=0)
    print(f"      Dimensi awal data kuesioner: {df_mendeley.shape[0]} baris, {df_mendeley.shape[1]} kolom")

    # 3. Pra-Pemrosesan & Rekayasa Fitur (Feature Engineering)
    print("\n[2/6] Mengeksekusi Pra-Pemrosesan & Penyelarasan Skala Fitur...")
    
    # Fitur 1: Pendapatan Bulanan (1-6)
    income_code = df_mendeley['Monthly Income'].astype(int)

    # Fitur 2: Rasio Pengeluaran Belanja Online terhadap Pendapatan (1-6)
    exp_ratio_code = df_mendeley['Average monthly expenditure for online shopping in relation to monthly income'].astype(int)

    # Fitur 3: Status Penggunaan E-Paylater (1 = Non-user, 2 = User)
    paylater_status = df_mendeley['E-Paylater User Status'].astype(int)

    # Fitur 4: Skor Sensitivitas Promo & Paylater (P_Score: P1 - P4)
    p_cols = [c for c in df_mendeley.columns if c.startswith('P') and not c.startswith('Pay')]
    p_score = df_mendeley[p_cols].mean(axis=1)

    # Fitur 5: Skor Pengaruh Sosial & FOMO (SI_Score: SI1 - SI6)
    si_cols = [c for c in df_mendeley.columns if c.startswith('SI')]
    si_score = df_mendeley[si_cols].mean(axis=1)

    # Fitur 6: Skor Motivasi Belanja Hedonis (H_Score: H1 - H4)
    h_cols = [c for c in df_mendeley.columns if c.startswith('H')]
    h_score = df_mendeley[h_cols].mean(axis=1)

    # Fitur 7: Skor Defisit Kontrol Diri (SC_Lack_Score: reverse coding SC1-SC5)
    # Penyelarasan arah skala: 6.0 - rata-rata(SC1..SC5) agar berkorelasi positif (+0.406) dengan impulsif
    sc_cols = [c for c in df_mendeley.columns if c.startswith('SC')]
    sc_lack_score = 6.0 - df_mendeley[sc_cols].mean(axis=1)

    # Variabel Target: Risk_Class dari rata-rata IBB1 - IBB4
    ibb_cols = [c for c in df_mendeley.columns if c.startswith('IBB')]
    ibb_mean = df_mendeley[ibb_cols].mean(axis=1)

    def discretize_risk(val):
        if val <= 2.00:
            return 0  # Aman
        elif val <= 3.00:
            return 1  # Waspada
        elif val <= 3.75:
            return 2  # Impulsif
        else:
            return 3  # Kritis

    risk_class = ibb_mean.apply(discretize_risk)

    # Susun DataFrame Fitur X dan Target y
    feature_names = [
        'Income_Code', 
        'Exp_Ratio_Code', 
        'Paylater_Status', 
        'P_Score', 
        'SI_Score', 
        'H_Score', 
        'SC_Lack_Score'
    ]
    X = pd.DataFrame({
        'Income_Code': income_code,
        'Exp_Ratio_Code': exp_ratio_code,
        'Paylater_Status': paylater_status,
        'P_Score': p_score,
        'SI_Score': si_score,
        'H_Score': h_score,
        'SC_Lack_Score': sc_lack_score
    }, columns=feature_names)
    y = risk_class

    class_dist = y.value_counts().sort_index().to_dict()
    print("      Distribusi 4 Kelas Risiko:")
    print(f"      - Kelas 0 (Aman): {class_dist.get(0, 0)} ({class_dist.get(0, 0)/len(y)*100:.1f}%)")
    print(f"      - Kelas 1 (Waspada): {class_dist.get(1, 0)} ({class_dist.get(1, 0)/len(y)*100:.1f}%)")
    print(f"      - Kelas 2 (Impulsif): {class_dist.get(2, 0)} ({class_dist.get(2, 0)/len(y)*100:.1f}%)")
    print(f"      - Kelas 3 (Kritis): {class_dist.get(3, 0)} ({class_dist.get(3, 0)/len(y)*100:.1f}%)")

    # 4. Stratified Train-Test Split (80:20)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )
    print(f"      Data Latih (80%): {X_train.shape[0]} baris | Data Uji (20%): {X_test.shape[0]} baris")

    # Normalisasi Z-Score (StandardScaler)
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    X_all_scaled = scaler.transform(X)

    joblib.dump(scaler, os.path.join('models', 'scaler.pkl'))
    print("      StandardScaler disimpan -> models/scaler.pkl")

    # 5. Pelatihan Model 1: K-Means Clustering (Spending Persona)
    print("\n[3/6] Melatih Model K-Means Clustering & Evaluasi Klaster...")
    elbow_data = []
    for k in range(2, 9):
        km = KMeans(n_clusters=k, init='k-means++', random_state=42, n_init=10)
        km.fit(X_all_scaled)
        sil = silhouette_score(X_all_scaled, km.labels_)
        elbow_data.append({
            'k': int(k),
            'wcss': round(float(km.inertia_), 2),
            'silhouette': round(float(sil), 4)
        })

    # Pelatihan K=4 Klaster Persona
    kmeans_model = KMeans(n_clusters=4, init='k-means++', random_state=42, n_init=10)
    raw_cluster_labels = kmeans_model.fit_predict(X_all_scaled)
    sil_k4 = silhouette_score(X_all_scaled, raw_cluster_labels)

    # Identifikasi Persona berdasarkan profil rata-rata tiap klaster
    temp_df = X.copy()
    temp_df['raw_cluster'] = raw_cluster_labels
    cluster_means = temp_df.groupby('raw_cluster').mean()

    # Logika pemetaan raw cluster ke persona 0..3:
    # Cluster 0: Rational & Mindful Planner (P & SI rendah, SC_Lack terendah, Paylater non-user)
    # Cluster 1: Lifestyle & Culinary Hedonist (H tinggi, Paylater rendah)
    # Cluster 2: Promo & FOMO Trend Hunter (P & SI tinggi, Paylater rendah)
    # Cluster 3: High-Risk Paylater Dependent (Paylater tertinggi ~2.0, Exp_Ratio tinggi, SC_Lack tinggi)
    cluster_mapping = {}
    remaining_clusters = list(range(4))

    # Temukan High-Risk Paylater Dependent (nilai Paylater_Status tertinggi)
    c3 = int(cluster_means['Paylater_Status'].idxmax())
    cluster_mapping[c3] = 3
    remaining_clusters.remove(c3)

    # Temukan Rational & Mindful Planner (nilai SC_Lack_Score terendah di antara sisa)
    c0 = int(cluster_means.loc[remaining_clusters, 'SC_Lack_Score'].idxmin())
    cluster_mapping[c0] = 0
    remaining_clusters.remove(c0)

    # Temukan Promo & FOMO Hunter (P_Score + SI_Score tertinggi di antara sisa)
    p_si_sum = cluster_means.loc[remaining_clusters, 'P_Score'] + cluster_means.loc[remaining_clusters, 'SI_Score']
    c2 = int(p_si_sum.idxmax())
    cluster_mapping[c2] = 2
    remaining_clusters.remove(c2)

    # Sisa adalah Lifestyle & Culinary Hedonist
    c1 = remaining_clusters[0]
    cluster_mapping[c1] = 1

    print(f"      Pemetaan Raw Cluster ke Persona: {cluster_mapping}")

    persona_definitions = {
        0: {
            "name": "Rational & Mindful Planner",
            "badge_color": "mint",
            "tagline": "Disiplin Finansial Tinggi & Kebal Godaan Diskon",
            "description": "Pengeluaran terencana dengan kontrol diri sangat kuat. Jarang tergoda promo kilat atau tren media sosial, serta menghindari utang konsumtif Paylater.",
            "recommendation": "Pertahankan kebiasaan bijak ini dan mulai alokasikan surplus dana bulanan ke instrumen investasi seperti Reksa Dana atau Deposito."
        },
        1: {
            "name": "Lifestyle & Culinary Hedonist",
            "badge_color": "amber",
            "tagline": "Pecinta Kuliner & Hiburan Santai",
            "description": "Pengeluaran didominasi kebutuhan emosional dan gaya hidup (kopi, jajan pesan-antar, bioskop/nonton). Masih enggan berhutang Paylater, namun rentan bocor halus di pos kuliner.",
            "recommendation": "Terapkan aturan batas anggaran kuliner (metode amplop digital) dan batasi frekuensi pesan antar makanan maksimal 2 kali seminggu."
        },
        2: {
            "name": "Promo & FOMO Trend Hunter",
            "badge_color": "lavender",
            "tagline": "Pemburu Diskon Tanggal Kembar & Tren Viral",
            "description": "Sangat responsif terhadap flash sale, gratis ongkir, dan tren produk media sosial. Membeli bukan karena butuh, melainkan takut ketinggalan promo spesial.",
            "recommendation": "Terapkan 'Aturan Tunggu 48 Jam' sebelum checkout barang non-esensial untuk menyaring dorongan impulsif sementara."
        },
        3: {
            "name": "High-Risk Paylater Dependent",
            "badge_color": "rose",
            "tagline": "Pengguna Aktif Kredit Digital & Kontrol Diri Rendah",
            "description": "Ketergantungan tinggi pada fasilitas Paylater dengan rasio belanja melampaui kemampuan kas riil. Kontrol diri defisit sehingga memicu risiko gagal bayar.",
            "recommendation": "Segera bekukan limit Paylater dan prioritaskan pelunasan cicilan berjalan sebelum arus kas bulanan mengalami defisit berkepanjangan."
        }
    }

    # Simpan model K-Means beserta pemetaan personanya
    kmeans_bundle = {
        'model': kmeans_model,
        'cluster_mapping': cluster_mapping,
        'persona_definitions': persona_definitions,
        'silhouette_score': round(float(sil_k4), 4)
    }
    joblib.dump(kmeans_bundle, os.path.join('models', 'kmeans_model.pkl'))
    print(f"      Model K-Means disimpan -> models/kmeans_model.pkl (Silhouette Score: {sil_k4:.4f})")

    # 6. Pelatihan Model 2: XGBoost Classifier vs Random Forest
    print("\n[4/6] Melatih Model Supervised (XGBoost vs Random Forest)...")
    
    # Model Utama: XGBoost
    xgb_model = XGBClassifier(
        n_estimators=200,
        max_depth=5,
        learning_rate=0.08,
        objective='multi:softprob',
        random_state=42,
        eval_metric='mlogloss'
    )
    xgb_model.fit(X_train_scaled, y_train)
    y_pred_xgb = xgb_model.predict(X_test_scaled)
    joblib.dump(xgb_model, os.path.join('models', 'xgboost_model.pkl'))

    # Model Pembanding: Random Forest
    rf_model = RandomForestClassifier(
        n_estimators=200,
        random_state=42
    )
    rf_model.fit(X_train_scaled, y_train)
    y_pred_rf = rf_model.predict(X_test_scaled)
    joblib.dump(rf_model, os.path.join('models', 'rf_model.pkl'))

    # Evaluasi Metrik
    cm_xgb = confusion_matrix(y_test, y_pred_xgb).tolist()
    cm_rf = confusion_matrix(y_test, y_pred_rf).tolist()

    metrics_comparison = {
        "xgboost": {
            "name": "XGBoost Classifier (Model Utama)",
            "accuracy": round(float(accuracy_score(y_test, y_pred_xgb)), 4),
            "precision_macro": round(float(precision_score(y_test, y_pred_xgb, average='macro', zero_division=0)), 4),
            "precision_weighted": round(float(precision_score(y_test, y_pred_xgb, average='weighted', zero_division=0)), 4),
            "recall_macro": round(float(recall_score(y_test, y_pred_xgb, average='macro', zero_division=0)), 4),
            "recall_weighted": round(float(recall_score(y_test, y_pred_xgb, average='weighted', zero_division=0)), 4),
            "f1_macro": round(float(f1_score(y_test, y_pred_xgb, average='macro', zero_division=0)), 4),
            "f1_weighted": round(float(f1_score(y_test, y_pred_xgb, average='weighted', zero_division=0)), 4),
            "confusion_matrix": cm_xgb
        },
        "random_forest": {
            "name": "Random Forest Classifier (Model Pembanding)",
            "accuracy": round(float(accuracy_score(y_test, y_pred_rf)), 4),
            "precision_macro": round(float(precision_score(y_test, y_pred_rf, average='macro', zero_division=0)), 4),
            "precision_weighted": round(float(precision_score(y_test, y_pred_rf, average='weighted', zero_division=0)), 4),
            "recall_macro": round(float(recall_score(y_test, y_pred_rf, average='macro', zero_division=0)), 4),
            "recall_weighted": round(float(recall_score(y_test, y_pred_rf, average='weighted', zero_division=0)), 4),
            "f1_macro": round(float(f1_score(y_test, y_pred_rf, average='macro', zero_division=0)), 4),
            "f1_weighted": round(float(f1_score(y_test, y_pred_rf, average='weighted', zero_division=0)), 4),
            "confusion_matrix": cm_rf
        }
    }

    # Feature Importance untuk XAI (Explainable AI)
    importances = xgb_model.feature_importances_
    xai_features = []
    for feat, imp in zip(feature_names, importances):
        xai_features.append({
            "feature": feat,
            "label": {
                'Income_Code': 'Tingkat Pendapatan',
                'Exp_Ratio_Code': 'Rasio Belanja / Pendapatan',
                'Paylater_Status': 'Status Pemakaian Paylater',
                'P_Score': 'Sensitivitas Promo & Diskon',
                'SI_Score': 'Pengaruh Sosial & FOMO Medsos',
                'H_Score': 'Motivasi Belanja Hedonis',
                'SC_Lack_Score': 'Defisit Kontrol Diri'
            }.get(feat, feat),
            "importance": round(float(imp), 4),
            "percentage": round(float(imp * 100), 2)
        })
    xai_features.sort(key=lambda x: x['importance'], reverse=True)

    print("      Model XGBoost & Random Forest berhasil dilatih dan disimpan.")
    print(f"      Top 3 Fitur Pemicu Risiko (XAI): {xai_features[0]['label']} ({xai_features[0]['percentage']}%), {xai_features[1]['label']} ({xai_features[1]['percentage']}%), {xai_features[2]['label']} ({xai_features[2]['percentage']}%)")

    # 7. Pelatihan Model 3: NLP TF-IDF Transaction Classifier
    print("\n[5/6] Melatih Model NLP TF-IDF Transaction Classifier...")
    csv_path = os.path.join('Dataset', 'transactions_rows.csv')
    df_tx = pd.read_csv(csv_path)
    df_exp = df_tx[df_tx['type'] == 'expense'].copy()

    needs_keywords = [
        'sembako', 'sarapan', 'makan siang', 'makan malam', 'krl', 'angkot', 
        'bensin', 'listrik', 'air pam', 'pulsa', 'internet', 'apotek', 'dokter', 
        'bpjs', 'vitamin', 'parkir', 'tol', 'bus transjakarta', 'donasi', 'arisan'
    ]

    def label_transaction(desc):
        desc_lower = str(desc).lower()
        for kw in needs_keywords:
            if kw in desc_lower:
                return 0  # Needs
        return 1  # Impulse/Wants

    df_exp['label'] = df_exp['description'].apply(label_transaction)
    
    tfidf_pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(ngram_range=(1, 2))),
        ('clf', LogisticRegression(random_state=42, max_iter=1000))
    ])
    tfidf_pipeline.fit(df_exp['description'], df_exp['label'])
    joblib.dump(tfidf_pipeline, os.path.join('models', 'tfidf_transaction_pipeline.pkl'))
    print(f"      Pipeline TF-IDF berhasil dilatih pada {len(df_exp)} transaksi dan disimpan -> models/tfidf_transaction_pipeline.pkl")

    # 8. Ekspor Komprehensif Seluruh Metrik ke evaluation_metrics.json
    print("\n[6/6] Mengekspor Metrik Evaluasi untuk Bab IV Skripsi & UI...")
    
    # Cuplikan 5 baris data untuk tab eksplorasi data sidang
    mendeley_preview = X.head(5).to_dict(orient='records')
    for idx, row in enumerate(mendeley_preview):
        row['Risk_Class'] = int(y.iloc[idx])
        row['Risk_Label'] = {0: 'Aman', 1: 'Waspada', 2: 'Impulsif', 3: 'Kritis'}[row['Risk_Class']]

    tx_preview = df_exp[['transaction_date', 'description', 'amount', 'label']].head(8).to_dict(orient='records')
    for row in tx_preview:
        row['category_type'] = 'Needs' if row['label'] == 0 else 'Impulse/Wants'
        row['amount_formatted'] = f"Rp {row['amount']:,}".replace(',', '.')

    full_evaluation = {
        "metadata": {
            "project_name": "DompetVibe AI",
            "study_program": "Informatika FTI Universitas Nusa Mandiri",
            "standard_outline": "Outline 01 (Perancangan Aplikasi Kecerdasan Artifisial)",
            "year": 2026,
            "total_mendeley_samples": len(X),
            "total_transaction_samples": len(df_tx),
            "train_samples": len(X_train),
            "test_samples": len(X_test),
            "features_count": len(feature_names),
            "risk_classes": [
                {"class_id": 0, "name": "Aman", "range": "IBB <= 2.00", "count": class_dist.get(0, 0)},
                {"class_id": 1, "name": "Waspada", "range": "2.01 <= IBB <= 3.00", "count": class_dist.get(1, 0)},
                {"class_id": 2, "name": "Impulsif", "range": "3.01 <= IBB <= 3.75", "count": class_dist.get(2, 0)},
                {"class_id": 3, "name": "Kritis", "range": "IBB > 3.75", "count": class_dist.get(3, 0)}
            ]
        },
        "kmeans_evaluation": {
            "elbow_data": elbow_data,
            "optimal_k": 4,
            "silhouette_score_k4": round(float(sil_k4), 4),
            "persona_definitions": persona_definitions
        },
        "classification_evaluation": metrics_comparison,
        "explainable_ai": {
            "feature_rankings": xai_features
        },
        "dataset_previews": {
            "mendeley_sample": mendeley_preview,
            "transaction_sample": tx_preview
        }
    }

    metrics_path = os.path.join('models', 'evaluation_metrics.json')
    with open(metrics_path, 'w', encoding='utf-8') as f:
        json.dump(full_evaluation, f, indent=2, ensure_ascii=False)
    print(f"      Berkas evaluasi Bab IV lengkap disimpan -> {metrics_path}")
    print("\n" + "=" * 60)
    print("FASE 1 SELESAI DENGAN SUKSES!")
    print("=" * 60)

if __name__ == '__main__':
    run_training()
