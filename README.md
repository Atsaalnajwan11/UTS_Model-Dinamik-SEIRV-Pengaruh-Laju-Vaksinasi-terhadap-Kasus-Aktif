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

## Hasil-Hasil


### WEBSITE

   ```bash
   
   ```


### DATASET(EXCEL)
data.mendeley.com
   ```bash
   https://data.mendeley.com/datasets/7szms6xrdb/1
   ```

### PENJELASAN YOUTUBE

   ```bash
   https://youtu.be/2yntjUo3fmQ
   ```
### RUJUKAN JURNAL

   ```bash

   ```
