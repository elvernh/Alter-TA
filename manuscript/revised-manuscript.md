<!--
REVISED MANUSCRIPT - draft revisi 1
Sumber: Jurnal_SKANIKA_HAProxy_Health_Check-reviewed BIMO.docx
Semua perubahan menanggapi 14 komentar pembimbing (Agustinus Gumelar, 2026-08-31)
ditandai inline dengan komentar <!-- REVISI #n: ... -->
Nilai hasil pada bagian utama dipertahankan; abstrak memakai pembulatan pada angka
headline agar ringkas sesuai arahan mentoring 2026-09-04. Nilai presisi tetap
tersedia pada tabel dan bagian hasil.

AUTHORSHIP RULE: Setiap ekspor DOCX wajib menetapkan metadata paket `dc:creator`
dan `cp:lastModifiedBy` menjadi `Christianto Elvern Haryanto`. Nama generator atau
perangkat lunak, termasuk `python-docx`, tidak boleh digunakan sebagai penulis.

FORMAT RULE (2026-09-23): pada bagian berbahasa Indonesia seluruh istilah bahasa
Inggris ditulis miring; abstrak bahasa Inggris tidak memakai huruf miring. Pemiringan
diterapkan saat ekspor DOCX oleh tools/journal/italicize_foreign_terms_2026_09_23.py
sehingga naskah ini tidak diberi markup miring pada bagian berbahasa Indonesia.
Tanpa em dash; rujukan antarbagian memakai istilah "Sub bagian".
-->

# Pengaruh Parameter Health Check HAProxy terhadap Failover Time dan Kinerja Microservice Berbasis Docker

Christianto Elvern Haryanto, Mychael Maoeretz Engel, Agustinus Bimo Gumelar\*

Fakultas Teknologi Informasi, Program Studi Informatika, Universitas Ciputra, Surabaya, Indonesia

E-mail: charyanto@student.ciputra.ac.id, mychael.engel@ciputra.ac.id, \*bimo.gumelar@ciputra.ac.id
  (\* : corresponding author)

---

## Abstrak

<!-- REVISI MENTORING 2026-09-04: abstrak disusun ulang dengan pola latar belakang–tujuan–metode–temuan–signifikansi; posisi load balancer dan kesimpulan dibuat eksplisit. -->

Dalam kondisi tertentu, microservice dapat mengalami failover yang mengharuskan permintaan pengguna diarahkan menuju instance microservice tertentu yang tidak dapat merespons. Kondisi tersebut menunjukkan pentingnya konfigurasi parameter health check yang tepat, karena pemeriksaan ketersediaan dan respons microservice yang terlalu sensitif, dapat menganggap gangguan sementara sebagai bentuk kegagalan layanan dan memicu proses failover secara berulang. Beberapa penelitian terdahulu membahas algoritma pembagian trafik, namun pengaruh konfigurasi parameter pemeriksaan berkala (health check) HAProxy terhadap waktu failover dan kinerja microservice masih belum banyak dikaji. Konfigurasi parameter health check menentukan seberapa cepat waktu respon HAProxy mendeteksi perubahan kondisi layanan dan melakukan pengalihan trafik, sehingga konfigurasi yang berbeda dapat menghasilkan waktu failover serta kinerja layanan yang berbeda. 
Penelitian ini menguji pengaruh parameter inter, fall, dan rise terhadap failover time, throughput, latensi, dan error rate pada microservice berbasis Docker. Sebelas skenario pengujian dilakukan sebanyak lima kali dengan 200 pengguna virtual konkuren yang dijalankan secara otomatis. Uji Kruskal–Wallis menunjukkan perbedaan signifikan pada metrik kinerja, sedangkan failover time berkisar 297 hingga 23668 ms. Pada kegagalan intermiten, nilai fall = 1 menghasilkan sekitar 39 status transisi per pengujian, sedangkan nilai fall = 5 menghasilkan kurang dari satu transisi. Deteksi yang lebih cepat meningkatkan throughput hingga 18%, sehingga nilai fall dipilih berdasarkan jenis kegagalan yang paling mungkin terjadi pada sistem sasaran.

**Kata kunci:** failover time, HAProxy, health check, load balancer, microservice

---

## Abstract

<!-- REVISI MENTORING 2026-09-04: English abstract aligned to the revised Indonesian structure and rounded headline values. -->

Under certain conditions, a microservice may experience a failover in which user requests are directed to a particular microservice instance that is unable to respond. This highlights the importance of configuring health-check parameters appropriately, as checks that are overly sensitive to microservice availability and responsiveness may interpret a temporary disruption as a service failure and repeatedly trigger the failover process. Previous studies have examined traffic-distribution algorithms; however, the effects of HAProxy's periodic health-check parameter configuration on failover time and microservice performance remain underexplored. Health-check parameter configuration determines how quickly HAProxy detects changes in service status and redirects traffic, meaning that different configurations may result in different failover times and levels of service performance.

This study examines the effects of the inter, fall, and rise parameters on failover time, throughput, latency, and error rate in Docker-based microservices. Eleven test scenarios were each conducted five times with 200 concurrent virtual users using an automated process. The Kruskal–Wallis test revealed significant differences in performance metrics, while failover time ranged from 297 to 23,668 ms. Under intermittent failure conditions, fall = 1 resulted in approximately 39 status transitions per test, whereas fall = 5 resulted in fewer than one transition. Faster detection increased throughput by up to 18%; therefore, the fall value should be selected according to the type of failure most likely to occur in the target system.

**Keywords:** failover time, HAProxy, health check, load balancer, microservice

---

## 1. PENDAHULUAN

