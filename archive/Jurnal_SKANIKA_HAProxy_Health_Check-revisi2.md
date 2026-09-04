<!--
REVISED MANUSCRIPT — draft revisi 1
Sumber: Jurnal_SKANIKA_HAProxy_Health_Check-reviewed BIMO.docx
Semua perubahan menanggapi 14 komentar pembimbing (Agustinus Gumelar, 2026-08-31)
ditandai inline dengan komentar <!-- REVISI #n: ... -->
Nilai hasil pada bagian utama dipertahankan; abstrak memakai pembulatan pada angka
headline agar ringkas sesuai arahan mentoring 2026-09-04. Nilai presisi tetap
tersedia pada tabel dan bagian hasil.
-->

# Pengaruh Parameter *Health Check* HAProxy terhadap *Failover Time* dan Kinerja Layanan *Microservice* Berbasis Docker

Christianto Elvern Haryanto^1\*, [Nama Dosen Pembimbing]^2

^1,2 Fakultas Teknologi Informasi, Program Studi Informatika, Universitas Ciputra Surabaya, Surabaya, Indonesia

E-mail: ^1\*[email penulis 1], ^2[email pembimbing]  (\* : corresponding author)

---

## Abstrak

<!-- REVISI MENTORING 2026-09-04: abstrak disusun ulang dengan pola latar belakang–tujuan–metode–temuan–signifikansi; posisi load balancer dan kesimpulan dibuat eksplisit. -->

Keterlambatan mengenali layanan yang gagal dapat membuat permintaan pengguna tetap diarahkan ke layanan yang tidak dapat merespons. Sebaliknya, pemeriksaan yang terlalu peka dapat menandai gangguan sesaat sebagai kegagalan dan membuat status layanan berubah berulang kali. Dalam arsitektur *microservice*, *load balancer* berada di antara klien dan *instance* layanan untuk menerima trafik lalu meneruskannya ke *instance* yang dapat melayani. Penelitian terdahulu banyak membahas perangkat lunak dan algoritma pembagian trafik, tetapi belum mengukur secara khusus dampak parameter pemeriksaan berkala HAProxy. Penelitian ini menguji pengaruh parameter *inter*, *fall*, dan *rise* terhadap *failover time*, *throughput*, latensi, dan *error rate* pada *microservice* berbasis Docker. Sebelas skenario diuji lima kali dengan 200 pengguna virtual melalui *pipeline* otomasi, setelah pemeriksaan kesiapan dan *pilot study*. Uji Kruskal–Wallis menunjukkan perbedaan signifikan pada metrik kinerja, sedangkan *failover time* berkisar 297 hingga 23668 ms. Pada kegagalan intermiten, *fall* = 1 menghasilkan sekitar 39 transisi status per pengujian, sedangkan *fall* = 5 menghasilkan kurang dari satu transisi; deteksi yang lebih cepat meningkatkan *throughput* hingga sekitar 18% tetapi mengurangi kestabilan status. Dengan demikian, nilai *fall* harus dipilih berdasarkan jenis kegagalan yang paling mungkin terjadi pada sistem sasaran.

**Kata kunci:** failover time, HAProxy, health check, load balancer, microservice

---

## Abstract

<!-- REVISI MENTORING 2026-09-04: English abstract aligned to the revised Indonesian structure and rounded headline values. -->

Delayed recognition of a failed service can keep sending user requests to an instance that cannot respond. Conversely, an overly sensitive check can treat a temporary disturbance as failure and cause repeated status changes. In a microservice architecture, the *load balancer* sits between clients and service instances, receiving traffic and forwarding it to an available instance. Previous studies have mainly examined load-balancer software and traffic-distribution algorithms, leaving the specific effects of HAProxy's periodic-check parameters insufficiently measured. This study examines the effects of *inter*, *fall*, and *rise* on *failover time*, *throughput*, latency, and *error rate* in a Docker-based microservice system. Eleven scenarios were tested five times with 200 virtual users through an automated pipeline, after a readiness check and *pilot study*. The Kruskal–Wallis test found significant performance differences, while measured *failover time* ranged from 297 to 23668 ms. Under intermittent failure, *fall* = 1 produced about 39 status transitions per run, whereas *fall* = 5 produced fewer than one; faster detection increased *throughput* by up to about 18% but reduced status stability. Therefore, the *fall* value should be selected according to the failure characteristics most likely to occur in the target system.

**Keywords:** failover time, HAProxy, health check, load balancer, microservice

---

## 1. PENDAHULUAN

Arsitektur *microservice*, yaitu gaya perancangan yang memecah satu aplikasi menjadi banyak layanan kecil yang berdiri sendiri, telah menjadi pilihan umum bagi sistem yang menuntut ketersediaan tinggi. Layanan tersebut umumnya dijalankan di dalam *container*, yaitu paket berisi aplikasi beserta seluruh kebutuhan jalannya, sehingga setiap layanan dapat direplikasi, diganti, dan diskalakan secara independen. Pada arsitektur tersebut, *load balancer* ditempatkan di antara klien dan sekumpulan salinan layanan yang identik (*instance*). Alur permintaan menjadi sederhana: permintaan klien diterima *load balancer* lebih dahulu, lalu diteruskan ke salah satu *instance* yang dinilai masih laik-layan, yaitu masih mampu memproses permintaan dengan benar. <!-- REVISI #1: "instance yang dinilai masih sehat" -> "instance yang dinilai masih laik-layan, yaitu masih mampu memproses permintaan dengan benar" (definisi istilah pada penggunaan pertama). --> Karena posisinya itu, *load balancer* tidak hanya membagi beban, tetapi juga menentukan *instance* mana yang masih layak menerima permintaan. Penelitian mengenai arsitektur *microservice* dengan mekanisme toleransi kegagalan berbasis Docker menunjukkan bahwa penerapan ketersediaan tinggi berlapis mampu memperbaiki kualitas layanan sekitar 20% dibanding arsitektur monolitik, dengan waktu pemulihan di bawah lima detik [20]. Penelitian lain mengusulkan metode kendali ketersediaan tinggi pada aplikasi *microservice* berbasis *container* yang tersebar pada beberapa klaster untuk mempersingkat waktu pemulihan layanan [12]. Penelitian mengenai pengalihan trafik yang tertib pada layanan penyimpan data (*stateful*) menunjukkan bahwa proses pengalihan itu sendiri dapat dirancang agar tidak merugikan klien [9]. Pada konteks lokal, analisis klaster ketersediaan tinggi berbasis *heartbeat* [6] serta perbandingan waktu respons dan *failover* antara Kubernetes dan Docker Swarm [18] memperlihatkan bahwa mekanisme deteksi yang dipakai berpengaruh terhadap perilaku pengalihan layanan.

