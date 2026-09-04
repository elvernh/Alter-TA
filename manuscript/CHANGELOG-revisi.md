# CHANGELOG Revisi 1 — Jurnal SKANIKA HAProxy Health Check

Naskah dasar: `Jurnal_SKANIKA_HAProxy_Health_Check-reviewed BIMO.docx`
Naskah hasil revisi: `manuscript/revised-manuscript.md`
Pereview: Agustinus Gumelar (14 komentar, 2026-08-31)

## 2026-09-04 — Revisi mentoring pembimbing

- Abstrak Indonesia dan Inggris ditulis ulang dengan pola latar belakang–tujuan–metode–temuan–signifikansi.
- Ditambahkan penjelasan bahwa *load balancer* berada di antara klien dan instance layanan.
- Pembukaan abstrak kini menjelaskan alasan pentingnya parameter *health check*; kalimat terakhir menyatakan kesimpulan praktis.
- Angka headline pada abstrak dibulatkan agar ringkas; angka presisi pada tabel dan bagian hasil tidak diubah.
- Ringkasan arahan mentoring disimpan di `revisions/04-professor-mentoring-summary-2026-09-04.md`.
- Referensi dataset dengan DOI placeholder `[21]` dihapus dari naskah; sitasi arsip akan ditambahkan setelah DOI nyata tersedia.

## Jumlah kata abstrak (komentar #0)

| Abstrak | Sebelum | Sesudah | Batas |
|---|---|---|---|
| Bahasa Indonesia | ±278 kata | **237 kata** | ≤ 250 (asumsi; **perlu dikonfirmasi pada pedoman SKANIKA** — sebagian jurnal ID membatasi 150–200 kata) |
| Bahasa Inggris | ±300 kata | **259 kata** | mengikuti; masih dapat dipangkas ±10 kata bila pedoman menuntut ≤ 250 |

## Prinsip revisi

- **Tidak ada satu pun nilai hasil yang diubah.** Semua angka (Tabel 3–9, failover 297–23668 ms, ε², 39,4 vs 0,8 transisi, 17,9%, dll.) identik dengan naskah asli.
- Perubahan hanya berupa **penambahan teks interpretasi/definisi** dan perbaikan redaksional/format.
- Pemisah desimal diseragamkan menjadi **koma** (standar Bahasa Indonesia) pada seluruh badan naskah Indonesia dan tabel; nilai tidak berubah (mis. `0.102` → `0,102`, `896.48` → `896,48`, `α = 0.05` → `α = 0,05`). Abstrak Inggris tetap memakai titik.
- Setiap perubahan ditandai inline pada `revised-manuscript.md` dengan `<!-- REVISI #n: ... -->`.

---

## 14 perubahan

### #0 — Jumlah kata abstrak
- **Komentar:** "Jumlah kata abstrak lihat lagi aturan yg berlaku di jurnalnya, biasanya tidak lebih dari 250 kata"
- **Perubahan:** Abstrak Indonesia diringkas 278→237 kata; abstrak Inggris diringkas paralel 300→259 kata. Kalimat kriteria pilot ("berkriteria eksplisit") dan klausa penutup ("dan bukan diwarisi begitu saja dari nilai bawaan") dipangkas; daftar metrik dipadatkan.
- **Lokasi:** Abstrak, Abstract.
- **Before:** "…didahului pilot study sebagai gerbang validasi berkriteria eksplisit. …bukan diwarisi begitu saja dari nilai bawaan."
- **After:** "…didahului pilot study sebagai gerbang validasi. …nilai fall perlu dipilih menurut karakteristik kegagalan dominan pada sistem sasaran."