Arsitektur microservice dengan mekanisme load balancing dan failover banyak digunakan pada sistem yang menuntut ketersediaan tinggi karena memungkinkan layanan direplikasi, diskalakan, dan dipulihkan secara independen. Penelitian terdahulu menunjukkan bahwa penerapan mekanisme ketersediaan tinggi pada arsitektur microservice berbasis container dapat meningkatkan kualitas layanan dibandingkan arsitektur monolitik, sedangkan metode kendali ketersediaan tinggi pada aplikasi microservice yang tersebar pada beberapa klaster dikembangkan untuk mempersingkat waktu pemulihan layanan [20], [12]. Dalam implementasinya, load balancer berperan dalam menentukan distribusi permintaan sekaligus mengarahkan trafik dari layanan yang mengalami kegagalan menuju instance yang masih dapat melayani permintaan. HAProxy merupakan salah satu perangkat lunak load balancer yang digunakan pada lingkungan web server, container, maupun klaster orkestrasi. Penelitian sebelumnya membandingkan kinerja HAProxy dan Nginx serta menunjukkan perbedaan response time dan throughput antara keduanya [14]. Penelitian lain pada HAProxy membandingkan algoritma round robin dan least connection serta menunjukkan bahwa pemilihan algoritma distribusi trafik berpengaruh terhadap kinerja server [8]. Kajian pada ingress controller juga menunjukkan bahwa perbedaan algoritma load balancing dapat mempengaruhi efisiensi dan kinerja sistem ter kontainer [7], sedangkan penelitian pada lingkungan on-premise dan cloud computing memperlihatkan bahwa penerapan load balancer berpengaruh terhadap kinerja layanan web [16]. Selain mekanisme distribusi trafik, penelitian mengenai deteksi kegagalan menunjukkan bahwa mekanisme pemeriksaan berkala (health check) memerlukan penyetelan yang tepat karena terdapat kompromi antara kecepatan deteksi dan ketepatan dalam menentukan status layanan. Penelitian pada pemantauan container di Kubernetes menunjukkan bahwa pemeriksaan berkala dapat mengalami keterlambatan dalam mendeteksi perubahan status dan berpotensi menurunkan ketersediaan layanan, sedangkan pendekatan berbasis sinyal mampu mempercepat deteksi kegagalan [15]. Penelitian mengenai heartbeat-based failure detector juga menempatkan waktu deteksi dan tingkat kesalahan penilaian status sebagai persoalan penting dalam mekanisme deteksi kegagalan [2]. Meskipun penelitian terdahulu telah membahas ketersediaan tinggi, failover, algoritma distribusi trafik, dan mekanisme deteksi kegagalan, sebagian besar kajian pada HAProxy masih berfokus pada algoritma load balancing dan belum secara khusus mengukur pengaruh konfigurasi parameter health check terhadap waktu deteksi kegagalan serta kinerja layanan. Dengan demikian, masih terdapat celah penelitian antara fungsi parameter health check yang telah didefinisikan dalam dokumentasi HAProxy dan bukti empiris mengenai konsekuensi pemilihan nilai parameter tersebut terhadap perilaku sistem [5], [13].

Celah tersebut menjadi penting karena HAProxy menentukan kapan sebuah instance dianggap tidak laik menerima trafik berdasarkan konfigurasi health check. Tiga parameter utama yang menentukan proses tersebut adalah inter, fall, dan rise. Parameter inter menentukan interval antar pemeriksaan, fall menentukan jumlah kegagalan pemeriksaan berturut-turut sebelum instance dinyatakan DOWN, sedangkan rise menentukan jumlah keberhasilan pemeriksaan berturut-turut sebelum instance dinyatakan pulih [5]. Konfigurasi parameter tersebut secara langsung berkaitan dengan kecepatan pengalihan trafik ketika terjadi kegagalan. Nilai inter atau fall yang kecil dapat mempercepat deteksi sehingga trafik lebih cepat dialihkan dari instance yang gagal, tetapi sensitivitas yang terlalu tinggi dapat membuat gangguan sementara dianggap sebagai kegagalan dan menyebabkan perubahan status berulang (flapping). Sebaliknya, konfigurasi yang lebih konservatif dapat mengurangi perubahan status yang tidak diperlukan, tetapi memperpanjang waktu ketika permintaan masih diarahkan menuju instance yang tidak dapat merespons. Kondisi tersebut dapat meningkatkan jumlah permintaan gagal dan menurunkan throughput layanan. Permasalahan ini menunjukkan adanya kebutuhan untuk memperoleh bukti kuantitatif mengenai kompromi antara kecepatan deteksi dan kestabilan status instance, terutama karena dokumentasi HAProxy hanya mendefinisikan fungsi dan nilai bawaan parameter tanpa memberikan dasar empiris untuk menentukan konfigurasi berdasarkan karakteristik kegagalan [5]. Oleh karena itu, penelitian ini menguji pengaruh parameter inter, fall, dan rise terhadap failover time, throughput, latensi, dan error rate pada sistem microservice berbasis Docker. Penelitian ini juga mengukur frekuensi perubahan status pada kondisi kegagalan intermiten untuk mengkuantifikasi fenomena flapping. <!-- REVISI 2026-09-23: probabilitas kegagalan p didefinisikan sebelum digunakan pada Sub bagian 2.2. --> Kegagalan intermiten dinyatakan dengan probabilitas kegagalan p, yaitu peluang sebuah pemeriksaan health check menghasilkan status tidak laik pada setiap siklus pemeriksaan meskipun proses layanan tetap berjalan. Selain itu, penelitian ini membandingkan failover time empiris dengan nilai teoritis berdasarkan hubungan inter × fall. Hasil pengukuran tersebut diharapkan dapat memberikan dasar berbasis data dalam menentukan konfigurasi health check sesuai karakteristik kegagalan yang mungkin terjadi pada sistem. Penelitian selanjutnya dapat memperluas pengujian pada lingkungan Linux bare-metal, orchestrator seperti Kubernetes, serta berbagai tingkat probabilitas kegagalan intermiten untuk mengetahui generalisasi hasil dan memodelkan hubungan antara konfigurasi health check, waktu deteksi, dan frekuensi flapping secara lebih luas.