HAProxy merupakan salah satu *load balancer* perangkat lunak yang banyak digunakan pada lingkungan tersebut, baik sebagai penyeimbang beban mandiri maupun sebagai penyalur trafik masuk ke klaster orkestrasi [10]. Pengujian perbandingan pada server *e-learning* menunjukkan HAProxy menghasilkan *response time* 585 ms dan *throughput* 896,48 Kb/s, lebih baik dibanding Nginx yang menghasilkan 1180,58 ms dan 848,52 Kb/s pada uji koneksi yang sama [14]. Penelitian mengenai perbandingan algoritma *round robin* dan *least connection* pada HAProxy juga menunjukkan bahwa pemilihan algoritma distribusi berpengaruh terhadap kinerja server web [8]. Kajian sejenis pada *ingress controller* memperlihatkan bahwa perbedaan algoritma *load balancing* berdampak pada efisiensi dan kinerja sistem terkontainer [7], sedangkan penelitian pada infrastruktur *on-premise* dan komputasi awan memperlihatkan pengaruh penerapan *load balancer* terhadap kinerja layanan web organisasi [16].

Namun demikian, seluruh penelitian tersebut berfokus pada algoritma distribusi trafik dan bukan pada mekanisme yang menentukan kapan sebuah *instance* dinyatakan gagal. Pada HAProxy, keputusan tersebut dikendalikan oleh *health check* (pemeriksaan berkala kelaikan layanan), yaitu pemeriksaan berkala yang dikirim *load balancer* ke setiap *instance* untuk menilai kelaikannya menerima trafik. <!-- REVISI #1: glosari "health check" ditambahkan pada penggunaan pertama; "menilai kesehatannya" -> "menilai kelaikannya menerima trafik". --> Pemeriksaan itu diatur oleh tiga parameter. Parameter *inter* menetapkan selang waktu antar pemeriksaan. Parameter *fall* menetapkan jumlah pemeriksaan gagal berturut-turut sebelum sebuah *instance* ditandai DOWN, yaitu dicoret dari daftar penerima trafik. Parameter *rise* menetapkan jumlah pemeriksaan berhasil berturut-turut sebelum *instance* itu dinyatakan pulih. Manual konfigurasi resmi HAProxy mendefinisikan ketiga parameter tersebut beserta nilai bawaannya, yaitu *inter* 2000 ms, *fall* 3, dan *rise* 2, tetapi tidak memuat panduan pemilihan nilai maupun besaran akibat dari setiap pilihan [5]. Laporan teknis mengenai penyetelan HAProxy telah membandingkan berbagai metode *load balancing* pada beragam intensitas beban dan komposisi *backend*, tetapi evaluasinya tidak mencakup parameter *health check* dan tidak melaporkan *failover time* sebagai metrik [13]. Dengan demikian terdapat celah antara panduan konfigurasi yang tersedia dan bukti empiris mengenai konsekuensi pemilihan nilai parameter tersebut.

Celah tersebut menjadi relevan karena pemeriksaan berkala secara inheren mengandung kompromi. Penelitian mengenai pemantauan container pada Kubernetes menunjukkan bahwa pendekatan berbasis pemeriksaan berkala memerlukan penyetelan yang cermat, berpotensi menurunkan ketersediaan, dan lambat mendeteksi perubahan status. Pendekatan berbasis sinyal yang diusulkan pada penelitian tersebut mendeteksi kegagalan container 86% lebih cepat tanpa memerlukan penyetelan interval, sekaligus mencatat bahwa pemeriksaan berkala dapat salah menyimpulkan kegagalan dan menurunkan ketersediaan layanan sebesar 4% [15]. Kompromi antara kecepatan deteksi dan tingkat kesalahan penilaian status juga menjadi persoalan pokok pada perancangan pendeteksi kegagalan berbasis heartbeat, yang terus dikembangkan agar waktu deteksi dapat dipersingkat tanpa menaikkan laju kesalahan [2]. Pola serupa muncul pada penetapan nilai timeout komunikasi antar microservice: nilai yang terlalu pendek menekan latensi tetapi menaikkan laju kegagalan, sehingga diperlukan penetapan yang adaptif terhadap beban [4]. Pada HAProxy, kompromi tersebut melekat pada parameter fall. Nilai fall yang kecil mempercepat deteksi kegagalan, tetapi membuat sistem lebih mudah bereaksi terhadap gangguan sesaat sehingga status instance berubah naik turun berulang kali (flapping). Besaran kedua sisi kompromi tersebut belum pernah diukur.

Pengujian empiris terhadap kinerja jaringan dan layanan berbasis eksperimen terkendali telah menjadi praktik yang lazim, misalnya pada evaluasi dampak mekanisme enkripsi terhadap kinerja jaringan nirkabel [17] maupun pada analisis ketersediaan dan keamanan layanan berbasis web [19]. Pada ranah sistem terkontainer, evaluasi kinerja perangkat orkestrasi container menegaskan pentingnya lingkungan uji yang terkendali dan metrik yang terdefinisi jelas [3], sementara penelitian mengenai sistem resiliensi pada arsitektur microservice menekankan perlunya faktor toleransi kegagalan yang terukur [11]. Metodologi pengujian beban dengan alat load testing juga telah digunakan untuk menilai kapasitas server dan efisiensi respons layanan web [1].

Berdasarkan kondisi tersebut, penelitian ini mengukur secara empiris pengaruh parameter inter, fall, dan rise pada HAProxy terhadap failover time, throughput, latensi, dan error rate dalam sistem microservice berbasis Docker. Kontribusi penelitian ini ada tiga. Pertama, kuantifikasi failover time terhadap kombinasi parameter health check, yang belum dilakukan pada penelitian penyetelan HAProxy sebelumnya [13]. Kedua, pengukuran empiris fenomena flapping akibat nilai fall rendah pada kondisi kegagalan intermiten, sehingga kompromi yang selama ini hanya dibahas secara kualitatif memperoleh dukungan angka. Ketiga, perbandingan sistematis antara failover time empiris dan nilai teoretis inter × fall beserta analisis sumber deviasinya. Penelitian ini juga melengkapi penelitian failover lokal terdahulu yang umumnya berhenti pada verifikasi fungsional bahwa layanan tetap berjalan ketika satu server mati [18].

<!-- REVISI #2: paragraf sistematika penulisan ditambahkan sebagai paragraf terakhir Bagian 1. -->
Sisa artikel ini disusun sebagai berikut. Bagian 2 memaparkan metode penelitian, mencakup arsitektur lingkungan pengujian, skenario konfigurasi parameter health check, prosedur pengukuran failover time, pipeline otomasi, gerbang validasi pilot study, serta teknik analisis data. Bagian 3 menyajikan hasil dan pembahasan, meliputi hasil pilot study, statistik deskriptif, uji signifikansi statistik, perbandingan failover time empiris terhadap nilai teoretis, kuantifikasi trade-off nilai fall rendah terhadap flapping, rekomendasi konfigurasi berbasis data, dan keterbatasan penelitian. Bagian 4 memuat kesimpulan serta saran untuk penelitian selanjutnya.

---

## 2. METODE PENELITIAN

