# Kernel Hálózati Rendszer és Konfiguráció
Verzió: 1.0-stable
Forrás: UNICAGD-Core Analízis
Státusz: HASZNÁLHATÓ

## 1. Mi az a Kernel Hálózati Rendszer?

A kernel hálózati rendszere kezeli az összes hálózati kommunikációt a rendszerben. Ez magában foglalja a csomagok küldését és fogadását, az útválasztást, a TCP/IP stack-et, és a hálózati eszközök kezelését.

## 2. Hálózati Rendszer Komponensei

### 2.1 Hálózati Eszközök (Network Devices)
- **Fizikai eszközök:** Hálókártya, WiFi adapter, modem
- **Virtuális eszközök:** Bridge, VLAN, tun/tap, veth
- **Kernel interfészek:** `eth0`, `wlan0`, `lo` (loopback)

### 2.2 TCP/IP Stack
- **IP (Internet Protocol):** Címzés és útválasztás
- **TCP (Transmission Control Protocol):** Kapcsolat orientált, megbízható
- **UDP (User Datagram Protocol):** Kapcsolat nélküli, gyors
- **ICMP (Internet Control Message Protocol):** Hálózati diagnosztika (ping)

### 2.3 Socket API
- **Socket:** Hálózati kommunikáció végpontja
- **Bind:** Socket cím hozzárendelése
- **Listen:** Kapcsolatok várakoztatása
- **Accept:** Kapcsolat elfogadása
- **Connect:** Kapcsolat létrehozása
- **Send/Recv:** Adat küldése/fogadása

### 2.4 Netfilter (Tűzfal)
- **iptables/nftables:** Csomag szűrés
- **NAT (Network Address Translation):** Címfordítás
- **Connection tracking:** Kapcsolat követés

## 3. Hálózati Konfiguráció

### 3.1 IP Cím Beállítás
```bash
# IP cím beállítása
ip addr add 192.168.1.100/24 dev eth0

# Alapértelmezett átjáró beállítása
ip route add default via 192.168.1.1

# DNS beállítása
echo "nameserver 8.8.8.8" > /etc/resolv.conf
```

### 3.2 Interface Kezelés
```bash
# Interface aktiválása
ip link set eth0 up

# Interface deaktiválása
ip link set eth0 down

# Interface információk megtekintése
ip addr show
ip link show
```

### 3.3 Útvonalak Kezelése
```bash
# Útvonal hozzáadása
ip route add 10.0.0.0/8 via 192.168.1.1

# Útvonal törlése
ip route del 10.0.0.0/8

# Útvonalak listázása
ip route show
```

## 4. Hálózati Eszközök Típusai

### 4.1 Fizikai Eszközök
- **Ethernet:** Kábel hálózat (RJ45)
- **WiFi:** Vezeték nélküli hálózat
- **Cellular:** Mobil hálózat (4G/5G)

### 4.2 Virtuális Eszközök
- **Bridge:** Több interface összekötése
- **VLAN:** Virtuális LAN
- **TUN/TAP:** Pont-pont vagy Ethernet virtuális eszköz
- **Veth:** Páros virtuális eszköz (konténerhez)
- **Dummy:** Teszteléshez, nincs fizikai háttér

## 5. Hálózati Teljesítmény

### 5.1 TCP Optimalizálás
```bash
# /etc/sysctl.conf
net.core.rmem_max = 16777216
net.core.wmem_max = 16777216
net.ipv4.tcp_rmem = 4096 87380 16777216
net.ipv4.tcp_wmem = 4096 65536 16777216
net.ipv4.tcp_congestion_control = bbr
```

### 5.2 Buffer Tuning
```bash
# Network buffer size
echo 16777216 > /proc/sys/net/core/rmem_max
echo 16777216 > /proc/sys/net/core/wmem_max

# Socket buffer (min default max)
echo "4096 87380 16777216" > /proc/sys/net/ipv4/tcp_rmem
echo "4096 65536 16777216" > /proc/sys/net/ipv4/tcp_wmem
```

### 5.3 IRQ Affinity
```bash
# IRQ affinitás beállítása
echo 1 > /proc/irq/XX/smp_affinity

# Multi-core TCP
echo 2 > /proc/sys/net/ipv4/tcp_syncookies
```

## 6. Hálózati Biztonság

### 6.1 Tűzfal (Firewall)
```bash
# iptables példa
iptables -A INPUT -p tcp --dport 22 -j ACCEPT
iptables -A INPUT -p tcp --dport 80 -j ACCEPT
iptables -A INPUT -j DROP

# nftables példa
nft add table inet filter
nft add chain inet filter input { type filter hook input priority 0 \; }
nft add rule inet filter input tcp dport 22 accept
```

### 6.2 Hálózati Naplózás
```bash
# Csomagok rögzítése
tcpdump -i eth0 -w capture.pcap

# Naplózás megtekintése
tcpdump -r capture.pcap
```

### 6.3 Hálózati Figyelés
```bash
# Kapcsolatok megtekintése
netstat -tuln
ss -tuln

# Hálózati statisztikák
netstat -s
ip -s link show
```

## 7. Hálózati Hibakeresés

### 7.1 Kapcsolat Tesztelés
```bash
# Ping teszt
ping 8.8.8.8

# DNS feloldás teszt
nslookup google.com
dig google.com

# Port teszt
nc -zv 192.168.1.1 80
telnet 192.168.1.1 80
```

### 7.2 Útvonal Követés
```bash
# Útvonal követés
traceroute 8.8.8.8
tracepath 8.8.8.8

# MPLS követés
mpls trace 8.8.8.8
```

### 7.3 Csomag Elemzés
```bash
# Csomagok rögzítése
tcpdump -i eth0 host 192.168.1.100

# Csomagok elemzése
wireshark capture.pcap
tshark -r capture.pcap
```

## 8. Kernel Hálózati Verem

### 8.1 Rétegek
1. **Socket layer:** Alkalmazás réteg
2. **Transport layer:** TCP, UDP
3. **Network layer:** IP, ICMP
4. **Link layer:** Ethernet, WiFi

### 8.2 Csomag Feldolgozás
1. **NIC:** Hálókártya fogadja a csomagot
2. **DMA:** Adat átvitel a memóriába
3. **Interrupt:** CPU értesítése
4. **NAPI:** Interrupt throttling
5. **Network stack:** Csomag feldolgozás
6. **Socket:** Adat átadása az alkalmazásnak

## 9. Összefoglalás

A kernel hálózati rendszere:
- **Kritikus fontosságú** a kommunikációhoz
- **Réteges architektúrával** rendelkezik
- **Testreszabható** teljesítmény és biztonság szempontjából
- **Monitorozható** eszközökkel

A hálózati konfiguráció:
- **Rendszeres ellenőrzés** szükséges
- **Biztonsági beállítások** figyelembevétele
- **Teljesítmény optimalizálás** szükséges nagy terhelés esetén

---

*Dokumentum státusz: STABIL. Nincs félreértés. Nincs feltételezés bizonyítás nélkül.*
