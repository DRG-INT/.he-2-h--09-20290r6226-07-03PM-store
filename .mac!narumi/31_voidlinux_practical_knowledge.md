# Void Linux – Gyakorlati Tudás és Terepi Ismertetők
Verzió: 1.0-stable
Forrás: UNICAGD-Core Analízis / DRG-INT Védelmi Rendszertan
Státusz: HASZNÁLHATÓ (Kritikus Infrastruktúra Kézikönyv)

## 1. Miért Void Linux a Kritikus Infrastruktúrában?

A Void Linux egy független, nem-systemd alapú Linux disztribúció, amely kifejezetten alkalmas izolált (air-gapped), beágyazott és magas megbízhatóságú védelmi környezetekhez.

Fő előnyei a terepi mérnök számára:
- **`runit` init rendszer:** Zéró socket-aktiváció, átlátható shell-szkript alapú supervision tree, determinisztikus indítási és leállítási sorrend.
- **`musl libc` változat:** Minimális memóriaterhelés, tiszta statikus bináris fordítás, alacsonyabb TCB (támadási felület).
- **`xbps` csomagkezelő:** Villámgyors, C-ben írt determinisztikus csomagkezelés SHA-256 integritás-ellenőrzéssel.
- **Nincs telemetria:** Zéró háttérbeli hálózati forgalom, tiszta offline működésre tervezve.

---

## 2. Telepítés és Alaprendszer Előkészítése

### 2.1 Musl vs Glibc Változat Kiválasztása
- **Glibc változat:** Kompatibilis a zárt forrású binárisokkal (pl. proprietáris FPGA SDK, MATLAB runtime).
- **Musl változat:** Ajánlott kritikus védelmi és SCADA célokra, ahol minden forrásból fordul és minimális TCB szükséges.

### 2.2 Lemezparticionálás és Titkosítás (LUKS + XBPS)
```bash
# Particionálás fdisk-kel vagy cfdisk-kel
# /dev/sda1 -> EFI System (512M)
# /dev/sda2 -> LUKS titkosított konténer (teljes maradék lemez)

# LUKS2 titkosítás katonai szintű AES-XTS titkosítással
cryptsetup luksFormat --type luks2 --cipher aes-xts-plain64 --key-size 512 --hash sha512 --pbkdf argon2id /dev/sda2
cryptsetup open /dev/sda2 cryptroot

# Fájlrendszer és swap előkészítése
mkfs.ext4 -L root /dev/mapper/cryptroot
mkfs.vfat -F32 -n EFI /dev/sda1

# Csatolás
mount /dev/mapper/cryptroot /mnt
mkdir -p /mnt/boot/efi
mount /dev/sda1 /mnt/boot/efi
```

### 2.3 Alaprendszer Telepítése (xbps-install)
```bash
# Alaprendszer másolása internet vagy helyi tükör nélkül, air-gapped ISO-ról:
XBPS_ARCH=x86_64-musl xbps-install -S -R /run/runit/pkgdb/ -r /mnt base-system cryptsetup grub-x86_64-efi
```

---

## 3. Runit Szolgáltatásfelügyelet és Gyakorlat

A `runit` három fázisból (stage) áll:
- **Stage 1 (`/etc/runit/1`):** Egyutas hardver inicializálás (devfs, sysfs, fstab mount, hostname, swap).
- **Stage 2 (`/etc/runit/2`):** Folyamatos szolgáltatásfelügyelet (`/var/service/` supervision tree).
- **Stage 3 (`/etc/runit/3`):** Szabályozott, tiszta leállítás (unmount, swapoff, hardver kikapcsolás).

### 3.1 Szolgáltatás Kezelése (`sv` parancs)
```bash
# Szolgáltatás engedélyezése (szimbolikus link létrehozásával)
ln -s /etc/sv/sshd /var/service/

# Státusz lekérdezése
sv status sshd
# Kimenet: run: sshd: (pid 842) 3421s

# Szolgáltatás újraindítása vagy leállítása
sv restart sshd
sv down sshd
sv up sshd

# Szolgáltatás ellenőrzése (hibakereséshez)
sv check sshd
```

### 3.2 Egyedi Terepi Szolgáltatás Létrehozása (Watchdog Démon Példa)
Hozzuk létre az `/etc/sv/scada-watchdog/run` futtatható szkriptet:
```bash
#!/bin/sh
exec 2>&1
echo "Indul a SCADA hardveres watchdog felügyelet..."

# Végtelen felügyeleti ciklus (ha a program kilép, a runit azonnal újraindítja)
exec /usr/local/bin/scada_daemon --config /etc/scada/config.json --foreground
```
Jogosultság beállítása és aktiválás:
```bash
chmod +x /etc/sv/scada-watchdog/run
ln -s /etc/sv/scada-watchdog /var/service/
```

---

## 4. XBPS Csomagkezelés Air-Gapped Környezetben

Elszigetelt hálózatokon tilos és lehetetlen külső repókból tölteni.

### 4.1 Helyi Csomagtár Szinkronizálása
```bash
# Helyi pendrive-on vagy optikai lemezen lévő archívum hozzáadása
xbps-install -R /media/airgap_repo/ -S
xbps-install -R /media/airgap_repo/ -u

# Telepített csomagok integritás-ellenőrzése (fájlmódosítások keresése)
xbps-pkgdb -a
```

### 4.2 Egyedi Csomag Fordítása (`xbps-src`)
```bash
# Void forráskód-fa letöltése előkészített fejlesztői gépen
git clone --depth=1 https://github.com/void-linux/void-packages.git
cd void-packages
./xbps-src binary-bootstrap

# Csomag lefordítása musl architektúrára
./xbps-src -a x86_64-musl pkg scada-control
```

---

## 5. Írásvédett (Read-Only Rootfs + Overlayfs) Üzemmód

Kritikus katonai és ipari berendezéseken elengedhetetlen, hogy a lemez hibás leállítás (pl. hirtelen áramszünet, EMP) esetén se sérüljön.

### 5.1 Fstab és Kernel Paraméterezés
A `/etc/fstab` beállítása csak olvasható módban:
```text
LABEL=root   /           ext4    ro,noatime,nodiratime,errors=remount-ro 0 1
tmpfs        /tmp        tmpfs   defaults,nosuid,nodev,noatime,size=512M 0 0
tmpfs        /var/run    tmpfs   defaults,nosuid,nodev,noatime,size=64M  0 0
tmpfs        /var/log    tmpfs   defaults,nosuid,nodev,noatime,size=128M 0 0
```

### 5.2 Rendszer Frissítése Írásvédett Állapotban
Ha karbantartásra van szükség:
```bash
# Átmeneti írhatóvá tétel
mount -o remount,rw /

# Karbantartási feladat elvégzése
xbps-install -Syu

# Visszaállítás írásvédettre
mount -o remount,ro /
```

---

## 6. Összefoglaló Ellenőrzőlista Terepi Üzembe Helyezéshez

1. [ ] **Musl Libc** alapértelmezett a minimális TCB érdekében.
2. [ ] **LUKS2 Argon2id** lemeztitkosítás aktív.
3. [ ] **Runit supervision** minden kritikus SCADA/hálózati démonra beállítva.
4. [ ] **Gyökérfájlrendszer** `ro` (read-only) állapotban rögzítve.
5. [ ] **`xbps-pkgdb -a`** lefutott, nincsenek manipulált rendszerbinárisok.

---
*Dokumentum státusz: STABIL · UNICAGD-Core Terepi Kézikönyv*
