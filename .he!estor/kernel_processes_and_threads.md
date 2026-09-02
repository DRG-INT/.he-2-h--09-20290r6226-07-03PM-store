# Kernel Processzek és Szálak Kezelése
Verzió: 1.0-stable
Forrás: UNICAGD-Core Analízis
Státusz: HASZNÁLHATÓ

## 1. Mi az a Processz a Kernelben?

A processz a rendszer alapvető egysége – egy futó program példány. Minden processznek van:
- **PID (Process ID):** Egyedi azonosító
- **Memória címtér:** Saját virtuális memória
- **Regiszterek:** CPU állapota
- **Nyitott fájlok:** Fájl leírók
- **Jogosultságok:** Felhasználó és csoport azonosítók

## 2. Processz életciklus

### 2.1 Allapotok
- **R (Running):** Fut vagy futásra kész
- **S (Sleeping):** Várakozik eseményre (pl. I/O)
- **D (Disk sleep):** Nem szakítható meg alvás (pl. I/O)
- **Z (Zombie):** Befejezett, de a szülő nem olvasta be a kilépési állapotot
- **T (Stopped):** Megállítva (pl. jelzéssel)
- **I (Idle):** Inaktív szál

### 2.2 Processz Létrehozás
1. **fork():** Szülő processz másolata
2. **exec():** Új program betöltése
3. **clone():** Szálak létrehozása

### 2.3 Processz Befejeztetés
1. **exit():** Processz kilépése
2. **wait():** Szülő várakozik a gyerek kilépésére
3. **kill():** Processz jelzés küldése

## 3. Szálak (Threads)

### 3.1 Mi az a Szál?
- Egy processz belsejében futó futási folyamat
- Ugyanazzal a memória címtérrel rendelkezik, mint a processz
- Saját verem, regiszterek, állapot

### 3.2 Szálak Előnyei
- **Parallelism:** Több dolog egyszerre
- **Responsiveness:** Egy szál blokkolódik, a másik fut
- **Memory sharing:** Gyors adatcsere a szálak között

### 3.3 Szál Modell
- **1:1 (Kernel-level threads):** Minden szál külön kernel szál (Linux, Windows)
- **N:1 (User-level threads):** Több felhasználói szál egy kernel szálon (régi rendszerek)
- **M:N (Hybrid)::** N felhasználói szál M kernel szálon (régi rendszerek)

## 4. Ütemező (Scheduler)

### 4.1 Cél
- A CPU idő (time slice) megosztása a folyamatok között
- Igazságos és hatékony erőforrás kiosztás

### 4.2 Alap Stratégiák
- **FCFS (First Come First Served):** Sorban, első beérkező először
- **Round Robin (RR):** Időzített kör, minden folyamat kap egy időt
- **Priority:** Prioritás alapján, magasabb előbb
- **Multilevel Queue:** Több prioritási szint

### 4.3 Linux Ütemező (CFS - Completely Fair Scheduler)
- **Red-Black Tree:** Folyamatok prioritás szerint rendezve
- **Virtual runtime:** Minden folyamatnak egy virtuális futási ideje van
- **Fairness:** Minden folyamat egyenlő CPU időt kap
- **Latency:** Alacsony késleltetés interaktív alkalmazásokhoz

### 4.4 Valós Idejű Ütemezés (RT)
- **SCHED_FIFO:** FIFO, magasabb prioritás szakítja meg a alacsonyabbat
- **SCHED_RR:** Round Robin, időzített
- **SCHED_DEADLINE:** Határidő alapján
- **SCHED_BATCH:** Batch feldolgozás, alacsony prioritu
- **SCHED_IDLE:** Csak akkor fut, ha nincs más

## 5. IPC (Inter-Process Communication)

### 5.1 Alapvető Mechanizmusok
- **Signálok:** Egyszerű jelzések
- **Pipe:** Folyamatok közötti adatcsatorna
- **FIFO (Named pipe):** Fájlrendszerben elérhető pipe
- **Message queues:** Üzenetsorok
- **Shared memory:** Közös memóriaterület
- **Semaphores:** Szinkronizálási eszközök
- **Sockets:** Hálózati kommunikáció

### 5.2 Linux Specifikus
- **Futex (Fast Userspace Mutex):** Gyors szinkronizálás
- **Eventfd:** Esemény jelzés
- **Signalfd:** Jelzés fájl deszkriptorrá alakítása
- **Timerfd:** Időzítő fájl deszkriptorrá alakítása

## 6. Processz és Szál Monitorozás

### 6.1 Processz Lista
```bash
# Futó processzek listája
ps aux
ps -ef
top
htop

# Részletes információk
ps -eo pid,ppid,user,pri,ni,vsz,rss,stat,start,time,command
```

### 6.2 Szálak Listája
```bash
# Szálak listája egy processzben
ps -T -p <PID>

# Összes szál listája
ps -eLf
top -H
```

### 6.3 Folyamat Tree
```bash
# Folyamat fa
pstree
pstree -p

# Szülő-gyerek kapcsolatok
ps -o pid,ppid,cmd -e
```

## 7. Processz Szignálok

### 7.1 Gyakori Szignálok
- **SIGTERM (15):** Befejezési kérés
- **SIGKILL (9):** Azonnali befejezés
- **SIGSTOP (19):** Megállítás
- **SIGCONT (18):** Folytatás
- **SIGINT (2):** Interrupt (Ctrl+C)
- **SIGSEGV (11):** Memória hozzáférési hiba
- **SIGCHLD (17):** Gyerek processz állapota változott

### 7.2 Szignál Küldése
```bash
# SIGTERM küldése
kill <PID>

# SIGKILL küldése
kill -9 <PID>

# Összes processznek szignál küldése
killall <processznev>
pkill <processznev>
```

## 8. Processz és Szál Hibakeresés

### 8.1 Deadlock (Zárolás)
- Két vagy több szál egymásra vár
- A rendszer befagy
- Detektálás: Lockdep, gdb

### 8.2 Starvation (Éhezés)
- Egy folyamat soha nem kap CPU időt
- Alacsony prioritású folyamatok
- Detektálás: Ütemező naplók

### 8.3 Priority Inversion
- Alacsony prioritású folyamat blokkol egy magas prioritásút
- Közepes prioritású folyamat elviszi a CPU időt
- Detektálás: Priority inheritance protocol

## 9. Processz és Szál Best Practices

### 9.1 Tervezés
- **Minimális szálak:** Ne indíts túl sok szálat
- **Szálpool:** Előre allokált szálak használata
- **Load balancing:** Munka elosztása a szálak között

### 9.2 Szinkronizálás
- **Mutex:** Költséges, de biztos
- **Spinlock:** Gyors, de csak rövid ideig
- **RCU:** Read-Copy-Update, olvasás optimalizált
- **Seqlock:** Irodalom-olvasás optimalizált

### 9.3 Hibakezelés
- **Mindig ellenőrizd a visszatérési értékeket**
- **Ne blokkolj a kernelben hosszú ideig**
- **Használj timeout-öket** a várakozásokhoz

## 10. Összefoglalás

A processzek és szálak kezelése:
- **Kritikus fontosságú** a rendszer működéséhez
- **Összetett ütemező** algoritmusokkal
- **Szinkronizációs mechanizmusok** szükségesek
- **Monitorozás** és **hibakeresés** fontos

A kernel processzkezelés megértése:
- **Processz életciklus** ismerete
- **Szálak működése** megértése
- **Ütemező algoritmusok** ismerete
- **IPC mechanizmusok** ismerete

---

*Dokumentum státusz: STABIL. Nincs félreértés. Nincs feltételezés bizonyítás nélkül.*
