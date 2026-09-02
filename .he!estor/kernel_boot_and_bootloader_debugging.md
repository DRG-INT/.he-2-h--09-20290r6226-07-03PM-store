# Kernel Boot és Bootloader Hibakeresés
Verzió: 1.0-stable
Forrás: UNICAGD-Core Analízis
Státusz: HASZNÁLHATÓ

## 1. Mi az a Bootloader?

A bootloader az a program, amely a számítógép bekapcsolása után fut le elsőként, és feladata a kernel betöltése. A bootloader a BIOS/UEFI és a kernel közötti híd.

## 2. Bootloader Típusok

### 2.1 BIOS Bootloader
- **GRUB (Grand Unified Bootloader):** Legnépszerűbb, támogatja a BIOS-t és UEFI-t
- **LILO (Linux Loader):** Régebbi, egyszerű
- **Syslinux:** Kisméretű,Live CD-khez

### 2.2 UEFI Bootloader
- **systemd-boot:** Egyszerű, systemd integráció
- **rEFInd:** Grafikus, multi-OS
- **GRUB UEFI:** UEFI módban is működik

## 3. GRUB Konfiguráció

### 3.1 GRUB Beállítás
```bash
# /etc/default/grub
GRUB_DEFAULT=0
GRUB_TIMEOUT=5
GRUB_DISTRIBUTOR=`lsb_release -i -s 2> /dev/null || echo Debian`
GRUB_CMDLINE_LINUX_DEFAULT="quiet splash"
GRUB_CMDLINE_LINUX=""
```

### 3.2 Boot Paraméterek
```bash
# Kernel paraméterek hozzáadása
GRUB_CMDLINE_LINUX_DEFAULT="debug initcall_debug earlyprintk=serial,ttyS0,115200"

# Kernel boot paraméterek
- root=/dev/sda1          # Gyökér partíció
- ro                      # Csak olvasható boot
- debug                   # Részletes naplózás
- init=/bin/bash          # Shell indítása
- single                  # Egylépcsős mód
- nomodeset               # Grafikus mód kikapcsolása
- acpi=off                # ACPI kikapcsolása
```

### 3.3 GRUB Konzol
```bash
# GRUB parancssor
grub> linux /boot/vmlinuz-6.1.0 root=/dev/sda1 ro
grub> initrd /boot/initrd.img-6.1.0
grub> boot

# Boot menü szerkesztése
grub> set root=(hd0,1)
grub> linux /boot/vmlinuz-6.1.0 root=/dev/sda1
grub> initrd /boot/initrd.img-6.1.0
grub> boot
```

## 4. Boot Folyamat

### 4.1 BIOS Boot
1. **Power On Self Test (POST):** Hardver ellenőrzés
2. **BIOS boot device:** Boot eszköz kiválasztása
3. **MBR (Master Boot Record):** Első 512 byte
4. **Bootloader:** GRUB, LILO
5. **Kernel betöltése:** vmlinuz, initrd
6. **Kernel inicializálás:** Kernel elindul

### 4.2 UEFI Boot
1. **UEFI firmware:** Secure Boot, GOP
2. **ESP (EFI System Partition):** FAT32 partíció
3. **Bootloader:** GRUB, systemd-boot
4. **Kernel betöltése:** EFI executable
5. **Kernel inicializálás:** Kernel elindul

### 4.3 Kernel Boot
1. **Early boot:** Arch specifikus inicializálás
2. **Memory setup:** Lapozás, TLB
3. **Driver init:** Eszközök inicializálása
4. **Rootfs mount:** Gyökér fájlrendszer mountolása
5. **Init process:** /sbin/init vagy systemd

## 5. Boot Hibakeresés

### 5.1 Kernel Nem Indul
```bash
# Boot paraméterek hozzáadása
GRUB_CMDLINE_LINUX_DEFAULT="debug initcall_debug earlyprintk=serial,ttyS0,115200"

# Single user mód
GRUB_CMDLINE_LINUX_DEFAULT="single"

# Shell indítása
GRUB_CMDLINE_LINUX_DEFAULT="init=/bin/bash"

# ACPI kikapcsolása
GRUB_CMDLINE_LINUX_DEFAULT="acpi=off"
```

### 5.2 Boot Naplók
```bash
# Boot napló megtekintése
dmesg | less
journalctl -b
cat /var/log/boot.log

# Boot hibák keresése
dmesg | grep -i error
dmesg | grep -i fail
journalctl -b -p err
```

