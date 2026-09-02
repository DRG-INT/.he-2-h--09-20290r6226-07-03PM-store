# OpenVMS – Gyakorlati Tudás és Ismertetők
Verzió: 1.0-stable
Forrás: UNICAGD-Core Analízis
Státusz: TUDNIVALÓ

## 1. Miért érdemes ma is az OpenVMS?
Az OpenVMS nem csak egy régi rendszer, hanem egy modern, kritikus rendszerekben használt operációs rendszer. A bankszektor, a repülőgép-irányítás, és a gyártósor-vezérlés ma is OpenVMS-t használ.

## 2. Hogyan indulj bele?
- A VSI (VMS Software Inc.) hivatalos honlapjáról letölthető az OpenVMS.
- VirtualBox és VMware támogatott.
- A Hobbyist Program ingyenes licencet ad egyéni használatra.

## 3. OpenVMS és a mai világ
### 3.1 Kritikus rendszerek
- Bankszektor
- Repülőgép-irányítás
- Gyártósor-vezérlés
- Orvosi berendezések

### 3.2 VSI (VMS Software Inc.)
- Jelenlegi OpenVMS fejlesztő
- x86_64 támogatás
- Aktív fejlesztés

## 4. OpenVMS és a Windows kernel kapcsolata
- A Windows NT a VMS-ről vett inspiráción
- Dave Cutler, a VMS architektája, a Windows NT vezető fejlesztője volt

## 5. OpenVMS és a Linux kernel kapcsolata
- Nincs közvetlen kapcsolat
- Mindkettő 64 bites rendszer
- Mindkettő SMP támogatás

## 6. OpenVMS driver fejlesztés
### 6.1 Driver model
- SYS$APORT, SYS$DAGoport
- Device driver API
- Kernel szintű driver-ek

### 6.2 Driver írás
- C és Assembly nyelven
- OpenVMS DDK (Device Driver Kit)
- Blisz, SYS$APORT használata

## 7. OpenVMS és a biztonság
### 7.1 Hozzáférési szabályok
- ACL (Access Control List)
- Privileges
- Auditing

### 7.2 Veszélyeztetettség
- A kritikus rendszerek miatt nagyon biztonságos
- C2 biztonsági osztály
- Common Criteria EAL5+

## 8. OpenVMS és a virtualizáció
### 8.1 VirtualBox és VMware
- OpenVMS futhat virtuális gépen
- Jó fejlesztési és tesztelési környezet

### 8.2 KVM
- KVM támogatás
- QEMU használata

## 9. OpenVMS és a clustering
### 9.1 VMScluster
- Több OpenVMS rendszer összekapcsolása
- Közös fájlrendszer
- Közös eszközök

## 10. OpenVMS tanulságai
- A hosszú életciklus (1977-től napjainkig)
- A kritikus rendszerekben való használat
- A clustering technológia
- A virtual memory kezelés

## 11. Összefoglalás
Az OpenVMS egy nagyon jó, stabil, biztonságos operációs rendszer. A kritikus rendszerekben való használata bizonyítja a megbízhatóságot. A VSI jelenlegi fejlesztése biztosítja, hogy az OpenVMS ma is használható maradjon.

---

*Dokumentum státusz: STABIL. Nincs félreértés. Nincs feltételezés bizonyítás nélkül.*
