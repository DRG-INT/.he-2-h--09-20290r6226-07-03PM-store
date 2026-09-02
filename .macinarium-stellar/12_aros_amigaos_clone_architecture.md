# AROS (AmigaOS Clone) Architecture
Verzió: 1.0-stable
Forrás: UNICAGD-Core Analízis
Státusz: HASZNÁLHATÓ

## 1. Mi az a AROS?
Az AROS (Amiga Research Operating System) egy nyílt forráskódú AmigaOS klón. Célja, hogy teljesen kompatibilis legyen az AmigaOS API-val, és modern hardveren is fusson.

## 2. Történelem
### 2.1 AmigaOS (1985)
- Commodore által készített
- Motorola 68000 processzorokon futott
- Grafikus felület, hang, multitasking

### 2.2 AROS indítása (1995)
- AROS projekt 1995-ben indult
- Cél: AmigaOS klón, nyílt forráskódú
- Az AmigaOS forráskódja nem elérhető, reverse engineering alapú

### 2.3 Jelenlegi állapot
- Aktív fejlesztés
- x86_64 támogatás
- ARM támogatás
- AmigaOS API kompatibilitás

## 3. AROS Architektúra

### 3.1 Kernel
- Hibrid mikrokernel/monolitikus szerkezet
- Preemptív multitasking
- SMP támogatás
- AmigaOS API kompatibilitás

### 3.2 Fájlrendszer
- FFS (Fast File System)
- SFS (Smart File System)
- Journaling
- Attribútumok

### 3.3 Grafikus rendszer
- 32 bites színmélység
- HAM (Hold And Modify) mód
- Chunky és planar mód
- Intuition grafikus rendszer

### 3.4 Hangrendszer
- 4 csatornás PCM hang
- Alacsony késleltetés
- MIDI támogatás

## 4. AROS és a mai világ

### 4.1 Alkalmazások
- AmigaOS alkalmazások futtathatók
- AROS alkalmazások
- Portolt alkalmazások (Firefox, VLC)

### 4.2 Hardware támogatás
- x86_64 processzorok
- ARM processzorok
- Hálókártyák, hangkártyák, grafikus kártyák

### 4.3 Közösség
- Aktív fejlesztés
- Open Source (MIT licenc)
- Közösségi támogatás

## 5. AROS és a Windows kernel kapcsolata
- Nincs közvetlen kapcsolat
- Az AROS saját kernelje van
- A Windows NT hibrid mikrokernel/monolitikus

## 6. AROS és a Linux kernel kapcsolata
- Nincs közvetlen kapcsolat
- Az AROS saját kernelje van
- Mindkettő 32 bites és 64 bites rendszer

## 7. AROS driver fejlesztés
### 7.1 Driver model
- Kernel szintű driver-ek
- AmigaOS API kompatibilitás
- Device driver API

### 7.2 Driver írás
- C nyelven
- AROS DDK (Device Driver Kit)
- Kernel API használata

## 8. AROS és a biztonság
### 8.1 Hozzáférési szabályok
- AmigaOS jogosultságok modelle
- ACL támogatás
- Felhasználók és csoportok

### 8.2 Veszélyeztetettség
- Kis felhasználói bázis
- Kevesebb támadási felület
- De kevésbé tesztelt

## 9. AROS és a Plan 9
- Nincs közvetlen kapcsolat
- Az AROS az AmigaOS öröksége
- A Plan 9 a Unix öröse
- Mindkettő egyszerű, hatékony rendszer

## 10. AROS és a Haiku
- Mindkettő nyílt forráskódú, másik operációs rendszer klónja
- A Haiku a BeOS klónja
- Az AROS az AmigaOS klónja
- Különböző célokat szolgálnak

## 11. AROS tanulságai
- Az AmigaOS öröksége él tovább
- A reverse engineering lehetővé teszi egy zárt rendszer újraépítését
- A modern hardver támogatása

## 12. Összefoglalás
Az AROS egy nagyon jó, de elfelejtett operációs rendszer. Az AmigaOS öröksége teljesen megőrizve van. Az AROS az AmigaOS-vágott modern korban való folytatása.

---

*Dokumentum státusz: STABIL. Nincs félreértés. Nincs feltételezés bizonyítás nélkül.*