### 5.3 Boot Problémák Gyakori Okaik
- **Hibás boot paraméter:** Rossz kernel paraméter
- **Hiányzó eszközmeghajtó:** Eszköz nem detektálható
- **Hibás initramfs:** Sérült vagy hiányos initrd
- **Lemezhiba:** Lemez nem elérhető

## 6. Initramfs és Initrd

### 6.1 Mi az az Initramfs?
Az initramfs (initial RAM filesystem) egy ideiglenes fájlrendszer, amelyet a kernel a boot során betölt. Tartalmazza a szükséges eszközmeghajtókat és eszközöket a teljes boot folyamatig.

### 6.2 Initramfs Létrehozása
```bash
# Initramfs frissítése
sudo update-initramfs -c -k $(uname -r)

# Initramfs ellenőrzése
ls -lh /boot/initrd.img-$(uname -r)
```

### 6.3 Initramfs Hibakeresés
```bash
# Initramfs kicsomagolása
mkdir /tmp/initramfs
cd /tmp/initramfs
zcat /boot/initrd.img-$(uname -r) | cpio -idmv

# Elemzés
ls -la
cat init
```

## 7. Kernel Panic a Boot Során

### 7.1 Kernel Panic Okaik
- **Hibás kernel build:** Hibásan fordított kernel
- **Hiányzó driver:** Eszközmeghajtó hiányzik
- **Memóriahiba:** Hibás RAM
- **Hibás boot paraméter:** Rossz konfiguráció

### 7.2 Kernel Panic Diagnózis
```bash
# Boot paraméterek ellenőrzése
cat /proc/cmdline

# Kernel napló ellenőrzése
dmesg | less

# Boot napló ellenőrzése
cat /var/log/boot.log
journalctl -b
```

### 7.3 Kernel Panic Javítása
1. **Boot paraméterek módosítása:** GRUB menü szerkesztése
2. **Régije kernel indítása:** Bootloader kernel választás
3. **Live CD használata:** Rendszer javítása
4. **Memória teszt:** memtest86+

## 8. Bootloader Biztonság

### 8.1 GRUB Biztonság
```bash
# GRUB jelszóvédelem
grub-mkpasswd-pbkdf2

# /etc/grub.d/40_custom
set superusers="root"
password_pbkdf2 root <hash>
```

### 8.2 Secure Boot
- **UEFI Secure Boot:** Aláírás ellenőrzés
- **shim:** GRUB betöltése aláírt bootloaderrel
- **MOK (Machine Owner Key):** Egyéni aláírás

### 8.3 Bootloader Veszélyeztetettség
- **Boot hijacking:** Bootloader helyettesítése
- **Bootkit:** Bootloader szintű malware
- **Mitigation:** Secure Boot, jelszóvédelem

## 9. Boot Optimalizálás

### 9.1 Boot Sebesség Növelése
```bash
# Parallel boot
CONFIG_BOOT_PRINTK_DELAY=n

# Quiet boot
GRUB_CMDLINE_LINUX_DEFAULT="quiet splash"

# Disable unnecessary services
sudo systemctl disable bluetooth
sudo systemctl disable cups
```

### 9.2 Parallel Init
- **systemd:** Parhuzamos inicializálás
- **OpenRC:** Egyszerű init rendszer
- **BusyBox init:** Minimalista init

## 10. Boot Monitoring

### 10.1 Boot Naplózás
```bash
# Systemd boot napló
journalctl -b

# Boot idő mérés
systemd-analyze

# Boot folyamat diagram
systemd-analyze plot > boot.svg
```

### 10.2 Boot Hibajelentés
```bash
# Boot hibák keresése
journalctl -b -p err

# Boot napló elemzés
grep -i error /var/log/boot.log

# Boot statisztikák
systemd-analyze blame
```

## 11. Összefoglalás

A bootloader és boot folyamat:
- **Kritikus** a rendszer elindításához
- **Összetett** folyamat BIOS/UEFI-től a kernelig
- **Hibakereshető** boot paraméterekkel és naplókkal
- **Biztonságos** konfiguráció szükséges

A kernel boot hibakeresés:
- **Boot paraméterek** módosítása
- **Naplók elemzése** dmesg, journalctl
- **Initramfs elemzése** és javítása
- **Bootloader konfiguráció** ellenőrzése

---

*Dokumentum státusz: STABIL. Nincs félreértés. Nincs feltételezés bizonyítás nélkül.*
