# Kernel Időzítés és Ütemezés
Verzió: 1.0-stable
Forrás: UNICAGD-Core Analízis
Státusz: HASZNÁLHATÓ

## 1. Mi az a Kernel Időzítés?

A kernel időzítése az a rendszer, amely kezeli az időzített eseményeket a rendszerben. Ez magában foglalja a rendszeridőt, a timer interruptokat, az időzítőket, és a periodikus feladatokat.

## 2. Időzítési Alapfogalmak

### 2.1 Rendszeridő (System Time)
- A rendszer által tartott idő
- Forrása: RTC (Real Time Clock) vagy NTP (Network Time Protocol)
- Formátum: Epoch idő (1970. január 1. óta eltart másodpercek)
- Belső ábrázolás: jiffies (timer interruptok száma)

### 2.2 Jiffies
- A kernel alap időegysége
- Egy jiffie = 1/HZ másodperc
- HZ = 100, 250, 300 vagy 1000 (architektúra függő)
- Példa: HZ=100 esetén 1 jiffie = 10 ms

### 2.3 Timer Interrupt
- Periodikus megszakítás a CPU-nak
- Időzített feladatok futtatására szolgál
- Gyakoriság: 100-1000 Hz
- Kernel vezérlés

## 3. Időzítő Típusok

### 3.1 Programozható Időzítők
- **POSIX timers:** `timer_create()`, `timer_settime()`
- **Alarm:** `alarm()` rendszerhívás
- **Sleep:** `sleep()`, `usleep()`, `nanosleep()`

### 3.2 Kernel Időzítők
- **High-resolution timers:** Magas felbontású időzítők
- **Tickless kernel:** Dinamikus timer interrupt
- **HRT (High-Resolution Timers):** Nanoszekundum felbontású időzítők

### 3.3 Hardware Timers
- **PIT (Programmable Interval Timer):** Régi, x86 architektúra
- **HPET (High Precision Event Timer):** Újabb, magas pontosság
- **APIC Timer:** Többprocesszoros rendszerekhez
- **TSC (Time Stamp Counter):** CPU órajel számláló

## 4. Ütemezés (Scheduling)

### 4.1 Cél
- CPU idő megosztása a folyamatok között
- Fairness és teljesítmény egyensúlya
- Valós idejű követelmények kielégítése

### 4.2 Ütemezési Stratégiák

#### 4.2.1 CFS (Completely Fair Scheduler)
- **Alapértelmezett** Linux ütemező
- **Red-Black Tree:** Folyamatok virtuális futási ideje alapján rendezve
- **Virtual runtime:** Minden folyamatnak egy számlálója van
- **Fairness:** Minden folyamat egyenlő CPU időt kap
- **Latency:** Alacsony késleltetés interaktív alkalmazásokhoz

#### 4.2.2 RT (Real-Time) Scheduler
- **SCHED_FIFO:** FIFO, magasabb prioritás szakítja meg az alacsonyabbat
- **SCHED_RR:** Round Robin, időzített
- **SCHED_DEADLINE:** Határidő alapján
- **SCHED_BATCH:** Batch feldolgozás
- **SCHED_IDLE:** Csak akkor fut, ha nincs más

#### 4.2.3 Deadline Scheduler
- **SCHED_DEADLINE:** CPU idő, határidő, periódus
- **Real-time garantálás:** CPU idő garantált
- **Energetikai optimalizálás:** CPU használat optimalizálása

### 4.3 CFS Paraméterek
```bash
# /proc/sys/kernel/sched_*
sched_min_granularity_ns = 10000000  # Minimum időtartam
sched_wakeup_granularity_ns = 15000000  # Felébresztés időtartama
sched_migration_cost = 500000  # Migrálási költség
sched_child_runs_first = 0  # Gyerek processz előny
```

## 5. Valós Idejű (Real-Time) Rendszerek

### 5.1 Hard Real-Time
- **Határidő:** Deterministicus, garantált
- **Példa:** Légi vezérlő, orvosi eszközök
- **Linux RT Patch:** Valós idejű kernel patch
- **PREEMPT_RT:** Teljesen preemptív kernel

