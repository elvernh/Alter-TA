<!--
CORE MANUSCRIPT - naskah untuk penerbit baru (2026-10-30)
Disusun dari manuscript/revised-manuscript.md (versi SKANIKA, tidak diubah).

Perubahan utama terhadap versi SKANIKA:
- Ruang lingkup dikurangi menjadi lima skenario inti (agresif, baseline, konservatif,
  flap_fall1, flap_fall5), 25 pengujian. Lihat revisions/06-core-experiment-and-comparison-2026-10-30.md.
- Seluruh angka hasil diambil dari artefak eksperimen 2026-09-26 (pilot: 2026-09-12)
  melalui haproxy-health-check-experiment/analyze_core.py dan results_recomputed.csv.
  Angka pada versi SKANIKA berasal dari naskah asli dan tidak dapat ditelusuri ke artefak.
- Ditambahkan model pembaruan untuk flapping (Persamaan 3-5) dan perbandingan dengan
  Roberts dkk. [15] (Sub bagian 3.6).
- Paragraf pertama Abstrak/Abstract dan paragraf saran pada Bagian 4 dipertahankan
  verbatim sesuai suntingan manual penulis.
- Referensi [17] Saputro dan [19] Wintolo (khusus SKANIKA) dihapus; [18] -> [17],
  [20] -> [18]. Seluruh referensi kini dirujuk dalam teks.

FORMAT RULE: istilah bahasa Inggris pada bagian berbahasa Indonesia dimiringkan saat
ekspor DOCX; abstrak bahasa Inggris tidak memakai huruf miring. Tanpa em dash;
rujukan antarbagian memakai "Sub bagian"; satuan throughput RPS (Requests per Second).
Metadata penulis DOCX: Christianto Elvern Haryanto.
-->

# Pengaruh Parameter Health Check HAProxy terhadap Failover Time dan Kinerja Microservice Berbasis Docker

Christianto Elvern Haryanto, Mychael Maoeretz Engel, Agustinus Bimo Gumelar\*

Fakultas Teknologi Informasi, Program Studi Informatika, Universitas Ciputra, Surabaya, Indonesia

E-mail: charyanto@student.ciputra.ac.id, mychael.engel@ciputra.ac.id, \*bimo.gumelar@ciputra.ac.id
  (\* : corresponding author)

---

## Abstrak

Dalam kondisi tertentu, microservice dapat mengalami failover yang mengharuskan permintaan pengguna diarahkan menuju instance microservice tertentu yang tidak dapat merespons. Kondisi tersebut menunjukkan pentingnya konfigurasi parameter health check yang tepat, karena pemeriksaan ketersediaan dan respons microservice yang terlalu sensitif, dapat menganggap gangguan sementara sebagai bentuk kegagalan layanan dan memicu proses failover secara berulang. Beberapa penelitian terdahulu membahas algoritma pembagian trafik, namun pengaruh konfigurasi parameter pemeriksaan berkala (health check) HAProxy terhadap waktu failover dan kinerja microservice masih belum banyak dikaji. Konfigurasi parameter health check menentukan seberapa cepat waktu respon HAProxy mendeteksi perubahan kondisi layanan dan melakukan pengalihan trafik, sehingga konfigurasi yang berbeda dapat menghasilkan waktu failover serta kinerja layanan yang berbeda. 
Penelitian ini menguji tiga profil parameter inter, fall, dan rise, yaitu profil agresif, profil bawaan HAProxy, dan profil konservatif, terhadap failover time, throughput, latensi, dan error rate pada microservice berbasis Docker, serta pengaruh nilai fall terhadap flapping pada kegagalan intermiten. Lima skenario pengujian dilakukan sebanyak lima kali dengan 200 pengguna virtual konkuren yang dijalankan secara otomatis. Uji Kruskal–Wallis menunjukkan perbedaan signifikan pada failover time, throughput, dan error rate, dengan failover time berkisar 317 hingga 23491 ms, sedangkan latensi tidak berbeda signifikan. Pada kegagalan intermiten, nilai fall = 1 menghasilkan sekitar 18 status transisi per pengujian dan mengeluarkan sekitar 17% kapasitas instance dari rotasi secara keliru, sedangkan nilai fall = 5 menghasilkan kurang dari satu transisi; kedua nilai tersebut sesuai dengan model probabilistik yang diusulkan. Deteksi yang lebih cepat meningkatkan throughput hingga 22%, sehingga nilai fall dipilih berdasarkan jenis kegagalan yang paling mungkin terjadi pada sistem sasaran.

**Kata kunci:** failover time, HAProxy, health check, load balancer, microservice

---

## Abstract

Under certain conditions, a microservice may experience a failover in which user requests are directed to a particular microservice instance that is unable to respond. This highlights the importance of configuring health-check parameters appropriately, as checks that are overly sensitive to microservice availability and responsiveness may interpret a temporary disruption as a service failure and repeatedly trigger the failover process. Previous studies have examined traffic-distribution algorithms; however, the effects of HAProxy's periodic health-check parameter configuration on failover time and microservice performance remain underexplored. Health-check parameter configuration determines how quickly HAProxy detects changes in service status and redirects traffic, meaning that different configurations may result in different failover times and levels of service performance.

This study examines three profiles of the inter, fall, and rise parameters, namely an aggressive profile, the HAProxy default profile, and a conservative profile, and their effects on failover time, throughput, latency, and error rate in Docker-based microservices, together with the effect of the fall value on flapping under intermittent failure. Five test scenarios were each conducted five times with 200 concurrent virtual users using an automated process. The Kruskal–Wallis test revealed significant differences in failover time, throughput, and error rate, with failover time ranging from 317 to 23,491 ms, whereas latency did not differ significantly. Under intermittent failure conditions, fall = 1 resulted in approximately 18 status transitions per test and wrongly removed about 17% of instance capacity from rotation, whereas fall = 5 resulted in fewer than one transition; both values agree with the proposed probabilistic model. Faster detection increased throughput by up to 22%; therefore, the fall value should be selected according to the type of failure most likely to occur in the target system.

**Keywords:** failover time, HAProxy, health check, load balancer, microservice

---

## 1. PENDAHULUAN

