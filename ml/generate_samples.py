import os
import pandas as pd

os.makedirs('sample_demo', exist_ok=True)

# 1. Si Mindful -> Target: Risk 0 (Aman), Persona 0 (Rational & Mindful Planner)
mindful_data = [
    {"tanggal": "2026-10-01", "jam": "08:00", "deskripsi": "Gaji bulanan kantor", "nominal": 4500000, "tipe": "income"},
    {"tanggal": "2026-10-02", "jam": "09:30", "deskripsi": "Belanja sembako bulanan beras minyak telur", "nominal": 450000, "tipe": "expense"},
    {"tanggal": "2026-10-03", "jam": "07:15", "deskripsi": "Top up kartu KRL Commuter Line", "nominal": 100000, "tipe": "expense"},
    {"tanggal": "2026-10-05", "jam": "12:00", "deskripsi": "Makan siang warteg sehat", "nominal": 25000, "tipe": "expense"},
    {"tanggal": "2026-10-07", "jam": "18:30", "deskripsi": "Token listrik PLN bulanan", "nominal": 200000, "tipe": "expense"},
    {"tanggal": "2026-10-10", "jam": "12:30", "deskripsi": "Makan siang soto ayam", "nominal": 25000, "tipe": "expense"},
    {"tanggal": "2026-10-12", "jam": "16:00", "deskripsi": "Isi bensin Pertalite motor", "nominal": 50000, "tipe": "expense"},
    {"tanggal": "2026-10-15", "jam": "19:00", "deskripsi": "Tagihan air PAM rumah", "nominal": 85000, "tipe": "expense"},
    {"tanggal": "2026-10-18", "jam": "13:00", "deskripsi": "Beli vitamin C dan apotek", "nominal": 75000, "tipe": "expense"},
    {"tanggal": "2026-10-21", "jam": "12:15", "deskripsi": "Makan siang soto kudus", "nominal": 28000, "tipe": "expense"},
    {"tanggal": "2026-10-23", "jam": "09:00", "deskripsi": "Donasi infaq jumat", "nominal": 50000, "tipe": "expense"},
    {"tanggal": "2026-10-25", "jam": "12:00", "deskripsi": "Makan siang nasi padang", "nominal": 30000, "tipe": "expense"},
    {"tanggal": "2026-10-28", "jam": "17:30", "deskripsi": "Paket data internet bulanan", "nominal": 100000, "tipe": "expense"},
    {"tanggal": "2026-10-30", "jam": "19:00", "deskripsi": "Belanja sayur pasar", "nominal": 95000, "tipe": "expense"}
]
pd.DataFrame(mindful_data).to_csv('sample_demo/mutasi_si_mindful.csv', index=False)

# 2. Anak Kopi -> Target: Risk 1 (Waspada), Persona 1 (Lifestyle & Culinary Hedonist)
kopi_data = [
    {"tanggal": "2026-10-01", "jam": "09:00", "deskripsi": "Gaji staf junior", "nominal": 3000000, "tipe": "income"},
    {"tanggal": "2026-10-02", "jam": "12:30", "deskripsi": "Makan siang soto ayam", "nominal": 25000, "tipe": "expense"},
    {"tanggal": "2026-10-03", "jam": "15:30", "deskripsi": "Kopi Kenangan mantan double shot", "nominal": 32000, "tipe": "expense"},
    {"tanggal": "2026-10-05", "jam": "14:15", "deskripsi": "Kopi Kulo americano", "nominal": 25000, "tipe": "expense"},
    {"tanggal": "2026-10-07", "jam": "16:45", "deskripsi": "Jajan boba brown sugar Mixue", "nominal": 22000, "tipe": "expense"},
    {"tanggal": "2026-10-09", "jam": "19:30", "deskripsi": "GoFood ayam geprek mozarella", "nominal": 48000, "tipe": "expense"},
    {"tanggal": "2026-10-11", "jam": "12:00", "deskripsi": "Makan siang warteg komplit", "nominal": 28000, "tipe": "expense"},
    {"tanggal": "2026-10-12", "jam": "15:00", "deskripsi": "Kopi Janji Jiwa latte toast", "nominal": 45000, "tipe": "expense"},
    {"tanggal": "2026-10-14", "jam": "20:00", "deskripsi": "Nongkrong cafe Tomoro Coffee", "nominal": 38000, "tipe": "expense"},
    {"tanggal": "2026-10-16", "jam": "17:30", "deskripsi": "Jajan martabak manis GoFood", "nominal": 65000, "tipe": "expense"},
    {"tanggal": "2026-10-18", "jam": "07:30", "deskripsi": "KRL commuter line kampus", "nominal": 50000, "tipe": "expense"},
    {"tanggal": "2026-10-19", "jam": "19:45", "deskripsi": "Tiket bioskop XXI nonton film", "nominal": 55000, "tipe": "expense"},
    {"tanggal": "2026-10-22", "jam": "14:30", "deskripsi": "Kopi Starbucks caramel macchiato", "nominal": 60000, "tipe": "expense"},
    {"tanggal": "2026-10-25", "jam": "13:30", "deskripsi": "Langganan Spotify premium musik", "nominal": 55000, "tipe": "expense"},
    {"tanggal": "2026-10-27", "jam": "16:15", "deskripsi": "Jajan croffle dan es krim", "nominal": 40000, "tipe": "expense"},
    {"tanggal": "2026-10-30", "jam": "15:00", "deskripsi": "Kopi susu tetangga Tuku", "nominal": 25000, "tipe": "expense"}
]
pd.DataFrame(kopi_data).to_excel('sample_demo/mutasi_anak_kopi.xlsx', index=False)
pd.DataFrame(kopi_data).to_csv('sample_demo/mutasi_anak_kopi.csv', index=False)

