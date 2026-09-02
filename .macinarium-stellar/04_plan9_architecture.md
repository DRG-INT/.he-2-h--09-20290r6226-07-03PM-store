# Plan 9 from Bell Labs Architecture
Verzió: 1.0-stable
Forrás: UNICAGD-Core Analízis
Státusz: HASZNÁLHATÓ

## 1. Mi az a Plan 9?
A Plan 9 a Bell Labs (Rob Pike, Ken Thompson, Dennis Ritchie) által készített operációs rendszer, a Unix öröse. 1992-ben jelent meg, és a "minden eszköz fájlrendszer" elvét követi.

## 2. Alap Elvek
### 2.1 Minden Eszköz Fájlrendszer
- Minden eszköz (egér, billentyűzet, hálózat, processzor) fájlrendszerként érhető el
- `/dev/cons` – konzol
- `/dev/mouse` – egér
- `/dev/net` – hálózat
- `/dev/prog` – processzorok
- `/dev/stat` – statisztikák

### 2.2 Nincs root felhasználó
- Minden felhasználó ugyanazokkal a jogokkal rendelkezik
- Az eszközök fájlrendszere a hozzáférési szint kezelése

### 2.3 Nincs nagy, monolitikus kernel
- A kernel csak a legszükségesebb funkciókat végzi
- A legtöbb szolgáltatás felhasználói szinten fut

## 3. Plan 9 Architektúra

### 3.1 Kernel
- Minimalista, mikrokernel-szerű
- Szálak, processzek, memóriakezelés
- Nincs hálózati verem a kernelben
- Nincs fájlrendszer VFS

### 3.2 9P Protokoll
- Minden erőforrás 9P protokollon keresztül elérhető
- Hálózati fájlrendszer
- Eszközök, processzek, adatok távoli elérése

### 3.3 Namespace
- Minden processznek saját névtere van
- Fájlok, eszközök, szolgáltatások különböző elérési útvonalakkal
- Példa: `/dev/cons` egy processznek konzol, a másiknak eszköz

### 4. Plan 9 Főbb Komponensei
- **Inferno:** Plan 9 unokaöccse, disztríbutált rendszer, Lua script nyelv
- **9front:** Aktív Plan 9 fork, modern hardver támogatással
- **9legacy:** Eredeti Plan 9 forráskód

## 5. Plan 9 és a mai világ
### 5.1 9front
- Aktív fejlesztés
- x86_64, ARM, RISC-V támogatás
- Modern alkalmazások: Firefox, Acme szerkesztő, rc shell
- Git backend

### 5.2 Örökség
- A Go nyelv (Rob Pike) tervezte a Plan 9-es tapasztalatokkal
- A UTF-8 elterjedése (Ken Thompson és Rob Pike)
- A /n/ (null-terminated strings) vs null-terminated strings viták
- A Plan 9-es minden-eszköz-fájlrendszer elv a modern Unix-ból hiányzik

## 6. Plan 9 és a kernel tanulás
### 6.1 Forráskód
- A Plan 9 forráskódja elérhető a Lucent Public License alatt
- Kis, olvasható kernel
- Nincs bonyolult VFS, nincs bonyolult hálózati verem

### 6.2 Plan 9 és a Unix
- A Plan 9 a Unix direkt utódja
- A /usr/src/linux (Linux) és a /sys/src (Plan 9) közötti különbségek tanulságosak
- A Plan 9 egyszerűsége ellenében a Linux bonyolultsága

## 7. Plan 9 és a disztribúált rendszerek
- A 9P protokoll lehetővé teszi, hogy több gép közös névteret használjon
- Távoli eszközök, fájlok, processzek ugyanúgy elérhetők, mint helyiek
- Nincs NFS, nincs CIFS, csak 9P

## 8. Plan 9 és a biztonság
- Minden eszköz fájlrendszerként van kezelve
- Hozzáférési szabályok egyszerűen kezelhetők (fájljogosultságok)
- Nincs root, nincs sudo, csak jogosultságok

## 9. Plan 9 és a modern rendszerek
### 9.1 A mi rendszereink
- A Linux nincs 9P alapú fájlrendszer alapból
- A Plan 9 eszközök nem elérhetők Linux alatt
- A /dev/plumb9 és hasonló eszközök hiányoznak

### 9.2 Mi veszett el?
- A Unix filozófiája ("minden eszköz fájl")
- A 9P protokoll
- A namespace izoláció
- A hálózati fájlrendszer egyszerűsége

## 10. Összefoglalás
A Plan 9 egy nagyon egyszerű, de nagyon hatékony operációs rendszer. A "minden eszköz fájlrendszer" elv még mindig a legjobb megoldás a disztribúlt rendszerekhez. A 9front projekt bizonyítja, hogy a Plan 9 öröksége él tovább.

---

*Dokumentum státusz: STABIL. Nincs félreértés. Nincs feltételezés bizonyítás nélkül.*