Arsitektur microservice dengan mekanisme load balancing dan failover banyak digunakan pada sistem yang menuntut ketersediaan tinggi karena memungkinkan layanan direplikasi, diskalakan, dan dipulihkan secara independen. Penelitian terdahulu menunjukkan bahwa penerapan mekanisme ketersediaan tinggi pada arsitektur microservice berbasis container dapat meningkatkan kualitas layanan dibandingkan arsitektur monolitik, sedangkan metode kendali ketersediaan tinggi pada aplikasi microservice yang tersebar pada beberapa klaster dikembangkan untuk mempersingkat waktu pemulihan layanan [18], [12], dan sistem ketahanan berbasis faktor toleransi kesalahan juga dikembangkan untuk arsitektur microservice [11]. Dalam implementasinya, load balancer berperan dalam menentukan distribusi permintaan sekaligus mengarahkan trafik dari layanan yang mengalami kegagalan menuju instance yang masih dapat melayani permintaan. HAProxy merupakan salah satu perangkat lunak load balancer yang digunakan pada lingkungan web server, container, maupun klaster orkestrasi [10]. Penelitian sebelumnya membandingkan kinerja HAProxy dan Nginx serta menunjukkan perbedaan response time dan throughput antara keduanya [14]. Penelitian lain pada HAProxy membandingkan algoritma round robin dan least connection serta menunjukkan bahwa pemilihan algoritma distribusi trafik berpengaruh terhadap kinerja server [8]. Kajian pada ingress controller juga menunjukkan bahwa perbedaan algoritma load balancing dapat mempengaruhi efisiensi dan kinerja sistem ter kontainer [7], sedangkan penelitian pada lingkungan on-premise dan cloud computing memperlihatkan bahwa penerapan load balancer berpengaruh terhadap kinerja layanan web [16]. Pengukuran failover juga telah dilakukan pada perbandingan orkestrator Kubernetes dan Docker Swarm [17] serta pada analisis kinerja high availability cluster berbasis heartbeat [6], sedangkan metode graceful failover dikembangkan untuk mengurangi gangguan pada microservice stateful berlatensi rendah [9]. Selain mekanisme distribusi trafik, penelitian mengenai deteksi kegagalan menunjukkan bahwa mekanisme pemeriksaan berkala (health check) memerlukan penyetelan yang tepat karena terdapat kompromi antara kecepatan deteksi dan ketepatan dalam menentukan status layanan. Penelitian pada pemantauan container di Kubernetes menunjukkan bahwa pemeriksaan berkala dapat mengalami keterlambatan dalam mendeteksi perubahan status, sedangkan konfigurasi pemeriksaan yang dipercepat menimbulkan deteksi kegagalan yang keliru sehingga ketersediaan layanan menurun [15]. Penelitian mengenai heartbeat-based failure detector juga menempatkan waktu deteksi dan tingkat kesalahan penilaian status sebagai persoalan penting dalam mekanisme deteksi kegagalan [2]. Meskipun penelitian terdahulu telah membahas ketersediaan tinggi, failover, algoritma distribusi trafik, dan mekanisme deteksi kegagalan, sebagian besar kajian pada HAProxy masih berfokus pada algoritma load balancing dan belum secara khusus mengukur pengaruh konfigurasi parameter health check terhadap waktu deteksi kegagalan serta kinerja layanan. Dengan demikian, masih terdapat celah penelitian antara fungsi parameter health check yang telah didefinisikan dalam dokumentasi HAProxy dan bukti empiris mengenai konsekuensi pemilihan nilai parameter tersebut terhadap perilaku sistem [5], [13].

Celah tersebut menjadi penting karena HAProxy menentukan kapan sebuah instance dianggap tidak laik menerima trafik berdasarkan konfigurasi health check. Tiga parameter utama yang menentukan proses tersebut adalah inter, fall, dan rise. Parameter inter menentukan interval antar pemeriksaan, fall menentukan jumlah kegagalan pemeriksaan berturut-turut sebelum instance dinyatakan DOWN, sedangkan rise menentukan jumlah keberhasilan pemeriksaan berturut-turut sebelum instance dinyatakan pulih [5]. Nilai inter atau fall yang kecil dapat mempercepat deteksi sehingga trafik lebih cepat dialihkan dari instance yang gagal, tetapi sensitivitas yang terlalu tinggi dapat membuat gangguan sementara dianggap sebagai kegagalan dan menyebabkan perubahan status berulang (flapping). Sebaliknya, konfigurasi yang lebih konservatif dapat mengurangi perubahan status yang tidak diperlukan, tetapi memperpanjang waktu ketika permintaan masih diarahkan menuju instance yang tidak dapat merespons, sehingga jumlah permintaan gagal meningkat dan throughput layanan menurun. Permasalahan ini menunjukkan adanya kebutuhan untuk memperoleh bukti kuantitatif mengenai kompromi antara kecepatan deteksi dan kestabilan status instance, terutama karena dokumentasi HAProxy hanya mendefinisikan fungsi dan nilai bawaan parameter tanpa memberikan dasar empiris untuk menentukan konfigurasi berdasarkan karakteristik kegagalan [5]. Oleh karena itu, penelitian ini menguji tiga profil konfigurasi health check, yaitu profil agresif, profil bawaan HAProxy, dan profil konservatif, terhadap failover time, throughput, latensi, dan error rate pada sistem microservice berbasis Docker. Penelitian ini juga mengukur frekuensi perubahan status pada kondisi kegagalan intermiten untuk mengkuantifikasi fenomena flapping. Kegagalan intermiten dinyatakan dengan probabilitas kegagalan p, yaitu peluang sebuah pemeriksaan health check menghasilkan status tidak laik pada setiap siklus pemeriksaan meskipun proses layanan tetap berjalan. Selain itu, penelitian ini membandingkan failover time empiris dengan nilai teoritis berdasarkan hubungan inter × fall, menguji model probabilistik frekuensi flapping, dan membandingkan hasilnya dengan penelitian deteksi kegagalan berbasis probe pada Kubernetes [15]. Hasil pengukuran tersebut diharapkan dapat memberikan dasar berbasis data dalam menentukan konfigurasi health check sesuai karakteristik kegagalan yang mungkin terjadi pada sistem. Penelitian selanjutnya dapat memperluas pengujian pada lingkungan Linux bare-metal, orchestrator seperti Kubernetes, serta berbagai tingkat probabilitas kegagalan intermiten untuk mengetahui generalisasi hasil dan memodelkan hubungan antara konfigurasi health check, waktu deteksi, dan frekuensi flapping secara lebih luas.

---

## 2. METODE PENELITIAN

Penelitian menggunakan pendekatan eksperimen kuantitatif dengan variabel bebas berupa profil nilai parameter health check HAProxy dan variabel terikat berupa failover time, throughput, latensi p50, latensi p95, error rate, serta frekuensi transisi status. Variabel kontrol mencakup jumlah instance layanan, alokasi sumber daya container, jumlah virtual user, durasi pengujian, serta waktu injeksi kegagalan.

Latensi p50 (persentil ke-50, setara median) menunjukkan nilai latensi yang berada di tengah distribusi hasil pengujian, yaitu 50% permintaan memiliki latensi di bawah atau sama dengan nilai tersebut dan 50% lainnya berada di atasnya. Latensi p95 (persentil ke-95) menunjukkan nilai latensi yang hanya dilampaui oleh sekitar 5% permintaan. Nilai p95 dapat digunakan sebagai metrik untuk mengevaluasi batas latensi yang ditetapkan dalam Service Level Objective (SLO) layanan [4]. Persentil ke-100 (nilai maksimum tunggal) tidak digunakan karena sangat sensitif terhadap nilai ekstrem dan dapat menghasilkan nilai yang tidak representatif terhadap distribusi latensi. Oleh karena itu, penelitian menggunakan p50 dan p95 untuk merepresentasikan nilai tengah dan latensi pada bagian distribusi yang lebih tinggi.

### 2.1. Arsitektur Lingkungan Pengujian

Lingkungan pengujian dibangun menggunakan Docker Compose dan terdiri atas satu container HAProxy, tiga container layanan yang identik, serta satu container load tester. Docker Compose membentuk jaringan bridge internal `experiment` dengan subnet 172.28.0.0/24. HAProxy menggunakan alamat 172.28.0.20, sedangkan `service1`, `service2`, dan `service3` masing-masing menggunakan alamat 172.28.0.31, 172.28.0.32, dan 172.28.0.33. Alamat IP container k6 dialokasikan secara dinamis pada subnet yang sama karena k6 hanya bertindak sebagai sumber trafik. Desain alamat IP dan aliran trafik ditunjukkan pada Gambar 1.

![Gambar 1](../[Gambar 1: gunakan kembali gambar arsitektur dari revisi7, word/media/image1.png])

**Gambar 1.** Desain alamat IP dan aliran trafik pada lingkungan pengujian berbasis Docker

