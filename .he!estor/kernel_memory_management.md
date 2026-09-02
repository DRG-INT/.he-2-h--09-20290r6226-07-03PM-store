# Kernel Memóriakezelés és Virtuális Memória
Verzió: 1.0-stable
Forrás: UNICAGD-Core Analízis
Státusz: HASZNÁLHATÓ

## 1. Mi az a Kernel Memóriakezelés?

A kernel memóriakezelése az a rendszer, amely kezeli a fizikai és virtuális memóriát a rendszerben. A memóriakezelés biztosítja, hogy minden folyamat saját memóriaterületet kapjon, és ne zavarja a másikat.

## 2. Fizikai és Virtuális Memória

### 2.1 Fizikai Memória (RAM)
- A gépes valós memóriája
- Mértékegység: MB, GB
- Korlát: A gépben lévő fizikai RAM mennyisége

### 2.2 Virtuális Memória
- Minden folyamat saját címteret kap (általában 4GB 32 bites, 128TB+ 64 bites rendszerekben)
- A virtuális cím nem feltétlenül a fizikai memóriában van
- Lapozás (paging) segítségével a kernel mozgatja az adatokat a lemez és a RAM között

### 2.3 Memóriakezelés Előnyei
- **Elszigetelés:** Folyamatok nem érik el egymás memóriáját
- **Növekvő memória:** Több memória, mint a fizikai RAM
- **Megosztott memória:** Folyamatok közötti adatcsere

## 3. Lapozási Rendszer (Paging)

### 3.1 Lapok (Pages)
- Alap memóriakezelési egység (általában 4KB)
- Minden lapnak van egy fizikai és virtuális címe
- Lapok táblázatokban (page tables) vannak nyilvántartva

### 3.2 Lapozási Táblák (Page Tables)
- **PGD (Page Global Directory):** Felső szint
- **PUD (Page Upper Directory):** Középső felső szint
- **PMD (Page Middle Directory):** Középső szint
- **PTE (Page Table Entry):** Alsó szint, a lap tényleges címe

### 3.3 TLB (Translation Lookaside Buffer)
- A lapcímtár gyorsítótárja a CPU-ban
- Gyorsabb címfordítás, mint a lapozási táblák olvasása
- TLB miss esetén a kernel be kell töltenie a lapcímet

## 4. Memóriakezelési Algoritmusok

### 4.1 Kivetítés (Swapping)
- Amikor elfogy a RAM, a kernel áthelyezi a kevésbé használt lapokat a lemezre (swap)
- Swap helye: `/swapfile` vagy `/dev/sda2` (swap partíció)
- Swapping lassú, mert a lemez sokkal lassabb, mint a RAM

### 4.2 Demand Paging
- Lapokat csak akkor tölt be, amikor ténylegesen szükség van rájuk
- Nem tölti be az egész programot egyben
- Lazy loading: csak a szükséges részek beolvasása

### 4.3 Copy-on-Write (CoW)
- Amikor két folyamat megosztja egy lapot, a kernel csak akkor másolja, ha az egyik folyamat módosítani szeretné
- Hatékonyabb memóriahasználat

## 5. Memóriakezelési Problémák

### 5.1 Memória Szivárgás (Memory Leak)
- Egy folyamat foglal memóriát, de soha nem szabadítja fel
- Lassúan elfogy a rendszer memóriája
- OOM killer (Out Of Memory) beavatkozhat

### 5.2 Oldalcsatorna (Page Fault)
- Egy folyamat olyan lapot próbál elérni, ami nincs a memóriában
- A kernel betölti a lapot a lemezről
- Túl sok page fault lassú a rendszert

### 5.3 TLB Shootdown
- Többprocesszoros rendszerekben, amikor egy lapcímet módosítanak, minden CPU TLB-jét frissíteni kell
- Ez költséges művelet, okozhat teljesítménycsökkenést

## 6. Memóriakezelési Konfiguráció

### 6.1 Swap Beállítás
```bash
# Swap létrehozása
dd if=/dev/zero of=/swapfile bs=1G count=4
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile

# Swap aktiválása boot időben
echo '/swapfile none swap sw 0 0' >> /etc/fstab
```

### 6.2 Swappiness
```bash
# Swappiness beállítása (0-100)
# 0: csak akkor swap, ha szükséges
# 100: agresszív swap
echo 10 > /proc/sys/vm/swappiness
```

### 6.3 Dirty Page Beállítások
```bash
# /etc/sysctl.conf
vm.dirty_ratio = 20
vm.dirty_background_ratio = 10
vm.dirty_expire_centisecs = 3000
vm.dirty_writeback_centisecs = 500
```

## 7. Memóriakezelési Monitorozás

### 7.1 Memória Használat
```bash
# Memória információk
free -h
cat /proc/meminfo
vmstat -s

# Per-folyamat memóriahasználat
ps aux --sort=-%mem
top
htop
```

### 7.2 Swap Használat
```bash
# Swap információk
swapon --show
free -h
cat /proc/swaps

# Swap használat monitorozása
vmstat 1
```

### 7.3 Page Fault Monitorozás
```bash
# Page fault információk
cat /proc/vmstat | grep pgfault
vmstat 1
```

## 8. Memóriakezelési Hibakeresés

### 8.1 OOM (Out of Memory) Hibák
```bash
# OOM naplók ellenőrzése
dmesg | grep -i oom
grep -i "out of memory" /var/log/kern.log

# OOM események listázása
journalctl -k | grep -i oom
```

### 8.2 Memóriaszivárgás Felismerése
1. **Memóriahasználat növekedése:** `free` parancs folyamatos futtatása
2. **Swap használat növekedése:** `swapon --show`
3. **OOM események:** `dmesg | grep -i oom`
4. **Processz elemzés:** `ps aux --sort=-%mem`

## 9. Memóriakezelési Best Practices

### 9.1 Memória Tervezés
- **Előre tervezni:** Mennyi memóriára van szükség?
- **Bufferok kezelése:** Ne foglalj túl sok memóriát egyszerre
- **Memory pool:** Előre allokált memóriakezelés

### 9.2 Hibakezelés
- **NULL pointer ellenőrzés:** Minden mutató ellenőrzése
- **Bounds checking:** Tömb és buffer határok ellenőrzése
- **Graceful degradation:** Ha elfogy a memória, ne omljunk össze

### 9.3 Monitorozás
- **Rendszeres ellenőrzés:** `free` parancs futtatása
- **Figyelmeztetések:** OOM események figyelése
- **Logok elemzése:** Rendszeres naplóelemzés

## 10. Összefoglalás

A kernel memóriakezelése:
- **Kritikus fontosságú** a rendszer stabilitásához
- **Összetett rendszer** a lapozás, TLB, swap részekből
- **Teljesítmény érzékeny** – túl sok page fault lassú
- **Biztonsági szempontok** – elszigetelés, jogosultságok

A virtuális memória:
- **Elszigetelést** biztosít a folyamatok között
- **Több memóriát** tesz elérhetővé, mint a fizikai RAM
- **Komplex kezelést** igényel a kernelben
- **Teljesítmény költséggel** jár (TLB miss, page fault)

---

*Dokumentum státusz: STABIL. Nincs félreértés. Nincs feltételezés bizonyítás nélkül.*
