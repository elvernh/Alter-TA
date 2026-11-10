# Ringkasan Revisi Pembimbing: 4-6 September 2026

**Tanggal:** 4 September 2026  
**Status:** arahan lanjutan; melengkapi, bukan menggantikan, komentar pembimbing
sebelumnya pada `00-revision-summary.md` dan `01-professor-comments.md`.

**Sumber ulasan terbaru:**
`Professor's Revision/review_Pengaruh Parameter Health Check HAProxy terhadap Failover Time dan Kinerja Layanan Microservice Berbasis Docker.docx`.
Berkas ini memuat 18 komentar terbuka, ID 0-17, tanpa tracked insertion atau
tracked deletion. Metadata komentar tercatat pada 5 September 2026 UTC, yang
setara dengan 6 September 2026 WIB.

## Catatan ruang lingkup abstrak — 7 September 2026

Revisi abstrak berikutnya harus memakai abstrak versi pertama yang dikirim ke
pembimbing sebagai teks dasar. Perubahan bukan penulisan ulang total: pertahankan
urutan masalah, konteks arsitektur, celah, metode, hasil, dan kesimpulan yang
sudah ada, lalu tambahkan keterangan minimum yang menjawab komentar pembimbing.
Keterangan itu mencakup objek instance yang gagal, mekanisme pemeriksaan
`/health`, hubungan antara keterlambatan dan sensitivitas pemeriksaan, alasan
pengukuran parameter, serta konteks skenario hasil. Abstract bahasa Inggris
harus tetap sepadan maknanya dengan abstrak Indonesia.

Jangan menambah konfigurasi, alamat IP, endpoint selain yang telah dicatat,
angka hasil baru, atau klaim pustaka baru ke abstrak. Bila suatu konteks tidak
didukung oleh metode atau hasil, nyatakan batasannya atau jangan tambahkan.

## Inti arahan

Proposal perlu dibaca dengan mudah oleh pembaca awam, tetapi tetap menunjukkan
landasan akademik yang dapat diperiksa. Prioritas revisinya adalah abstrak yang
memberi gambaran utuh penelitian, konsistensi bahasa dan format, serta referensi
yang nyata, mutakhir, dan tertata. Ulasan terbaru menambahkan satu syarat utama:
setiap istilah, hubungan, dan alasan harus spesifik terhadap sistem yang diuji.
Kata umum tidak boleh menggantikan objek, kondisi, mekanisme, atau bukti yang
sebenarnya tersedia.

## 1. Abstrak

Gunakan pola **latar belakang → tujuan → metode → temuan → signifikansi** dalam
satu alur yang mudah diikuti.

1. Awali dengan masalah yang spesifik terhadap objek penelitian. Nyatakan jenis
   layanan yang dimaksud, definisi operasional kegagalan, pemeriksaan yang
   dilakukan HAProxy, dan akibatnya terhadap aliran permintaan. Jangan memakai
   kata “layanan”, “gagal”, “peka”, atau “gangguan sesaat” tanpa penjelasan yang
   dapat ditelusuri ke metode penelitian.
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

### Kerangka isi abstrak yang diperbarui

Jangan menggunakan contoh kalimat lama sebagai teks siap pakai. Susun satu alur
dengan unsur berikut dan isi hanya dari bukti yang tersedia:

1. objek sistem yang diuji, termasuk jenis layanan dan posisi HAProxy;
2. definisi kegagalan total dan/atau intermiten yang benar-benar diterapkan;
3. akibat terukur ketika HAProxy belum atau keliru mengubah status instance;
4. celah penelitian yang dibandingkan secara eksplisit dengan studi terverifikasi;
5. parameter, jumlah skenario, pengulangan, beban uji, dan metrik yang relevan;
6. hasil utama dengan angka, satuan, pembanding, dan kondisi pengujian; dan
7. kesimpulan yang ruang berlakunya dibatasi pada lingkungan eksperimen.

Kalimat pertama tidak boleh mengandalkan frasa umum seperti “layanan yang gagal”.
Untuk naskah ini, rincian operasional harus diambil dari metode: kegagalan total
dibuat dengan menghentikan paksa container target, sedangkan kegagalan intermiten
dibuat melalui respons tidak laik dari endpoint `/health` dengan probabilitas
yang ditetapkan per pemeriksaan. Ringkas rincian tersebut sesuai batas kata
abstrak tanpa mengubah jenis kegagalannya.

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