Pada setiap pengulangan, k6 mengirim permintaan HTTP `GET /api` ke HAProxy pada 172.28.0.20:8080. HAProxy membagi trafik tersebut menggunakan algoritma roundrobin ke `service1`, `service2`, dan `service3` pada port 3000. Secara terpisah, HAProxy mengirim permintaan `GET /health` ke port 3000 pada setiap instance untuk menentukan status UP atau DOWN. Seluruh komunikasi berlangsung di jaringan bridge internal Docker dan tidak melewati port forwarding host.

Layanan yang diuji merupakan aplikasi Node.js sederhana dengan dua endpoint, yaitu `/api` yang mensimulasikan pekerjaan bisnis selama kurang lebih 5 ms dan `/health` yang digunakan HAProxy sebagai target health check untuk menilai kelaikan instance. Endpoint `/health` dapat dikonfigurasi untuk mengembalikan respons tidak laik secara probabilistik guna mensimulasikan kegagalan intermiten. Spesifikasi platform implementasi disajikan pada Tabel 1.

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

Docker Desktop pada macOS menjalankan seluruh container di dalam virtual machine Linux, bukan langsung pada kernel host. Untuk menjaga konsistensi antar skenario, alokasi sumber daya virtual machine ditetapkan secara eksplisit dan tidak diubah selama seluruh rangkaian eksperimen. Seluruh image container yang digunakan merupakan image ARM64 native untuk menghindari overhead emulasi, dan aplikasi lain pada host ditutup selama pengujian berlangsung.

### 2.2. Skenario Pengujian

Lima skenario konfigurasi diuji sebagaimana disajikan pada Tabel 2. Tiga skenario pertama merupakan profil konfigurasi yang diuji pada kegagalan total. Profil baseline menggunakan nilai bawaan HAProxy, yaitu inter = 2000 ms, fall = 3, dan rise = 2 [5], sehingga menjadi titik acuan konfigurasi yang paling banyak dijumpai pada penerapan nyata. Profil agresif mewakili konfigurasi yang memprioritaskan kecepatan deteksi, sedangkan profil konservatif mewakili konfigurasi yang memprioritaskan kestabilan status. Pembagian ke dalam profil kecepatan, bawaan, dan kestabilan ini sejalan dengan pembandingan konfigurasi probe bawaan dan probe cepat pada penelitian di Kubernetes [15]. Dua skenario terakhir menguji kegagalan intermiten dengan nilai fall = 1 dan fall = 5, yaitu nilai fall pada profil agresif dan konservatif, dengan nilai inter dan rise bawaan. Setiap skenario diulang lima kali sehingga total pengujian berjumlah 25 kali.

Pada dua skenario terakhir, kegagalan intermiten disimulasikan dengan mengatur endpoint `/health` agar mengembalikan status tidak laik secara acak dengan probabilitas p = 0,3 pada setiap pemeriksaan health check (bukan crash proses), sedangkan endpoint `/api` tetap melayani permintaan secara normal. Nilai p = 0,3 dipilih sebagai representasi kegagalan intermiten tingkat sedang karena cukup sering untuk memicu perubahan status berulang pada nilai fall rendah, tetapi tidak menyerupai kegagalan total. Nilai tersebut dijaga konstan pada seluruh pengulangan kedua skenario agar pengaruh nilai fall dapat dibandingkan pada tingkat probabilitas kegagalan yang sama.

**Tabel 2.** Skenario konfigurasi parameter health check

| No | Skenario | inter (ms) | fall (kali) | rise (kali) | Jenis kegagalan |
|---|---|---|---|---|---|
| 1 | agresif | 500 | 1 | 1 | Total (crash) |
| 2 | baseline | 2000 | 3 | 2 | Total (crash) |
| 3 | konservatif | 5000 | 5 | 5 | Total (crash) |
| 4 | flap_fall1 | 2000 | 1 | 2 | Intermiten (p = 0,3 per check) |
| 5 | flap_fall5 | 2000 | 5 | 2 | Intermiten (p = 0,3 per check) |

### 2.3. Prosedur Pengujian dan Pengukuran

Setiap pengulangan mengikuti urutan yang sama dengan konfigurasi HAProxy yang dibangkitkan dari templat sesuai nilai parameter skenario. Seluruh stack container akan dibangun ulang, kemudian sistem dibiarkan menghangat selama 15 detik. Load test, yaitu pengujian kapasitas server melalui pembangkitan permintaan secara serentak [1], dijalankan selama 120 detik dengan 200 virtual user yang berjalan secara konkuren menggunakan executor constant-vus. Setiap virtual user mengirim permintaan `GET /api` secara berulang tanpa jeda, sehingga jumlah pengguna aktif tetap 200 sepanjang pengujian. Pada detik ke-30 satu dari tiga instance dihentikan menggunakan perintah `docker kill`, dan pada detik ke-90 instance tersebut dipulihkan. Perintah `docker kill` dipilih dibanding `docker stop` karena keduanya mengirim sinyal yang berbeda ke proses utama container. Perintah `docker stop` mengirim sinyal SIGTERM (signal terminate), yaitu permintaan agar proses berhenti secara teratur (graceful shutdown), dan baru mengirim SIGKILL apabila proses belum berhenti setelah tenggang waktu bawaan 10 detik. Pada layanan yang diuji, proses Node.js berjalan sebagai PID 1 tanpa penanganan SIGTERM sehingga sinyal tersebut diabaikan dan layanan tetap merespons pemeriksaan health check selama tenggang waktu, yang mengaburkan titik awal kegagalan. Sebaliknya, `docker kill` secara bawaan mengirim SIGKILL yang tidak dapat ditangkap atau diabaikan oleh proses, sehingga container berhenti seketika dan titik awal kegagalan dapat ditentukan secara tepat.

Failover time diukur sebagai selisih dua timestamp yang keduanya bersumber dari clock Docker daemon yang sama untuk menghindari clock skew antara sistem operasi host dan virtual machine tempat Docker Engine berjalan. Timestamp pertama adalah waktu berhentinya container yang diperoleh dari atribut `State.FinishedAt` melalui perintah `docker inspect`. Timestamp kedua adalah waktu HAProxy menandai instance sebagai tidak laik (DOWN), yang diperoleh dari baris log berpola `"Server ... is DOWN"` pada keluaran `docker logs -t`. Pada fall = 1, HAProxy dapat mencatat status DOWN beberapa saat sebelum Docker mencatat `State.FinishedAt`; selisih negatif hingga 100 ms dicatat sebagai 0 ms. Nilai teoretis failover time dihitung menggunakan Persamaan (1).

$$t_\text{teoretis} = inter \times fall \qquad (1)$$

Karena titik kegagalan instance dapat jatuh di mana saja di dalam siklus pemeriksaan, failover time empiris diprediksi berada pada rentang yang dinyatakan Persamaan (2), dengan `t_ovh` merupakan overhead deteksi berupa durasi pemeriksaan itu sendiri.

$$inter \times (fall - 1) \le t_\text{empiris} \le inter \times fall + t_\text{ovh} \qquad (2)$$

Pada skenario kegagalan intermiten, failover time tidak dapat didefinisikan karena tidak terdapat titik kegagalan tunggal. Metrik yang dicatat pada kedua skenario tersebut adalah frekuensi transisi status instance, yaitu jumlah perpindahan status UP dan DOWN yang terekstraksi dari log HAProxy selama jendela load test, serta total durasi instance berstatus DOWN. Karena endpoint `/api` pada instance tersebut tetap melayani permintaan, setiap status DOWN pada skenario ini merupakan penandaan yang keliru. Kapasitas yang hilang akibat penandaan keliru dinyatakan sebagai proporsi waktu-instance di luar rotasi, yaitu durasi DOWN dibagi tiga kali panjang jendela pengujian.