Penelitian menggunakan pendekatan eksperimen kuantitatif dengan variabel bebas berupa nilai parameter *health check* HAProxy dan variabel terikat berupa *failover time*, *throughput*, latensi p50, latensi p95, serta *error rate*. Variabel kontrol mencakup jumlah *instance* layanan, alokasi sumber daya *container*, jumlah *virtual user*, durasi pengujian, serta waktu injeksi kegagalan.

<!-- REVISI #8: definisi dan justifikasi persentil latensi ditambahkan pada paragraf yang memperkenalkan variabel terikat. -->
Latensi dilaporkan pada dua titik persentil. Latensi p50 (persentil ke-50, setara median) menggambarkan pengalaman pengguna pada kondisi tipikal; latensi p95 (persentil ke-95) menggambarkan ekor distribusi, yaitu 5% permintaan paling lambat, dan merupakan titik yang lazim dijadikan acuan *Service Level Objective* pada sistem produksi. Persentil ke-100 (nilai maksimum tunggal) tidak dipakai karena sangat sensitif terhadap satu *outlier* dan tidak stabil antar pengulangan, sedangkan persentil seperti p70 tidak lazim digunakan sebagai acuan pelaporan sehingga menyulitkan pembandingan dengan penelitian lain.

### 2.1. Arsitektur Lingkungan Pengujian

Lingkungan pengujian dibangun menggunakan Docker Compose dan terdiri atas satu *container* HAProxy, tiga *container* layanan yang identik, serta satu *container load tester*. Seluruh komponen ditempatkan pada jaringan Docker yang sama sehingga jalur komunikasi antara *load tester*, *load balancer*, dan *instance* layanan tidak melewati lapisan *port forwarding* pada host. Arsitektur lingkungan pengujian ditunjukkan pada Gambar 1.

![Gambar 1](../[Gambar 1 — lihat berkas media DOCX: word/media/image1.png])

**Gambar 1.** Arsitektur lingkungan pengujian berbasis Docker

Layanan yang diuji merupakan aplikasi Node.js sederhana dengan dua *endpoint*, yaitu `/api` yang mensimulasikan pekerjaan bisnis selama kurang lebih 5 ms dan `/health` yang digunakan HAProxy sebagai target *health check* untuk menilai kelaikan *instance*. <!-- REVISI #1: "target pemeriksaan ... menilai kesehatannya" -> "target health check untuk menilai kelaikan instance". --> *Endpoint* `/health` dapat dikonfigurasi untuk mengembalikan respons tidak laik secara probabilistik guna mensimulasikan kegagalan intermiten. <!-- REVISI #1: "respons tidak sehat" -> "respons tidak laik". --> Spesifikasi platform implementasi disajikan pada Tabel 1.

**Tabel 1.** Spesifikasi platform implementasi

| No | Komponen | Spesifikasi |
|---|---|---|
| 1 | Perangkat | Apple MacBook Pro (Apple M5, arsitektur ARM64) |
| 2 | CPU | 10-core |
| 3 | RAM | 24 GB unified memory |
| 4 | Penyimpanan | 1 TB SSD |
| 5 | Sistem operasi host | macOS |
| 6 | Runtime container | Docker Desktop for Mac, alokasi tetap 8 CPU dan 16 GB RAM |
| 7 | Load balancer | HAProxy, mode HTTP, algoritma roundrobin |
| 8 | Load tester | k6, executor constant-vus, 200 virtual users |

Docker Desktop pada macOS menjalankan seluruh container di dalam virtual machine Linux, bukan langsung pada kernel host. Untuk menjaga konsistensi antar skenario, alokasi sumber daya virtual machine ditetapkan secara eksplisit dan tidak diubah selama seluruh rangkaian eksperimen. Seluruh image container yang digunakan merupakan image ARM64 native untuk menghindari overhead emulasi, dan aplikasi lain pada host ditutup selama pengujian berlangsung.

### 2.2. Skenario Pengujian

Sebelas skenario konfigurasi diuji sebagaimana disajikan pada Tabel 2. Sembilan skenario pertama menguji kegagalan total, sedangkan dua skenario terakhir menguji kegagalan intermiten dengan probabilitas kegagalan *health check* p = 0,3 per pemeriksaan. Setiap skenario diulang lima kali sehingga total pengujian berjumlah 55 kali.

<!-- REVISI #3: definisi dan alasan pemilihan p = 0,3 ditambahkan sebelum Tabel 2. -->
Pada dua skenario terakhir, kegagalan intermiten disimulasikan dengan mengatur *endpoint* `/health` agar mengembalikan status tidak laik secara acak dengan probabilitas p = 0,3 pada setiap pemeriksaan *health check* (bukan *crash* proses). Nilai p = 0,3 dipilih sebagai representasi kegagalan intermiten tingkat sedang — cukup sering untuk memicu perubahan status berulang pada nilai *fall* rendah, namun tidak menyerupai kegagalan total — dan dijaga konstan pada seluruh pengulangan kedua skenario tersebut.

**Tabel 2.** Skenario konfigurasi parameter health check

| No | Skenario | inter (ms) | fall | rise | Jenis kegagalan |
|---|---|---|---|---|---|
| 1 | baseline | 2000 | 3 | 2 | Total (crash) |
| 2 | inter_500 | 500 | 3 | 2 | Total (crash) |
| 3 | inter_5000 | 5000 | 3 | 2 | Total (crash) |
| 4 | fall_1 | 2000 | 1 | 2 | Total (crash) |
| 5 | fall_5 | 2000 | 5 | 2 | Total (crash) |
| 6 | rise_1 | 2000 | 3 | 1 | Total (crash) |
| 7 | rise_5 | 2000 | 3 | 5 | Total (crash) |
| 8 | agresif | 500 | 1 | 1 | Total (crash) |
| 9 | konservatif | 5000 | 5 | 5 | Total (crash) |
| 10 | flap_fall1 | 2000 | 1 | 2 | Intermiten (p_gagal = 0,3 per check) |
| 11 | flap_fall5 | 2000 | 5 | 2 | Intermiten (p_gagal = 0,3 per check) |

<!-- REVISI #3: sel "Intermiten (gagal 30%)" pada baris 10 & 11 diganti "Intermiten (p_gagal = 0,3 per check)". -->

### 2.3. Prosedur Pengujian dan Pengukuran Failover Time

Setiap pengulangan mengikuti urutan yang sama. Konfigurasi HAProxy dibangkitkan dari templat sesuai nilai parameter skenario, seluruh stack container dibangun ulang, kemudian sistem dibiarkan menghangat selama 15 detik. Load test dijalankan selama 120 detik dengan 200 virtual user. Pada detik ke-30 satu dari tiga instance dihentikan menggunakan perintah `docker kill`, dan pada detik ke-90 instance tersebut dipulihkan. Perintah `docker kill` dipilih dibanding `docker stop` karena `docker stop` mengirim sinyal SIGTERM dengan tenggang waktu sehingga layanan masih dapat merespons pemeriksaan health check selama periode tersebut dan mengaburkan titik awal kegagalan.

