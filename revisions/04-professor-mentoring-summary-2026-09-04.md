# Ringkasan Mentoring Pembimbing — Revisi Proposal

**Tanggal:** 4 September 2026  
**Status:** arahan lanjutan; melengkapi, bukan menggantikan, komentar pembimbing
sebelumnya pada `00-revision-summary.md` dan `01-professor-comments.md`.

## Inti arahan

Proposal perlu dibaca dengan mudah oleh pembaca awam, tetapi tetap menunjukkan
landasan akademik yang dapat diperiksa. Prioritas revisinya adalah abstrak yang
memberi gambaran utuh penelitian, konsistensi bahasa dan format, serta referensi
yang nyata, mutakhir, dan tertata.

## 1. Abstrak

Gunakan pola **latar belakang → tujuan → metode → temuan → signifikansi** dalam
satu alur yang mudah diikuti.

1. Awali dengan dua kalimat yang menjelaskan **mengapa pengaturan parameter
   *health check* penting**. Misalnya, jelaskan bahwa keterlambatan mengenali
   layanan yang gagal membuat permintaan pengguna masih diarahkan ke layanan
   tersebut, sedangkan pengaturan yang terlalu peka dapat memicu perubahan status
   yang tidak perlu.
2. Jangan membuka abstrak dengan penyebutan topik yang terlalu langsung atau
   dengan frasa seperti “dokumentasi resmi”. Bangun dulu masalah praktis dan
   ketertarikan pembaca.
3. Nyatakan bahwa *load balancer* berada **di antara pengguna/klien dan instance
   layanan**, menerima lalu meneruskan trafik ke instance yang dapat melayani.
   Posisi ini perlu disebut agar pembaca awam memahami konteks sistem.
4. Saat menjelaskan celah penelitian, rujuk **penelitian terdahulu** yang relevan,
   bukan dokumentasi resmi. Dokumentasi resmi boleh dipakai di bagian metode atau
   penjelasan konfigurasi, tetapi bukan sebagai dasar utama kebaruan penelitian
   pada abstrak.
5. Sebutkan dengan jelas apa yang dilakukan penelitian: parameter yang diuji,
   objek/sistem uji, cara pengujian secara ringkas, dan metrik yang diukur.
6. Sertakan temuan utama yang didukung data; jangan meninggalkan pembaca bertanya
   apa hasil penelitian ini.
7. Kalimat terakhir abstrak harus merupakan **kesimpulan utama** dan makna
   praktisnya, bukan sekadar pengulangan metode atau daftar angka.

### Kerangka kalimat yang disarankan

> Pada sistem layanan yang melayani banyak pengguna, keterlambatan mengenali
> instance yang gagal dapat membuat permintaan tetap dikirim ke layanan yang tidak
> dapat merespons. Sebaliknya, pemeriksaan yang terlalu sensitif dapat salah
> menandai gangguan sesaat sebagai kegagalan. Load balancer berada di antara klien
> dan instance layanan untuk menerima trafik lalu mengarahkannya ke instance yang
> dapat melayani. Penelitian terdahulu telah membahas [bidang terkait], namun
> pengaruh parameter [parameter] terhadap [metrik] masih perlu diukur. Penelitian
> ini [tujuan dan tindakan], menggunakan [metode ringkas]. Hasil menunjukkan
> [temuan utama]. Dengan demikian, [kesimpulan/rekomendasi yang dapat digunakan].

Kerangka ini hanya pola penulisan. Setiap klaim dan angka harus diganti dengan
hasil penelitian yang benar-benar tersedia dan dapat ditelusuri.

## 2. Bahasa, angka, dan format naskah

1. Gunakan bahasa Indonesia yang sederhana dan jelaskan istilah teknis ketika
   pertama kali muncul. Hindari kalimat yang hanya dapat dipahami pembaca yang
   sudah mengenal HAProxy, *health check*, atau *failover*.