Apabila setiap pemeriksaan gagal secara independen dengan probabilitas p, waktu rata-rata instance bertahan pada status UP sama dengan waktu tunggu hingga terjadi fall kegagalan berturut-turut, sedangkan waktu rata-rata pada status DOWN sama dengan waktu tunggu hingga terjadi rise keberhasilan berturut-turut. Keduanya dinyatakan pada Persamaan (3) dan (4).

$$T_\text{UP} = inter \times \frac{1 - p^{fall}}{(1 - p)\, p^{fall}} \qquad (3)$$

$$T_\text{DOWN} = inter \times \frac{1 - (1 - p)^{rise}}{p\, (1 - p)^{rise}} \qquad (4)$$

Satu siklus UP dan DOWN menghasilkan dua transisi, sehingga jumlah transisi yang diharapkan selama jendela pengujian W dan proporsi waktu DOWN dinyatakan pada Persamaan (5).

$$N_\text{transisi} = \frac{2W}{T_\text{UP} + T_\text{DOWN}}, \qquad f_\text{DOWN} = \frac{T_\text{DOWN}}{T_\text{UP} + T_\text{DOWN}} \qquad (5)$$

### 2.4. Pipeline Otomasi

Seluruh tahapan dijalankan oleh skrip otomasi tanpa intervensi manual, mencakup substitusi konfigurasi HAProxy, pembangunan ulang stack container, eksekusi load test, injeksi kegagalan, pemulihan instance, ekstraksi metrik dari ringkasan load tester dan log HAProxy, hingga penyimpanan hasil ke berkas CSV. Alur satu pengulangan disajikan pada Algoritma 1. Otomasi penuh diperlukan agar ke-25 pengujian (5 skenario × 5 pengulangan, lihat Sub bagian 2.2) dijalankan dengan prosedur yang identik sehingga variasi hasil tidak bersumber dari perbedaan perlakuan antar pengulangan. Seluruh artefak mentah setiap pengulangan, termasuk log HAProxy, ringkasan dan data mentah k6, serta versi image, disimpan untuk keperluan audit.

**Algoritma 1.** Pipeline otomasi untuk satu pengulangan

| Baris | Langkah | Keterangan |
|---|---|---|
| Masukan | skenario s = (inter, fall, rise, jenis_kegagalan); indeks pengulangan r | |
| Keluaran | satu baris metrik pada `results.csv` | |
| 1 | Render `haproxy.cfg` dari templat dengan nilai (inter, fall, rise, timeout = 100 ms) | Konfigurasi skenario |
| 2 | `docker compose down -v`; `docker compose up -d --build` | Bangun ulang stack |
| 3 | Tunggu 15 detik | Warm-up |
| 4 | Jalankan k6 (constant-vus, 200 VU, 120 s) secara asynchronous | Mulai load test |
| 5 | Jika jenis_kegagalan = total: pada t = 30 s `docker kill service3`, pada t = 90 s `docker start service3` | Injeksi kegagalan dan pemulihan |
| 6 | Tunggu proses k6 selesai | |
| 7 | kill_ts ← `docker inspect -f '{{.State.FinishedAt}}' service3` | Waktu container berhenti |
| 8 | down_ts ← timestamp baris "is DOWN" pertama setelah kill_ts dari `docker logs -t haproxy` | Waktu status DOWN |
| 9 | failover_ms ← (down_ts − kill_ts) dalam milidetik | Failover time |
| 10 | (throughput, p50, p95, error_rate) ← parse ringkasan JSON k6 | Metrik kinerja |
| 11 | Jika jenis_kegagalan = intermiten: transisi dan durasi DOWN ← perpindahan UP ↔ DOWN pada jendela load test; failover_ms ← N/A | Skenario flapping |
| 12 | Tambahkan baris (s, r, throughput, p50, p95, error_rate, failover_ms, transisi) ke `results.csv` | Simpan hasil |

### 2.5. Pilot Study sebagai Gerbang Validasi

Sebelum pilot study, dilakukan pemeriksaan kesiapan pipeline (uji asap) untuk memastikan seluruh tahap otomasi berjalan penuh dan setiap metrik dapat diekstraksi; temuan pada tahap ini dilaporkan pada Sub bagian 3.1.

Pilot study dilaksanakan sebagai gerbang validasi sebelum pengujian utama menggunakan konfigurasi baseline dengan tiga pengulangan. Pengujian utama dilaksanakan apabila kelima kriteria berikut terpenuhi: (1) failover time dapat diekstraksi dari log pada seluruh pengulangan; (2) selisih failover time antar pengulangan tidak melebihi satu kali nilai inter; (3) penggunaan CPU container load tester berada di bawah 80% dari total alokasi 8 CPU sehingga load tester tidak menjadi bottleneck; (4) error terkonsentrasi di sekitar periode kegagalan, bukan tersebar sepanjang pengujian; dan (5) pipeline otomasi berjalan penuh tanpa intervensi manual.

### 2.6. Teknik Analisis Data

Data dianalisis menggunakan statistik deskriptif berupa rata-rata dan standar deviasi per skenario. Karena setiap skenario diulang lima kali dan distribusi metrik kinerja tidak dapat diasumsikan normal, uji signifikansi menggunakan statistik non-parametrik pada taraf signifikansi α = 0,05, yaitu perbedaan dinyatakan signifikan apabila p-value < 0,05. P-value merupakan peluang memperoleh perbedaan sebesar yang teramati apabila sebenarnya tidak terdapat perbedaan antar skenario. Perbedaan antar tiga profil kegagalan total diuji dengan uji Kruskal-Wallis dan, apabila signifikan, dilanjutkan dengan uji post-hoc Dunn dengan koreksi Bonferroni. Besaran praktis perbedaan dilaporkan menggunakan effect size epsilon-squared (ε²). Perbedaan antara dua skenario kegagalan intermiten diuji dengan uji Mann-Whitney U eksak dua sisi dengan effect size korelasi rank-biserial (r). Selain itu, failover time empiris dibandingkan terhadap nilai teoretis pada Persamaan (1) dan (2), sedangkan frekuensi transisi dan proporsi waktu DOWN dibandingkan terhadap prediksi Persamaan (3) sampai (5).

---

## 3. HASIL DAN PEMBAHASAN

### 3.1. Hasil Pilot Study

Seluruh kriteria gerbang validasi terpenuhi. Failover time berhasil diekstraksi pada ketiga pengulangan dengan nilai 5907 ms, 5870 ms, dan 5937 ms, sehingga selisih maksimum antar pengulangan hanya 67 ms atau jauh di bawah ambang satu kali nilai inter sebesar 2000 ms; kriteria 1 dan 2 dengan demikian terpenuhi. Ketiga nilai tersebut berada dalam rentang prediksi Persamaan (2), yaitu 4000 ms hingga 6000 ms ditambah overhead pemeriksaan. Penggunaan CPU container load tester sepanjang pengujian tetap berada di bawah ambang 80% dari alokasi CPU sehingga load tester tidak menjadi bottleneck (kriteria 3). Latensi median stabil pada 6,26 sampai 6,51 ms dan error rate pada 0,022 sampai 0,024%. Throughput pada dua pengulangan pertama sebesar 28494 dan 29283 RPS, sedangkan pengulangan ketiga lebih rendah, yaitu 18677 RPS. Penurunan tersebut tidak disertai perubahan failover time maupun error rate sehingga tidak memengaruhi validitas pengukuran deteksi, tetapi menjadi dasar untuk menutup seluruh aplikasi lain pada host selama pengujian utama. Seluruh 2313 permintaan gagal pada ketiga pengulangan pilot tercatat antara sekitar 0,41 detik setelah instance dimatikan hingga sesaat setelah HAProxy menandainya DOWN, tanpa satu pun error di luar jendela tersebut, sehingga error merupakan konsekuensi langsung dari kegagalan yang diinjeksikan dan bukan gejala ketidakstabilan lingkungan uji (kriteria 4). Pola yang sama juga berlaku pada seluruh 15 pengujian kegagalan total pada pengujian utama. Dengan seluruh kriteria pada Sub bagian 2.5 terpenuhi, termasuk kriteria 5 karena pipeline berjalan tanpa intervensi manual, pengujian utama dilanjutkan. Ringkasan hasil pilot study disajikan pada Tabel 3.