1. Gunakan hanya sumber terbit **2021-2026**. Periksa tahun terbit pada laman
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
| Hilangkan pecahan sesuai arahan | Belum ada pada komentar 0-13 | Buat keputusan pembulatan yang tidak mengubah makna statistik dan gunakan konsisten. |
| Font seragam; Inggris *italic* | Berkaitan dengan #12: karakter harus tampil benar | Terapkan template jurnal; lakukan pemeriksaan visual pada PDF final. |
| Kata kunci dan daftar pustaka alfabetis | Memperkuat komentar #13 | Urutkan keduanya setelah semua referensi diperiksa. |
| Referensi 2021-2026 dan bukan rekaan | Memperkuat #13 dan kebutuhan bukti #4 | Audit semua sitasi sebelum digunakan; hapus/ganti entri yang tidak terverifikasi atau di luar rentang tahun. |
| Tanggal akses beragam dalam satu bulan | Belum ada pada komentar 0-13 | Terapkan hanya untuk sumber daring yang memerlukan tanggal akses. |

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
  metadata dan tahun 2021-2026 diverifikasi satu per satu.
- Entri daring HAProxy saat ini memakai satu tanggal akses. Bila sumber daring
  lain juga memakai tanggal akses, tanggal-tanggal itu perlu dicatat sebagai
  tanggal pemeriksaan yang berbeda dalam satu bulan.
- Pemakaian pecahan saat ini banyak pada hasil dan statistik. Jangan mengubahnya
  tanpa keputusan pembulatan yang terdokumentasi karena dapat memengaruhi
  ketepatan pelaporan ilmiah.

## 6. Urutan kerja yang disarankan

1. Simpan dan pertahankan `00`-`03` sebagai rekam komentar sebelumnya.
2. Buat daftar semua sitasi yang dipakai; verifikasi keaslian dan metadata setiap
   entri, lalu singkirkan/ganti sumber di luar 2021-2026.
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

## 7. Komentar pembimbing pada berkas ulasan terbaru

Sebelas komentar pertama, ID 0-10, menempel pada paragraf abstrak yang sama.
Karena itu, tindak lanjutnya bukan sekadar mengganti kata yang disorot. Abstrak
perlu ditulis ulang sebagai satu argumen yang menyebut objek, jenis kegagalan,
mekanisme pemeriksaan, alasan penelitian, metode, hasil, dan batas konteksnya.

