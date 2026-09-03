# Zajmentes Rendszerkonfiguráció – Gyakorlati Útmutató
Verzió: 1.0-stable
Forrás: UNICAGD-Core Analízis
Státusz: HASZNÁLHATÓ (Terepi Kézikönyv)

---

## 1. Mi az a Rendszerzaj és Hogyan Iktassuk Ki?

A rendszerzaj minden olyan háttérfolyamat, hálózati sugárzás vagy felesleges I/O művelet, amit a felhasználó vagy a kritikus alkalmazás nem kért kifejezetten.

### 1.1 Hálózati Zaj Teljes Lekapcsolása (Offline / Air-Gap Gép)
```bash
# Hálózati interfészek fizikai lekapcsolása a kernelben
sudo ip link set dev eth0 down
sudo ip link set dev wlan0 down

# Vagy a modulok feketelistázása (grub boot paraméterben):
# modprobe.blacklist=r8169,e1000e,iwlwifi

# Csak a loopback interfész engedélyezése belső folyamatoknak:
sudo ip link set dev lo up
```

### 1.2 Telemetria és Hátterdémonok Kiiktatása
```bash
# Felesleges felfedező és felhő-démonok letiltása Linux alatt
sudo systemctl stop avahi-daemon cups-browsed systemd-resolved 2>/dev/null
sudo systemctl disable avahi-daemon cups-browsed systemd-resolved 2>/dev/null

# Alpine Linux (OpenRC) esetén:
# rc-update del avahi-daemon default
# rc-update del wpa_supplicant default
```

---

## 2. Zajmentes TUI Alkalmazás Indítása Boot Során

Hogy a gép közvetlenül a vezérlőfelületre induljon bejelentkezési sallangok és grafikus felület nélkül:

### 2.1 `/etc/inittab` (Alpine / Busybox / SysV):
```text
tty1::respawn:/usr/local/bin/zero_noise_dashboard
```

### 2.2 Systemd Automatikus TUI Szolgáltatás:
`/etc/systemd/system/dashboard.service`:
```ini
[Unit]
Description=Zero Noise Control Dashboard
After=network.target

[Service]
Type=simple
ExecStart=/usr/local/bin/zero_noise_dashboard
StandardInput=tty
StandardOutput=tty
TTYPath=/dev/tty1
Restart=always

[Install]
WantedBy=multi-user.target
```

---
*Dokumentum státusz: STABIL · UNICAGD-Core Terepi Útmutató*
