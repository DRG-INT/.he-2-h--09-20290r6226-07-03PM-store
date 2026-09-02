# Kernel Boot Folyamat – Lépésről Lépésre
Verzió: 1.0-stable
Forrás: UNICAGD-Core Analízis
Státusz: HASZNÁLHATÓ

## 1. Mi történik, amikor bekapcsolod a gépet?

A kernel boot folyamata egyszerre hardveres és szoftveres folyamatok sorozata. Itt a legfontosabb lépések:

### 1.1 BIOS/UEFI Fázis
- A számítógép bekapcsolásakor a BIOS/UEFI fut le először
- Hardveres öntesztelés (POST) – ellenőrzi, hogy a memória, lemez, processzor működik-e
- Boot eszköz kiválasztása (lemez, SSD, hálózat)
- A BIOS/UEFI betölti a bootloader-t (pl. GRUB, systemd-boot)

### 1.2 Bootloader Fázis
- A bootloader betölti a kernel képfájlját (vmlinuz) a lemezről
- A kernel képfájl tömörített formátumban van (gzip, xz)
- A bootloader átadja a vezérlést a kernelnek

### 1.3 Kernel Inicializálás
- A kernel kicsomagolja saját magát a memóriába
- Az architektúra-specifikus kód fut (pl. x86_64, ARM)
- A processzorok inicializálása (SMP - Symmetric Multi-Processing)
- A memóriakezelés beállítása (lapozás, TLB)

### 1.4 Rendszer Inicializálás
- **Early printk:** A korai naplózás elérése a konzolra
- **Interrupt kezelés:** A megszakításvezérlő beállítása
- **Időzítők:** A rendszeridő és a timer interrupt beállítása
- **Fájlrendszer:** A gyökér fájlrendszer (rootfs) beolvasása
- **Eszközök:** A hardvereszközök felfedezése és inicializálása

### 1.5 Felhasználói Tér Elérése
- Az **init** folyamat indítása (PID 1)
- A szolgáltatások elindítása (systemd, SysV init)
- A bejelentkezési képernyő megjelenítése

## 2. Fontos Koncepciók a Boot Folyamatban

### 2.1 Boot Parancssor
- A kernel indításakor átadott paraméterek
- Pl. `root=/dev/sda1`, `quiet`, `debug`, `init=/bin/bash`
- A boot parancssor megváltoztathatja a kernel viselkedését

### 2.2 Initramfs
- Egy ideiglenes fájlrendszer, amelyet a kernel a boot során betölt
- Tartalmazza a szükséges eszközmeghajtókat és eszközöket a teljes boot folyamatig
- A teljes rendszer elérhetése után eltávolítódik

### 2.3 Kernel Panic a Boot Során
- Ha a kernel nem tudja elindítani a rendszert, összeomlik
- Gyakori okok:
  - Hibás boot parancssor
  - Hiányzó vagy hibás eszközmeghajtó
  - Memóriahiba
  - Nem támogatott hardver

## 3. Gyakorlati Tippek a Boot Folyamat Megismeréséhez

### 3.1 Boot Naplózás
- A `dmesg` parancs kiírja a boot naplót
- A `/var/log/boot.log` fájl tartalmazza a boot üzeneteket
- A `journalctl -b` parancs a systemd boot naplóját mutatja

### 3.2 Boot Paraméterek
- `debug`: Részletes naplózás bekapcsolása
- `init=/bin/bash`: Közvetlenül a shellbe indítás (javításra)
- `single`: Egylépcsős mód (csak root felhasználó)
- `nomodeset`: Grafikus mód kikapcsolása (problémák esetén)

### 3.3 Kernel Panic Diagnózis
- Ha a kernel összeomlik a boot során:
  1. Ellenőrizd a boot parancssort
  2. Ellenőrizd az eszközök detektálását (`dmesg | less`)
  3. Próbálj ki egy korábbi kernel verziót
  4. Ellenőrizd a memóriát (memtest86+)

## 4. Összefoglalás

A kernel boot folyamata összetett, de rendszerszintű. Megértése segít:
- Hibakeresésben
- Rendszeroptimalizálásban
- Biztonsági auditokban

A legfontosabb: a boot folyamat minden lépése naplózott, így bármilyen probléma nyomozható vissza.

---

*Dokumentum státusz: STABIL. Nincs félreértés. Nincs feltételezés bizonyítás nélkül.*