---

## 2. METODE PENELITIAN

Penelitian menggunakan pendekatan eksperimen kuantitatif dengan variabel bebas berupa nilai parameter health check HAProxy dan variabel terikat berupa failover time, throughput, latensi p50, latensi p95, serta error rate. Variabel kontrol mencakup jumlah instance layanan, alokasi sumber daya container, jumlah virtual user, durasi pengujian, serta waktu injeksi kegagalan.

Latensi p50 (persentil ke-50, setara median) menunjukkan nilai latensi yang berada di tengah distribusi hasil pengujian, yaitu 50% permintaan memiliki latensi di bawah atau sama dengan nilai tersebut dan 50% lainnya berada di atasnya. Latensi p95 (persentil ke-95) menunjukkan nilai latensi yang hanya dilampaui oleh sekitar 5% permintaan. Nilai p95 dapat digunakan sebagai metrik untuk mengevaluasi batas latensi yang ditetapkan dalam Service Level Objective (SLO) layanan. Persentil ke-100 (nilai maksimum tunggal) tidak digunakan karena sangat sensitif terhadap nilai ekstrem dan dapat menghasilkan nilai yang tidak representatif terhadap distribusi latensi. Oleh karena itu, penelitian menggunakan p50 dan p95 untuk merepresentasikan nilai tengah dan latensi pada bagian distribusi yang lebih tinggi.

### 2.1. Arsitektur Lingkungan Pengujian

<!-- REVISI #10: komentar "IP dan desain trafik perlu ditampilkan dan dijelaskan" ditindaklanjuti pada paragraf pembuka, Gambar 1, dan paragraf penjelas aliran trafik. -->
Lingkungan pengujian dibangun menggunakan Docker Compose dan terdiri atas satu container HAProxy, tiga container layanan yang identik, serta satu container load tester. Docker Compose membentuk jaringan bridge internal `experiment` dengan subnet 172.28.0.0/24. HAProxy menggunakan alamat 172.28.0.20, sedangkan `service1`, `service2`, dan `service3` masing-masing menggunakan alamat 172.28.0.31, 172.28.0.32, dan 172.28.0.33. Alamat IP container k6 dialokasikan secara dinamis pada subnet yang sama karena k6 hanya bertindak sebagai sumber trafik. Desain alamat IP dan aliran trafik ditunjukkan pada Gambar 1.

![Gambar 1](../[Gambar 1: lihat berkas media DOCX: word/media/image1.png])

**Gambar 1.** Desain alamat IP dan aliran trafik pada lingkungan pengujian berbasis Docker

Pada setiap pengulangan, k6 mengirim permintaan HTTP `GET /api` ke HAProxy pada 172.28.0.20:8080. HAProxy membagi trafik tersebut menggunakan algoritma roundrobin ke `service1`, `service2`, dan `service3` pada port 3000. Secara terpisah, HAProxy mengirim permintaan `GET /health` ke port 3000 pada setiap instance untuk menentukan status UP atau DOWN. Seluruh komunikasi berlangsung di jaringan bridge internal Docker dan tidak melewati port forwarding host.

Layanan yang diuji merupakan aplikasi Node.js sederhana dengan dua endpoint, yaitu `/api` yang mensimulasikan pekerjaan bisnis selama kurang lebih 5 ms dan `/health` yang digunakan HAProxy sebagai target health check untuk menilai kelaikan instance. <!-- REVISI #1: "target pemeriksaan ... menilai kesehatannya" -> "target health check untuk menilai kelaikan instance". --> Endpoint `/health` dapat dikonfigurasi untuk mengembalikan respons tidak laik secara probabilistik guna mensimulasikan kegagalan intermiten. <!-- REVISI #1: "respons tidak sehat" -> "respons tidak laik". --> Spesifikasi platform implementasi disajikan pada Tabel 1.

**Tabel 1.** Spesifikasi platform implementasi

| No | Komponen | Spesifikasi |
|---|---|---|
| 1 | Perangkat | Apple MacBook Pro (Apple M5, arsitektur ARM64) |
| 2 | CPU | 10-core |
| 3 | RAM | 24 GB unified memory |
| 4 | Penyimpanan | 1 TB SSD |
| 5 | Sistem operasi host | macOS Tahoe 26.6.2 |
| 6 | Runtime container | Docker Desktop 4.75.0 for Mac (Docker Engine 29.5.2, Docker Compose v5.1.3), alokasi tetap 8 CPU dan 16 GB RAM |
| 7 | Load balancer | HAProxy 3.2 (image haproxy:3.2-alpine), mode HTTP, algoritma roundrobin |
| 8 | Load tester | k6 1.3.0, executor constant-vus, 200 virtual user konkuren |

<!-- REVISI 2026-09-23: versi Docker, HAProxy, k6, dan macOS dicantumkan; versi Docker dan image dari versions.txt setiap run, versi macOS dari perangkat uji. -->

Docker Desktop pada macOS menjalankan seluruh container di dalam virtual machine Linux, bukan langsung pada kernel host. Untuk menjaga konsistensi antar skenario, alokasi sumber daya virtual machine ditetapkan secara eksplisit dan tidak diubah selama seluruh rangkaian eksperimen. Seluruh image container yang digunakan merupakan image ARM64 native untuk menghindari overhead emulasi, dan aplikasi lain pada host ditutup selama pengujian berlangsung.

### 2.2. Skenario Pengujian

Sebelas skenario konfigurasi diuji sebagaimana disajikan pada Tabel 2. Sembilan skenario pertama menguji kegagalan total, sedangkan dua skenario terakhir menguji kegagalan intermiten dengan probabilitas kegagalan health check p = 0,3 per pemeriksaan. Setiap skenario diulang lima kali sehingga total pengujian berjumlah 55 kali.