| ID | Teks yang disorot | Komentar pembimbing | Makna dalam konteks dan tindak lanjut |
|---:|---|---|---|
| 0 | “layanan” pada kalimat pembuka abstrak | “Layanan apa? Layanan bagaimana>” | Sebutkan jenis layanan yang diuji dan perannya. Jangan membiarkan “layanan” merujuk secara samar ke aplikasi, instance, endpoint, atau seluruh sistem. |
| 1 | “gagal” pada kalimat pembuka abstrak | “Gagal apa? Gagal yang bagaimana?” | Bedakan kegagalan total berupa penghentian container target dari kegagalan intermiten berupa respons `/health` tidak laik. Gunakan hanya jenis kegagalan yang memang relevan pada kalimat tersebut. |
| 2 | “layanan” pada frasa “layanan yang tidak dapat merespons” | “Layanan apa?” | Pertahankan referen yang sama dari awal kalimat. Nyatakan apakah yang tidak merespons adalah instance target, endpoint aplikasi, atau objek lain berdasarkan metode. |
| 3 | “Sebaliknya” | “Sebaliknya dari apa? Relevansinya darimana?” | Jangan memakai penghubung kontras sebelum dua kondisi yang dibandingkan dinyatakan jelas. Hubungan antara deteksi lambat dan perubahan status berulang harus dijelaskan dan didukung metode atau hasil. |
| 4 | “pemeriksaan” | “Pemeriksaan apa? Untuk apa? Kenapa?” | Sebutkan pemeriksaan berkala HAProxy terhadap endpoint `/health`, tujuan penilaian status instance, dan kaitannya dengan keputusan `UP` atau `DOWN`. |
| 5 | “peka” | “Peka?” | Ganti penilaian kualitatif dengan parameter terukur, misalnya nilai `inter` atau `fall` yang relevan, tanpa memperluas kesimpulan di luar skenario uji. |
| 6 | “gangguan sesaat” | “Gangguan apa?” | Definisikan gangguan sesuai simulasi eksperimen. Jangan menggantinya dengan contoh produksi seperti kehabisan memori atau jeda pengumpulan sampah kecuali contoh itu memiliki sumber dan dinyatakan sebagai ilustrasi, bukan kondisi yang diuji. |
| 7 | “banyak” pada pernyataan penelitian terdahulu | “Banyak itu apa? Secara kuantitas atau kualitas?” | Hindari kuantifier tanpa dasar. Sebutkan studi yang dibandingkan dan aspek yang mereka teliti, atau gunakan rumusan terbatas yang dapat dibuktikan oleh tinjauan pustaka. |
| 8 | “mengukur secara khusus” | “Mengapa harus dianggap khusus?” | Rumuskan celah penelitian sebagai perbedaan variabel, parameter, metrik, objek, atau rancangan uji yang dapat dibandingkan dengan studi terdahulu. Hapus kata “khusus” jika tidak menambah makna. |
| 9 | kalimat tujuan penelitian | “Kenapa ini perlu dilakukan?” | Hubungkan tujuan dengan masalah terukur dan celah pustaka. Tujuan tidak boleh berdiri sebagai daftar parameter dan metrik tanpa alasan ilmiah atau praktis. |
| 10 | “pipeline otomasi” | “Tidak ada struktur kalimat bahasa Indonesia demikian” | Gunakan susunan Indonesia yang alami, misalnya “rangkaian proses pengujian yang diotomatisasi”, bila sesuai dengan implementasi. Periksa kembali seluruh frasa terjemahan langsung. |
| 11 | “gaya perancangan” pada definisi *microservice* | “Gaya? Serius? Apa maksudnya?” | Definisikan *microservice* secara konkret sebagai arsitektur aplikasi yang membagi fungsi ke layanan-layanan yang dapat dijalankan secara terpisah. Jangan memakai label abstrak yang tidak menjelaskan struktur sistem. |
| 12 | “analisis klaster ketersediaan tinggi berbasis *heartbeat*” | “Apa ini maksudnya?” | Jelaskan objek, mekanisme *heartbeat*, dan temuan studi yang relevan dengan penelitian ini. Nama topik atau judul singkat tidak cukup sebagai sintesis pustaka. |
| 13 | “kondisi tipikal” pada penjelasan p50 | “Kondisi apa? Yang bagaimana maksudnya?” | Definisikan p50 secara matematis sebagai nilai yang membatasi 50% waktu respons, lalu jelaskan artinya pada permintaan dalam pengujian ini. Hindari kata “tipikal” tanpa populasi atau kondisi yang dirujuk. |
| 14 | “sistem produksi” pada penjelasan p95 | “Sistem produksi apa yang dimaksud?” | Jangan menggeneralisasi ke sistem produksi yang tidak diteliti. Jelaskan p95 pada distribusi waktu respons eksperimen; bila praktik industri dipakai sebagai alasan pemilihan metrik, sertakan sumber yang terverifikasi. |
| 15 | “menyulitkan” pada alasan tidak memilih p70 | “Kalau menyulitkan lantas apa solusinya? Dan kenapa jadi curhat?” | Hapus alasan subjektif. Nyatakan definisi dan alasan pemilihan p50/p95 secara objektif serta berbasis sumber. Tidak perlu membahas p70 atau p100 jika tidak membantu menjawab metode penelitian. |
| 16 | “Docker Compose” pada arsitektur lingkungan uji | “Ip dan desain trafik perlu ditampilkan dan dijelaskan” | Tambahkan alamat IP atau skema pengalamatan yang benar-benar dipakai dan gambar/alur trafik dari k6 ke HAProxy lalu ke instance layanan, termasuk trafik pemeriksaan `/health`. Ambil nilai dari konfigurasi atau hasil inspeksi lingkungan uji; jangan membuat alamat IP, subnet, port, atau arah trafik berdasarkan asumsi. |
| 17 | tanda em dash pada penjelasan `p = 0,3` | “Tidak ada dalam bahasa Indonesia penggunaan em-dash” | Hapus em dash dari naskah Indonesia. Pecah kalimat atau gunakan koma, titik, titik dua, atau tanda kurung sesuai hubungan logisnya. |

## 8. Aturan wajib untuk penulisan revisi berikutnya

Aturan ini berlaku pada setiap perubahan abstrak, isi naskah, tabel, gambar,
caption, dan ringkasan revisi.

1. **Tetapkan referen sebelum menulis.** Setiap penggunaan “layanan”, “instance”,
   “sistem”, “kegagalan”, “pemeriksaan”, atau “gangguan” harus menunjuk ke objek
   yang sudah disebut dan tidak berubah makna di tengah kalimat.
2. **Gunakan definisi operasional eksperimen.** Kegagalan total, kegagalan
   intermiten, status `UP`/`DOWN`, *failover time*, dan transisi status harus
   mengikuti prosedur dan metrik pada metode. Jangan mengganti definisi itu dengan
   pengertian umum dari sistem produksi.
3. **Nyatakan hubungan, bukan hanya urutan kalimat.** Kata “sebaliknya”, “karena”,
   “sehingga”, “menunjukkan”, dan “membuktikan” hanya boleh dipakai bila dua sisi
   hubungan dan bukti pendukungnya jelas. Jika data hanya menunjukkan perbedaan
   atau asosiasi, jangan menulis hubungan sebab-akibat.
