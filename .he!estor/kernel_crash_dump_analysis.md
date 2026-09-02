# Kernel Crash Dump Elemzési Útmutató
Verzió: 1.0-stable
Forrás: UNICAGD-Core Analízis
Státusz: HASZNÁLHATÓ

## 1. Mi az a Kernel Crash Dump?

A kernel crash dump a kernel összeomlásakor rögzített memóriatartalom. Segítségével később elemezhetjük, hogy mi okozta a hibát.

## 2. Crash Dump Típusok

### 2.1 Full Dump (Teljes memóriakép)
- A teljes RAM mentése
- Nagy méretű (pl. 16GB RAM = 16GB dump)
- Lassú mentés és elemzés

### 2.2 Filtered Dump (Szűrt memóriakép)
- Csak a kernel szükséges részeinek mentése
- Kisebb méretű
- Gyorsabb mentés és elemzés

### 2.3 vmcore
- A dump formátum neve Linux rendszerekben
- Általában tömörített (zlib, lz4)

## 3. kdump Beállítás

### 3.1 kdump Telepítés
```bash
# Debian/Ubuntu
sudo apt install kdump-tools crash

# RHEL/CentOS/Fedora
sudo dnf install kexec-tools crash

# Arch
sudo pacman -S kexec-tools crash
```

### 3.2 Boot Paraméter
```bash
# /etc/default/grub
GRUB_CMDLINE_LINUX_DEFAULT="crashkernel=256M"

# Grub frissítése
sudo update-grub
```

### 3.3 kdump Indítás
```bash
# Debian/Ubuntu
sudo systemctl enable kdump
sudo systemctl start kdump

# RHEL/CentOS/Fedora
sudo systemctl enable kdump
sudo systemctl start kdump
```

## 4. Crash Dump Elemzés

### 4.1 Crash Eszköz
```bash
# Crash indítása
sudo crash /usr/lib/debug/boot/vmlinux-$(uname -r) /var/crash/$(uname -r)/vmcore

# Gyakori parancsok a crashben:
bt -a             # Minden CPU backtrace
bt <PID>          # Egy processz backtrace
files             # Folyamatok fájljai
kmem -s           # Memóriahasználat
log               # Kernel napló
ps                # Processzek listája
vm                # Virtuális memória
```

### 4.2 elemzési lépések
1. **Boot paraméter ellenőrzése:** `dmesg | grep -i panic`
2. **Napló elemzés:** `dmesg`, `/var/log/kern.log`
3. **Call trace elemzés:** A hívási lánc értelmezése
4. **Forráskód keresése:** A hibás sor megkeresése
5. **Javítás:** A hiba javítása és tesztelése

## 5. Crash Dump Hibakeresés

### 5.1 Gyakori Hibák
- **Hiányzó dump:** Nincs mentett crash dump
- **Hibás dump:** Sérült vagy hiányos memóriakép
- **Hibás elemzés:** Rosszul értelmezett adatok

### 5.2 Hibakeresési Lépések
1. **kdump állapot ellenőrzése:** `systemctl status kdump`
2. **Boot paraméter ellenőrzése:** `cat /proc/cmdline | grep crashkernel`
3. **Dump fájl ellenőrzése:** `ls -lh /var/crash/`
4. **Crash napló ellenőrzése:** `journalctl -u kdump`

## 6. Crash Dump Biztonság

### 6.1 Adatvédelem
- A crash dump tartalmazhat érzékeny adatokat (jelszavak, kulcsok)
- A dumpokat biztonságosan tárold
- Hozzáférés korlátozása

### 6.2 Integritás
- A dump integritását ellenőrizd
- Használj hash-eket (SHA256)
- Tárold külön helyen

## 7. Crash Dump Automatizálás

### 7.1 Automatikus Elemzés
```bash
# Script példa automatikus elemzéshez
#!/bin/bash
CRASH_DIR="/var/crash"
CRASH_TOOL="/usr/bin/crash"

for dump in $(ls $CRASH_DIR/*/vmcore 2>/dev/null); do
    echo "Elemzés: $dump"
    $CRASH_TOOL /usr/lib/debug/boot/vmlinux-$(uname -r) $dump <<EOF
bt -a
log
ps
EOF
done
```

### 7.2 Automatikus Jelentés
- Email értesítés crash dump esetén
- Automatikus törlés régi dumpokról
- Rendszeres összefoglaló

## 8. Crash Dump és Kernel Frissítés

### 8.1 Dump Kompatibilitás
- A dump csak azzal a kernel verzióval elemezhető, amivel készült
- Kernel frissítés után régi dumpok nem elemezhetők
- Tartsd meg a régi vmlinux fájlokat

### 8.2 Dump Tárolás
- Dumpok tárolása külön partíción
- Rendszeres archiválás
- Törlési szabályzat

## 9. Összefoglalás

A crash dump elemzés:
- **Kritikus fontosságú** a kernel hibák diagnosztikájához
- **Rendszeres gyakorlat** igényel
- **Automatizálható** a rutin elemzésekhez
- **Biztonságos tárolás** szükséges

A kdump beállítás:
- **Könnyű** telepítés és konfiguráció
- **Alacsony overhead** futás közben
- **Magas érték** hibakereséshez

---

*Dokumentum státusz: STABIL. Nincs félreértés. Nincs feltételezés bizonyítás nélkül.*
