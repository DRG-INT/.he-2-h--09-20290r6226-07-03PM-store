# Windows NT Debugging and Networking
Verzió: 1.0-stable
Forrás: UNICAGD-Core Analízis
Státusz: HASZNÁLHATÓ

## 1. Windows NT Debugging

### 1.1 WinDbg
- Microsoft kernel debugger
- Kernel dump elemzés
- Live kernel debugging

### 1.2 Kernel Crash Dump
- **Complete memory dump:** Teljes RAM
- **Kernel memory dump:** Csak kernel memória
- **Small memory dump:** 64KB

### 1.3 Hibakeresési eszközök
- **WinDbg:** Kernel és user mode debug
- **Windows Performance Toolkit:** Teljesítmény elemzés
- **Event Tracing for Windows (ETW):** Rendszeresemények naplózása

## 2. WinDbg használata

### 2.1 Kernel dump elemzés
```bash
# WinDbg indítása
windbg -z C:\Windows\MEMORY.DMP

# Kernel dump elemzés
!analyze -v
```

### 2.2 Live kernel debugging
```bash
# Távoli kapcsolódás
windbg -k net:port=50000,key=1.2.3.4

# Vagy soros porton
windbg -k com:port=COM1,baud=115200
```

### 2.3 Gyakori parancsok
```bash
# Kernel napló
!process 0 0

# Processzek listája
!process

# Szálak listája
!thread

# Memória információk
!vm

# Eszközök listája
!devobj
```

## 3. Kernel hibakeresés

### 3.1 Kernel panic (Blue Screen of Death)
- STOP kód
- Hibajelentés
- Crash dump

### 3.2 Kernel oops
- Nem végzetes hiba
- Kernel továbbműködik
- Naplózás

### 3.3 Kernel bug
- Assert hiba
- Kernel leáll
- Naplózás

## 4. Windows NT Networking

### 4.1 TCP/IP stack
- IPv4 és IPv6
- TCP, UDP, ICMP
- Sockets API

### 4.2 Hálózati eszközök
- Ethernet
- WiFi
- Bluetooth
- Cellular

### 4.3 Hálózati szolgáltatások
- DNS
- DHCP
- WINS
- NetBIOS

## 5. Hálózati konfiguráció

### 5.1 IP cím beállítás
```cmd
# IP cím beállítása
netsh interface ip set address "Ethernet" static 192.168.1.100 255.255.255.0 192.168.1.1

# DNS beállítása
netsh interface ip set dns "Ethernet" static 8.8.8.8
```

### 5.2 Hálózati eszközök
```cmd
# Hálózati eszközök listázása
ipconfig /all

# Hálózati kapcsolatok listázása
netstat -an

# Tűzfal beállítás
netsh advfirewall set allprofiles state on
```

## 6. Hálózati biztonság

### 6.1 Windows Firewall
- Beépített tűzfal
- Szabályok
- Portok

### 6.2 IPsec
- Titkosítás
- Hitelesítés
- VPN

### 6.3 SSL/TLS
- Titkosított kommunikáció
- Certifikátumok
- HTTPS

## 7. Hálózati monitorozás

### 7.1 Network Monitor
- Csomagok rögzítése
- Hálózati forgalom elemzése

### 7.2 Performance Monitor
- Hálózati teljesítmény
- Sávszélesség
- Késleltetés

### 7.3 Event Viewer
- Hálózati események
- Naplózás

## 8. Hálózati hibakeresés

### 8.1 Csomag elemzés
- Wireshark
- Microsoft Message Analyzer
- Network Monitor

### 8.2 Kapcsolat tesztelés
```cmd
# Ping teszt
ping 8.8.8.8

# Port teszt
telnet 192.168.1.1 80

# DNS feloldás
nslookup google.com
```

### 8.3 Útvonal követés
```cmd
# Traceroute
tracert 8.8.8.8

# Útvonalak listázása
route print
```

## 9. Windows NT és a virtualizáció

### 9.1 Hyper-V
- Type-1 hypervisor
- Windows Server 2008+
- Virtuális gépek futtatása

### 9.2 WSL2
- Windows Subsystem for Linux 2
- Teljes Linux kernel virtualizáció alatt
- TLM (Transparent Linux Memory)

### 9.3 Virtual Machine Platform
- Windows 10/11
- KVM-szerű virtualizáció
- WSL2 alapja

## 10. Összefoglalás
A Windows NT hibakeresés és hálózat összetett, de jól strukturált rendszer. A WinDbg és a Windows Performance Toolkit eszközök segítenek a hibakeresésben és a teljesítmény elemzésben. A hálózati rendszer TCP/IP alapú, és számos szolgáltatást és biztonsági mechanizmust biztosít.

---

*Dokumentum státusz: STABIL. Nincs félreértés. Nincs feltételezés bizonyítás nélkül.*