**Tabel 3.** Hasil pilot study pada konfigurasi baseline (inter = 2000 ms, fall = 3, rise = 2)

| Rep | Throughput (RPS) | Latensi p50 (ms) | Latensi p95 (ms) | Error rate (%) | Failover time (ms) |
|---|---|---|---|---|---|
| 1 | 28493,57 | 6,46 | 8,47 | 0,022 | 5907 |
| 2 | 29282,83 | 6,26 | 8,26 | 0,022 | 5870 |
| 3 | 18677,37 | 6,51 | 10,03 | 0,024 | 5937 |

Keterangan: RPS = Requests per Second, yaitu jumlah permintaan HTTP yang diproses per detik.

Pada pemeriksaan kesiapan pipeline sebelum pilot study ditemukan bahwa nilai bawaan timeout connect HAProxy sebesar 2 detik menyebabkan setiap pemeriksaan health check yang gagal ikut menunggu penuh durasi timeout tersebut alih-alih gagal seketika, sehingga failover time terukur mencapai dua kali lipat nilai teoretis. Setelah timeout connect dan timeout check diturunkan menjadi 100 ms, nilai yang aman karena seluruh komunikasi terjadi dalam jaringan Docker internal dengan latensi milidetik, failover time kembali sesuai rentang teoretis. Temuan ini menunjukkan bahwa parameter timeout perlu diperlakukan sebagai bagian dari konfigurasi health check, bukan sebagai pengaturan terpisah.

### 3.2. Statistik Deskriptif

Tabel 4 merangkum rata-rata dan standar deviasi metrik pada lima skenario dengan lima pengulangan per skenario. Nilai failover time pada dua skenario flapping tidak tersedia karena skenario tersebut tidak melibatkan kegagalan total yang dapat diukur waktu deteksinya.

**Tabel 4.** Statistik deskriptif per skenario (rata-rata ± standar deviasi, n = 5)

| Skenario | Throughput (RPS) | Latensi p50 (ms) | Latensi p95 (ms) | Error rate (%) | Failover (ms) |
|---|---|---|---|---|---|
| agresif | 30046,7 ± 1294,2 | 6,44 ± 0,29 | 8,47 ± 0,55 | 0,003 ± 0,001 | 317,0 ± 21,7 |
| baseline | 29063,2 ± 1463,9 | 6,45 ± 0,36 | 8,51 ± 0,54 | 0,017 ± 0,002 | 4352,8 ± 42,3 |
| konservatif | 24625,7 ± 606,3 | 6,38 ± 0,19 | 8,38 ± 0,27 | 0,095 ± 0,003 | 23490,8 ± 18,6 |
| flap_fall1 | 30596,8 ± 866,8 | 6,38 ± 0,22 | 8,24 ± 0,25 | 0,000 ± 0,000 | – |
| flap_fall5 | 30688,5 ± 1196,6 | 6,34 ± 0,26 | 8,27 ± 0,49 | 0,000 ± 0,000 | – |

Keterangan: RPS = Requests per Second, yaitu jumlah permintaan HTTP yang diproses per detik. Konfigurasi parameter setiap skenario mengacu pada Tabel 2.

Terdapat hubungan yang konsisten antara kecepatan deteksi dan dampak kegagalan terhadap pengguna. Profil konservatif menghasilkan throughput terendah sebesar 24625,7 RPS dengan error rate tertinggi sebesar 0,095%, sedangkan profil agresif mempertahankan throughput 30046,7 RPS dengan error rate 0,003%, sehingga throughput profil agresif 22,0% lebih tinggi dan error rate-nya sekitar 30 kali lebih rendah. Perbedaan ini bersumber dari lamanya periode ketika load balancer masih mengarahkan trafik ke instance yang sudah mati. Selisih throughput antara kedua profil setara dengan sekitar 650 ribu permintaan selama 120 detik, atau sekitar 92% throughput profil agresif apabila seluruhnya terjadi dalam jendela deteksi 23,5 detik pada profil konservatif. Besaran ini mengindikasikan bahwa selama jendela deteksi sebagian besar virtual user tertahan pada permintaan yang diarahkan ke instance mati hingga upaya koneksi HAProxy gagal. Permintaan gagal pertama pada setiap pengujian tercatat sekitar 0,41 detik setelah instance dimatikan, sesuai dengan empat upaya koneksi, yaitu satu upaya awal dan tiga retries bawaan HAProxy [5], yang masing-masing dibatasi timeout connect 100 ms. Akibatnya, dampak keterlambatan deteksi terhadap throughput jauh lebih besar daripada dampaknya terhadap jumlah permintaan yang gagal. Sebaliknya, latensi p50 dan p95 pada kelima skenario berada pada kisaran yang sama, yaitu 6,3 sampai 6,5 ms dan 8,2 sampai 8,5 ms, karena permintaan yang berhasil dilayani tetap diproses oleh instance yang laik. Throughput dan failover time setiap profil ditunjukkan pada Gambar 2.

![Gambar 2](../[Gambar 2: digambar dari Tabel 4 saat ekspor DOCX; batang throughput per skenario dan batang failover time profil agresif, baseline, konservatif dengan garis nilai teoretis inter × fall])

**Gambar 2.** Throughput (RPS) per skenario dan failover time per profil terhadap nilai teoretis inter × fall (rata-rata ± standar deviasi, data pada Tabel 4 dan Tabel 7)

### 3.3. Uji Signifikansi Statistik

Hasil uji Kruskal-Wallis antar tiga profil kegagalan total disajikan pada Tabel 5. Throughput, error rate, dan failover time berbeda signifikan antar profil pada taraf α = 0,05, sedangkan latensi p50 dan p95 tidak berbeda signifikan.

**Tabel 5.** Hasil uji Kruskal-Wallis antar profil agresif, baseline, dan konservatif (n = 5 per profil)

| Metrik | H | p-value | ε² | Kesimpulan |
|---|---|---|---|---|
| Throughput | 10,22 | 0,0060 | 0,730 | Signifikan |
| Latensi p50 | 0,06 | 0,9704 | 0,004 | Tidak signifikan |
| Latensi p95 | 0,32 | 0,8521 | 0,023 | Tidak signifikan |
| Error rate | 12,50 | 0,0019 | 0,893 | Signifikan |
| Failover time | 12,50 | 0,0019 | 0,893 | Signifikan |

Effect size yang besar pada throughput, error rate, dan failover time (ε² ≥ 0,73) menunjukkan bahwa pemilihan profil health check bukan sekadar berpengaruh secara statistik, melainkan juga substansial secara praktis. Nilai H = 12,50 pada error rate dan failover time merupakan nilai maksimum untuk tiga kelompok berukuran lima, yang berarti kelima pengulangan setiap profil terpisah sepenuhnya tanpa tumpang tindih. Sebaliknya, effect size pada latensi mendekati nol, yang menunjukkan bahwa parameter health check memengaruhi ketersediaan layanan, bukan kecepatan respons permintaan yang berhasil dilayani.

