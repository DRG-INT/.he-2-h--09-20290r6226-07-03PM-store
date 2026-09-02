# Plan 9 – Gyakorlati Tudás és Ismertetők
Verzió: 1.0-stable
Forrás: UNICAGD-Core Analízis
Státusz: TUDNIVALÓ

## 1. Miért érdemes ma is a Plan 9?
A Plan 9 nem csak egy operációs rendszer, hanem egy teljesen új gondolkodásmód a számítástechnikában. A "minden eszköz fájlrendszer" elv, a 9P protokoll, és a disztribúlt rendszerek kezelése ma is használatos.

## 2. Hogyan indulj bele?
- Töltsd le a 9front ISO-t.
- Írd egy pendrive-ra.
- Bootolj belőle.
- A parancssor a `rc` shell, hasonlít a bashhez, de más.
- Az `acme` szerkesztő a rendszer része.

## 3. Plan 9 és a modern rendszerek
### 3.1 9P protokoll
- A 9P protokoll ma is használatos
- A Linux kernel támogatja a 9P-t
- A WSL (Windows Subsystem for Linux) hasonló koncepciót használ

### 3.2 Nincs root
- Nincs sudo, nincs su
- Minden felhasználó ugyanazokkal a jogokkal rendelkezik
- Az eszközök fájlrendszere a hozzáférési szint kezelése

### 3.3 Nincs nagy kernel
- A kernel csak a legszükségesebb funkciókat végzi
- A legtöbb szolgáltatás felhasználói szinten fut

## 4. Plan 9 fejlesztés
### 4.1 Forráskód
- A Plan 9 forráskódja elérhető a Lucent Public License alatt
- Kis, olvasható kernel
- Nincs bonyolult VFS, nincs bonyolult hálózati verem

### 4.2 Nyelv
- A `rc` shell a bash helyett
- Az `acme` szerkesztő a vim helyett
- A Plan 9 saját eszközei

## 5. Plan 9 és a biztonság
### 5.1 Hozzáférési szabályok
- Fájljogosultságok
- Nincs root
- Nincs sudo

### 5.2 Veszélyeztetettség
- Kis felhasználói bázis
- Kevesebb támadási felület
- De kevésbé tesztelt

## 6. Plan 9 és a virtualizáció
### 6.1 QEMU
- Plan 9 futhat QEMU-ban
- Jó fejlesztési és tesztelési környezet

### 6.2 VMware és VirtualBox
- Plan 9 futhat VirtualBox-ban és VMware-ban
- Jó fejlesztési és tesztelési környezet

## 7. Plan 9 és a Linux kernel kapcsolata
- A Plan 9 a Unix öröse
- A Linux kernel a Unix öröse
- Mindkettő POSIX kompatibilis
- A Plan 9 egyszerűbb, a Linux bonyolultabb

## 8. Plan 9 és a Windows kernel kapcsolata
- Nincs közvetlen kapcsolat
- A Plan 9 a Unix öröse
- A Windows NT hibrid mikrokernel/monolitikus

## 9. Plan 9 tanulságai
- A "minden eszköz fájlrendszer" elv még mindig a legjobb megoldás
- A disztribúlt rendszerek kezelése egyszerűbben
- A 9P protokoll ma is használatos

## 10. Összefoglalás
A Plan 9 egy nagyon jó, de elfelejtett operációs rendszer. A "minden eszköz fájlrendszer" elv, a 9P protokoll, és a disztribúlt rendszerek kezelése ma is használatos. A Plan 9 a Unix öröksége, de saját úton halad.

---

*Dokumentum státusz: STABIL. Nincs félreértés. Nincs feltételezés bizonyítás nélkül.*