<!-- REVISI #3: definisi dan alasan pemilihan p = 0,3 ditambahkan sebelum Tabel 2. -->
<!-- REVISI #11: tanda em dash pada Sub bagian 2.2 dihapus tanpa mengubah makna paragraf. -->
Pada dua skenario terakhir, kegagalan intermiten disimulasikan dengan mengatur endpoint `/health` agar mengembalikan status tidak laik secara acak dengan probabilitas p = 0,3 pada setiap pemeriksaan health check (bukan crash proses). Nilai p = 0,3 dipilih sebagai representasi kegagalan intermiten tingkat sedang karena cukup sering untuk memicu perubahan status berulang pada nilai fall rendah, tetapi tidak menyerupai kegagalan total. Nilai tersebut dijaga konstan pada seluruh pengulangan kedua skenario agar pengaruh nilai fall dapat dibandingkan pada tingkat probabilitas kegagalan yang sama.

**Tabel 2.** Skenario konfigurasi parameter health check

| No | Skenario | inter (ms) | fall (kali) | rise (kali) | Jenis kegagalan |
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
| 10 | flap_fall1 | 2000 | 1 | 2 | Intermiten (p = 0,3 per check) |
| 11 | flap_fall5 | 2000 | 5 | 2 | Intermiten (p = 0,3 per check) |

<!-- REVISI #3: sel "Intermiten (gagal 30%)" pada baris 10 & 11 diganti "Intermiten (p = 0,3 per check)". -->
<!-- REVISI 2026-09-23: satuan fall dan rise dinyatakan sebagai jumlah pemeriksaan berturut-turut (kali); notasi p_gagal diseragamkan menjadi p. -->

### 2.3. Prosedur Pengujian dan Pengukuran Failover Time

Setiap pengulangan mengikuti urutan yang sama dengan konfigurasi HAProxy yang dibangkitkan dari templat sesuai nilai parameter skenario. Seluruh stack container akan dibangun ulang, kemudian sistem dibiarkan menghangat selama 15 detik. Load test dijalankan selama 120 detik dengan 200 virtual user yang berjalan secara konkuren menggunakan executor constant-vus. Setiap virtual user mengirim permintaan `GET /api` secara berulang tanpa jeda, sehingga jumlah pengguna aktif tetap 200 sepanjang pengujian. Pada detik ke-30 satu dari tiga instance dihentikan menggunakan perintah `docker kill`, dan pada detik ke-90 instance tersebut dipulihkan. Perintah `docker kill` dipilih dibanding `docker stop` karena keduanya mengirim sinyal yang berbeda ke proses utama container. Perintah `docker stop` mengirim sinyal SIGTERM (signal terminate), yaitu permintaan agar proses berhenti secara teratur (graceful shutdown), dan baru mengirim SIGKILL apabila proses belum berhenti setelah tenggang waktu bawaan 10 detik. Pada layanan yang diuji, proses Node.js berjalan sebagai PID 1 tanpa penanganan SIGTERM sehingga sinyal tersebut diabaikan dan layanan tetap merespons pemeriksaan health check selama tenggang waktu, yang mengaburkan titik awal kegagalan. Sebaliknya, `docker kill` secara bawaan mengirim SIGKILL yang tidak dapat ditangkap atau diabaikan oleh proses, sehingga container berhenti seketika dan titik awal kegagalan dapat ditentukan secara tepat. <!-- REVISI 2026-09-23: konkurensi 200 virtual user dan penjelasan SIGTERM/SIGKILL ditambahkan. -->

Failover time diukur sebagai selisih dua timestamp yang keduanya bersumber dari [clock Docker daemon] yang sama untuk menghindari clock skew antara sistem operasi host dan virtual machine tempat Docker Engine berjalan. Timestamp pertama adalah waktu berhentinya container yang diperoleh dari atribut `State.FinishedAt` melalui perintah `docker inspect`. Timestamp kedua adalah waktu HAProxy menandai instance sebagai tidak laik (DOWN), yang diperoleh dari baris log berpola `"Server ... is DOWN"` pada keluaran `docker logs -t`. <!-- REVISI #1: "menandai instance sebagai tidak sehat" -> "menandai instance sebagai tidak laik (DOWN)". --> Nilai teoretis failover time dihitung menggunakan Persamaan (1).

$$t_\text{teoretis} = inter \times fall \qquad (1)$$

Karena titik kegagalan instance terjadi acak di dalam siklus pemeriksaan, failover time empiris diprediksi berada pada rentang yang dinyatakan Persamaan (2), dengan `t_ovh` merupakan overhead deteksi berupa durasi pemeriksaan itu sendiri.

$$inter \times (fall - 1) \le t_\text{empiris} \le inter \times fall + t_\text{ovh} \qquad (2)$$

Pada skenario kegagalan intermiten, failover time tidak dapat didefinisikan karena tidak terdapat titik kegagalan tunggal. Metrik yang dicatat pada kedua skenario tersebut adalah frekuensi transisi status instance, yaitu jumlah perpindahan status UP dan DOWN yang terekstraksi dari log HAProxy selama satu pengujian.

### 2.4. Pipeline Otomasi

Seluruh tahapan dijalankan oleh skrip otomasi tanpa intervensi manual, mencakup substitusi konfigurasi HAProxy, pembangunan ulang stack container, eksekusi load test, injeksi kegagalan, pemulihan instance, ekstraksi metrik dari ringkasan load tester dan log HAProxy, hingga penyimpanan hasil ke berkas CSV. Alur satu pengulangan disajikan pada Algoritma 1. <!-- REVISI #4: rujukan ke Algoritma 1 ditambahkan. --> Otomasi penuh diperlukan agar ke-55 pengujian (11 skenario × 5 pengulangan, lihat Sub bagian 2.2) dijalankan dengan prosedur yang identik sehingga variasi hasil tidak bersumber dari perbedaan perlakuan antar pengulangan. <!-- REVISI #5: "55 pengujian" -> "ke-55 pengujian (11 skenario × 5 pengulangan, lihat Sub bagian 2.2)". -->

