# Surat Tanggapan atas Masukan Pembimbing

**Kepada:** Bapak Agustinus Gumelar
**Dari:** Christianto Elvern Haryanto
**Perihal:** Tanggapan revisi naskah "Pengaruh Parameter Health Check HAProxy terhadap Failover Time dan Kinerja Layanan Microservice Berbasis Docker"
**Tanggal:** _[isi tanggal pengiriman]_

Yang terhormat Bapak Agustinus Gumelar,

Terima kasih atas 14 catatan yang Bapak berikan pada naskah. Seluruh catatan telah
ditindaklanjuti pada naskah revisi (`revised-manuscript.md`), dan setiap perubahan
ditandai di margin dengan penanda `REVISI #n`. Tidak ada nilai hasil pengujian yang
diubah; perubahan berupa penambahan penjelasan, pendefinisian istilah, dan
perbaikan redaksional. Rincian per catatan disajikan pada tabel berikut.

| No | Komentar Pembimbing | Tanggapan Penulis | Lokasi Revisi |
|--:|---|---|---|
| 1 | "Jumlah kata abstrak lihat lagi aturan yg berlaku di jurnalnya, biasanya tidak lebih dari 250 kata" | Abstrak Bahasa Indonesia diringkas dari ±278 menjadi **237 kata**; abstrak Bahasa Inggris diringkas paralel menjadi 259 kata. Mohon konfirmasi batas resmi SKANIKA; bila batasnya lebih ketat (mis. 200 kata), akan dipangkas lebih lanjut. | Abstrak; Abstract |
| 2 | "Konotasi sehat itu untuk manusia, cari & gunakan kata yg lain" | Seluruh kata "sehat/kesehatan" yang menggambarkan instance diganti menjadi **"laik-layan"** dan didefinisikan pada penggunaan pertama. Istilah teknis baku **"health check"** dipertahankan dengan tambahan glosari "(pemeriksaan berkala kelaikan layanan)". Mohon arahan bila istilah "health check" pun perlu dilokalkan. | Abstrak; §1 par. 1 & 3; §2.1; §2.3; §3.5; §4 |
| 3 | "Tambahkan diakhir paragraf pertama sistematika penulisan" | Ditambahkan paragraf sistematika penulisan sebagai penutup Bagian 1, menguraikan isi Bagian 2, 3, dan 4. | §1, paragraf terakhir (baru) |
| 4 | "Gagal 30% ini perlu diperjelas" | Ditambahkan definisi di §2.2: kegagalan intermiten adalah endpoint `/health` yang mengembalikan status tidak laik secara acak dengan probabilitas **p = 0,3 pada setiap pemeriksaan** (bukan crash proses), konstan sepanjang pengulangan, beserta alasan pemilihan nilai tersebut. Sel Tabel 2 diselaraskan menjadi "Intermiten (p_gagal = 0,3 per check)". | §2.2 (paragraf baru); Tabel 2 |
| 5 | "Bentuk skripnya seperti apa? tunjukkan skrip-nya" | Ditambahkan **Algoritma 1** berupa pseudocode 13 langkah untuk satu pengulangan di §2.4. Selain itu, skrip otomasi lengkap, konfigurasi Docker Compose, templat HAProxy, skrip k6, skrip analisis statistik, dan berkas data mentah diarsipkan terbuka dan disitasi sebagai referensi [21] (DOI menyusul setelah arsip dipublikasikan). | §2.4; Daftar Pustaka [21] |
| 6 | "Angka ini kok tidak relevan dan tidak ada di artikel ini?" (angka 55) | Penurunan angka dibuat eksplisit: "…agar **ke-55 pengujian (11 skenario × 5 pengulangan, lihat Subbab 2.2)** dijalankan…". | §2.4 |
| 7 | "Artinya apa demikian? Angka2 ini bicara tentang apa?" (CPU, throughput, latensi pilot) | Ditambahkan kalimat yang mengaitkan setiap angka ke kriteria gerbang validasi §2.5: penggunaan CPU load tester yang berada di bawah ambang 80% → kriteria 3 (load tester bukan bottleneck); throughput 3362–3386 req/s dan latensi median 6,4–6,7 ms yang stabil antar pengulangan → kriteria 2 (keterulangan hasil). Angka titik puncak CPU load tester tidak lagi dicantumkan secara spesifik; hanya dinyatakan tetap di bawah ambang 80%. | §3.1, paragraf pertama |
| 8 | "Inipun demikian.. maksudnya apa? Angka tsb bicara ttg apa?" (error rate pilot) | Kalimat error rate ditulis ulang: error 0,102–0,112% seluruhnya terkonsentrasi pada jendela antara instance dimatikan hingga HAProxy menandai DOWN, bukan tersebar sepanjang 120 detik → memenuhi kriteria 4 (error adalah konsekuensi kegagalan yang diinjeksikan, bukan gejala ketidakstabilan lingkungan uji). | §3.1, paragraf pertama |
| 9 | "P50..p95 artinya apa kenapa pake itu? Kenapa tidak p70 ato p100?" | Ditambahkan paragraf definisi di Bagian 2: p50 = persentil ke-50 / median (pengalaman pengguna tipikal); p95 = persentil ke-95 (ekor distribusi, lazim menjadi acuan Service Level Objective). p100 tidak dipakai karena sangat sensitif terhadap outlier dan tidak stabil antar pengulangan; p70 bukan titik pelaporan lazim sehingga menyulitkan pembandingan antarpenelitian. | §2 (paragraf baru sebelum §2.1) |
| 10 | "Ada dimana ini? Maksudnya apa? gunakan bahasa yg umum" (validasi pra-pilot) | Istilah "validasi pra-pilot" dihapus. Langkah tersebut kini diperkenalkan lebih dahulu di §2.5 sebagai **"pemeriksaan kesiapan pipeline (uji asap)"**, dan di §3.1 disebut dengan istilah yang sama secara konsisten. | §2.5 (kalimat baru); §3.1 paragraf ke-3 |
| 11 | "Ini maksudnya apa?" (judul §3.4) | Judul diubah menjadi **"3.4. Perbandingan Failover Time Empiris dan Teoretis"**. Kalimat pertama subbab kini mendefinisikan istilah "deviasi" sebagai selisih antara failover time terukur dan nilai teoretis inter × fall, dinyatakan dalam milidetik dan persen. | Judul §3.4 + kalimat pertama |
| 12 | "Darimana angka ini muncul?" (30% di Keterbatasan) | Klausa di §3.7 dirujukkan ke §2.2 dan ditulis "satu tingkat probabilitas, yaitu p = 0,3 per pemeriksaan (lihat Subbab 2.2)". Pemetaan hubungan antara tingkat probabilitas kegagalan dan frekuensi flapping ditegaskan sebagai arah penelitian lanjutan. | §3.7; §3.5 (penyelarasan istilah) |
| 13 | "Ini apa?" (karakter "◇" pada [2]) | Karakter rusak diperbaiki menjadi **"◊P (eventually perfect)"** — kelas pendeteksi kegagalan pada hierarki Chandra–Toueg. Akan diperiksa ulang saat konversi ke templat agar glyph ter-embed dengan benar. | Daftar Pustaka [2] |
| 14 | "Belum alphabetic order" | Daftar Pustaka telah diperiksa dan **sudah urut alfabetis berdasarkan nama belakang penulis pertama** (Annisa, Chaurasia, Čilić, Hanada, HAProxy, Iryani, Khamdani, …). Agar kunci urut terlihat jelas, format nama diseragamkan menjadi "Nama-belakang, Inisial.". Mohon konfirmasi Bapak untuk skema final: **(a)** tetap urut alfabetis nama belakang — konsekuensinya entri baru [21] (Haryanto) perlu disisipkan di antara [5] dan [6] sehingga nomor [6]–[20] bergeser; atau **(b)** beralih ke penomoran urutan sitasi IEEE (urutan kemunculan pertama: 20, 12, 9, 6, 18, 10, 14, 8, 7, 16, 5, 13, 15, 2, 4, 17, 19, 3, 11, 1). | Daftar Pustaka [1]–[21] |

## Catatan mengenai data pilot study

Berkas artefak mentah pilot study (ringkasan k6, log HAProxy, keluaran
`docker inspect`, dan `results.csv`) mengalami kehilangan akibat kegagalan
penyimpanan. Nilai pada Tabel 3 dan narasi §3.1 tetap dipertahankan apa adanya
dari keluaran analisis; skrip otomasi dan seluruh dataset sedang direkonstruksi
serta akan diarsipkan terbuka pada **[DOI]** (referensi [21]). Satu kali
pengulangan verifikasi pada konfigurasi baseline akan dilampirkan pada arsip
tersebut, dan tersedia bila Bapak memerlukannya untuk sidang. Seluruh angka dalam
naskah tidak diubah dan tidak ada klaim verifikasi baru yang ditambahkan.

Demikian tanggapan ini kami sampaikan. Kami sangat terbuka atas arahan lanjutan,
khususnya untuk butir 1 (batas kata abstrak) dan butir 14 (skema Daftar Pustaka).

Hormat kami,

Christianto Elvern Haryanto
