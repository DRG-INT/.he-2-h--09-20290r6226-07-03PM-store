# Kernel Naplózás és Logok Elemzése
Verzió: 1.0-stable
Forrás: UNICAGD-Core Analízis
Státusz: HASZNÁLHATÓ

## 1. Mi az a Kernel Naplózás?

A kernel naplózás az a folyamat, amely során a kernel eseményeket rögzíti a rendszer naplófájljaiban. Ezek az információk kritikusak a hibakereséshez, a biztonsági auditokhoz és a teljesítmény elemzéshez.

## 2. Naplózási Rendszerek

### 2.1 Kernel Naplózás (printk)
- A kernel `printk()` függvényével naplózza az eseményeket
- A naplóüzenetek `dmesg` paranccsal elérhetők
- `log_level` alapján szűrhetők (KERN_INFO, KERN_WARNING, KERN_ERR)

### 2.2 Systemd Naplózás (journald)
- A systemd által kezelt naplózási rendszer
- Strukturált, indexelt naplózás
- `journalctl` paranccsal elérhető
- Rendszeres naplórotáció

### 2.3 Syslog
- Hagyományos Unix naplózási rendszer
- `/var/log/syslog`, `/var/log/kern.log`
- Rendszeres naplórotáció

## 3. Naplófájlok Típusai

### 3.1 Kernel Naplók
- `/var/log/kern.log` – Kernel napló
- `/var/log/dmesg` – Boot napló
- `/var/log/syslog` – Rendszeres napló

### 3.2 Rendszer Naplók
- `/var/log/syslog` – Rendszeres események
- `/var/log/auth.log` – Hitelesítési események
- `/var/log/boot.log` – Boot folyamat naplója

### 3.3 Alkalmazás Naplók
- `/var/log/apache2/` – Apache web szerver naplói
- `/var/log/mysql/` – MySQL adatbázis naplói
- `/var/log/nginx/` – Nginx web szerver naplói

## 4. Napló Elemzési Technikák

### 4.1 Alap Elemzés
```bash
# Kernel napló megtekintése
dmesg
dmesg | less
dmesg | grep error

# Systemd napló megtekintése
journalctl
journalctl -u ssh.service
journalctl -p err

# Rendszeres napló megtekintése
cat /var/log/kern.log
cat /var/log/syslog
```

### 4.2 Szűrés és Keresés
```bash
# Hibák keresése
grep -i error /var/log/kern.log
grep -i fail /var/log/syslog

# Idő szerinti szűrés
journalctl --since "2024-01-01" --until "2024-01-02"
dmesg -T | grep -i error

# Modul szerinti szűrés
dmesg | grep -i ext4
journalctl -u systemd-modules-load
```

### 4.3 Statisztikák
```bash
# Hibák számlálása
grep -c error /var/log/kern.log

# Leggyakoribb hibák
grep error /var/log/kern.log | sort | uniq -c | sort -nr

# Időbeli eloszlás
awk '{print $1, $2, $3}' /var/log/kern.log | cut -d: -f1-2 | sort | uniq -c
```

## 5. Hibakeresés Naplókból

### 5.1 Kernel Panic Elemzés
1. **Napló összegyűjtése:** `dmesg` és `/var/log/kern.log`
2. **Hibaüzenet keresése:** `BUG`, `Oops`, `Panic`, `segfault`
3. **Call trace elemzés:** A hívási lánc értelmezése
4. **Időpont meghatározása:** Mikor történt a hiba

### 5.2 Driver Hibák Elemzése
1. **Modul betöltési hibák:** `insmod` hibaüzenetek
2. **Eszköz inicializálási hibák:** `dmesg | grep -i error`
3. **IOMMU hibák:** `dmesg | grep -i dma`
4. **Interrupt hibák:** `/proc/interrupts` ellenőrzése

### 5.3 Teljesítmény Problémák Elemzése
1. **CPU túlterhelés:** `top`, `htop`, `mpstat`
2. **Memória elfogyás:** `free`, `vmstat`, `dmesg | grep -i oom`
3. **I/O blokkolás:** `iostat`, `iotop`, `dmesg | grep -i block`
4. **Hálózati problémák:** `ifconfig`, `ip`, `netstat`, `dmesg | grep -i net`

## 6. Naplózási Beállítások

### 6.1 Kernel Naplózási Szint
```bash
# /etc/sysctl.conf vagy /etc/sysctl.d/*.conf
kernel.printk = 4 4 1 7

# 1. console_loglevel: Konzolra kiírt üzenetek szintje
# 2. default_message_loglevel: Alapértelmezett üzenetszint
# 3. minimum_console_loglevel: Minimum konzol szint
# 4. default_console_loglevel: Alapértelmezett konzol szint
```

### 6.2 Systemd Naplózási Beállítások
```bash
# /etc/systemd/journald.conf
[Journal]
Storage=persistent
Compress=yes
MaxRetentionSec=1week
SystemMaxUse=1G
```

### 6.3 Naplórotáció
```bash
# /etc/logrotate.conf
/var/log/kern.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
}
```

## 7. Naplózási Best Practices

### 7.1 Naplózási Szint Beállítása
- **Fejlesztés:** Minden üzenet naplózása (debug)
- **Tesztelés:** Hibák és figyelmeztetések naplózása (info, warning)
- **Produkció:** Csak hibák naplózása (error, critical)

### 7.2 Napló Formátum
- Időbélyeg minden naplóüzenetben
- Modul/komponens azonosító
- Hibakód vagy üzenetszint
- Részletes leírás

### 7.3 Napló Biztonság
- Naplók védelme jogosultságok korlátozásával
- Naplók titkosítása (ha szükséges)
- Naplók integritás ellenőrzése

## 8. Összefoglalás

A kernel naplózás:
- **Kritikus fontosságú** a hibakereséshez
- **Rendszeres figyelést igényel**
- **Strukturált formátum** használata ajánlott
- **Biztonságos tárolás** szükséges

A naplók elemzése:
- **Mintázatfelismerés** a hibák korai detektálásához
- **Automatizálás** a rutinfeladatokhoz
- **Közösségi eszközök** használata ajánlott

---

*Dokumentum státusz: STABIL. Nincs félreértés. Nincs feltételezés bizonyítás nélkül.*
