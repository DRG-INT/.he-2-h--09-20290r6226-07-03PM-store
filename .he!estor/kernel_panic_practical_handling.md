# Kernel Panic Gyakorlati Kezelés
Verzió: 1.0-stable
Forrás: UNICAGD-Core Analízis
Státusz: HASZNÁLHATÓ

## 1. Mi történik, amikor a kernel összeomlik?

Amikor a kernel panic előfordul:
1. A kernel leállítja az összes processzort
2. Naplózza a hibát a képernyőre és a naplófájlokba
3. Alapértelmezés szerint újraindul a rendszer (ha be van állítva)

## 2. Gyakorlati Lépések a Kernel Panic Kezeléséhez

### 2.1 Azonnali Lépések
1. **Ne nyomj Control+Alt+Delete-t** – várj, ha a rendszer automatikusan újraindul
2. **Jegyzd fel a hibaüzenetet** – írd le, amit a képernyőn látsz
3. **Ellenőrizd a naplókat** – `dmesg` vagy `/var/log/kern.log`

### 2.2 Ha a Rendszer Nem Indul Újra
1. **Indíts egy Live CD/USB-t** – pl. Ubuntu Live
2. **Csatlakoztasd a rendszerlemezt** – mount-old a `/mnt` alá
3. **Ellenőrizd a boot naplókat** – `/mnt/var/log/kern.log`
4. **Javítsd a konfigurációt** – ha hibás beállítás okozta a panikot

### 2.3 Gyakori Okok és Javításuk

| Ok | Javítás |
|----|---------|
| Hibás driver | Bootolj régebbi kernel verzióval, távolítsd el a hibás drivert |
| Memóriahiba | Futtasd memtest86+-t, cseréld le a RAM-ot |
| Lemezhiba | Futtasd fsck-t a rendszerlemez ellenőrzéséhez |
| Hibás konfiguráció | Indíts egy egyszerű boot paraméterekkel |

## 3. Kernel Panic Megelőzés

### 3.1 Rendszeres Frissítések
- Frissítsd a rendszert rendszeresen (`apt update && apt upgrade`)
- Használj stabil kernel verziókat, ne testing/experimental verziókat

### 3.2 Hardver Ellenőrzés
- Futtasd memtest86+-t boot során
- Ellenőrizd a lemez állapotát (`smartctl`)
- Figyeld a hőmérsékletet (`lm-sensors`)

### 3.3 Konfiguráció Biztonság
- Készíts biztonsági másolatot a fontos konfigurációkról
- Használj verziókezelést a konfigurációkhoz (pl. Git)
- Teszteld a kernel frissítéseket virtuális gépen először

## 4. Speciális Technikák

### 4.1 Kernel Crash Dump
- A kernel összeomlásakor automatikusan menti a memóriatartalmat
- Később elemzéshez használható
- Beállítás: `kdump` csomag telepítése

### 4.2 Netconsole
- A kernel naplókat hálózaton keresztül küldi egy másik gépnek
- Hasznos, ha nincs helyi naplózás

### 4.3 Serial Console
- A kernel kimenetet soros portra irányítja
- Távollenőrzéshez hasznos

## 5. Összefoglalás

A kernel panic kezelése során:
1. Maradj nyugodt – a rendszer alapértelmezés szerint újraindul
2. Jegyzd fel a hibaüzenetet
3. Ellenőrizd a naplókat
4. Ne változtass sokat egyszerre – teszteld a javításokat
5. Készíts biztonsági másolatot minden változtatás előtt

---

*Dokumentum státusz: STABIL. Nincs félreértés. Nincs feltételezés bizonyítás nélkül.*
