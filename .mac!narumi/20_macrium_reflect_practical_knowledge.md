# Macrium Reflect – Gyakorlati Tudás és Ismertetők
Verzió: 1.0-stable
Forrás: UNICAGD-Core Analízis
Státusz: TUDNIVALÓ

## 1. Miért érdemes a Macrium Reflect?
A Macrium Reflect nem csak egy backup program. Olyan kernel szintű eszköz, amivel teljes lemezképeket készíthetsz, klónozhatsz, és helyreállíthatsz anélkül, hogy a Windows elérhető lenne. Kritikus rendszereknél, OEM és deployment esetén ez a sorsfordító.

## 2. Hogyan indulj bele?
- Töltsd le a Macrium Reflect-t.
- Indíts egy mentést: válaszd ki a céllemezt, a formátumot (VHDX, VMDK, RAW), és a tömörítést.
- Ha mentés közben akarsz kilépni, beállíthatsz ütemezett feladatot.
- Ha helyreállítani akarsz, készíts Recovery Media-t (USB vagy ISO).

## 3. Gyakorlati használat

### 3.1 Teljes lemezkép
- Kiválasztod a forráslemezt.
- Kiválasztod a célhelyet (külső HDD, NAS, USB).
- Beállítod a tömörítést és a titkosítást.
- Elindítod a mentést.

### 3.2 Delta és Incrementális mentés
- Először teljes mentés.
- Utána inkrementális vagy differenciális mentések.
- Csak a változott blokkok mentése.
- Helytakarékos és gyors.

### 3.3 Delta restore
- Csak a változott blokkok helyreállítása.
- RTO minimalizálása.
- Nagy rendszereknél időtakarékos.

## 4. OEM és Deployment

### 4.1 Golden image
- Egy alapértelmezett Windows rendszerkép.
- Alkalmazások, beállítások, driver-ek beleépítve.
- Több célpontra történő üzembe helyezés.

### 4.2 Mass deployment
- Több gép egyszerre történő telepítése.
- Network boot: PXE, HTTP, FTP, SMB.
- Unattended telepítés.

## 5. Recovery

### 5.1 Recovery Media
- WinPE alapú recovery.
- Linux Rescue Media.
- USB, CD/DVD, ISO.
- UEFI, Secure Boot, NVMe, USB 3.0 támogatás.

### 5.2 Universal Restore
- Másik hardverre történő helyreállítás.
- CPU, chipset, storage controller váltás.
- Windows újrainaktiválása vagy sysprep.

## 6. VSS és alkalmazáskonzisztencia

### 6.1 VSS bekapcsolása
- Exchange, SQL Server, Active Directory.
- Alkalmazások adatkonzisztenciája pillanatkép ideje alatt.
- Post-snapshot parancsok futtatása.

### 6.2 VSS hibakeresés
- `vssadmin list writers` állapot ellenőrzés.
- `diskshadow` használata.
- Writer timeout és freeze/thaw hiba.

## 7. Kernel szintű részletek

### 7.1 Block I/O
- Raw sector access.
- Filter driver és miniport driver réteg.
- Disk I/O szabályozás és időzítés.

### 7.2 Fájlrendszerek
- NTFS, FAT, exFAT, ReFS, ext2/3/4, HFS+.
- Partíciók detektálása.
- Boot sector és partition table mentés.

### 7.3 Kompresszió és titkosítás
- LZ4, LZO, zlib, bzip2.
- AES-256 titkosítás.
- XTS mód.

## 8. Hibakeresés

### 8.1 Image hibakeresés
- `macrium_verify` image validáció.
- Log elemzés.
- Recovery Media indítási problémák.

### 8.2 Kernel I/O hibakeresés
- Block device hozzáférés.
- Driver konfliktus.
- Disk partíció és fájlrendszer hiba.

## 9. Összefoglalás
A Macrium Reflect egy megbízható, kernel szintű rendszerkép és helyreállítási megoldás. VSS, delta restore, OEM deployment és mass deployment képességekkel rendelkezik. Kritikus rendszereknél, ahol az uptime és a helyreállítási idő kulcsfontosságú, a Macrium egy ipari szintű választás.

---

*Dokumentum státusz: STABIL. Nincs félreértés. Nincs feltételezés bizonyítás nélkül.*