### 5.2 Soft Real-Time
- **Határidő:** Nem determinisztikus, de preferált
- **Példa:** Video lejátszás, hangfeldolgozás
- **CFS:** Alapértelmezett, soft real-time

### 5.3 Valós Idejű Paraméterek
```bash
# /etc/sysctl.conf
kernel.sched_rt_period_us = 1000000  # RT periódus (1 másodperc)
kernel.sched_rt_runtime_us = 950000  # RT runtime (950 ms)
```

## 6. Időzítés és Ütemezés Hibakeresés

### 6.1 Időzítési Problémák
- **Timer drift:** Időzítőpont eltérés
- **Missed timer:** Időzítő nem fut le
- **Late timer:** Időzítő késve fut le

### 6.2 Ütemezési Problémák
- **Priority inversion:** Alacsony prioritású folyamat blokkol magasabbat
- **Starvation:** Egy folyamat soha nem kap CPU időt
- **Deadlock:** Folyamatok egymásra várnak

### 6.3 Diagnosztikai Eszközök
- **ftrace:** Függvényhívás nyomkövetés
- **perf:** Teljesítmény elemzés
- **latencytop:** Késleltetés elemzés
- **sched_debug:** Ütemező debug információ

## 7. Időzítés és Ütemezés Optimalizálás

### 7.1 Timer Optimalizálás
- **Tickless kernel:** Csak akkor fut a timer interrupt, ha kell
- **HRT (High-Resolution Timers):** Magas pontosságú időzítők
- **Timer coalescing:** Időzítők csoportosítása

### 7.2 Ütemező Optimalizálás
- **CPU affinity:** Folyamatok processzorokhoz kötése
- **IRQ affinity:** Megszakítások processzorokhoz kötése
- **Scheduler tuning:** Ütemező paraméterek finomhangolása

### 7.3 Valós Idejű Optimalizálás
- **CPU isolation:** CPU-k dedikálása RT folyamatokhoz
- **IRQ isolation:** Megszakítások eltávolítása RT CPU-król
- **Memory locking:** Memória zárolása, swap kizárása

## 8. Időzítés és Ütemezés Konfiguráció

### 8.1 Sysctl Paraméterek
```bash
# /etc/sysctl.conf
kernel.sched_min_granularity_ns = 10000000
kernel.sched_wakeup_granularity_ns = 15000000
kernel.sched_migration_cost = 500000
kernel.sched_rt_period_us = 1000000
kernel.sched_rt_runtime_us = 950000
```

### 8.2 CPU Governor
```bash
# CPU frekvencia beállítása
echo performance > /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor
echo powersave > /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor
echo schedutil > /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor
```

### 8.3 CPU Affinity
```bash
# Folyamat CPU affinitás beállítása
taskset -c 0-3 <program>

# CPU affinitás beállítása futó processzhez
taskset -pc 0-3 <PID>

# IRQ affinitás beállítása
echo 1 > /proc/irq/XX/smp_affinity
```

## 9. Időzítés és Ütemezés Biztonság

### 9.1 Időzítés Biztonság
- **RTC ellenőrzés:** Hardver óra ellenőrzése
- **NTP szinkronizálás:** Hálózati idő szinkronizálás
- **Időzítő korlátok:** Időzítő túlcsordulás kezelése

### 9.2 Ütemező Biztonság
- **Priority ceiling:** Prioritás korlátok
- **Priority inheritance:** Prioritás öröklés
- **Deadlock detektálás:** Zárolási problémák felismerése

## 10. Összefoglalás

Az időzítés és ütemezés:
- **Kritikus fontosságú** a rendszer működéséhez
- **Összetett algoritmusokkal** rendelkezik
- **Teljesítmény érzékeny** a beállításokra
- **Valós idejű** követelményekkel rendelkezik

A kernel időzítés és ütemezés megértése:
- **Jiffies** és **timer interrupt** fogalmak ismerete
- **CFS** és **RT ütemező** működésének megértése
- **Időzítő típusok** és **használati esetek** ismerete
- **Hibakeresési eszközök** ismerete

---

*Dokumentum státusz: STABIL. Nincs félreértés. Nincs feltételezés bizonyítás nélkül.*
