# FreeBSD – Gyakorlati Rendszerkezelés és Terepi Ismertetők
Verzió: 1.0-stable
Forrás: UNICAGD-Core Analízis / DRG-INT Védelmi Rendszertan
Státusz: HASZNÁLHATÓ (Kritikus Infrastruktúra Kézikönyv)

## 1. Miért FreeBSD a Védelmi és Ipari Hálózatokban?

A FreeBSD a világ egyik legstabilabb monolitikus operációs rendszere. Kiváló hálózati veremmel, zéró-másolásos adatmozgatással és szigorú architektúrális szeparáltsággal rendelkezik (a Base System és a Third-Party szoftverek élesen el vannak választva).

Fő erősségei kritikus feladatoknál:
- **`GEOM` moduláris blokk-réteg:** Titkosított partíciók és katonai szintű titkosított crash dumpok (`dumpon -k`).
- **`Capsicum` képesség-alapú sandboxing:** Fájlleíró szinten korlátozható rendszerhívási jogok.
- **`DTrace` natív támogatás:** Mikroszekundumos kernel nyomkövetés a termelési rendszer megállítása nélkül.
- **`OpenZFS` integritás:** Öngyógyító adatintegritás, snapshotok és boot környezetek (`beadm`, `bectl`).

---

## 2. Alaprendszer és Hálózati Konfiguráció

### 2.1 A `/etc/rc.conf` Központi Konfiguráció
Minden rendszerszolgáltatás és hálózati interfész a `/etc/rc.conf` állományban definiált:
```bash
# Gépnév és hálózat
hostname="node-defense-alpha"
ifconfig_em0="inet 192.168.10.5 netmask 255.255.255.0"
defaultrouter="192.168.10.1"

# Biztonsági szolgáltatások
sshd_enable="YES"
pf_enable="YES"
pf_rules="/etc/pf.conf"

# Memóriakép mentés összeomláskor
dumpdev="AUTO"
crashinfo_enable="YES"
```

### 2.2 Szolgáltatások Kezelése (`service` parancs)
```bash
# Szolgáltatás státusza és újraindítása
service pf status
service pf restart

# Démonok engedélyezése közvetlenül parancssorból
sysrc sshd_enable="YES"
sysrc dumpdev="AUTO"
```

---

## 3. GEOM és Titkosított Memóriakép Mentés (GELI & dumpon)

Katonai és titkosított rendszereken tilos sima szövegként a lemezre írni a kernel crash dumpot, mert az memóriatartalmat (kulcsokat, titkosított adatfolyamokat) tartalmaz.

### 3.1 Titkosított Dump Eszköz Beállítása (`dumpon -k`)
```bash
# Dump eszköz konfigurálása RSA nyilvános kulccsal védett AES-CBC titkosítással:
# 1. RSA kulcspár generálása
openssl genrsa -out /etc/crash_dump.key 4096
openssl rsa -in /etc/crash_dump.key -pubout -out /etc/crash_dump.pub

# 2. Titkosított dump konfigurálása a cserehelyre (swap)
dumpon -k /etc/crash_dump.pub /dev/da0p2

# 3. Összeomlás utáni dekódolás (elszigetelt gépen a privát kulccsal):
savecore -k /etc/crash_dump.key /var/crash/
```

### 3.2 ZFS Tükrözés és Boot Környezetek (`bectl`)
```bash
# Új boot környezet létrehozása frissítés előtt
bectl create pre-upgrade-kernel

# Boot környezetek listázása
bectl list

# Visszaállás vészhelyzet esetén
bectl activate pre-upgrade-kernel
```

---

## 4. Jails és Hálózati Izoláció (VNET)

A Jail egy könnyűsúlyú, szigorúan elkülönített operációsrendszer-szintű virtualizáció.

### 4.1 Jail Konfiguráció (`/etc/jail.conf`)
```text
# Globális beállítások
exec.start = "/bin/sh /etc/rc";
exec.stop = "/bin/sh /etc/rc.shutdown";
exec.clean;
mount.devfs;

# SCADA izolált hálózati csomópont
scada_jail {
    path = "/jails/scada_node";
    host.hostname = "scada-isolated.local";
    ip4.addr = 192.168.10.50;
    interface = em0;
    allow.raw_sockets = 0;   # RAW socket tiltás (nem tud csomagot injektálni)
}
```

### 4.2 Jail Indítása és Felügyelete
```bash
# Jail indítása és leállítása
jail -c scada_jail
jail -r scada_jail

# Futó jailek megtekintése
jls

# Belépés a jail környezetbe
jexec scada_jail /bin/sh
```

---

## 5. DTrace Gyakorlati Használat Incidenskezeléskor

A `dtrace` a rendszer legmélyebb pontjait képes vizsgálni valós időben:

```bash
# 1. Rendszerhívások számlálása folyamatonként (Top Syscallers)
dtrace -n 'syscall:::entry { @[execname] = count(); }'

# 2. Fájl megnyitások valós idejű követése
dtrace -n 'syscall::openat:entry { printf("%s -> %s", execname, copyinstr(arg1)); }'

# 3. Kernel zár várakozási idők (lock contention audit)
dtrace -n 'lockstat:::adaptive-block { @[execname] = sum(arg1); }'

# 4. Hálózati csomagok beérkezési késleltetése
dtrace -n 'fbt::ip_input:entry { @[stack()] = count(); }'
```

---

## 6. Összeomlás (Panic) Hibakeresés FreeBSD-n

Ha a FreeBSD kernel pánikba esik, a következő parancsokkal elemezhető:

```bash
# Crash dump könyvtár tartalma
ls -la /var/crash/
# Megtalálható: core.txt.0 (crashinfo szöveges elemzés) és vmcore.0

# Elemzés kgdb segítségével
kgdb /boot/kernel/kernel /var/crash/vmcore.0

# KGDB parancsok a hiba okának kiderítéséhez:
(kgdb) bt                   # Stack backtrace
(kgdb) ps                   # Folyamatok állapota
(kgdb) print panicstr       # A pontos pánik üzenet sztringje
```

---
*Dokumentum státusz: STABIL · UNICAGD-Core Terepi Kézikönyv*
