import pandas as pd
import os

df = pd.read_csv('Dataset/transactions_rows.csv')
os.makedirs('sample_demo', exist_ok=True)

# 1. User 6d681108 (Pola Terencana / Kebutuhan Sehari-hari)
u1 = df[df['user_id'] == '6d681108-6cfd-4e90-aef6-470047b94796'].head(30)
u1_export = u1[['transaction_date', 'description', 'amount', 'type']].copy()
u1_export.columns = ['tanggal', 'deskripsi', 'nominal', 'tipe']
u1_export.to_csv('sample_demo/real_mutasi_user_6d68.csv', index=False)

# 2. User 0929f055 (Pola Kuliner & Kafe)
u2 = df[df['user_id'] == '0929f055-08fe-48be-a629-085630e2307f'].head(30)
u2_export = u2[['transaction_date', 'description', 'amount', 'type']].copy()
u2_export.columns = ['tanggal', 'deskripsi', 'nominal', 'tipe']
u2_export.to_excel('sample_demo/real_mutasi_user_0929.xlsx', index=False)
u2_export.to_csv('sample_demo/real_mutasi_user_0929.csv', index=False)

# 3. User 14c9585c (Pola Belanja Online & E-Commerce)
u3 = df[df['user_id'] == '14c9585c-a11a-432a-932c-49a032ee3a50'].head(30)
u3_export = u3[['transaction_date', 'description', 'amount', 'type']].copy()
u3_export.columns = ['tanggal', 'deskripsi', 'nominal', 'tipe']
u3_export.to_csv('sample_demo/real_mutasi_user_14c9.csv', index=False)

# 4. User e4fa4032 (Pola Promo & Transaksi Berulang)
u4 = df[df['user_id'] == 'e4fa4032-ecc9-461d-bdb8-e55e2ec044f5'].head(30)
u4_export = u4[['transaction_date', 'description', 'amount', 'type']].copy()
u4_export.columns = ['tanggal', 'deskripsi', 'nominal', 'tipe']
u4_export.to_csv('sample_demo/real_mutasi_user_e4fa.csv', index=False)

print("4 Berkas Mutasi Riil dari transactions_rows.csv berhasil diekspor!")