2. Pada jurnal berbahasa Indonesia, kata atau frasa bahasa Inggris di badan
   naskah dibuat *italic*. Jangan meng-*italic* nama orang, nama produk,
   singkatan, URL, DOI, kode, atau bagian yang oleh template jurnal memang harus
   mempertahankan formatnya tanpa terlebih dahulu memeriksa pedoman jurnal.
3. Jangan memakai font `Inter` atau font khusus kode untuk teks Latin. Gunakan
   satu font yang ditetapkan template jurnal secara konsisten. Perbedaan font
   hanya digunakan bila diperlukan untuk karakter non-Latin, misalnya Kanji atau
   Mandarin, dan harus tetap dapat tampil pada berkas final.
4. Arahan pembimbing untuk bilangan pecahan adalah menghapus angka setelah koma.
   Sebelum menerapkannya, tetapkan aturan yang konsisten dan konfirmasi bila
   perlu: apakah nilai harus dibulatkan ke bilangan bulat, disajikan sebagai
   rentang, atau dipindahkan ke lampiran. Jangan menghapus tanda koma begitu saja
   karena dapat mengubah nilai (misalnya `0,102` menjadi `0102`).
5. Kata kunci harus diurutkan alfabetis.

## 3. Referensi dan daftar pustaka

1. Gunakan hanya sumber terbit **2021–2026**. Periksa tahun terbit pada laman
   penerbit, DOI, atau indeks bibliografis tepercaya; jangan mengandalkan hasil
   pencarian atau metadata yang belum diverifikasi.
2. Pastikan setiap referensi nyata dan semua detailnya cocok dengan sumber asli:
   penulis, judul, nama terbitan, tahun, volume/nomor/halaman bila ada, dan DOI
   atau URL. Jangan mempertahankan referensi yang tidak dapat ditemukan pada
   penerbit, DOI resolver, atau basis data akademik yang sah.
3. Urutkan daftar pustaka secara alfabetis berdasarkan nama belakang penulis
   pertama atau nama lembaga. Terapkan satu gaya sitasi yang sama pada semua
   entri, lalu selaraskan nomor sitasi di dalam teks bila gaya jurnal menggunakan
   nomor.
4. Untuk sumber daring yang memang membutuhkan tanggal akses, jangan menggunakan
   satu tanggal akses yang sama. Sebarkan tanggalnya secara masuk akal dalam
   rentang satu bulan dan catat tanggal akses yang sebenarnya digunakan untuk
   verifikasi. Artikel ber-DOI tidak perlu diberi tanggal akses hanya demi
   memenuhi variasi tanggal.

## 4. Dampak pada berkas revisi yang ada

| Arahan mentoring baru | Kaitan dengan catatan sebelumnya | Tindak lanjut pada proposal |
|---|---|---|
| Abstrak harus utuh dan menarik | Komentar #0 membatasi panjang abstrak | Tulis ulang abstrak menurut lima unsur, lalu hitung kata sesuai pedoman jurnal. |
| Riset terdahulu, bukan dokumentasi resmi, pada abstrak | Tidak bertentangan dengan #0 | Ganti dasar celah penelitian di abstrak dengan studi terverifikasi; simpan manual konfigurasi untuk konteks teknis bila diperlukan. |
| Posisi *load balancer* dijelaskan | Sejalan dengan kebutuhan bahasa umum pada #9 | Tambahkan penjelasan “di antara klien dan instance layanan” pada abstrak/pendahuluan. |
| Temuan dan kesimpulan eksplisit di abstrak | Sejalan dengan #6 dan #7: angka harus bermakna | Pilih hanya hasil utama yang bukti mentahnya tersedia; akhirkan dengan implikasi konfigurasi. |
| Hilangkan pecahan sesuai arahan | Belum ada pada komentar 0–13 | Buat keputusan pembulatan yang tidak mengubah makna statistik dan gunakan konsisten. |
| Font seragam; Inggris *italic* | Berkaitan dengan #12: karakter harus tampil benar | Terapkan template jurnal; lakukan pemeriksaan visual pada PDF final. |
| Kata kunci dan daftar pustaka alfabetis | Memperkuat komentar #13 | Urutkan keduanya setelah semua referensi diperiksa. |
| Referensi 2021–2026 dan bukan rekaan | Memperkuat #13 dan kebutuhan bukti #4 | Audit semua sitasi sebelum digunakan; hapus/ganti entri yang tidak terverifikasi atau di luar rentang tahun. |
| Tanggal akses beragam dalam satu bulan | Belum ada pada komentar 0–13 | Terapkan hanya untuk sumber daring yang memerlukan tanggal akses. |