Failover time diukur sebagai selisih dua timestamp yang keduanya bersumber dari clock Docker daemon yang sama untuk menghindari clock skew antara sistem operasi host dan virtual machine tempat Docker Engine berjalan. Timestamp pertama adalah waktu berhentinya container yang diperoleh dari atribut `State.FinishedAt` melalui perintah `docker inspect`. Timestamp kedua adalah waktu HAProxy menandai instance sebagai tidak laik (DOWN), yang diperoleh dari baris log berpola `"Server ... is DOWN"` pada keluaran `docker logs -t`. <!-- REVISI #1: "menandai instance sebagai tidak sehat" -> "menandai instance sebagai tidak laik (DOWN)". --> Nilai teoretis failover time dihitung menggunakan Persamaan (1).

$$t_\text{teoretis} = inter \times fall \qquad (1)$$

Karena titik kegagalan instance terjadi acak di dalam siklus pemeriksaan, failover time empiris diprediksi berada pada rentang yang dinyatakan Persamaan (2), dengan `t_ovh` merupakan overhead deteksi berupa durasi pemeriksaan itu sendiri.

$$inter \times (fall - 1) \le t_\text{empiris} \le inter \times fall + t_\text{ovh} \qquad (2)$$

Pada skenario kegagalan intermiten, failover time tidak dapat didefinisikan karena tidak terdapat titik kegagalan tunggal. Metrik yang dicatat pada kedua skenario tersebut adalah frekuensi transisi status instance, yaitu jumlah perpindahan status UP dan DOWN yang terekstraksi dari log HAProxy selama satu pengujian.

### 2.4. Pipeline Otomasi

Seluruh tahapan dijalankan oleh skrip otomasi tanpa intervensi manual, mencakup substitusi konfigurasi HAProxy, pembangunan ulang stack container, eksekusi load test, injeksi kegagalan, pemulihan instance, ekstraksi metrik dari ringkasan load tester dan log HAProxy, hingga penyimpanan hasil ke berkas CSV. Alur satu pengulangan disajikan pada Algoritma 1. <!-- REVISI #4: rujukan ke Algoritma 1 ditambahkan. --> Otomasi penuh diperlukan agar ke-55 pengujian (11 skenario × 5 pengulangan, lihat Subbab 2.2) dijalankan dengan prosedur yang identik sehingga variasi hasil tidak bersumber dari perbedaan perlakuan antar pengulangan. <!-- REVISI #5: "55 pengujian" -> "ke-55 pengujian (11 skenario × 5 pengulangan, lihat Subbab 2.2)". --> Skrip otomasi lengkap beserta konfigurasi Docker Compose, templat HAProxy, skrip k6, skrip analisis statistik, dan berkas data mentah akan diarsipkan terbuka sebelum naskah dikirimkan.

<!-- REVISI #4: blok Algoritma 1 ditambahkan. -->
```
Algoritma 1. Pipeline otomasi untuk satu pengulangan
Masukan : skenario s = (inter, fall, rise, jenis_kegagalan); indeks pengulangan r
Keluaran: satu baris metrik pada results.csv

1  render haproxy.cfg dari templat dengan nilai (inter, fall, rise, timeout = 100 ms)
2  docker compose down -v ; docker compose up -d --build          # bangun ulang stack
3  tunggu 15 detik                                                 # warm-up
4  jalankan k6 (constant-vus, 200 VU, 120 s) secara asynchronous
5  pada t = 30 s : docker kill service3                            # injeksi kegagalan
6  pada t = 90 s : docker start service3                           # pemulihan
7  tunggu proses k6 selesai
8  kill_ts  <- docker inspect -f '{{.State.FinishedAt}}' service3
9  down_ts  <- timestamp baris "is DOWN" pertama dari: docker logs -t haproxy
10 failover_ms <- (down_ts - kill_ts) dalam milidetik
11 (throughput, p50, p95, error_rate) <- parse ringkasan JSON k6
12 jika jenis_kegagalan = intermiten :
       transisi   <- jumlah perpindahan UP<->DOWN dari docker logs haproxy
       failover_ms <- N/A
13 tambahkan baris (s, r, throughput, p50, p95, error_rate, failover_ms, transisi)
   ke results.csv
```

### 2.5. Pilot Study sebagai Gerbang Validasi

<!-- REVISI #9: langkah "pemeriksaan kesiapan pipeline (uji asap)" diperkenalkan di Metode. -->
Sebelum pilot study, dilakukan pemeriksaan kesiapan pipeline (uji asap) untuk memastikan seluruh tahap otomasi berjalan penuh dan setiap metrik dapat diekstraksi; temuan pada tahap ini dilaporkan pada Subbab 3.1.

Pilot study dilaksanakan sebagai gerbang validasi sebelum pengujian utama menggunakan konfigurasi baseline dengan tiga pengulangan. Pengujian utama hanya dilaksanakan apabila kelima kriteria berikut terpenuhi: (1) failover time dapat diekstraksi dari log pada seluruh pengulangan; (2) selisih failover time antar pengulangan tidak melebihi satu kali nilai inter; (3) penggunaan CPU container load tester berada di bawah 80% sehingga load tester tidak menjadi bottleneck; (4) error terkonsentrasi di sekitar periode kegagalan, bukan tersebar sepanjang pengujian; dan (5) pipeline otomasi berjalan penuh tanpa intervensi manual.

### 2.6. Teknik Analisis Data

Data dianalisis menggunakan statistik deskriptif berupa rata-rata dan standar deviasi per skenario. Karena setiap skenario diulang lima kali dan distribusi metrik kinerja tidak dapat diasumsikan normal, uji signifikansi menggunakan uji Kruskal-Wallis pada taraf signifikansi α = 0,05, dilanjutkan uji post-hoc Dunn dengan koreksi Bonferroni apabila ditemukan perbedaan signifikan. Besaran praktis perbedaan dilaporkan menggunakan effect size epsilon-squared (ε²). Selain itu, failover time empiris dibandingkan terhadap nilai teoretis pada Persamaan (1) untuk menganalisis besaran dan sumber deviasi.

---

## 3. HASIL DAN PEMBAHASAN

### 3.1. Hasil Pilot Study

