# IBM OS/2 Architecture and Legacy
Verzió: 1.0-stable
Forrás: UNICAGD-Core Analízis
Státusz: HASZNÁLHATÓ

## 1. Mi az az OS/2?
Az OS/2 (Operating System/2) az IBM és a Microsoft közös fejlesztésű operációs rendszer, amely 1987-ben jelent meg. A cél az MS-DOS és Windows 3.x utódlása volt, saját, stabil, 16 bites és később 32 bites platformon.

## 2. Történelem
### 2.1 OS/2 1.x (1987-1992)
- 16 bites, csak szöveges felület
- Intel 286/386 processzorokon futott
- MS-DOS kompatibilitás (text-mode DOS session)

### 2.2 OS/2 2.0 (1992)
- 32 bites, Windows 3.x-szerű grafikus felület (Workplace Shell)
- VBDOS (Virtual Box DOS) – teljes MS-DOS 5.0 virtualizáció
- Win-OS/2 – Windows 3.x alkalmazások futtatása OS/2 alatt
- IBM és Microsoft szétválása 1990-ben, a 2.0 már csak IBM fejlesztette

### 2.3 OS/2 Warp (1994-1999)
- OS/2 3.0 és 4.0 verziók
- Javított grafikus felület
- Hálózati támogatás (TCP/IP, NetBIOS)
- Java támogatás

### 2.4 eComStation és ArcaOS
- eComStation (2001-2011): Serenity Systems fejlesztette OS/2-t
- ArcaOS (2017-): Jelenlegi, aktív OS/2 verzió

## 3. OS/2 Architektúra

### 3.1 Kernel
- Hibrid mikrokernel/monolitikus szerkezet
- 16 bites és 32 bites mód támogatása
- Preemptív multitasking

### 3.2 Workplace Shell
- Grafikus felület, objektumorientált
- Hasonlít a gépre dobogós ikonokra, de önálló fejlesztésű
- Nem Windows 3.x, nem UNIX, hanem saját paradigmák

### 3.3 Virtual DOS Machine (VDM)
- Minden DOS alkalmazás saját, izolált környezetben fut
- Teljes MS-DOS kompatibilitás
- Nem egyszerűen emulálás, hanem valódi virtualizáció

### 3.4 Win-OS/2
- Windows 3.x alkalmazások futtatása OS/2 alatt
- A Windows kernel szintű integráció
- Nem csak emuláció, hanem közvetlenül a Windows és az OS/2 közötti kommunikáció

## 4. OS/2 és a Windows kernel kapcsolata
- A Windows NT eredetileg OS/2 3.0-ra lett tervezve (NT = New Technology)
- A Microsoft és IBM együttműködése során a Windows NT 3.1 lett a váltott, az OS/2 pedig önállóan folytatta
- A Windows NT kernel első tervekben nagyban hasonlított az OS/2 kernel struktúrájára

## 5. OS/2 fájlrendszer: HPFS
- High Performance File System
- 255 karakteres fájlnevek (MS-DOS: 8.3)
- Jobb könyvtár struktúra
- Long filename támogatás
- Journaling (későbbi verziókban)

## 6. OS/2 hálózat
- TCP/IP beépített támogatás
- NetBIOS, NetWare, LAN Manager kompatibilitás
- Sockets API (BSD-szerű)

## 7. OS/2 és a mai világ
- ArcaOS: Jelenleg aktív OS/2 verzió, 64 bites UEFI rendszereket is támogat
- Open Source driver fejlesztés
- Legacy alkalmazások futtatása (pl. bankrendszerek, gyártósorok)
- Hobbyist és collector közösség

## 8. OS/2 tanulságai
- A "két nagy" együttműködése (IBM + Microsoft) végül nem működik
- A Windows 3.x és OS/2 közötti kettősség végül a Windows nyert
- A Workplace Shell még mindig a legjobb grafikus felületek egyike (sokan így vélik)
- A hosszú életciklus (1987-től napjainkig) ritka a PC világban

## 9. OS/2 és a kernel tanulás
- A Workplace Shell forráskódja (régebbi verziók) elérhető
- Az OS/2 kernel forráskódja nem nyilvános, de a ReactOS fejlesztők elemzik a működését
- Az OS/2 driver fejlesztés sok-sok Unix és Windows kernel koncepciót egyesít

## 10. Összefoglalás
Az OS/2 egy nagyon jó, de elfelejtett operációs rendszer. A Workplace Shell a grafikus felületek egyik legjobbjának számított. Az IBM és Microsoft közös projekte végül a Windows nyert, de az OS/2 öröksége él tovább az ArcaOS-ban és a retro computing közösségben.

---

*Dokumentum státusz: STABIL. Nincs félreértés. Nincs feltételezés bizonyítás nélkül.*
