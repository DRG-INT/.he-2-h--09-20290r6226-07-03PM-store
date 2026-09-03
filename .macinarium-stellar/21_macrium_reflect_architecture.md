# Macrium Reflect – System Imaging és Recovery Technikai Dokumentáció
Verzió: 1.0-stable
Forrás: UNICAGD-Core Analízis
Státusz: HASZNÁLHATÓ

## 1. Mi az a Macrium Reflect?
A Macrium Reflect egy Windows alapú rendszerkép-készítő (system imaging) és helyreállítási szoftver. Kernel szintű block I/O-t és VSS-t használ, így teljes lemezképeket készíthet futó rendszerről is.

## 2. Architektúra és Működés

### 2.1 Reflect Imaging Engine
- Kernel szintű szektorolvasás és írás
- Fájlrendszer-független, raw block szintű képkészítés
- NTFS, FAT, exFAT, ReFS, ext2/3/4, HFS+ támogatás
- Dinamikus és alapértelmezett lemezpartíciók detektálása

### 2.2 VSS (Volume Shadow Copy Service) integráció
- Windows VSS API használata
- Alkalmazások adatkonzisztenciája pillanatkép ideje alatt
- Exchange, SQL Server, Active Directory támogatott
- Post-snapshot parancsok futtatása

### 2.3 Delta és Incrementális Képek
- Teljes, inkrementális és differenciális mentések
- Blokkszintű delta-észlelés
- Delta restore: csak a változott blokkok helyreállítása
- RTO (Recovery Time Objective) optimalizálás

### 2.4 Kernel szintű I/O
- Direct disk access
- Boot sector és partition table mentés
- Fizikai és logikai lemezek kezelése
- GPT és MBR partíciók támogatása

## 3. Backup és Recovery Módok

### 3.1 Disk Imaging
- Teljes lemez képkészítés
- Partícióalapú képkészítés
- Rendszerpartíció, boot partíció, adatpartíciók külön-külön

### 3.2 File and Folder Backup
- Fájl és mappa szintű mentés
- Zip kompresszió
- AES-256 titkosítás
- Jelszóvédelem

### 3.3 Recovery
- Delta restore
- Partíció visszaállítás
- Lemez klónozás
- Universal Restore: másik hardverre történő helyreállítás
- WinPE vagy Linux Recovery Media alapú helyreállítás

## 4. OEM, Deployment és Mass Deployment

### 4.1 OEM és System Integrators
- Golden image készítés és üzembe helyezés
- Reseller és OEM licencmodellek
- OEM Recovery Partitions létrehozása
- Custom recovery environments

### 4.2 Mass Deployment
- Szabványosított rendszerképek
- Több célpont üzembe helyezése
- Script alapú telepítés
- Active Directory integráció

### 4.3 Deployment Tools
- Reflect Deploy
- Macrium Deployment Kit
- WinPE Recovery Media Builder
- USB, CD/DVD, ISO támogatás

## 5. Kernel szintű Részletek

### 5.1 Block I/O
- Raw sector access a Windows I/O manageren keresztül
- Filter driver és miniport driver réteg
- Disk I/O szabályozás és időzítés

### 5.2 VSS Integration
- VSS Writer regisztráció
- Copy-on-write snapshot
- Application-consistent és crash-consistent mentések
- Writers: MSDE, Exchange, SQL, SharePoint

### 5.3 Recovery Media
- WinPE alapú recovery
- Linux Rescue Media
- Network boot: PXE, HTTP, FTP, SMB
- USB 3.0, NVMe, UEFI, Secure Boot támogatás

## 6. Biztonság és Integritás

### 6.1 Image Integritás
- MD5, SHA-1, SHA-256 checksum
- Képek érvényesítése mentés előtt és után
- Rendszerindítási ellenőrzés

### 6.2 Titkosítás
- AES-256 titkosítás a képeken
- Jelszóvédelem
- XTS mód

### 6.3 Kompresszió
- LZ4, LZO, zlib, bzip2
- Mentési sebesség és helyfoglalás egyensúlya
- Blokkszintű duplikáció elkerülése

## 7. Hibakeresés és Karbantartás

### 7.1 Image Hibakeresés
- `macrium_verify` image validáció
- Log elemzés
- Recovery Media indítási problémák

### 7.2 VSS Hibakeresés
- VSS Writer állapot
- `vssadmin` és `diskshadow` használata
- Writer timeout és freeze/thaw hiba

### 7.3 Kernel I/O Hibakeresés
- Block device hozzáférés
- Driver konfliktus
- Disk partíció és fájlrendszer hiba

## 8. Összefoglalás
A Macrium Reflect egy megbízható, kernel szintű rendszerkép és helyreállítási megoldás. VSS, delta restore, OEM deployment és mass deployment képességekkel rendelkezik. Kritikus rendszerekben, ahol az uptime és a helyreállítási idő kulcsfontosságú, a Macrium egy ipari szintű választás.

---

*Dokumentum státusz: STABIL. Nincs félreértés. Nincs feltételezés bizonyítás nélkül.*