Seluruh kriteria gerbang validasi terpenuhi. Failover time berhasil diekstraksi pada ketiga pengulangan dengan nilai 4512 ms, 4521 ms, dan 4531 ms, sehingga selisih maksimum antar pengulangan hanya 19 ms atau jauh di bawah ambang satu kali nilai inter sebesar 2000 ms; kriteria 1 dan 2 dengan demikian terpenuhi. Ketiga nilai tersebut berada dalam rentang prediksi Persamaan (2). Penggunaan CPU container load tester sepanjang pengujian tetap berada di bawah ambang 80%, sedangkan throughput stabil pada kisaran 3362 sampai 3386 request per detik dengan latensi median 6,4 sampai 6,7 ms. <!-- REVISI #6: interpretasi angka terhadap kriteria gerbang validasi ditambahkan (lanjutan paragraf). Angka spesifik puncak CPU load tester dihilangkan; hanya kepatuhan terhadap ambang 80% yang dinyatakan. --> Angka-angka tersebut dibaca terhadap kelima kriteria gerbang validasi pada Subbab 2.5: penggunaan CPU load tester yang tidak melampaui ambang 80% memastikan load tester bukan menjadi bottleneck (kriteria 3); throughput yang stabil pada 3362–3386 req/s dan latensi median 6,4–6,7 ms antar ketiga pengulangan menunjukkan lingkungan uji berperilaku konsisten, sejalan dengan kriteria 2 tentang keterulangan hasil. <!-- REVISI #7: kalimat error rate ditulis ulang dan dikaitkan ke kriteria 4. --> Error rate berkisar 0,102–0,112% dan seluruhnya terkonsentrasi pada jendela waktu antara instance dimatikan hingga HAProxy menandainya DOWN, bukan tersebar sepanjang 120 detik pengujian; pola ini memenuhi kriteria 4, yaitu error merupakan konsekuensi langsung dari kegagalan yang diinjeksikan dan bukan gejala ketidakstabilan lingkungan uji. Dengan seluruh kriteria pada Subbab 2.5 terpenuhi — termasuk kriteria 5 karena pipeline berjalan tanpa intervensi manual — pengujian utama dilanjutkan. Ringkasan hasil pilot study disajikan pada Tabel 3.

**Tabel 3.** Hasil pilot study pada konfigurasi baseline (inter = 2000 ms, fall = 3, rise = 2)

| Rep | Throughput (req/s) | Latensi p50 (ms) | Latensi p95 (ms) | Error rate (%) | Failover time (ms) |
|---|---|---|---|---|---|
| 1 | 3386,35 | 6,43 | 8,75 | 0,102 | 4512 |
| 2 | 3362,47 | 6,70 | 9,61 | 0,112 | 4521 |
| 3 | 3365,83 | 6,67 | 9,42 | 0,102 | 4531 |

<!-- REVISI #9: "Pada tahap validasi pra-pilot ditemukan bahwa" -> "Pada pemeriksaan kesiapan pipeline sebelum pilot study ditemukan bahwa". -->
Pada pemeriksaan kesiapan pipeline sebelum pilot study ditemukan bahwa nilai bawaan timeout connect HAProxy sebesar 2 detik menyebabkan setiap pemeriksaan health check yang gagal ikut menunggu penuh durasi timeout tersebut alih-alih gagal seketika, sehingga failover time terukur mencapai dua kali lipat nilai teoretis. Setelah timeout connect dan timeout check diturunkan menjadi 100 ms, nilai yang aman karena seluruh komunikasi terjadi dalam jaringan Docker internal dengan latensi milidetik, failover time kembali sesuai rentang teoretis. Temuan ini menunjukkan bahwa parameter timeout perlu diperlakukan sebagai bagian dari konfigurasi health check, bukan sebagai pengaturan terpisah.

### 3.2. Statistik Deskriptif

Tabel 4 merangkum rata-rata dan standar deviasi kelima metrik pada sebelas skenario dengan lima pengulangan per skenario. Nilai failover time pada dua skenario flapping tidak tersedia karena skenario tersebut tidak melibatkan kegagalan total yang dapat diukur waktu deteksinya.

**Tabel 4.** Statistik deskriptif per skenario (rata-rata ± standar deviasi, n = 5)

| Skenario | Throughput (req/s) | Latensi p50 (ms) | Latensi p95 (ms) | Error rate (%) | Failover (ms) |
|---|---|---|---|---|---|
| baseline | 3362,5 ± 23,5 | 6,69 ± 0,24 | 9,55 ± 0,80 | 0,11 ± 0,00 | 4516,0 ± 23,0 |
| inter_500 | 3428,8 ± 15,3 | 6,68 ± 0,20 | 9,38 ± 0,64 | 0,04 ± 0,00 | 1607,8 ± 196,3 |
| inter_5000 | 3146,5 ± 8,5 | 6,90 ± 0,07 | 10,60 ± 0,40 | 0,34 ± 0,01 | 13457,2 ± 12,8 |
| fall_1 | 3453,1 ± 24,4 | 6,70 ± 0,25 | 9,50 ± 0,83 | 0,00 ± 0,00 | 297,0 ± 24,3 |
| fall_5 | 3253,6 ± 26,8 | 6,83 ± 0,27 | 10,41 ± 0,95 | 0,21 ± 0,01 | 8715,0 ± 20,8 |
| rise_1 | 3304,5 ± 19,7 | 7,22 ± 0,23 | 11,69 ± 0,52 | 0,11 ± 0,01 | 4526,4 ± 15,5 |
| rise_5 | 3338,4 ± 14,7 | 6,91 ± 0,12 | 10,52 ± 0,63 | 0,11 ± 0,00 | 4531,8 ± 8,4 |
| agresif | 3440,1 ± 7,2 | 6,86 ± 0,11 | 9,93 ± 0,25 | 0,01 ± 0,00 | 320,2 ± 214,7 |
| konservatif | 2946,5 ± 10,5 | 6,65 ± 0,13 | 9,95 ± 0,52 | 0,63 ± 0,01 | 23668,0 ± 18,2 |
| flap_fall1 | 3470,6 ± 13,4 | 6,57 ± 0,14 | 9,36 ± 0,52 | 0,00 ± 0,00 | – |
| flap_fall5 | 3474,9 ± 12,4 | 6,53 ± 0,10 | 9,22 ± 0,52 | 0,00 ± 0,00 | – |

Terdapat hubungan yang konsisten antara kecepatan deteksi dan dampak kegagalan terhadap pengguna. Skenario konservatif menghasilkan throughput terendah sebesar 2946,5 req/s dengan error rate tertinggi sebesar 0,63%, sedangkan skenario dengan deteksi cepat seperti fall_1 dan agresif mempertahankan throughput di atas 3440 req/s dengan error rate mendekati nol. Selisih throughput antara konfigurasi tercepat dan terlambat mencapai sekitar 17,9%. Perbedaan ini bersumber dari lamanya periode ketika load balancer masih mengarahkan trafik ke instance yang sudah mati, sehingga semakin lambat deteksi, semakin banyak permintaan yang gagal. Perbandingan throughput dan failover time antar skenario ditunjukkan pada Gambar 2 dan Gambar 3.

![Gambar 2](../[Gambar 2 — lihat berkas media DOCX: word/media/image2.png])

**Gambar 2.** Perbandingan throughput antar skenario (rata-rata ± standar deviasi)

![Gambar 3](../[Gambar 3 — lihat berkas media DOCX: word/media/image3.png])

**Gambar 3.** Perbandingan failover time antar skenario (rata-rata ± standar deviasi)

### 3.3. Uji Signifikansi Statistik

Hasil uji Kruskal-Wallis pada kelima metrik disajikan pada Tabel 5. Seluruh metrik menunjukkan perbedaan yang signifikan antar skenario pada taraf α = 0,05.

**Tabel 5.** Hasil uji Kruskal-Wallis antar sebelas skenario

