# Kernel Hibakeresés és Debug Technikák
Verzió: 1.0-stable
Forrás: UNICAGD-Core Analízis
Státusz: HASZNÁLHATÓ

## 1. Mi az a Kernel Hibakeresés?

A kernel hibakeresés az a folyamat, amely során a kernel hibáinak okát és megoldását keressük. Mivel a kernel a rendszer legbelső rétege, a hibakeresés különleges eszközöket és módszereket igényel.

## 2. Hibakeresési Eszközök

### 2.1 Parancssori Eszközök
- **dmesg:** Kernel napló megtekintése
- **journalctl:** Systemd napló megtekintése
- **cat /proc/kallsyms:** Kernel szimbólumok listája
- **cat /proc/modules:** Betöltött kernel modulok listája
- **cat /proc/interrupts:** Megszakítások listája

### 2.2 Debug Eszközök
- **gdb:** GNU Debugger – kernel kód debugolásához
- **kgdb:** Kernel remote debugger
- **kdb:** Kernel debugger konzol
- **crash:** Kernel crash dump elemzés

### 2.3 Monitor Eszközök
- **perf:** Teljesítmény elemzés
- **ftrace:** Függvényhívás nyomkövetés
- **bpftrace:** BPF alapú monitorozás
- **SystemTap:** Rendszeresemény figyelés

## 3. Gyakori Hibakeresési Technikák

### 3.1 Kernel Panic Elemzés
1. **Napló összegyűjtése:** `dmesg` és `/var/log/kern.log`
2. **Call trace elemzés:** A hívási lánc értelmezése
3. **Regiszter állapot elemzés:** CPU regiszterek értékeinek elemzése
4. **Forráskód keresése:** A hibás sor megkeresése a kernel forráskódban

### 3.2 Driver Hibakeresés
1. **Modul betöltés/eltávolítás tesztelése:** `insmod`/`rmmod`
2. **printk üzenetek:** Naplózás a modul működéséről
3. **Eszköz fájl tesztelése:** `cat /dev/device`, `echo test > /dev/device`
4. **IOMMU bekapcsolása:** DMA hibák detektálása

### 3.3 Teljesítmény Hibakeresés
1. **CPU profil készítése:** `perf top`, `perf record`
2. **Memória profil készítése:** `kmemleak`, `slabtop`, `perf kmem` (kernel-szintű) vagy `memleak-bpfcc`
3. **I/O profil készítése:** `iostat`, `blktrace`
4. **Hálózati profil készítése:** `tcpdump`, `wireshark`

## 4. Kernel Build és Debug

### 4.1 Debug Kernel Build
```bash
# Konfiguráció
make menuconfig
# -> Kernel hacking -> Compile-time checks and compiler options
# -> Kernel debugging
# -> Debug information
# -> KGDB: kernel debugger

# Fordítás
make -j$(nproc) KCFLAGS=-g

# Telepítés
sudo make modules_install install
```

### 4.2 Kernel Build Verziók
- **Vanilla:** Eredeti kernel forráskód
- **Debug:** Hibakeresési információk beépítve
- **Vanilla + patches:** Egyéni patch-ek alkalmazva

## 5. Hibakeresési Stratégia

### 5.1 Reprodukálás
- A hibát reprodukálni kell
- A reprodukálási lépéseket dokumentálni kell
- A környezetet rögzíteni kell (verziók, konfigurációk)

### 5.2 Izoláció
- A hibát izolálni kell
- A hibás komponenst megkeresni
- A hibás kódot behatárolni

### 5.3 Javítás és Verifikáció
- A hibát javítani kell
- A javítást tesztelni kell
- A javítás nem okoz-e új hibákat

## 6. Speciális Hibakeresési Technikák

### 6.1 Kernel Crash Dump
- A kernel összeomlásakor automatikusan menti a memóriatartalmat
- Később elemzéshez használható
- Beállítás: `kdump` csomag telepítése

### 6.2 Live Kernel Patching
- Futó kernel módosítása újraindítás nélkül
- `kpatch`, `kgraft` eszközök

### 6.3 Tracepoints és kprobes
- Dinamikus breakpointok beépítése
- Függvények megszakítása naplózáshoz

## 7. Best Practices

### 7.1 Dokumentáció
- Minden hibakeresési lépés dokumentálása
- A javítások magyarázata
- A környezet leírása

### 7.2 Biztonság
- Hibakereséshez virtuális gépet használni
- Nem módosítani a produktív rendszert
- Biztonsági mentés készítése

### 7.3 Együttműködés
- Hibajelentés küldése a kernel fejlesztőknek
- Patch beküldése a kernel mailing listre
- Közösségi támogatás igénybevétele

## 8. Gyakorlati Tippek

### 8.1 Kezdőknek
- Kezdj egyszerű hibakereséssel
- Használj virtuális gépet
- Tanuld meg a kernel forráskódot
- Használj debug kernel-t

### 8.2 Haladóknak
- Tanuld meg a kernel adatstruktúrákat
- Használj speciális hibakeresési eszközöket
- Vegyél részt a kernel fejlesztésben
- Közösségi projektben dolgozz

## 9. Összefoglalás

A kernel hibakeresés:
- **Korlátok között történik** – a kernel nem bírja a hibákat
- **Rendszeres munkát igényel** – nem egyszeri teendő
- **Közösségi erőforrások** – a kernel közösség segít
- **Tanulási folyamat** – fokozatosan tanulhatod meg

---

*Dokumentum státusz: STABIL. Nincs félreértés. Nincs feltételezés bizonyítás nélkül.*