<!-- REVISI #4: blok Algoritma 1 ditambahkan. -->
<!-- REVISI 2026-09-23: Algoritma 1 disajikan sebagai tabel berbingkai, bukan blok kode. -->
**Algoritma 1.** Pipeline otomasi untuk satu pengulangan

| Baris | Langkah | Keterangan |
|---|---|---|
| Masukan | skenario s = (inter, fall, rise, jenis_kegagalan); indeks pengulangan r | |
| Keluaran | satu baris metrik pada `results.csv` | |
| 1 | Render `haproxy.cfg` dari templat dengan nilai (inter, fall, rise, timeout = 100 ms) | Konfigurasi skenario |
| 2 | `docker compose down -v`; `docker compose up -d --build` | Bangun ulang stack |
| 3 | Tunggu 15 detik | Warm-up |
| 4 | Jalankan k6 (constant-vus, 200 VU, 120 s) secara asynchronous | Mulai load test |
| 5 | Pada t = 30 s: `docker kill service3` | Injeksi kegagalan |
| 6 | Pada t = 90 s: `docker start service3` | Pemulihan |
| 7 | Tunggu proses k6 selesai | |
| 8 | kill_ts ← `docker inspect -f '{{.State.FinishedAt}}' service3` | Waktu container berhenti |
| 9 | down_ts ← timestamp baris "is DOWN" pertama dari `docker logs -t haproxy` | Waktu status DOWN |
| 10 | failover_ms ← (down_ts − kill_ts) dalam milidetik | Failover time |
| 11 | (throughput, p50, p95, error_rate) ← parse ringkasan JSON k6 | Metrik kinerja |
| 12 | Jika jenis_kegagalan = intermiten: transisi ← jumlah perpindahan UP ↔ DOWN dari `docker logs haproxy`; failover_ms ← N/A | Skenario flapping |
| 13 | Tambahkan baris (s, r, throughput, p50, p95, error_rate, failover_ms, transisi) ke `results.csv` | Simpan hasil |

### 2.5. Pilot Study sebagai Gerbang Validasi

<!-- REVISI #9: langkah "pemeriksaan kesiapan pipeline (uji asap)" diperkenalkan di Metode. -->
Sebelum pilot study, dilakukan pemeriksaan kesiapan pipeline (uji asap) untuk memastikan seluruh tahap otomasi berjalan penuh dan setiap metrik dapat diekstraksi; temuan pada tahap ini dilaporkan pada Sub bagian 3.1.

Pilot study dilaksanakan sebagai gerbang validasi sebelum pengujian utama menggunakan konfigurasi baseline dengan tiga pengulangan. Pengujian utama dilaksanakan apabila kelima kriteria berikut terpenuhi: (1) failover time dapat diekstraksi dari log pada seluruh pengulangan; (2) selisih failover time antar pengulangan tidak melebihi satu kali nilai inter; (3) penggunaan CPU container load tester berada di bawah 80% sehingga load tester tidak menjadi bottleneck; (4) error terkonsentrasi di sekitar periode kegagalan, bukan tersebar sepanjang pengujian; dan (5) pipeline otomasi berjalan penuh tanpa intervensi manual.

### 2.6. Teknik Analisis Data

Data dianalisis menggunakan statistik deskriptif berupa rata-rata dan standar deviasi per skenario. Karena setiap skenario diulang lima kali dan distribusi metrik kinerja tidak dapat diasumsikan normal, uji signifikansi menggunakan uji Kruskal-Wallis pada taraf signifikansi α = 0,05, yaitu perbedaan dinyatakan signifikan apabila p-value < 0,05. P-value merupakan peluang memperoleh perbedaan sebesar yang teramati apabila sebenarnya tidak terdapat perbedaan antar skenario. Apabila ditemukan perbedaan signifikan, pengujian dilanjutkan dengan uji post-hoc Dunn dengan koreksi Bonferroni. <!-- REVISI 2026-09-23: p-value didefinisikan dan ditulis lengkap agar tidak tertukar dengan probabilitas kegagalan p. --> Besaran praktis perbedaan dilaporkan menggunakan effect size epsilon-squared (ε²). Selain itu, failover time empiris dibandingkan terhadap nilai teoretis pada Persamaan (1) untuk menganalisis besaran dan sumber deviasi.

---

## 3. HASIL DAN PEMBAHASAN

### 3.1. Hasil Pilot Study

Seluruh kriteria gerbang validasi terpenuhi. Failover time berhasil diekstraksi pada ketiga pengulangan dengan nilai 4512 ms, 4521 ms, dan 4531 ms, sehingga selisih maksimum antar pengulangan hanya 19 ms atau jauh di bawah ambang satu kali nilai inter sebesar 2000 ms; kriteria 1 dan 2 dengan demikian terpenuhi. Ketiga nilai tersebut berada dalam rentang prediksi Persamaan (2). Penggunaan CPU container load tester sepanjang pengujian tetap berada di bawah ambang 80%, sedangkan throughput stabil pada kisaran 3362 sampai 3386 request per detik (RPS, Requests per Second) dengan latensi median 6,4 sampai 6,7 ms. <!-- REVISI #6: interpretasi angka terhadap kriteria gerbang validasi ditambahkan (lanjutan paragraf). Angka spesifik puncak CPU load tester dihilangkan; hanya kepatuhan terhadap ambang 80% yang dinyatakan. --> Angka-angka tersebut dibaca terhadap kelima kriteria gerbang validasi pada Sub bagian 2.5: penggunaan CPU load tester yang tidak melampaui ambang 80% memastikan load tester bukan menjadi bottleneck (kriteria 3); throughput yang stabil pada 3362–3386 RPS dan latensi median 6,4–6,7 ms antar ketiga pengulangan menunjukkan lingkungan uji berperilaku konsisten, sejalan dengan kriteria 2 tentang keterulangan hasil. <!-- REVISI #7: kalimat error rate ditulis ulang dan dikaitkan ke kriteria 4. --> Error rate berkisar 0,102–0,112% dan seluruhnya terkonsentrasi pada jendela waktu antara instance dimatikan hingga HAProxy menandainya DOWN, bukan tersebar sepanjang 120 detik pengujian; pola ini memenuhi kriteria 4, yaitu error merupakan konsekuensi langsung dari kegagalan yang diinjeksikan dan bukan gejala ketidakstabilan lingkungan uji. Dengan seluruh kriteria pada Sub bagian 2.5 terpenuhi, termasuk kriteria 5 karena pipeline berjalan tanpa intervensi manual, pengujian utama dilanjutkan. Ringkasan hasil pilot study disajikan pada Tabel 3.

