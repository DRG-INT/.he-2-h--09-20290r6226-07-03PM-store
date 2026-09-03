# macOS (Darwin & XNU) – Gyakorlati Rendszerkezelés és Terepi Ismertetők
Verzió: 1.0-stable
Forrás: UNICAGD-Core Analízis / DRG-INT Védelmi Rendszertan
Státusz: HASZNÁLHATÓ (Kritikus Infrastruktúra Kézikönyv)

## 1. Miért Érdekes a macOS a Rendszermérnök Számára?

A macOS a világ legszélesebb körben elterjedt tanúsított UNIX rendszere (Open Group UNIX 03 tanúsítvány). A felhasználói felület (Aqua) alatt a robusztus nyílt forráskódú **Darwin** alaprendszer és az **XNU** (X is Not Unix) hibrid kernel dolgozik.

Fő jellemzői a terepi mérnök számára:
- **`launchd` PID 1:** A világ első univerzális eseményvezérelt szolgáltatásfelügyelője (a systemd ihletője).
- **APFS (Apple File System):** Natív pont-az-időben pillanatképek (snapshots), írás közbeni másolás (Copy-on-Write) és hardveresen titkosított konténerek.
- **SIP (System Integrity Protection) & SSV:** Írásvédett, kriptográfiailag aláírt és lepecsételt rendszervolumen (Signed System Volume).
- **Unified Logging:** Bináris, alacsony késleltetésű strukturált naplózási motor (`log` parancs).

---

## 2. Szolgáltatásfelügyelet: A `launchd` Rendszer

A macOS-en nincsenek System V init szkriptek és nincs systemd sem. Minden háttérfolyamatot a `/sbin/launchd` kezel XML formátumú `.plist` (Property List) fájlok alapján.

### 2.1 Konfigurációs Útvonalak
- `/System/Library/LaunchDaemons`: Apple által aláírt alaprendszeri démonok (SIP védett, nem módosítható).
- `/Library/LaunchDaemons`: Rendszerszintű, root joggal induló háttérdémonok (SCADA, VPN, biztonsági szondák).
- `/Library/LaunchAgents`: Minden bejelentkezett felhasználó kontextusában futó háttérfolyamatok.

### 2.2 Szolgáltatások Kezelése (`launchctl`)
```bash
# Démon betöltése és azonnali elindítása (Modern API)
sudo launchctl bootstrap system /Library/LaunchDaemons/com.defense.telemetry.plist

# Futó szolgáltatás állapotának lekérdezése
sudo launchctl print system/com.defense.telemetry

# Szolgáltatás újraindítása (kill & restart)
sudo launchctl kickstart -k system/com.defense.telemetry

# Szolgáltatás eltávolítása a futási körből
sudo launchctl bootout system/com.defense.telemetry
```

---

## 3. APFS Pillanatképek és Helyreállítás

Az APFS fájlrendszer lehetővé teszi a pillanatszerű, zéró lemezterület-igényű snapshotok készítését:

```bash
# Helyi pillanatkép készítése a gyökérkötetről
tmutil localsnapshot

# Elérhető pillanatképek listázása
diskutil apfs listSnapshots /

# Pillanatkép írásvédett csatolása vizsgálathoz vagy adatmentéshez
mkdir -p /Volumes/snapshot_inspect
mount_apfs -s "com.apple.TimeMachine.2026-09-03-013000.local" / /Volumes/snapshot_inspect

# Visszaállítás korábbi pillanatképből a macOS Recovery környezetből
# (Vészhelyzetben a terminálból): apfs_snapshot_revert
```

---

## 4. Rendszervédelem: SIP és SSV Kezelése

### 4.1 System Integrity Protection (SIP)
A SIP megakadályozza, hogy még a `root` felhasználó is módosítsa a kritikus rendszerbinárisokat vagy kext-et injektáljon a kernelbe.

```bash
# SIP státusz ellenőrzése
csrutil status
# Normál kimenet: System Integrity Protection status: enabled.

# Hitelesített Rendszervolumen (Signed System Volume - SSV) ellenőrzése:
csrutil authenticated-root status
```
*Megjegyzés:* A SIP kikapcsolása kizárólag Recovery módban (`csrutil disable`) hajtható végre, és éles rendszereken szigorúan ellenjavallt.

---

## 5. Unified Logging: Nagysebességű Naplóelemzés

A hagyományos `syslog` és szöveges `/var/log` fájlok helyett a macOS bináris ring-buffereket használ:

```bash
# Élő naplófolyam szűrése kernel pánikok és I/O hibák esetén
log stream --predicate 'eventMessage CONTAINS[c] "panic" OR eventMessage CONTAINS[c] "I/O error"' --level debug

# Adott alrendszer (pl. IOKit vagy hálózat) elmúlt 1 órájának elemzése
log show --predicate 'subsystem == "com.apple.kernel"' --last 1h --style syslog

# Crash reportok közvetlen elérése
ls -la /Library/Logs/DiagnosticReports/
```

---

## 6. DriverKit és Kext Diagnosztika

A macOS a veszélyes Ring-0 Kernel kiterjesztéseket (kext) kivezette, és a felhasználói térben futó **DriverKit** (`.dext`) architektúrát használja.

```bash
# Betöltött kext-ek listázása (csak a harmadik féltől származók)
kextstat | grep -v com.apple

# Modern DriverKit rendszerkiterjesztések (DEXT) auditálása
systemextensionsctl list

# Kernel modulok ellenőrzése és diagnosztikája (kmutil)
kmutil check
```

---
*Dokumentum státusz: STABIL · UNICAGD-Core Terepi Kézikönyv*
