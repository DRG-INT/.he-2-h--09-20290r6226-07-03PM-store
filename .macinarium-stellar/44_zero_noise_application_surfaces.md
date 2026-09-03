# Zajmentes Alkalmazásfelületek (Zero-Noise Application Surfaces)
Verzió: 1.0-stable
Forrás: UNICAGD-Core / DRG-INT Védelmi Rendszertan
Státusz: HASZNÁLHATÓ (Zéró-Telemetria és Elszigetelt Felhasználói Felületek)

---

## 1. A "Zajmentes" (Zero-Noise) Tervezési Alapelv

A modern operációs rendszerek felhasználói rétege tele van háttérzajjal: mDNS felderítő csomagok, D-Bus feliratkozások, X11/Wayland szerverek IPC forgalma, böngészőmotorok háttérszálai és automatikus csomagfrissítési lekérdezések.

Kritikus, offline (air-gapped) és védett rendszereken **minden felesleges folyamat és hálózati csomag biztonsági kockázat és zajforrás**.

```
+─────────────────────────────────────────────────────────────────────────────+
|               ZAJMENTES ALKALMAZÁSI ARCHITEKTÚRA (ZERO-NOISE)               |
+─────────────────────────────────────────────────────────────────────────────+
|                                                                             |
|   [ FELÜLET 1: KÖZVETLEN DRM/KMS KERETPUFFER (DUMB BUFFER) ]                |
|   • Nincs X11, nincs Wayland, nincs ablakkezelő                             |
|   • Közvetlen rajzolás a grafikus kártya memóriájába (/dev/dri/card0)       |
|                                                                             |
|   [ FELÜLET 2: FÜGGETLEN ANSI/VT100 TUI KONZOL ]                            |
|   • Zéró külső függőség (ncurses-mentes tiszta ANSI szekvenciák)            |
|   • Villogásmentes kettős pufferelés a soros vagy virtuális TTY-n           |
|                                                                             |
|   [ FELÜLET 3: HELYI UNIX DOMAIN SOCKET IPC ]                               |
|   • Nincs nyitott TCP/IP port (0.0.0.0 zárva, offline integritás)           |
|   • Determinisztikus bináris vagy JSON-RPC üzenetváltás (/run/app.sock)     |
|                                                                             |
+─────────────────────────────────────────────────────────────────────────────+
```

---

## 2. A Három Zajmentes Felület Részletei

### 2.1 Felület 1: Közvetlen DRM/KMS Keretpuffer (Zero Desktop)
- Az alkalmazás közvetlenül a Linux Kernel Mode Setting (KMS) felületéhez csatlakozik az `ioctl(fd, DRM_IOCTL_MODE_CREATE_DUMB, ...)` hívással.
- **Eredmény:** Teljes képernyős, alacsony késleltetésű grafikus felület anélkül, hogy futna az Xorg, a Mutter vagy a Wayland. Zéró memóriaszemét, azonnali renderelés.

### 2.2 Felület 2: Független ANSI/VT100 TUI Műszerfal
- Bármilyen szöveges terminálon, soros konzolon (RS-232/RS-485) vagy SSH-n azonnal működik.
- Nem igényel betöltött grafikus meghajtót vagy bonyolult widget-könyvtárakat.
- Egyszerű vezérlőkódokkal (`\033[2J`, `\033[H`) másodpercenként 60-szor frissíthető anélkül, hogy CPU terhelést vagy hálózati forgalmat generálna.

### 2.3 Felület 3: Zárt Helyi IPC (UNIX Domain Socket)
- Az offline gépen nincs szükség hálózati csatolóra (`eth0` lekapcsolva).
- A folyamatok közötti kommunikáció kizárólag fájlrendszer-alapú UNIX sockettel (`AF_UNIX`) vagy osztott memóriával (`shm_open`) történik.
- Nincs DNS-keresés, nincs ARP sugárzás, nincs adatküldés a helyi hálózatra.

---

## 3. Rendszerzaj Iktatási Szabályzat (Field Hardening Checklist)

1. **Rendszerdémonok kiiktatása:** `avahi-daemon`, `cups`, `systemd-resolved`, `whoopsie`, `ModemManager` letiltása.
2. **Konzolra szűkítés:** A rendszer automatikusan a TUI műszerfalra induljon el `systemd.default_target=multi-user.target` vagy Void/Alpine alatt `inittab` közvetlen TTY terminálon.
3. **Immutábilis naplózás:** Memóriába (RAM disk / tmpfs) történő strukturált körkörös naplózás, felesleges lemezműveletek nélkül.

---
*Dokumentum státusz: STABIL · UNICAGD-Core Zéró-Zaj Architektúra*