**Tabel 3.** Hasil pilot study pada konfigurasi baseline (inter = 2000 ms, fall = 3, rise = 2)

| Rep | Throughput (RPS) | Latensi p50 (ms) | Latensi p95 (ms) | Error rate (%) | Failover time (ms) |
|---|---|---|---|---|---|
| 1 | 3386,35 | 6,43 | 8,75 | 0,102 | 4512 |
| 2 | 3362,47 | 6,70 | 9,61 | 0,112 | 4521 |
| 3 | 3365,83 | 6,67 | 9,42 | 0,102 | 4531 |

Keterangan: RPS = Requests per Second, yaitu jumlah permintaan HTTP yang diproses per detik. <!-- REVISI 2026-09-23: keterangan RPS juga ditempatkan di bawah Tabel 3, tabel pertama yang memakai satuan RPS. -->

<!-- REVISI #9: "Pada tahap validasi pra-pilot ditemukan bahwa" -> "Pada pemeriksaan kesiapan pipeline sebelum pilot study ditemukan bahwa". -->
Pada pemeriksaan kesiapan pipeline sebelum pilot study ditemukan bahwa nilai bawaan timeout connect HAProxy sebesar 2 detik menyebabkan setiap pemeriksaan health check yang gagal ikut menunggu penuh durasi timeout tersebut alih-alih gagal seketika, sehingga failover time terukur mencapai dua kali lipat nilai teoretis. Setelah timeout connect dan timeout check diturunkan menjadi 100 ms, nilai yang aman karena seluruh komunikasi terjadi dalam jaringan Docker internal dengan latensi milidetik, failover time kembali sesuai rentang teoretis. Temuan ini menunjukkan bahwa parameter timeout perlu diperlakukan sebagai bagian dari konfigurasi health check, bukan sebagai pengaturan terpisah.

### 3.2. Statistik Deskriptif

Tabel 4 merangkum rata-rata dan standar deviasi kelima metrik pada sebelas skenario dengan lima pengulangan per skenario. Nilai failover time pada dua skenario flapping tidak tersedia karena skenario tersebut tidak melibatkan kegagalan total yang dapat diukur waktu deteksinya.

**Tabel 4.** Statistik deskriptif per skenario (rata-rata ± standar deviasi, n = 5)

| Skenario | Throughput (RPS) | Latensi p50 (ms) | Latensi p95 (ms) | Error rate (%) | Failover (ms) |
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

Keterangan: RPS = Requests per Second, yaitu jumlah permintaan HTTP yang diproses per detik. Konfigurasi parameter setiap skenario mengacu pada Tabel 2. <!-- REVISI 2026-09-23: satuan throughput diganti menjadi RPS (Requests per Second) beserta keterangannya. -->

Terdapat hubungan yang konsisten antara kecepatan deteksi dan dampak kegagalan terhadap pengguna. Skenario konservatif menghasilkan throughput terendah sebesar 2946,5 RPS dengan error rate tertinggi sebesar 0,63%, sedangkan skenario dengan deteksi cepat seperti fall_1 dan agresif mempertahankan throughput di atas 3440 RPS dengan error rate mendekati nol. Selisih throughput antara konfigurasi tercepat dan terlambat mencapai sekitar 17,9%. Perbedaan ini bersumber dari lamanya periode ketika load balancer masih mengarahkan trafik ke instance yang sudah mati, sehingga semakin lambat deteksi, semakin banyak permintaan yang gagal. Perbandingan throughput dan failover time antar skenario ditunjukkan pada Gambar 2 dan Gambar 3.

![Gambar 2](../[Gambar 2: lihat berkas media DOCX: word/media/image2.png])

**Gambar 2.** Perbandingan throughput (RPS) antar skenario (rata-rata ± standar deviasi, data pada Tabel 4) <!-- REVISI 2026-09-23: Gambar 2 dan 3 digambar ulang dari Tabel 4 dengan label sumbu dan legenda di bawah grafik. -->

![Gambar 3](../[Gambar 3: lihat berkas media DOCX: word/media/image3.png])

**Gambar 3.** Perbandingan failover time antar skenario (rata-rata ± standar deviasi, data pada Tabel 4)

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

Uji post-hoc Dunn dengan koreksi Bonferroni pada failover time menunjukkan bahwa pasangan yang berbeda signifikan secara konsisten adalah skenario dengan nilai inter × fall teoretis kecil dibandingkan skenario dengan nilai teoretis besar, sebagaimana disajikan pada Tabel 6. Pasangan agresif terhadap konservatif menghasilkan p-value = 0,0002 dan fall_1 terhadap konservatif menghasilkan p-value = 0,0003. Sebaliknya, pasangan rise_1 terhadap rise_5 tidak berbeda signifikan, yang menegaskan bahwa parameter rise tidak berperan dalam proses deteksi kegagalan melainkan hanya pada proses pemulihan.

**Tabel 6.** Nilai p-value uji Dunn terkoreksi Bonferroni pada failover time (pasangan terpilih)

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