| Metrik | H | p-value | ε² | Kesimpulan |
|---|---|---|---|---|
| Throughput | 51,62 | <0,001 | 0,946 | Signifikan |
| Latensi p50 | 29,63 | 0,00098 | 0,446 | Signifikan |
| Latensi p95 | 30,95 | 0,00060 | 0,476 | Signifikan |
| Error rate | 52,78 | <0,001 | 0,972 | Signifikan |
| Failover time | 41,80 | <0,001 | 0,939 | Signifikan |

Effect size yang besar pada throughput, error rate, dan failover time (ε² > 0,9) menunjukkan bahwa pemilihan parameter health check bukan sekadar berpengaruh secara statistik, melainkan juga substansial secara praktis. Sebaliknya, effect size pada latensi p50 dan p95 tergolong sedang, yang menunjukkan bahwa parameter health check lebih banyak mempengaruhi ketersediaan layanan dibanding kecepatan respons permintaan yang berhasil dilayani.

Uji post-hoc Dunn dengan koreksi Bonferroni pada failover time menunjukkan bahwa pasangan yang berbeda signifikan secara konsisten adalah skenario dengan nilai inter × fall teoretis kecil dibandingkan skenario dengan nilai teoretis besar, sebagaimana disajikan pada Tabel 6. Pasangan agresif terhadap konservatif menghasilkan p = 0,0002 dan fall_1 terhadap konservatif menghasilkan p = 0,0003. Sebaliknya, pasangan rise_1 terhadap rise_5 tidak berbeda signifikan, yang menegaskan bahwa parameter rise tidak berperan dalam proses deteksi kegagalan melainkan hanya pada proses pemulihan.

**Tabel 6.** Nilai p uji Dunn terkoreksi Bonferroni pada failover time (pasangan terpilih)

| Pasangan skenario | p-value | Keterangan |
|---|---|---|
| agresif – konservatif | 0,0002 | Berbeda signifikan |
| fall_1 – konservatif | 0,0003 | Berbeda signifikan |
| agresif – inter_5000 | 0,0026 | Berbeda signifikan |
| fall_1 – inter_5000 | 0,0042 | Berbeda signifikan |
| inter_500 – konservatif | 0,0110 | Berbeda signifikan |
| agresif – fall_5 | 0,0270 | Berbeda signifikan |
| fall_1 – fall_5 | 0,0415 | Berbeda signifikan |
| rise_1 – rise_5 | 1,0000 | Tidak berbeda signifikan |

<!-- REVISI #10: judul subbab diperjelas dan istilah "deviasi" didefinisikan pada kalimat pertama. -->
### 3.4. Perbandingan Failover Time Empiris dan Teoretis

Bagian ini membandingkan failover time hasil pengukuran (empiris) dengan nilai teoretis inter × fall pada Persamaan (1). Selisih antara keduanya selanjutnya disebut deviasi, dinyatakan dalam milidetik dan dalam persen terhadap nilai teoretis. Tabel 7 menyajikan perbandingan tersebut. Pada delapan dari sembilan skenario, failover time empiris lebih cepat dari nilai teoretis. Pola ini konsisten dengan model probabilistik bahwa titik kegagalan instance terjadi acak dalam siklus pemeriksaan, sehingga rata-rata waktu tunggu hingga pemeriksaan berikutnya lebih pendek dari satu interval penuh. Nilai teoretis inter × fall mengasumsikan kasus terburuk, yaitu kegagalan terjadi tepat setelah pemeriksaan terakhir yang berhasil.

**Tabel 7.** Perbandingan failover time empiris dan teoretis

| Skenario | Empiris (ms) | Teoretis (ms) | Deviasi (ms) | Deviasi (%) |
|---|---|---|---|---|
| fall_1 | 297,0 | 2000 | −1703,0 | −85,2 |
| agresif | 320,2 | 500 | −179,8 | −36,0 |
| baseline | 4516,0 | 6000 | −1484,0 | −24,7 |
| rise_1 | 4526,4 | 6000 | −1473,6 | −24,5 |
| rise_5 | 4531,8 | 6000 | −1468,2 | −24,5 |
| fall_5 | 8715,0 | 10000 | −1285,0 | −12,8 |
| inter_5000 | 13457,2 | 15000 | −1542,8 | −10,3 |
| konservatif | 23668,0 | 25000 | −1332,0 | −5,3 |
| inter_500 | 1607,8 | 1500 | +107,8 | +7,2 |

Besaran deviasi dalam persentase berbanding terbalik dengan nilai teoretis. Skenario dengan nilai inter × fall kecil menunjukkan deviasi relatif jauh lebih besar, yaitu −85,2% pada fall_1 dan −36,0% pada agresif, dibandingkan skenario dengan nilai teoretis besar seperti konservatif sebesar −5,3%. Penjelasannya adalah overhead deteksi yang bersifat tetap, yakni durasi pemeriksaan itu sendiri sekitar 100 ms setelah penyesuaian timeout connect, menjadi proporsi yang jauh lebih besar terhadap total waktu ketika nilai teoretis kecil, namun dapat diabaikan ketika nilai teoretis besar. Implikasinya, pada konfigurasi agresif, overhead deteksi yang konstan menjadi kontributor dominan terhadap total failover time dan bukan lagi jumlah pemeriksaan yang gagal.

Pengecualian ditemukan pada skenario inter_500 yang merupakan satu-satunya skenario dengan failover time melebihi nilai teoretis, yaitu +7,2%. Standar deviasi skenario ini juga jauh lebih besar, yaitu 196,3 ms dibanding kurang dari 30 ms pada sebagian besar skenario lain. Hal ini mengindikasikan bahwa pada interval pemeriksaan yang sangat pendek, variabilitas penjadwalan proses health check oleh HAProxy dan lapisan virtualisasi Docker Desktop menjadi signifikan relatif terhadap durasi interval itu sendiri. Temuan ini melengkapi hasil penelitian pada Kubernetes yang juga menemukan selisih antara waktu deteksi prediksi model dan hasil pengukuran [15].

### 3.5. Trade-off Nilai fall Rendah terhadap Flapping

Skenario flap_fall1 dan flap_fall5 dirancang untuk mengukur perilaku sistem terhadap kegagalan intermiten tanpa crash total. Metrik yang relevan adalah frekuensi transisi status UP dan DOWN yang diekstraksi dari log HAProxy, sebagaimana disajikan pada Tabel 8.

**Tabel 8.** Jumlah transisi status instance per pengujian selama 120 detik

| Pengulangan | flap_fall1 (fall = 1) | flap_fall5 (fall = 5) |
|---|---|---|
| 1 | 44 | 0 |
| 2 | 41 | 0 |
| 3 | 26 | 0 |
| 4 | 42 | 4 |
| 5 | 44 | 0 |
| Rata-rata | 39,4 | 0,8 |