Uji post-hoc Dunn dengan koreksi Bonferroni disajikan pada Tabel 6. Pada ketiga metrik yang signifikan, hanya pasangan agresif dan konservatif yang berbeda signifikan. Pasangan yang bersebelahan, yaitu agresif dengan baseline dan baseline dengan konservatif, tidak mencapai signifikansi meskipun urutan nilainya konsisten pada seluruh pengulangan. Hal ini mencerminkan keterbatasan daya uji lima pengulangan per kelompok setelah koreksi Bonferroni, bukan ketiadaan perbedaan, karena failover time ketiga profil tidak saling tumpang tindih sama sekali (Tabel 4).

**Tabel 6.** Nilai p-value uji Dunn terkoreksi Bonferroni

| Pasangan profil | Throughput | Error rate | Failover time |
|---|---|---|---|
| agresif – baseline | 1,0000 | 0,2313 | 0,2313 |
| agresif – konservatif | 0,0056 | 0,0012 | 0,0012 |
| baseline – konservatif | 0,0851 | 0,2313 | 0,2313 |

### 3.4. Perbandingan Failover Time Empiris dan Teoretis

Bagian ini membandingkan failover time hasil pengukuran (empiris) dengan nilai teoretis inter × fall pada Persamaan (1). Selisih antara keduanya selanjutnya disebut deviasi, dinyatakan dalam milidetik dan dalam persen terhadap nilai teoretis. Tabel 7 menyajikan perbandingan tersebut. Pada ketiga profil, failover time empiris lebih cepat dari nilai teoretis dan berada di dalam rentang Persamaan (2). Nilai teoretis inter × fall mengasumsikan kasus terburuk, yaitu kegagalan terjadi tepat setelah pemeriksaan terakhir yang berhasil, sehingga pemeriksaan gagal pertama baru terjadi satu interval penuh kemudian.

**Tabel 7.** Perbandingan failover time empiris dan teoretis

| Skenario | Empiris (ms) | Teoretis (ms) | Rentang Persamaan (2) (ms) | Deviasi (ms) | Deviasi (%) |
|---|---|---|---|---|---|
| agresif | 317,0 | 500 | 0 – 500 + t_ovh | −183,0 | −36,6 |
| baseline | 4352,8 | 6000 | 4000 – 6000 + t_ovh | −1647,2 | −27,5 |
| konservatif | 23490,8 | 25000 | 20000 – 25000 + t_ovh | −1509,2 | −6,0 |

Besaran deviasi absolut ditentukan oleh posisi titik kegagalan di dalam siklus pemeriksaan, yaitu jarak antara waktu instance dimatikan dan pemeriksaan berikutnya. Pada ketiga profil deviasi absolut bernilai sekitar 0,3 hingga 0,8 kali nilai inter, sehingga deviasi relatif mengecil ketika nilai teoretis membesar, yaitu −36,6% pada profil agresif dan −6,0% pada profil konservatif. Standar deviasi failover time yang sangat kecil, yaitu 18,6 hingga 42,3 ms, menunjukkan bahwa posisi tersebut hampir sama pada setiap pengulangan karena kegagalan selalu diinjeksikan pada detik ke-30 setelah stack dibangun ulang. Hal ini dikonfirmasi oleh pilot study: dengan konfigurasi baseline yang identik, failover time pada sesi pilot berkisar 5870 hingga 5937 ms, sedangkan pada pengujian utama berkisar 4330 hingga 4428 ms. Kedua sesi konsisten secara internal dan berada di dalam rentang Persamaan (2), tetapi berbeda sekitar 1,5 detik karena fase pemeriksaan terhadap titik kegagalan berbeda antar sesi. Dengan demikian, Persamaan (2) lebih tepat digunakan sebagai prediksi failover time daripada Persamaan (1), dan nilai rata-rata pada satu sesi pengujian tidak boleh dibaca sebagai nilai harapan untuk titik kegagalan yang acak.

### 3.5. Trade-off Nilai fall Rendah terhadap Flapping

Skenario flap_fall1 dan flap_fall5 dirancang untuk mengukur perilaku sistem terhadap kegagalan intermiten tanpa crash total. Metrik yang relevan adalah frekuensi transisi status UP dan DOWN serta durasi status DOWN yang diekstraksi dari log HAProxy selama jendela load test, sebagaimana disajikan pada Tabel 8.

**Tabel 8.** Transisi status dan durasi DOWN instance per pengujian selama jendela load test 120 detik

| Pengulangan | flap_fall1 transisi | flap_fall1 DOWN (s) | flap_fall5 transisi | flap_fall5 DOWN (s) |
|---|---|---|---|---|
| 1 | 22 | 74,0 | 0 | 0,0 |
| 2 | 18 | 57,9 | 0 | 0,0 |
| 3 | 12 | 55,9 | 0 | 0,0 |
| 4 | 18 | 54,0 | 2 | 4,0 |
| 5 | 20 | 68,0 | 0 | 0,0 |
| Rata-rata ± SD | 18,0 ± 3,7 | 62,0 ± 8,6 | 0,4 ± 0,9 | 0,8 ± 1,8 |
| Prediksi Persamaan (5) | 17,6 | 61,2 | 0,2 | 0,7 |
| Kapasitas pool di luar rotasi | 17,2% | | 0,2% | |

Dengan fall = 1, satu kegagalan pemeriksaan sudah cukup untuk menandai instance sebagai DOWN, sehingga probabilitas kegagalan p = 0,3 per pemeriksaan langsung diterjemahkan menjadi transisi status yang sering, yaitu rata-rata 18,0 transisi per pengujian atau kurang lebih satu transisi setiap tujuh detik. Instance yang sebenarnya tetap mampu melayani permintaan berada di luar rotasi selama rata-rata 62,0 detik, atau sekitar separuh jendela pengujian, sehingga 17,2% kapasitas waktu-instance pool hilang akibat penandaan yang keliru. Sebaliknya, dengan fall = 5, instance baru ditandai DOWN setelah lima kegagalan berturut-turut yang pada probabilitas kegagalan independen p = 0,3 memiliki peluang kejadian sekitar 0,24%, sehingga hanya satu siklus DOWN dan UP yang teramati pada lima pengulangan. Uji Mann-Whitney U eksak menunjukkan bahwa perbedaan jumlah transisi dan kapasitas pool di luar rotasi antara kedua skenario signifikan (U = 25, p-value = 0,0079, r = 1,00 untuk keduanya), yaitu nilai p-value terkecil yang mungkin untuk dua kelompok berukuran lima.

Model pada Persamaan (3) sampai (5) memprediksi hasil tersebut dengan baik. Untuk flap_fall1, Persamaan (3) dan (4) menghasilkan T_UP = 6,67 detik dan T_DOWN = 6,94 detik, sehingga diperoleh prediksi 17,6 transisi dan 61,2 detik status DOWN per 120 detik, sangat dekat dengan hasil pengukuran 18,0 transisi dan 62,0 detik. Untuk flap_fall5, T_UP mencapai sekitar 1173 detik sehingga prediksi hanya 0,2 transisi per pengujian, sejalan dengan hasil pengukuran 0,4 transisi. Kesesuaian ini menunjukkan bahwa frekuensi flapping dapat diperkirakan sebelum penerapan dari empat besaran yang dapat diketahui operator, yaitu inter, fall, rise, dan perkiraan probabilitas kegagalan pemeriksaan p. Sebagai ilustrasi, model yang sama memprediksi sekitar 2,2 transisi per 120 detik dan sekitar 2,1% kapasitas pool di luar rotasi untuk nilai bawaan fall = 3 pada p = 0,3; nilai ini merupakan prediksi model dan tidak diukur pada penelitian ini.