<!-- REVISI #10: judul sub bagian diperjelas dan istilah "deviasi" didefinisikan pada kalimat pertama. -->
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
| Balanced | inter = 2000 ms, fall = 3, rise = 2 | Failover 4,5 detik, error rate 0,11%, throughput stabil 3362 RPS; berada di antara fall = 1 yang rentan flapping dan fall = 5 yang lambat |

### 3.7. Keterbatasan Penelitian

Pengujian dilakukan pada satu perangkat dengan Docker Desktop pada macOS yang menjalankan container di dalam virtual machine Linux, sehingga terdapat lapisan virtualisasi tambahan yang tidak ada pada deployment Linux bare-metal. Karena seluruh pengukuran failover time bersumber dari log internal HAProxy dan clock Docker daemon yang konsisten, lapisan tersebut tidak mempengaruhi validitas pengukuran failover time, melainkan membatasi generalisasi nilai absolut throughput dan latensi. <!-- REVISI #11: klausa "30%" dirujukkan ke Sub bagian 2.2 dan pemetaan probabilitas dijadikan arah penelitian lanjutan. --> Selain itu, kegagalan intermiten hanya disimulasikan pada satu tingkat probabilitas, yaitu p = 0,3 per pemeriksaan (lihat Sub bagian 2.2), sehingga hubungan antara tingkat probabilitas kegagalan dan frekuensi flapping belum dipetakan; pemetaan itu menjadi salah satu arah penelitian lanjutan. Jumlah instance layanan juga dibatasi pada tiga unit sehingga dampak flapping terhadap ketersediaan pada konfigurasi dengan jumlah instance lebih sedikit belum teramati.

---

## 4. KESIMPULAN DAN SARAN

Penelitian ini membuktikan bahwa parameter health check HAProxy berpengaruh signifikan terhadap failover time, throughput, dan error rate pada sistem microservice berbasis Docker, dengan effect size yang besar pada ketiga metrik tersebut. Failover time terukur berkisar dari 297 ms pada konfigurasi fall = 1 hingga 23668 ms pada konfigurasi konservatif, sedangkan throughput menurun sekitar 17,9% dan error rate meningkat dari mendekati nol menjadi 0,63% ketika deteksi kegagalan melambat. Parameter inter dan fall terbukti mendominasi durasi deteksi, sedangkan parameter rise tidak berpengaruh terhadap failover time karena hanya berperan pada proses pemulihan. Pada delapan dari sembilan skenario, failover time empiris lebih cepat dari nilai teoretis inter × fall, dengan besaran deviasi relatif yang semakin besar ketika nilai teoretis semakin kecil akibat kontribusi overhead deteksi yang bersifat tetap. Kontribusi utama penelitian ini adalah kuantifikasi kompromi antara kecepatan deteksi dan kestabilan status: konfigurasi fall = 1 menghasilkan rata-rata 39,4 transisi status per pengujian pada kondisi kegagalan intermiten, sedangkan konfigurasi fall = 5 hanya menghasilkan 0,8 transisi. Kelebihan penelitian ini terletak pada penggunaan pilot study sebagai gerbang validasi berkriteria eksplisit dan pengujian signifikansi statistik non-parametrik, sedangkan kekurangannya terletak pada penggunaan satu lingkungan uji tervirtualisasi dan satu tingkat probabilitas kegagalan intermiten.

Penelitian selanjutnya yang dapat dilakukan antara lain: yang pertama adalah mereplikasi pengujian pada lingkungan Linux bare-metal dan pada orkestrator container seperti Kubernetes untuk menilai sejauh mana pola deviasi failover time bersifat spesifik terhadap HAProxy. Berikutnya yang kedua adalah menambah variasi tingkat probabilitas kegagalan intermiten perlu diperluas agar hubungan antara tingkat kegagalan, nilai fall, dan frekuensi flapping dapat dimodelkan secara kuantitatif. Yang ketiga, menyesuaikan nilai inter dan fall berdasarkan riwayat kelaikan instance layak diteliti sebagai upaya menurunkan waktu deteksi dan laju false positive secara bersamaan. <!-- REVISI #1: "riwayat kesehatan instance" -> "riwayat kelaikan instance". -->

---

## DAFTAR PUSTAKA

<!-- REVISI #13: format nama penulis diseragamkan menjadi "Nama-belakang, Inisial." agar kunci pengurutan alfabetis terlihat jelas. Urutan angka dipertahankan. -->

[1] Annisa, A., M. Ardiana, P. N. Rahayu, T. Brian, dan M. A. Jami'in, "Performance Evaluation of Web Applications Using JMeter Load Testing for Server Capacity and Response Efficiency," *Journal of Applied Informatics and Computing*, vol. 10, no. 1, pp. 585–590, 2026. doi: 10.30871/jaic.v10i1.11840. [Diakses: 06-Agu-2026]

[2] Chaurasia, B., A. Verma, dan P. Verma, "IHFD: an improved heartbeat-based failure detector of ◊P (eventually perfect) class for partially synchronous hierarchical distributed systems," *Complex & Intelligent Systems*, 2026. doi: 10.1007/s40747-026-02423-z. [Diakses: 04-Sep-2026] <!-- REVISI #12: karakter rusak "◇" diperbaiki menjadi "◊P" dan diberi glosari "(eventually perfect)". Verifikasi embedding font ◊ saat konversi ke templat SKANIKA; bila font tidak mendukung, tulis "(eventually perfect, ◊P)". -->

[3] Čilić, I., P. Krivić, I. Podnar Žarko, dan M. Kušek, "Performance Evaluation of Container Orchestration Tools in Edge Computing Environments," *Sensors*, vol. 23, no. 8, art. 4008, 2023. doi: 10.3390/s23084008. [Diakses: 08-Agu-2026]

[4] Hanada, H., dan K. Ishibashi, "Service-Level Objective-Aware Load-Adaptive Timeout: Balancing Failure Rate and Latency in Microservices Communication," *IEEE Access*, vol. 13, pp. 137881–137895, 2025. doi: 10.1109/ACCESS.2025.3596118. [Diakses: 10-Agu-2026]