### #1 — Konotasi "sehat"
- **Komentar:** "Konotasi sehat itu untuk manusia, cari & gunakan kata yg lain"
- **Perubahan:** Seluruh "sehat / kesehatan / tidak sehat" yang menggambarkan instance diganti **"laik-layan"** (didefinisikan pada penggunaan pertama di §1). Istilah majemuk **"health check" dipertahankan** dan diberi glosari sekali: "(pemeriksaan berkala kelaikan layanan)". Pada abstrak Inggris "the healthy instances" → "the available instances".
- **Lokasi:** Abstrak; §1 par. 1 & par. 3; §2.1; §2.3; §3.5; §4.
- **Before → After (contoh):** "instance yang sehat" → "instance yang laik-layan"; "menilai kesehatannya" → "menilai kelaikannya menerima trafik"; "respons tidak sehat" → "respons tidak laik"; "dua instance sehat lainnya" → "dua instance laik-layan lainnya"; "riwayat kesehatan instance" → "riwayat kelaikan instance".

### #2 — Sistematika penulisan
- **Komentar:** "Tambahkan diakhir paragraf pertama sistematika penulisan"
- **Perubahan:** Ditambahkan paragraf baru sebagai penutup Bagian 1 yang menguraikan isi Bagian 2, 3, dan 4.
- **Lokasi:** §1, paragraf terakhir (baru).
- **After (kutipan):** "Sisa artikel ini disusun sebagai berikut. Bagian 2 memaparkan metode penelitian… Bagian 3 menyajikan hasil dan pembahasan… Bagian 4 memuat kesimpulan serta saran…"

### #3 — "Gagal 30%" perlu diperjelas
- **Komentar:** "Gagal 30% ini perlu diperjelas"
- **Perubahan:** Ditambahkan paragraf definisi di §2.2: kegagalan intermiten = endpoint `/health` mengembalikan status tidak laik secara acak dengan **p = 0,3 per pemeriksaan** (bukan crash), konstan sepanjang pengulangan; disertai alasan pemilihan nilai (representasi kegagalan intermiten tingkat sedang). Sel Tabel 2 baris flap_fall1 & flap_fall5 diubah.
- **Lokasi:** §2.2 (paragraf baru); Tabel 2 kolom "Jenis kegagalan".
- **Before → After (tabel):** "Intermiten (gagal 30%)" → "Intermiten (p_gagal = 0,3 per check)".

### #4 — Tunjukkan skrip otomasi
- **Komentar:** "Bentuk skripnya seperti apa? tunjukkan skrip-nya"
- **Perubahan:** (a) Ditambahkan **Algoritma 1** (pseudocode 13 langkah untuk satu pengulangan) di §2.4. (b) Ditambahkan kalimat bahwa skrip lengkap + Docker Compose + templat HAProxy + skrip k6 + skrip analisis + data mentah diarsipkan terbuka di **[DOI]**, disitasi sebagai **[21]** dan ditambahkan ke Daftar Pustaka (format dataset/software Zenodo, DOI placeholder).
- **Lokasi:** §2.4; Daftar Pustaka [21].
- **Catatan:** Repo/arsip nyata sedang direkonstruksi di workspace terpisah `haproxy-healthcheck-study/`; DOI diisi setelah publikasi arsip.

### #5 — Angka "55"
- **Komentar:** "Angka ini kok tidak relevan dan tidak ada di artikel ini?"
- **Perubahan:** Penurunan angka dibuat eksplisit di titik penggunaan.
- **Lokasi:** §2.4.
- **Before:** "…agar 55 pengujian dijalankan dengan prosedur yang identik…"
- **After:** "…agar ke-55 pengujian (11 skenario × 5 pengulangan, lihat Subbab 2.2) dijalankan dengan prosedur yang identik…"