Temuan ini mengkuantifikasi kompromi yang selama ini hanya dinyatakan secara kualitatif: menurunkan nilai fall mempercepat deteksi kegagalan total sebagaimana ditunjukkan Tabel 7, namun secara signifikan meningkatkan kerentanan terhadap flapping pada kondisi kegagalan intermiten. Throughput, error rate, dan latensi p95 kedua skenario tidak berbeda signifikan (p-value = 1,0000 untuk ketiganya) karena load balancer tetap mengalihkan trafik ke dua instance laik-layan lainnya selama instance ketiga berstatus DOWN, dan kedua instance tersebut masih memiliki kapasitas yang cukup untuk menampung beban. Meskipun demikian, frekuensi transisi yang tinggi tetap relevan secara operasional karena mengurangi cadangan kapasitas yang tersedia apabila terjadi kegagalan kedua dan berpotensi memicu alerting berlebihan pada sistem pemantauan produksi. Hasil ini sejalan dengan literatur pendeteksi kegagalan yang menyatakan bahwa penurunan waktu deteksi cenderung menaikkan laju kesalahan penilaian status [2], sekaligus perlu dibaca dengan catatan bahwa kompromi tersebut dapat dilonggarkan apabila ambang deteksi ditetapkan secara adaptif terhadap kondisi beban [4].

![Gambar 3](../[Gambar 3: digambar dari Tabel 8 saat ekspor DOCX; transisi per pengulangan untuk flap_fall1 dan flap_fall5 dengan garis prediksi Persamaan (5)])

**Gambar 3.** Jumlah transisi status per pengulangan pada flap_fall1 dan flap_fall5 terhadap prediksi Persamaan (5) (data pada Tabel 8)

### 3.6. Perbandingan dengan Penelitian Terdahulu

Hasil penelitian ini dibandingkan dengan penelitian Roberts dkk. [15] yang mengukur waktu deteksi kegagalan dan dampak deteksi yang keliru pada pemantauan container berbasis probe di Kubernetes. Penelitian tersebut dipilih karena memiliki rancangan yang paling mendekati, yaitu membandingkan konfigurasi bawaan dan konfigurasi cepat dari mekanisme pemeriksaan berkala setelah proses layanan dihentikan di bawah beban, serta membandingkan hasil pengukuran dengan model waktu deteksi. Perbandingan disajikan pada Tabel 9.

**Tabel 9.** Perbandingan dengan penelitian deteksi kegagalan berbasis probe pada Kubernetes [15]

| Aspek | Penelitian ini | Roberts dkk. [15] |
|---|---|---|
| Platform | Docker Compose, HAProxy 3.2, tiga replika layanan | Kubernetes 1.27.8 satu node, CRI-O, satu replika per layanan |
| Mekanisme pemeriksaan | HTTP health check aktif oleh load balancer (`GET /health`) | Liveness dan readiness probe oleh kubelet |
| Konfigurasi cepat | inter = 500 ms, fall = 1 (agresif) | periode 1 s, ambang 1 kegagalan |
| Konfigurasi bawaan | inter = 2000 ms, fall = 3 (baseline) | periode 3 s, ambang 3 kegagalan (liveness) |
| Injeksi kegagalan | SIGKILL pada detik ke-30; `/health` gagal dengan p = 0,3 | proses dihentikan pada detik ke-60 |
| Beban | k6, 200 virtual user konstan, sekitar 24600 sampai 30700 RPS | Locust, dibatasi 100 permintaan per detik |
| Pengulangan dan resolusi waktu | 5 pengulangan, milidetik | 30 pengulangan, detik |
| Waktu deteksi konfigurasi cepat | 0,32 ± 0,02 s | 0,7 ± 0,5 s |
| Waktu deteksi konfigurasi bawaan | 4,35 ± 0,04 s | 8,7 ± 0,5 s |
| Model terhadap hasil pengukuran | pengukuran 6,0% sampai 36,6% lebih cepat dari inter × fall | pengukuran 8,7 s terhadap prediksi 7,7 s (13% lebih lambat) |
| Deteksi keliru pada konfigurasi cepat | 18,0 transisi per 120 s; 17,2% kapasitas pool di luar rotasi | 2 sampai 6 restart (rata-rata 3 ± 1) terhadap 2 yang diharapkan; ketersediaan 4% lebih rendah |
| Dampak deteksi keliru terhadap permintaan | tidak signifikan terhadap throughput dan error rate | tambahan respons HTTP 500 dan permintaan gagal |
| Uji statistik | Kruskal-Wallis, Dunn, Mann-Whitney U | rata-rata dan standar deviasi |

Perbandingan tersebut menghasilkan tiga temuan. Pertama, kedua penelitian menunjukkan bahwa hasil kali periode pemeriksaan dan ambang kegagalan menentukan waktu deteksi, dengan rasio waktu deteksi konfigurasi bawaan terhadap konfigurasi cepat sekitar 14 kali pada penelitian ini dan 12 kali pada [15]. Health check HAProxy mencapai waktu deteksi di bawah satu detik karena interval pemeriksaan dapat ditetapkan dalam milidetik, sedangkan konfigurasi tercepat pada [15] menggunakan periode 1 detik. Kedua, kedua penelitian sama-sama menemukan deviasi antara model dan hasil pengukuran yang bersumber dari posisi titik kegagalan di dalam siklus pemeriksaan, tetapi dengan arah yang berlawanan. Pada [15], hasil pengukuran lebih lambat dari prediksi karena latensi probe dan proses restart ditambahkan setelah deteksi, sedangkan pada penelitian ini hasil pengukuran lebih cepat dari inter × fall karena pemeriksaan pertama setelah instance mati sudah dihitung sebagai kegagalan dan nilai inter × fall merupakan kasus terburuk. Ketiga, biaya deteksi keliru ditentukan oleh tindakan yang diambil mekanisme pemeriksaan. Pada [15], liveness probe yang keliru memicu restart container sehingga ketersediaan turun dan permintaan gagal bertambah. Pada penelitian ini, status DOWN yang keliru hanya mengeluarkan satu dari tiga replika dari rotasi sehingga dengan kapasitas cadangan yang memadai tidak terjadi kehilangan permintaan, dan biaya flapping muncul sebagai berkurangnya cadangan kapasitas serta tingginya frekuensi perubahan status. Penelitian ini juga melengkapi [15] dengan model yang memprediksi frekuensi deteksi keliru, bukan hanya waktu deteksi.

### 3.7. Rekomendasi Konfigurasi Berbasis Data

Berdasarkan keseluruhan hasil, tiga profil kebutuhan konfigurasi dapat dirumuskan sebagaimana disajikan pada Tabel 10. Rekomendasi bersifat kondisional terhadap karakteristik kegagalan yang diantisipasi pada sistem produksi dan terhadap kapasitas cadangan yang tersedia. Apabila kegagalan yang dominan berupa crash total seperti OOM kill atau panic proses dan sinyal health check dapat diandalkan, profil latency-sensitive lebih sesuai. Apabila kegagalan yang dominan berupa degradasi kinerja intermiten seperti jeda garbage collection atau kontensi sumber daya sesaat, profil stability-sensitive lebih sesuai untuk menghindari flapping yang tidak perlu. Untuk kondisi di antara keduanya, Persamaan (3) sampai (5) dapat digunakan untuk memperkirakan frekuensi flapping dari probabilitas kegagalan pemeriksaan yang teramati sebelum nilai fall ditetapkan.

