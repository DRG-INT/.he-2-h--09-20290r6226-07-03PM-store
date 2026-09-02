# DOS – Gyakorlati Tudás és Ismertetők
Verzió: 1.0-stable
Forrás: UNICAGD-Core Analízis
Státusz: TUDNIVALÓ

## 1. Miért érdemes ma is a DOS?
A DOS ma is használatos, mert sok régi szoftver (pl. örökölt gyártósor-vezérlő, régión belüli adatbázis, speciális CAD) csak DOS alatt fut. Emellett a DOS rendkívül egyszerű, gyors, és teljes kontrollt ad a hardver felett.

## 2. DOS verziók
### 2.1 MS-DOS
- Microsoft által készített
- 1981-től 2000-ig
- IBM PC DOS és MS-DOS különbségei minimálisak

### 2.2 PC DOS
- IBM által készített
- MS-DOS változat

### 2.3 DR-DOS
- Digital Research által készített
- Kompatibilis MS-DOS-szal
- Több funkció

### 2.4 FreeDOS
- Nyílt forráskódú DOS klón
- 1994-től napjainkig
- Aktív fejlesztés

## 3. DOS Architektúra

### 3.1 Kernel
- Monolitikus kernel
- 16 bites rendszer
- BIOS megszakítások használata
- Memóriakezelés (640KB konvencionális memória)

### 3.2 Parancsértelmező
- COMMAND.COM
- Batch fájlok
- DOS parancsok

### 3.3 Eszközmeghajtók
- Device drivers
- BIOS megszakítások
- INT 13h, INT 21h API

### 3.4 Fájlrendszer
- FAT12, FAT16
- 8.3 fájlnevek
- Nincs jogosultságok

## 4. DOS és a Windows kernel kapcsolata
- A Windows 1.x-3.x a DOS-ra épült
- A Windows 9x/ME a DOS bootol után Windows kernel-t indít
- A Windows NT/XP/7/8/10/11 nem DOS-alapú

## 5. DOS és a Linux kernel kapcsolata
- Nincs közvetlen kapcsolat
- A Linux kernel nem DOS-alapú
- A DOS 16 bites, a Linux 32/64 bites

## 6. DOS fejlesztés
### 6.1 Fejlesztői eszközök
- Turbo Pascal
- Turbo C
- MASM (Microsoft Macro Assembler)
- DEBUG.EXE

### 6.2 Assembly
- x86 assembly
- BIOS megszakítások
- INT 21h API

### 6.3 C fejlesztés
- Turbo C
- Borland C
- DJGPP (32 bites DOS)

## 7. DOS és a biztonság
### 7.1 Hozzáférési szabályok
- Nincs jogosultságok
- Minden program teljes hozzáférést kap
- Nincs felhasználói elkülönítés

### 7.2 Veszélyeztetettség
- Nincs memóriavédelem
- Nincs felhasználói elkülönítés
- Minden program kernel szinten fut

## 8. DOS és a Plan 9
- Nincs közvetlen kapcsolat
- A DOS a CP/M öröse
- A Plan 9 a Unix öröse
- Mindkettő egyszerű, hatékony rendszer

## 9. DOS és a Haiku
- Mindkettő nyílt forráskódú
- A Haiku a BeOS klónja
- A DOS saját rendszer
- Különböző célokat szolgálnak

## 10. DOS tanulságai
- A DOS ma is használatos
- A régi szoftverek futtathatók
- A DOS rendkívül egyszerű
- A DOS teljes kontrollt ad a hardver felett

## 11. Összefoglalás
A DOS egy nagyon jó, de elfelejtett operációs rendszer. Ma is használatos, mert sok régi szoftver csak DOS alatt fut. A FreeDOS a DOS öröksége, nyílt forráskódú formában.

---

*Dokumentum státusz: STABIL. Nincs félreértés. Nincs feltételezés bizonyítás nélkül.*
