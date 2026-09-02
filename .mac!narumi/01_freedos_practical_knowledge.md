# FreeDOS – Gyakorlati Tudás és Ismertetők
Verzió: 1.0-stable
Forrás: UNICAGD-Core Analízis
Státusz: TUDNIVALÓ

## 1. Miért érdemes ma is a FreeDOS?
A FreeDOS nem csak játékok futtatására jó. Sok régi szoftver (pl. örökölt gyártósor-vezérlő, régión belüli adatbázis, speciális CAD) ma sem frissült át Windows 10-re. A FreeDOS ezeket életben tartja anélkül, hogy érvényesített DOS-licencre lenne szükség.

## 2. Hogyan indulj bele?
- Tölts le egy FreeDOS Live CD ISO-t.
- Írd egy pendrive-ra (Unetbootin, Rufus).
- Bootolj belőle.
- A parancssor hasonlít a régi DOShoz: `DIR`, `COPY`, `EDIT`, `FDISK`.
- A `CONFIG.SYS` és az `AUTOEXEC.BAT` határozza meg a bootolási viselkedést.

## 3. Ha driver kell
- A FreeDOS CD több drivert is tartalmaz.
- A `FDAPM` segítségével energiahatékonyságot is kezelhetsz laptopon.
- Az `FDNET` és `FDUSB` csomagok hálózati és USB támogatást adnak.
- Grafikus mód: `DISPLAY` és `GEM` rendszer elérhető.

## 4. Hálózat
- A FreeDOS nem csak önállóan használható.
- Van `mTCP` csomag, amivel TCP/IP kapcsolatot is létesíthetsz.
- Lehetőség van teljes DOS-alapú routerre, SQL-kliensekre, sőt webszerverre.

## 5. Fejlesztés
- A `DJGPP` egy GCC alapú fejlesztői környezet 32 bites DOS alkalmazásokhoz.
- Régi assembler, C, Pascal kódok újrafordíthatók és futtathatók.
- A `DEBUG.EXE` és a `TD` (Turbo Debugger) továbbra is elérhetőek hibakereséshez.

## 6. Gyakorlati tip
- Sose írd felül a rendszerpartíciót, amíg nem vagy benne biztos.
- Készíts `BOOT` floppykés másolatot.
- Használj `HIMEM.SYS` és `EMM386.EXE`-t a memóriakezeléshez.
- Ha `UMB`-re van szükséged, a `HMAMON` hasznos.

## 7. Összefoglalás
A FreeDOS nem játék. Éles környezetben is használható, ahol csak DOS API elérés kell. Stabilitás, egyszerűség, és teljes kontroll – nincs rejtett kernel, nincs háttérben futó service.

---

*Dokumentum státusz: STABIL. Nincs félreértés. Nincs feltételezés bizonyítás nélkül.*