**Tabel 10.** Rekomendasi konfigurasi berdasarkan profil kebutuhan

| Profil | Rekomendasi | Justifikasi berbasis hasil |
|---|---|---|
| Latency-sensitive | inter ≤ 500 ms, fall = 1 | Failover 317 ms, error rate 0,003%, throughput tertinggi; pada kegagalan intermiten p = 0,3 menghasilkan 18,0 transisi per 120 s dan 17,2% kapasitas di luar rotasi, sehingga hanya sesuai bila tersedia kapasitas cadangan |
| Balanced | inter = 2000 ms, fall = 3, rise = 2 (bawaan HAProxy) | Failover 4,35 s dan error rate 0,017%; model memprediksi sekitar 2,2 transisi per 120 s pada p = 0,3 |
| Stability-sensitive | inter sedang hingga besar, fall ≥ 5 | Transisi status mendekati nol (0,4 pada flap_fall5) dengan konsekuensi failover 23,5 s, error rate 0,095%, dan throughput 18,0% lebih rendah dari profil agresif |

### 3.8. Keterbatasan Penelitian

Pengujian dilakukan pada satu perangkat dengan Docker Desktop pada macOS yang menjalankan container di dalam virtual machine Linux, sehingga terdapat lapisan virtualisasi tambahan yang tidak ada pada deployment Linux bare-metal. Karena seluruh pengukuran failover time bersumber dari log internal HAProxy dan clock Docker daemon yang konsisten, lapisan tersebut tidak mempengaruhi validitas pengukuran failover time, melainkan membatasi generalisasi nilai absolut throughput dan latensi, karena kinerja container bergantung pada lingkungan dan alat orkestrasi tempat container dijalankan [3]. Kegagalan total selalu diinjeksikan pada detik ke-30, sehingga posisi titik kegagalan di dalam siklus pemeriksaan hampir sama pada setiap pengulangan dalam satu sesi (Sub bagian 3.4); pengacakan waktu injeksi dalam rentang satu interval pemeriksaan diperlukan untuk memperoleh distribusi failover time yang mewakili titik kegagalan acak. Load test menggunakan model beban tertutup dengan jumlah virtual user tetap, sehingga virtual user yang tertahan pada instance mati menurunkan laju permintaan berikutnya dan dapat memperbesar dampak keterlambatan deteksi terhadap throughput dibandingkan beban terbuka dengan laju kedatangan tetap. Ketiga profil mengubah inter, fall, dan rise secara bersamaan sehingga kontribusi masing-masing parameter tidak dipisahkan; pengaruh parameter secara individual dan waktu pemulihan yang ditentukan oleh rise belum dianalisis. Selain itu, kegagalan intermiten hanya disimulasikan pada satu tingkat probabilitas, yaitu p = 0,3 per pemeriksaan (lihat Sub bagian 2.2), sehingga Persamaan (3) sampai (5) baru divalidasi pada satu tingkat probabilitas dan dua nilai fall. Jumlah instance layanan juga dibatasi pada tiga unit sehingga dampak flapping terhadap ketersediaan pada konfigurasi dengan jumlah instance lebih sedikit belum teramati.

---

## 4. KESIMPULAN DAN SARAN

Penelitian ini membuktikan bahwa profil parameter health check HAProxy berpengaruh signifikan terhadap failover time, throughput, dan error rate pada sistem microservice berbasis Docker, dengan effect size yang besar pada ketiga metrik tersebut, sedangkan latensi permintaan yang berhasil dilayani tidak terpengaruh. Failover time terukur berkisar dari 317 ms pada profil agresif hingga 23491 ms pada profil konservatif, sedangkan throughput menurun 18,0% dan error rate meningkat dari 0,003% menjadi 0,095% ketika deteksi kegagalan melambat. Pada ketiga profil, failover time empiris lebih cepat dari nilai teoretis inter × fall dan berada di dalam rentang Persamaan (2), dengan deviasi yang ditentukan oleh posisi titik kegagalan di dalam siklus pemeriksaan. Kontribusi utama penelitian ini adalah kuantifikasi kompromi antara kecepatan deteksi dan kestabilan status: konfigurasi fall = 1 menghasilkan rata-rata 18,0 transisi status per pengujian dan mengeluarkan 17,2% kapasitas pool dari rotasi secara keliru pada kondisi kegagalan intermiten, sedangkan konfigurasi fall = 5 hanya menghasilkan 0,4 transisi, dan kedua hasil tersebut diprediksi dengan baik oleh model probabilistik yang diusulkan. Dibandingkan penelitian pada probe Kubernetes, biaya deteksi keliru pada health check load balancer lebih rendah karena tidak memicu restart dan tidak menghilangkan permintaan selama kapasitas cadangan tersedia. Kelebihan penelitian ini terletak pada penggunaan pilot study sebagai gerbang validasi berkriteria eksplisit, pengujian signifikansi statistik non-parametrik, dan model flapping yang tervalidasi, sedangkan kekurangannya terletak pada penggunaan satu lingkungan uji tervirtualisasi, waktu injeksi kegagalan yang tetap, dan satu tingkat probabilitas kegagalan intermiten.

Penelitian selanjutnya yang dapat dilakukan antara lain: yang pertama adalah mereplikasi pengujian pada lingkungan Linux bare-metal dan pada orkestrator container seperti Kubernetes untuk menilai sejauh mana pola deviasi failover time bersifat spesifik terhadap HAProxy. Berikutnya yang kedua adalah menambah variasi tingkat probabilitas kegagalan intermiten perlu diperluas agar hubungan antara tingkat kegagalan, nilai fall, dan frekuensi flapping dapat dimodelkan secara kuantitatif. Yang ketiga, menyesuaikan nilai inter dan fall berdasarkan riwayat kelaikan instance layak diteliti sebagai upaya menurunkan waktu deteksi dan laju false positive secara bersamaan.

---

## DAFTAR PUSTAKA

[1] Annisa, A., M. Ardiana, P. N. Rahayu, T. Brian, dan M. A. Jami'in, "Performance Evaluation of Web Applications Using JMeter Load Testing for Server Capacity and Response Efficiency," *Journal of Applied Informatics and Computing*, vol. 10, no. 1, pp. 585–590, 2026. doi: 10.30871/jaic.v10i1.11840. [Diakses: 06-Agu-2026]

[2] Chaurasia, B., A. Verma, dan P. Verma, "IHFD: an improved heartbeat-based failure detector of ◊P (eventually perfect) class for partially synchronous hierarchical distributed systems," *Complex & Intelligent Systems*, 2026. doi: 10.1007/s40747-026-02423-z. [Diakses: 04-Sep-2026]

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

[17] Sugiyatno, dan I. M, "Analisis Perbandingan Performasi Respon Waktu Web Server dan Failover Antara Kubernetes Dan Docker Swarm pada Container Orchestration," *Jurnal Informatika Komputer, Bisnis dan Manajemen*, vol. 21, no. 3, pp. 43–53, 2023. doi: 10.61805/fahma.v21i3.9. [Diakses: 09-Agu-2026]

[18] Zhang, P., L. Xiang, Z. Song, dan Y. Yang, "Adaptive load balancing and fault-tolerant microservices architecture for high-availability web systems using docker and spring cloud," *Discover Applied Sciences*, vol. 7, no. 7, art. 705, 2025. doi: 10.1007/s42452-025-07320-7. [Diakses: 31-Agu-2026]