### #6 — Angka CPU/throughput/latensi pilot tanpa interpretasi
- **Komentar:** "Artinya apa demikian? Angka2 ini bicara tentang apa?"
- **Perubahan:** Ditambahkan kalimat yang membaca setiap angka terhadap kriteria gerbang validasi §2.5: penggunaan CPU load tester di bawah ambang 80% → kriteria 3 (bukan bottleneck); throughput 3362–3386 req/s & latensi median 6,4–6,7 ms stabil antar pengulangan → kriteria 2 (keterulangan).
- **Lokasi:** §3.1, paragraf pertama (lanjutan).
- **After (kutipan):** "…penggunaan CPU load tester yang tidak melampaui ambang 80% memastikan load tester bukan menjadi bottleneck (kriteria 3)…"
- **Pemutakhiran pasca-verifikasi (2026-08-31):** angka spesifik "57%" **dihilangkan** dari §3.1. Artefak mentah pilot hilang sehingga nilai titik puncak CPU load tester tidak dapat diverifikasi ulang; re-run verifikasi pada pipeline rekonstruksi memakai regime beban berbeda sehingga angka absolutnya tidak sebanding. Yang dipertahankan hanya pernyataan kepatuhan terhadap ambang 80% (kriteria 3). Throughput dan latensi tetap (ada di Tabel 3, tereproduksi pada re-run). Lihat `experiment/docs/PILOT-RERUN-2026-08-31.md`.

### #7 — Angka error rate pilot tanpa interpretasi
- **Komentar:** "Inipun demikian.. maksudnya apa? Angka tsb bicara ttg apa?"
- **Perubahan:** Kalimat error rate ditulis ulang dan dikaitkan ke kriteria 4: error 0,102–0,112% terkonsentrasi pada jendela antara instance dimatikan hingga HAProxy menandai DOWN, tidak tersebar sepanjang 120 s → error adalah konsekuensi kegagalan yang diinjeksikan, bukan ketidakstabilan lingkungan.
- **Lokasi:** §3.1, paragraf pertama.
- **Before:** "Error rate berkisar 0.102% sampai 0.112% dan terkonsentrasi pada jendela waktu antara instance dimatikan hingga HAProxy menandainya DOWN."
- **After:** "Error rate berkisar 0,102–0,112% dan seluruhnya terkonsentrasi pada jendela waktu antara instance dimatikan hingga HAProxy menandainya DOWN, bukan tersebar sepanjang 120 detik pengujian; pola ini memenuhi kriteria 4…"

### #8 — p50 / p95: definisi & alasan
- **Komentar:** "P50..p95 artinya apa kenapa pake itu? Kenapa tidak p70 ato p100?"
- **Perubahan:** Ditambahkan paragraf di Bagian 2 (setelah daftar variabel terikat): p50 = median (pengalaman tipikal); p95 = ekor distribusi / acuan SLO; p100 ditolak (sensitif outlier, tidak stabil antar pengulangan); p70 ditolak (bukan titik pelaporan lazim, menyulitkan pembandingan).
- **Lokasi:** §2 (paragraf baru sebelum §2.1).

### #9 — "validasi pra-pilot" tidak terdefinisi
- **Komentar:** "Ada dimana ini? Maksudnya apa? gunakan bahasa yg umum"
- **Perubahan:** (a) §2.5 diberi kalimat pembuka yang mendefinisikan langkah **"pemeriksaan kesiapan pipeline (uji asap)"** sebelum pilot study, dengan rujukan bahwa temuannya dilaporkan di §3.1. (b) Di §3.1 istilah "validasi pra-pilot" diganti "pemeriksaan kesiapan pipeline sebelum pilot study". Tidak ada kemunculan "pra-pilot" lain.
- **Lokasi:** §2.5 (kalimat baru); §3.1 paragraf ke-3.
- **Before:** "Pada tahap validasi pra-pilot ditemukan bahwa nilai bawaan timeout connect HAProxy…"
- **After:** "Pada pemeriksaan kesiapan pipeline sebelum pilot study ditemukan bahwa nilai bawaan timeout connect HAProxy…"