Dengan fall = 1, satu kegagalan pemeriksaan sudah cukup untuk menandai instance sebagai DOWN, sehingga probabilitas kegagalan p = 0,3 per pemeriksaan langsung diterjemahkan menjadi transisi status yang sering, yaitu rata-rata 39,4 transisi per pengujian atau kurang lebih satu transisi setiap tiga detik. <!-- REVISI #3/#11: "probabilitas kegagalan 30% per pemeriksaan" -> "probabilitas kegagalan p = 0,3 per pemeriksaan". --> Sebaliknya, dengan fall = 5, instance baru ditandai DOWN setelah lima kegagalan berturut-turut yang pada probabilitas kegagalan independen p = 0,3 memiliki peluang kejadian sekitar 0,24%, sehingga transisi nyaris tidak pernah terjadi.

Temuan ini mengkuantifikasi kompromi yang selama ini hanya dinyatakan secara kualitatif: menurunkan nilai fall mempercepat deteksi kegagalan total sebagaimana ditunjukkan Tabel 7, namun secara signifikan meningkatkan kerentanan terhadap flapping pada kondisi kegagalan intermiten. Tidak ditemukan tambahan error rate akibat flapping pada kedua skenario karena load balancer tetap mengalihkan trafik ke dua instance laik-layan lainnya selama instance ketiga berstatus DOWN. <!-- REVISI #1: "dua instance sehat lainnya" -> "dua instance laik-layan lainnya". --> Meskipun demikian, frekuensi transisi yang tinggi tetap relevan secara operasional karena berpotensi memicu alerting berlebihan pada sistem pemantauan produksi. Hasil ini sejalan dengan literatur pendeteksi kegagalan yang menyatakan bahwa penurunan waktu deteksi cenderung menaikkan laju kesalahan penilaian status [2], sekaligus perlu dibaca dengan catatan bahwa kompromi tersebut dapat dilonggarkan apabila ambang deteksi ditetapkan secara adaptif terhadap kondisi beban [4].

### 3.6. Rekomendasi Konfigurasi Berbasis Data

Berdasarkan keseluruhan hasil, tiga profil kebutuhan konfigurasi dapat dirumuskan sebagaimana disajikan pada Tabel 9. Rekomendasi bersifat kondisional terhadap karakteristik kegagalan yang diantisipasi pada sistem produksi. Apabila kegagalan yang dominan berupa crash total seperti OOM kill atau panic proses, profil latency-sensitive lebih sesuai. Apabila kegagalan yang dominan berupa degradasi kinerja intermiten seperti jeda garbage collection atau kontensi sumber daya sesaat, profil stability-sensitive lebih sesuai untuk menghindari flapping yang tidak perlu.

**Tabel 9.** Rekomendasi konfigurasi berdasarkan profil kebutuhan

| Profil | Rekomendasi | Justifikasi berbasis hasil |
|---|---|---|
| Latency-sensitive | inter ≤ 500 ms, fall = 1–2 | Failover 297–320 ms dengan error rate mendekati nol; hanya sesuai bila kegagalan yang diantisipasi berupa crash total |
| Stability-sensitive | inter sedang hingga besar, fall ≥ 5 | Transisi status mendekati nol (0,8 pada flap_fall5) dengan konsekuensi failover 8,7–23,7 detik dan error rate hingga 0,63% |
| Balanced | inter = 2000 ms, fall = 3, rise = 2 | Failover 4,5 detik, error rate 0,11%, throughput stabil 3362 req/s; berada di antara fall = 1 yang rentan flapping dan fall = 5 yang lambat |

### 3.7. Keterbatasan Penelitian

Pengujian dilakukan pada satu perangkat dengan Docker Desktop pada macOS yang menjalankan container di dalam virtual machine Linux, sehingga terdapat lapisan virtualisasi tambahan yang tidak ada pada deployment Linux bare-metal. Karena seluruh pengukuran failover time bersumber dari log internal HAProxy dan clock Docker daemon yang konsisten, lapisan tersebut tidak mempengaruhi validitas pengukuran failover time, melainkan membatasi generalisasi nilai absolut throughput dan latensi. <!-- REVISI #11: klausa "30%" dirujukkan ke Subbab 2.2 dan pemetaan probabilitas dijadikan arah penelitian lanjutan. --> Selain itu, kegagalan intermiten hanya disimulasikan pada satu tingkat probabilitas, yaitu p = 0,3 per pemeriksaan (lihat Subbab 2.2), sehingga hubungan antara tingkat probabilitas kegagalan dan frekuensi flapping belum dipetakan; pemetaan itu menjadi salah satu arah penelitian lanjutan. Jumlah instance layanan juga dibatasi pada tiga unit sehingga dampak flapping terhadap ketersediaan pada konfigurasi dengan jumlah instance lebih sedikit belum teramati.

---

## 4. KESIMPULAN DAN SARAN

Penelitian ini membuktikan bahwa parameter health check HAProxy berpengaruh signifikan terhadap failover time, throughput, dan error rate pada sistem microservice berbasis Docker, dengan effect size yang besar pada ketiga metrik tersebut. Failover time terukur berkisar dari 297 ms pada konfigurasi fall = 1 hingga 23668 ms pada konfigurasi konservatif, sedangkan throughput menurun sekitar 17,9% dan error rate meningkat dari mendekati nol menjadi 0,63% ketika deteksi kegagalan melambat. Parameter inter dan fall terbukti mendominasi durasi deteksi, sedangkan parameter rise tidak berpengaruh terhadap failover time karena hanya berperan pada proses pemulihan. Pada delapan dari sembilan skenario, failover time empiris lebih cepat dari nilai teoretis inter × fall, dengan besaran deviasi relatif yang semakin besar ketika nilai teoretis semakin kecil akibat kontribusi overhead deteksi yang bersifat tetap. Kontribusi utama penelitian ini adalah kuantifikasi kompromi antara kecepatan deteksi dan kestabilan status: konfigurasi fall = 1 menghasilkan rata-rata 39,4 transisi status per pengujian pada kondisi kegagalan intermiten, sedangkan konfigurasi fall = 5 hanya menghasilkan 0,8 transisi. Kelebihan penelitian ini terletak pada penggunaan pilot study sebagai gerbang validasi berkriteria eksplisit dan pengujian signifikansi statistik non-parametrik, sedangkan kekurangannya terletak pada penggunaan satu lingkungan uji tervirtualisasi dan satu tingkat probabilitas kegagalan intermiten.

Penelitian selanjutnya disarankan mereplikasi pengujian pada lingkungan Linux bare-metal dan pada orkestrator container seperti Kubernetes untuk menilai sejauh mana pola deviasi failover time bersifat spesifik terhadap HAProxy. Variasi tingkat probabilitas kegagalan intermiten perlu diperluas agar hubungan antara tingkat kegagalan, nilai fall, dan frekuensi flapping dapat dimodelkan secara kuantitatif. Selain itu, mekanisme health check adaptif yang menyesuaikan nilai inter dan fall berdasarkan riwayat kelaikan instance layak diteliti sebagai upaya menurunkan waktu deteksi dan laju false positive secara bersamaan. <!-- REVISI #1: "riwayat kesehatan instance" -> "riwayat kelaikan instance". -->

---

## DAFTAR PUSTAKA