4. **Hapus kuantifier dan penilaian samar.** Kata seperti “banyak”, “umum”,
   “khusus”, “peka”, “tipikal”, “tinggi”, “rendah”, “stabil”, dan “signifikan”
   harus memiliki ukuran, pembanding, ambang, hasil uji, atau sumber. Jika tidak,
   ganti dengan uraian faktual atau hapus.
5. **Tulis celah penelitian sebagai perbandingan yang dapat diperiksa.** Sebutkan
   studi, apa yang diukurnya, dan unsur yang belum dicakup. Jangan menyimpulkan
   bahwa sesuatu “belum pernah diteliti” kecuali penelusuran pustaka mendukung
   klaim tersebut.
6. **Gunakan bahasa Indonesia yang alami.** Hindari terjemahan kata per kata dan
   susunan campuran seperti “pipeline otomasi”. Definisikan istilah teknis pada
   penggunaan pertama, gunakan istilah secara konsisten, dan jangan memakai em
   dash dalam naskah Indonesia.
7. **Jelaskan metrik dalam konteks data penelitian.** Definisi p50, p95, *error
   rate*, *throughput*, dan *failover time* harus menyebut populasi pengukuran,
   satuan, jendela waktu, dan cara baca yang relevan. Alasan pemilihan metrik yang
   berasal dari praktik atau literatur harus mempunyai sitasi terverifikasi.
8. **Turunkan arsitektur dari artefak nyata.** IP, subnet, port, nama container,
   arah trafik, endpoint, dan urutan proses harus disalin atau dihitung dari
   `docker-compose`, konfigurasi HAProxy, skrip uji, log, atau hasil inspeksi yang
   tersedia. Jika artefaknya tidak tersedia, tandai informasi sebagai belum
   terverifikasi dan jangan mengisinya dengan perkiraan.
9. **Pertahankan konteks angka.** Setiap angka harus tetap memiliki metrik,
   satuan, skenario, jumlah pengulangan, dan pembandingnya. Pembulatan tidak boleh
   mengubah interpretasi; aturan pecahan harus diputuskan dan diterapkan secara
   konsisten.
10. **Pisahkan fakta, interpretasi, dan rekomendasi.** Fakta berasal dari data atau
    sumber. Interpretasi harus menyebut dasar faktanya. Rekomendasi harus dibatasi
    pada kondisi yang diuji atau secara jelas dinyatakan memerlukan validasi
    lanjutan.
11. **Periksa konsistensi lintasbagian setelah setiap perubahan.** Cocokkan
    abstrak, metode, tabel/gambar, hasil, pembahasan, kesimpulan, dan daftar
    pustaka. Perubahan istilah, angka, atau ruang lingkup pada satu bagian harus
    diperiksa pada semua bagian yang mengulang klaim tersebut.
12. **Jangan menutup celah sumber dengan kalimat yang terdengar meyakinkan.** Jika
    konfigurasi, log, data mentah, atau referensi belum dapat diperiksa, tulis
    statusnya dalam catatan revisi dan tunda klaim tersebut sampai bukti tersedia.

### Pemeriksaan konteks sebelum sebuah kalimat dimasukkan

Sebelum menambahkan atau mengubah kalimat, jawab lima pertanyaan berikut:

1. Objek spesifik apa yang dibicarakan?
2. Istilah dan kondisi apa yang harus didefinisikan agar kalimat tidak ambigu?
3. Data, artefak, atau sumber mana yang mendukung setiap klaim?
4. Apakah kata penghubung menyatakan hubungan yang benar-benar dibuktikan?
5. Bagian lain mana yang harus diselaraskan agar konteksnya tetap konsisten?

Jika salah satu jawaban belum tersedia, jangan mengarang isinya. Pertahankan
ketidakpastian secara eksplisit atau catat sebagai pekerjaan yang masih terbuka.

## Kondisi selesai

Revisi mentoring ini dapat dinyatakan selesai bila abstrak dapat menjawab, tanpa
memerlukan penjelasan tambahan: masalah apa yang penting, posisi *load balancer*
di sistem, celah penelitian sebelumnya, apa yang diteliti dan bagaimana caranya,
temuan utama, serta arti temuannya. Selain itu, setiap referensi harus dapat
ditelusuri dan berada dalam rentang 2021-2026, sementara bahasa serta formatnya
konsisten dengan pedoman jurnal Indonesia yang dipakai. Semua 18 komentar pada
berkas ulasan terbaru juga harus dapat ditutup dengan perubahan yang dapat
ditelusuri ke naskah atau dengan keputusan pembimbing yang terdokumentasi.
