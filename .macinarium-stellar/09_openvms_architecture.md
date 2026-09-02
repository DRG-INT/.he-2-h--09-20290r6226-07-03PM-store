# OpenVMS Architecture and Legacy
Verzió: 1.0-stable
Forrás: UNICAGD-Core Analízis
Státusz: HASZNÁLHATÓ

## 1. Mi az a OpenVMS?
Az OpenVMS (Open Virtual Memory System) a DEC (Digital Equipment Corporation) által készített operációs rendszer, később a VSI (VMS Software Inc.) fejlesztette. 1977 óta elérhető, és ma is aktívan használatos kritikus rendszerekben.

## 2. Történelem
### 2.1 VMS (1977)
- DEC VAX processzorokon futott
- 32 bites rendszer
- Virtual memory, cluastering

### 2.2 OpenVMS (1992)
- DEC Alpha processzorokra portolták
- 64 bites rendszer
- OpenVMS névre keresztelték

### 2.3 Itanium és x86_64
- HP Itanium támogatás
- VSI x86_64 port

## 3. OpenVMS Architektúra

### 3.1 Kernel
- Monolitikus kernel
- 64 bites virtuális memória
- Symmetric Multi-Processing (SMP)
- Real-time támogatás

### 3.2 Fájlrendszer
- ODS-2 (On-Disk Structure 2)
- ODS-5 ( támogatja a hosszú fájlnevet )
- Journaling
- RAID támogatás

### 3.3 Hálózat
- DECnet
- TCP/IP
- Sockets API
- Clustering (VMScluster)

### 3.4 Adatbázis
- RDB (Relational Database)
- RMS (Record Management Services)
- DBMS

## 4. OpenVMS és a mai világ

### 4.1 Kritikus rendszerek
- Bankszektor
- Repülőgép-irányítás
- Gyártósor-vezérlés
- Orvosi berendezések

### 4.2 VSI (VMS Software Inc.)
- Jelenlegi OpenVMS fejlesztő
- x86_64 támogatás
- Aktív fejlesztés

### 4.3 Hobbyist Program
- Egyéni használatra ingyenes licenc
- VirtualBox és VMware támogatás

## 5. OpenVMS és a Windows kernel kapcsolata
- Nincs közvetlen kapcsolat
- A Windows NT a VMS-ről vett inspiráción
- Dave Cutler, a VMS architektája, a Windows NT vezető fejlesztője volt

## 6. OpenVMS és a Linux kernel kapcsolata
- Nincs közvetlen kapcsolat
- Mindkettő 64 bites rendszer
- Mindkettő SMP támogatás
- Mindkettő virtualizációs képességek

## 7. OpenVMS és a Plan 9 kapcsolata
- Nincs közvetlen kapcsolat
- A Plan 9 a Unix öröse
- Az OpenVMS a VAX öröse
- Mindkettő "minden eszköz fájlrendszer" elvet követi

## 8. OpenVMS driver fejlesztés
### 8.1 Driver model
- SYS$APORT, SYS$DAGoport
- Device driver API
- Kernel szintű driver-ek

### 8.2 Driver írás
- C és Assembly nyelven
- OpenVMS DDK (Device Driver Kit)
- Blisz, SYS$APORT használata

## 9. OpenVMS és a biztonság
### 9.1 Hozzáférési szabályok
- ACL (Access Control List)
- Privileges
- Auditing

### 9.2 Veszélyeztetettség
- A kritikus rendszerek miatt nagyon biztonságos
- C2 biztonsági osztály
- Common Criteria EAL5+

## 10. OpenVMS és a virtualizáció
### 10.1 VirtualBox és VMware
- OpenVMS futhat virtuális gépen
- Jó fejlesztési és tesztelési környezet

### 10.2 KVM
- KVM támogatás
- QEMU használata

## 11. OpenVMS tanulságai
- A hosszú életciklus (1977-től napjainkig)
- A kritikus rendszerekben való használat
- A clustering technológia
- A virtual memory kezelés

## 12. Összefoglalás
Az OpenVMS egy nagyon jó, stabil, biztonságos operációs rendszer. A kritikus rendszerekben való használata bizonyítja a megbízhatóságot. A VSI jelenlegi fejlesztése biztosítja, hogy az OpenVMS ma is használható maradjon.

---

*Dokumentum státusz: STABIL. Nincs félreértés. Nincs feltételezés bizonyítás nélkül.*
