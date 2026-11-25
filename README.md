# Paket Proyek UTS Pemodelan dan Simulasi — Model Sistem Dinamik SEIRV Jawa Barat

Isi Paket ZIP:
1. `Model_SEIRV_COVID19_Jawa_Barat.ipynb` — Notebook Google Colab untuk pemodelan ODE SEIRV, kalibrasi parameter (L-BFGS-B), uji validasi kurva, dan grafik skenario vaksinasi.
2. `flask_web/` — Aplikasi Web Full-Stack berbasis **Python Flask** dengan dashboard interaktif:
   - `flask_web/app.py` — Backend Flask + solver numerik `scipy.integrate.odeint` & endpoint API `/api/simulate`.
   - `flask_web/templates/index.html` — Antarmuka dashboard interaktif (Chart.js + kontrol parameter real-time + ekspor CSV).
   - `flask_web/requirements.txt` — Daftar dependensi Python untuk instalasi lokal maupun *deployment* (Render / Railway / PythonAnywhere).
   - `flask_web/DataSetCvd.xlsx` — Dataset empiris Jawa Barat & vaksinasi.
3. `DataSetCvd.xlsx` — Salinan dataset di root folder untuk kemudahan unggah ke Google Colab.

Cara Menjalankan Aplikasi Web Flask:
```bash
cd flask_web
pip install -r requirements.txt
python app.py
```
Lalu buka browser ke `http://127.0.0.1:5000`.

---

## Cara Deploy ke Vercel

Aplikasi ini sudah dikonfigurasi dengan `vercel.json` dan serverless entrypoint `api/index.py`.

### Opsi 1: Deploy via GitHub (Paling Mudah & Otomatis)
1. Push repositori ini ke GitHub:
   ```bash
   git init
   git add .
   git commit -m "Initial commit for Vercel deployment"
   git branch -M main
   git remote add origin https://github.com/<username>/<repo-name>.git
   git push -u origin main
   ```
2. Buka [Vercel Dashboard](https://vercel.com/) dan login.
3. Klik **"Add New..."** > **"Project"**.
4. Pilih repositori GitHub Anda lalu klik **"Import"**.
5. Vercel akan otomatis mendeteksi konfigurasi `vercel.json` dan `requirements.txt`. Klik tombol **"Deploy"**.

### Opsi 2: Deploy via Vercel CLI
1. Pasang Vercel CLI (jika belum ada):
   ```bash
   npm install -g vercel
   ```
2. Jalankan perintah deployment dari direktori proyek:
   ```bash
   vercel
   ```
3. Ikuti instruksi terminal (tekan Enter untuk pilihan default). Untuk deploy ke production:
   ```bash
   vercel --prod
   ```