<!-- REVISI #13: format nama penulis diseragamkan menjadi "Nama-belakang, Inisial." agar kunci pengurutan alfabetis terlihat jelas. Urutan angka mengikuti skema daftar pustaka yang dipakai naskah. -->

[1] Annisa, A., M. Ardiana, P. N. Rahayu, T. Brian, dan M. A. Jami'in, "Performance Evaluation of Web Applications Using JMeter Load Testing for Server Capacity and Response Efficiency," *Journal of Applied Informatics and Computing*, vol. 10, no. 1, pp. 585–590, 2026. doi: 10.30871/jaic.v10i1.11840.

[2] Chaurasia, B., A. Verma, dan P. Verma, "IHFD: an improved heartbeat-based failure detector of ◊P (eventually perfect) class for partially synchronous hierarchical distributed systems," *Complex & Intelligent Systems*, 2026. doi: 10.1007/s40747-026-02423-z. <!-- REVISI #12: karakter rusak "◇" diperbaiki menjadi "◊P" dan diberi glosari "(eventually perfect)". Verifikasi embedding font ◊ saat konversi ke templat SKANIKA; bila font tidak mendukung, tulis "(eventually perfect, ◊P)". -->

[3] Čilić, I., P. Krivić, I. Podnar Žarko, dan M. Kušek, "Performance Evaluation of Container Orchestration Tools in Edge Computing Environments," *Sensors*, vol. 23, no. 8, art. 4008, 2023. doi: 10.3390/s23084008.

[4] Hanada, H., dan K. Ishibashi, "Service-Level Objective-Aware Load-Adaptive Timeout: Balancing Failure Rate and Latency in Microservices Communication," *IEEE Access*, vol. 13, pp. 137881–137895, 2025. doi: 10.1109/ACCESS.2025.3596118.

[5] HAProxy, *HAProxy version 3.2.22 – Configuration Manual*, 2026. [Daring]. Tersedia: https://docs.haproxy.org/3.2/configuration.html. [Diakses: 19-Agu-2026]

[6] Iryani, N., K. D. Ayatri, dan R. D. Wahyuningrum, "Analisis performansi high availability cluster server menggunakan heartbeat pada private cloud," *JITEL (Jurnal Ilmiah Telekomunikasi, Elektronika, dan Listrik Tenaga)*, vol. 2, no. 2, pp. 129–138, 2022. doi: 10.35313/jitel.v2.i2.2022.129-138.

[7] Khamdani, A. R., A. R. Muslikh, dan A. S. Affandi, "Comparative Analysis of Performance and Efficiency of Load Balancing Algorithms on Ingress Controller," *Jurnal Teknik Informatika (JUTIF)*, vol. 6, no. 1, pp. 453–468, 2025. doi: 10.52436/1.jutif.2025.6.1.4040.

[8] Laksono, P. A., dan S. D. Riskiono, "Analisis Perbandingan Algoritma Round Robin dan Least Connection dalam Haproxy untuk Load Balancer Server Web," *Dinamik*, vol. 30, no. 2, pp. 351–360, 2025. doi: 10.35315/dinamik.v30i2.10154.

[9] Pakrijauskas, K., dan D. Mažeika, "A Method of Transparent Graceful Failover in Low Latency Stateful Microservices," *Electronics*, vol. 11, no. 23, art. 3936, 2022. doi: 10.3390/electronics11233936.

[10] Pratama, R. K. A., dan Supatman, "Implementasi HAProxy sebagai external traffic load balancer cluster Kubernetes yang berjalan di atas Openstack," *Jurnal RESTIKOM: Riset Teknik Informatika dan Komputer*, vol. 6, no. 3, pp. 462–473, 2024. doi: 10.52005/restikom.v6i3.360.

[11] Putra, K. R., S. Umaroh, N. F. Fahrudin, dan P. W. Pandji, "Renovator: Resilience System in Microservices Architecture Using Fault Tolerance Factor," *MIND Journal*, vol. 10, no. 2, pp. 235–249, 2025. doi: 10.26760/mindjournal.v10i2.235-249.

[12] Ramasamy, B., Y. Na, W. Kim, K. Chea, dan J. Kim, "HACM: High Availability Control Method in Container-Based Microservice Applications Over Multiple Clusters," *IEEE Access*, vol. 11, pp. 3461–3471, 2023. doi: 10.1109/ACCESS.2022.3233159.

[13] Rawls, C., dan M. Amini Salehi, "Load Balancer Tuning: Comparative Analysis of HAProxy Load Balancing Methods," pracetak arXiv:2212.14198, 2022. doi: 10.48550/arXiv.2212.14198.

[14] Riskiono, S. D., dan D. Pasha, "Analisis Perbandingan Server Load Balancing dengan Haproxy & Nginx dalam Mendukung Kinerja Server E-Learning," *InComTech: Jurnal Telekomunikasi dan Komputer*, vol. 10, no. 3, pp. 135–144, 2021. doi: 10.22441/incomtech.v10i3.8751.

[15] Roberts, J., B. Archibald, dan P. Trinder, "Signalling Health for Improved Kubernetes Microservice Availability," pracetak arXiv:2507.02158, 2025. doi: 10.48550/arXiv.2507.02158.

[16] Saleh, R. F., dan Kusrini, "Analisis Perbandingan Kinerja Web Humas Infrastruktur On-Premise dan Cloud Computing dengan Load Balancer Round Robin," *MALCOM: Indonesian Journal of Machine Learning and Computer Science*, vol. 5, no. 3, pp. 1107–1116, 2025. doi: 10.57152/malcom.v5i3.2182.

[17] Saputro, V. A., dan A. Jaenul, "Evaluasi Dampak Opportunistic Wireless Encryption (OWE) terhadap Kinerja Jaringan Nirkabel IEEE 802.11ax," *SKANIKA: Sistem Komputer dan Teknik Informatika*, vol. 8, no. 1, pp. 35–45, 2025. doi: 10.36080/skanika.v8i1.3295.

[18] Sugiyatno, dan I. M, "Analisis Perbandingan Performasi Respon Waktu Web Server dan Failover Antara Kubernetes Dan Docker Swarm pada Container Orchestration," *Jurnal Informatika Komputer, Bisnis dan Manajemen*, vol. 21, no. 3, pp. 43–53, 2023. doi: 10.61805/fahma.v21i3.9.

[19] Wintolo, H., I. Riadi, dan A. Yudhana, "Analisis Deteksi Penyusup pada Layanan Open Journal System Menggunakan Metode Network Forensic Development Life Cycle," *SKANIKA: Sistem Komputer dan Teknik Informatika*, vol. 8, no. 1, pp. 133–144, 2025. doi: 10.36080/skanika.v8i1.3284.

[20] Zhang, P., L. Xiang, Z. Song, dan Y. Yang, "Adaptive load balancing and fault-tolerant microservices architecture for high-availability web systems using docker and spring cloud," *Discover Applied Sciences*, vol. 7, no. 7, art. 705, 2025. doi: 10.1007/s42452-025-07320-7.