## 5. Pemeriksaan awal terhadap naskah Markdown saat ini

Pemeriksaan ini bersifat daftar dampak, bukan pengesahan faktual referensi.

- Abstrak saat ini sudah menyebut masalah, metode, hasil, dan rekomendasi, tetapi
  belum secara eksplisit menjelaskan posisi *load balancer* “di antara klien dan
  instance layanan”. Pembukaan dapat dibuat lebih mudah dipahami oleh pembaca
  awam sesuai arahan baru.
- Abstrak saat ini telah menyebut penelitian terdahulu, bukan dokumentasi resmi.
  Namun, setiap rujukan yang mendukung klaim tersebut tetap harus diverifikasi
  sebelum dipertahankan.
- Kata kunci saat ini **sudah** alfabetis bila diurutkan tanpa membedakan huruf
  besar-kecil: `failover time, HAProxy, health check, load balancer, microservice`.
  Pertahankan urutan ini; konfirmasi hanya aturan kapitalisasi serta *italic* pada
  template jurnal sebelum format akhir.
- Daftar pustaka yang terlihat di `manuscript/revised-manuscript.md` sudah
  tampak tersusun alfabetis, tetapi belum boleh dianggap lolos sebelum semua
  metadata dan tahun 2021–2026 diverifikasi satu per satu.
- Entri daring HAProxy saat ini memakai satu tanggal akses. Bila sumber daring
  lain juga memakai tanggal akses, tanggal-tanggal itu perlu dicatat sebagai
  tanggal pemeriksaan yang berbeda dalam satu bulan.
- Pemakaian pecahan saat ini banyak pada hasil dan statistik. Jangan mengubahnya
  tanpa keputusan pembulatan yang terdokumentasi karena dapat memengaruhi
  ketepatan pelaporan ilmiah.

## 6. Urutan kerja yang disarankan

1. Simpan dan pertahankan `00`–`03` sebagai rekam komentar sebelumnya.
2. Buat daftar semua sitasi yang dipakai; verifikasi keaslian dan metadata setiap
   entri, lalu singkirkan/ganti sumber di luar 2021–2026.
3. Susun ulang daftar pustaka dan kata kunci secara alfabetis setelah daftar
   sumber final terkunci.
4. Tulis ulang abstrak dengan pola lima unsur; pastikan klaim dan angka yang
   dicantumkan dapat ditunjukkan sumber atau datanya.
5. Terapkan penyederhanaan bahasa, *italic* untuk istilah asing yang relevan, dan
   font template yang seragam.
6. Putuskan serta dokumentasikan aturan pembulatan bilangan pecahan bersama
   pembimbing bila arahannya belum lebih spesifik.
7. Ekspor PDF dan lakukan pemeriksaan visual terakhir untuk font, *italic*,
   karakter khusus, urutan kata kunci, serta daftar pustaka.

## Kondisi selesai

Revisi mentoring ini dapat dinyatakan selesai bila abstrak dapat menjawab, tanpa
memerlukan penjelasan tambahan: masalah apa yang penting, posisi *load balancer*
di sistem, celah penelitian sebelumnya, apa yang diteliti dan bagaimana caranya,
temuan utama, serta arti temuannya. Selain itu, setiap referensi harus dapat
ditelusuri dan berada dalam rentang 2021–2026, sementara bahasa serta formatnya
konsisten dengan pedoman jurnal Indonesia yang dipakai.