[5] HAProxy, *HAProxy version 3.2.23 – Configuration Manual*, 2026. [Daring]. Tersedia: https://docs.haproxy.org/3.2/configuration.html. [Diakses: 03-Sep-2026]

[6] Iryani, N., K. D. Ayatri, dan R. D. Wahyuningrum, "Analisis performansi high availability cluster server menggunakan heartbeat pada private cloud," *JITEL (Jurnal Ilmiah Telekomunikasi, Elektronika, dan Listrik Tenaga)*, vol. 2, no. 2, pp. 129–138, 2022. doi: 10.35313/jitel.v2.i2.2022.129-138. [Diakses: 12-Agu-2026]

[7] Khamdani, A. R., A. R. Muslikh, dan A. S. Affandi, "Comparative Analysis of Performance and Efficiency of Load Balancing Algorithms on Ingress Controller," *Jurnal Teknik Informatika (JUTIF)*, vol. 6, no. 1, pp. 453–468, 2025. doi: 10.52436/1.jutif.2025.6.1.4040. [Diakses: 14-Agu-2026]

[8] Laksono, P. A., dan S. D. Riskiono, "Analisis Perbandingan Algoritma Round Robin dan Least Connection dalam Haproxy untuk Load Balancer Server Web," *Dinamik*, vol. 30, no. 2, pp. 351–360, 2025. doi: 10.35315/dinamik.v30i2.10154. [Diakses: 16-Agu-2026]

[9] Pakrijauskas, K., dan D. Mažeika, "A Method of Transparent Graceful Failover in Low Latency Stateful Microservices," *Electronics*, vol. 11, no. 23, art. 3936, 2022. doi: 10.3390/electronics11233936. [Diakses: 18-Agu-2026]

[10] Pratama, R. K. A., dan Supatman, "Implementasi HAProxy sebagai external traffic load balancer cluster Kubernetes yang berjalan di atas Openstack," *Jurnal RESTIKOM: Riset Teknik Informatika dan Komputer*, vol. 6, no. 3, pp. 462–473, 2024. doi: 10.52005/restikom.v6i3.360. [Diakses: 20-Agu-2026]

[11] Putra, K. R., S. Umaroh, N. F. Fahrudin, dan P. W. Pandji, "Renovator: Resilience System in Microservices Architecture Using Fault Tolerance Factor," *MIND Journal*, vol. 10, no. 2, pp. 235–249, 2025. doi: 10.26760/mindjournal.v10i2.235-249. [Diakses: 22-Agu-2026]

[12] Ramasamy, B., Y. Na, W. Kim, K. Chea, dan J. Kim, "HACM: High Availability Control Method in Container-Based Microservice Applications Over Multiple Clusters," *IEEE Access*, vol. 11, pp. 3461–3471, 2023. doi: 10.1109/ACCESS.2022.3233159. [Diakses: 24-Agu-2026]

[13] Rawls, C., dan M. Amini Salehi, "Load Balancer Tuning: Comparative Analysis of HAProxy Load Balancing Methods," pracetak arXiv:2212.14198, 2022. doi: 10.48550/arXiv.2212.14198. [Diakses: 26-Agu-2026]

[14] Riskiono, S. D., dan D. Pasha, "Analisis Perbandingan Server Load Balancing dengan Haproxy & Nginx dalam Mendukung Kinerja Server E-Learning," *InComTech: Jurnal Telekomunikasi dan Komputer*, vol. 10, no. 3, pp. 135–144, 2020. doi: 10.22441/incomtech.v10i3.8751. [Diakses: 28-Agu-2026]

[15] Roberts, J., B. Archibald, dan P. Trinder, "Signalling Health for Improved Kubernetes Microservice Availability," pracetak arXiv:2507.02158, 2025. doi: 10.48550/arXiv.2507.02158. [Diakses: 30-Agu-2026]

[16] Saleh, R. F., dan Kusrini, "Analisis Perbandingan Kinerja Web Humas Infrastruktur On-Premise dan Cloud Computing dengan Load Balancer Round Robin," *MALCOM: Indonesian Journal of Machine Learning and Computer Science*, vol. 5, no. 3, pp. 1107–1116, 2025. doi: 10.57152/malcom.v5i3.2182. [Diakses: 01-Sep-2026]

[17] Saputro, V. A., dan A. Jaenul, "Evaluasi Dampak Opportunistic Wireless Encryption (OWE) terhadap Kinerja Jaringan Nirkabel IEEE 802.11ax," *SKANIKA: Sistem Komputer dan Teknik Informatika*, vol. 8, no. 1, pp. 35–45, 2025. doi: 10.36080/skanika.v8i1.3295. [Diakses: 02-Sep-2026]

[18] Sugiyatno, dan I. M, "Analisis Perbandingan Performasi Respon Waktu Web Server dan Failover Antara Kubernetes Dan Docker Swarm pada Container Orchestration," *Jurnal Informatika Komputer, Bisnis dan Manajemen*, vol. 21, no. 3, pp. 43–53, 2023. doi: 10.61805/fahma.v21i3.9. [Diakses: 09-Agu-2026]

[19] Wintolo, H., I. Riadi, dan A. Yudhana, "Analisis Deteksi Penyusup pada Layanan Open Journal System Menggunakan Metode Network Forensic Development Life Cycle," *SKANIKA: Sistem Komputer dan Teknik Informatika*, vol. 8, no. 1, pp. 133–144, 2025. doi: 10.36080/skanika.v8i1.3284. [Diakses: 17-Agu-2026]

[20] Zhang, P., L. Xiang, Z. Song, dan Y. Yang, "Adaptive load balancing and fault-tolerant microservices architecture for high-availability web systems using docker and spring cloud," *Discover Applied Sciences*, vol. 7, no. 7, art. 705, 2025. doi: 10.1007/s42452-025-07320-7. [Diakses: 31-Agu-2026]