### #10 — Judul §3.4 tidak jelas
- **Komentar:** "Ini maksudnya apa?"
- **Perubahan:** Judul "3.4. Deviasi Failover Time Empiris terhadap Nilai Teoretis" → **"3.4. Perbandingan Failover Time Empiris dan Teoretis"**; kalimat pertama mendefinisikan "deviasi" = selisih antara failover time terukur dan nilai teoretis inter × fall (Persamaan 1), dalam ms dan persen.
- **Lokasi:** Judul §3.4 + kalimat pertama.

### #11 — Dari mana angka 30%
- **Komentar:** "Darimana angka ini muncul?"
- **Perubahan:** Klausa di §3.7 dirujukkan ke §2.2; "tingkat probabilitas tunggal sebesar 30%" → "satu tingkat probabilitas, yaitu p = 0,3 per pemeriksaan (lihat Subbab 2.2)"; pemetaan hubungan probabilitas–flapping dinyatakan sebagai arah penelitian lanjutan. Kemunculan "30%" di §3.5 juga diselaraskan menjadi "p = 0,3".
- **Lokasi:** §3.7; §3.5.

### #12 — Karakter "◇" pada [2]
- **Komentar:** "Ini apa?"
- **Perubahan:** "◇P" → **"◊P (eventually perfect)"** pada judul referensi [2].
- **Lokasi:** Daftar Pustaka [2].
- **Catatan:** Pastikan glyph ◊ ter-embed saat konversi ke templat SKANIKA; bila font tidak mendukung, tulis "(eventually perfect, ◊P)". Judul persis perlu dicek ulang di doi:10.1007/s40747-026-02423-z.

### #13 — Daftar Pustaka belum alphabetic order
- **Komentar:** "Belum alphabetic order"
- **Perubahan:** Daftar Pustaka **sudah** urut alfabetis berdasarkan nama belakang penulis pertama (Annisa < Chaurasia < Čilić < Hanada < HAProxy < Iryani < …). Untuk membuat kunci urut terlihat, format nama diseragamkan menjadi **"Nama-belakang, Inisial."** pada 21 entri. **Nomor tidak diubah** (sesuai arahan).
- **Lokasi:** Daftar Pustaka [1]–[21].
- **Keputusan tertunda (butir untuk pembimbing):**
  1. Pertahankan urut alfabetis-nama-belakang (kondisi saat ini) — bila ya, entri baru **[21] Haryanto** semestinya disisipkan di antara [5] HAProxy dan [6] Iryani sehingga [6]–[20] menjadi [7]–[21]; **atau**
  2. Ganti ke penomoran **urutan sitasi IEEE** — urutan kemunculan pertama saat ini: 20, 12, 9, 6, 18, 10, 14, 8, 7, 16, 5, 13, 15, 2, 4, 17, 19, 3, 11, 1.

---

## Perubahan format tambahan (bukan bagian 14 komentar, dicatat untuk transparansi)

| Item | Tindakan |
|---|---|
| Pemisah desimal | Titik → koma di seluruh badan Indonesia + Tabel 1–9 (nilai identik). |
| `t_teoretis`, Persamaan (1)/(2) | Ditulis ulang dalam notasi matematika; substansi sama. |
| Gambar 1–3 | Placeholder rujukan ke `word/media/image1–3.png` dari DOCX asli; perlu di-render ulang ≥ 300 dpi dengan label sumbu (lihat `toolkit/manuscript-and-submission-checklist.md`). |

## Yang MASIH perlu dikerjakan penulis

1. Konfirmasi batas kata abstrak & skema Daftar Pustaka pada pedoman SKANIKA / ke pembimbing.
2. Isi `[Nama Dosen Pembimbing]`, email, dan DOI arsip [21].
3. Selesaikan rekonstruksi arsip skrip+data (workspace `haproxy-healthcheck-study/`) dan terbitkan DOI.
4. Render ulang Gambar 1–3; konversi `revised-manuscript.md` ke templat DOCX SKANIKA (pandoc belum terpasang di mesin ini).
5. Cek ulang judul persis referensi [2] pada laman DOI.