# 3. Pejuang 12.12 -> Target: Risk 2 (Impulsif), Persona 2 (Promo & FOMO Trend Hunter)
fomo_data = [
    {"tanggal": "2026-10-01", "jam": "10:00", "deskripsi": "Gaji staf content creator", "nominal": 3500000, "tipe": "income"},
    {"tanggal": "2026-10-04", "jam": "12:00", "deskripsi": "Makan siang ayam", "nominal": 30000, "tipe": "expense"},
    {"tanggal": "2026-10-07", "jam": "07:30", "deskripsi": "KRL transportasi", "nominal": 50000, "tipe": "expense"},
    {"tanggal": "2026-10-10", "jam": "00:15", "deskripsi": "Shopee promo 10.10 flash sale sneakers", "nominal": 450000, "tipe": "expense"},
    {"tanggal": "2026-10-10", "jam": "12:30", "deskripsi": "Shopee diskon tanggal kembar voucher outfit", "nominal": 280000, "tipe": "expense"},
    {"tanggal": "2026-10-10", "jam": "21:30", "deskripsi": "TikTok Shop live flash sale jaket tren", "nominal": 320000, "tipe": "expense"},
    {"tanggal": "2026-10-15", "jam": "14:00", "deskripsi": "Tokopedia beli skincare diskon viral", "nominal": 260000, "tipe": "expense"},
    {"tanggal": "2026-10-18", "jam": "17:30", "deskripsi": "Belanja sembako minimarket", "nominal": 120000, "tipe": "expense"},
    {"tanggal": "2026-10-25", "jam": "11:00", "deskripsi": "Payday sale Tokopedia promo cashback", "nominal": 350000, "tipe": "expense"},
    {"tanggal": "2026-10-26", "jam": "20:00", "deskripsi": "Payday diskon Shopee elektronik TWS", "nominal": 290000, "tipe": "expense"},
    {"tanggal": "2026-10-27", "jam": "19:15", "deskripsi": "Beli casing hp estetik tren fashion", "nominal": 120000, "tipe": "expense"},
    {"tanggal": "2026-10-28", "jam": "21:40", "deskripsi": "Voucher diskon gajian belanja pakaian", "nominal": 240000, "tipe": "expense"}
]
pd.DataFrame(fomo_data).to_csv('sample_demo/mutasi_pejuang_1212.csv', index=False)

# 4. Raja Paylater -> Target: Risk 3 (Kritis), Persona 3 (High-Risk Paylater Dependent)
paylater_data = [
    {"tanggal": "2026-10-01", "jam": "09:00", "deskripsi": "Uang saku bulanan magang", "nominal": 3000000, "tipe": "income"},
    {"tanggal": "2026-10-02", "jam": "12:30", "deskripsi": "Makan siang warteg", "nominal": 25000, "tipe": "expense"},
    {"tanggal": "2026-10-04", "jam": "23:45", "deskripsi": "SPayLater cicilan gadget smartwatch promo", "nominal": 350000, "tipe": "expense"},
    {"tanggal": "2026-10-07", "jam": "01:20", "deskripsi": "GoPayLater midnight jajan kuliner boba cafe", "nominal": 95000, "tipe": "expense"},
    {"tanggal": "2026-10-10", "jam": "02:15", "deskripsi": "Kredivo cicilan checkout sepatu branded flash sale", "nominal": 380000, "tipe": "expense"},
    {"tanggal": "2026-10-12", "jam": "23:30", "deskripsi": "SPayLater belanja baju fashion tren viral", "nominal": 280000, "tipe": "expense"},
    {"tanggal": "2026-10-15", "jam": "00:45", "deskripsi": "Akulaku cicilan perlengkapan game online", "nominal": 190000, "tipe": "expense"},
    {"tanggal": "2026-10-18", "jam": "01:10", "deskripsi": "GoPayLater nongkrong kopi cafe midnight", "nominal": 110000, "tipe": "expense"},
    {"tanggal": "2026-10-22", "jam": "22:50", "deskripsi": "SPayLater jajan dessert cemilan malam", "nominal": 85000, "tipe": "expense"},
    {"tanggal": "2026-10-25", "jam": "23:40", "deskripsi": "SPayLater diskon gajian belanja headphone musik", "nominal": 220000, "tipe": "expense"},
    {"tanggal": "2026-10-28", "jam": "23:15", "deskripsi": "Kredivo tagihan cicilan jajan belanja online", "nominal": 250000, "tipe": "expense"}
]
pd.DataFrame(paylater_data).to_csv('sample_demo/mutasi_raja_paylater.csv', index=False)

print("Demo sample files recalibrated successfully.")
