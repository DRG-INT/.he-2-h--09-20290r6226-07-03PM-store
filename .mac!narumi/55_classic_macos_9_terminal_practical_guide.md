# Classic Mac OS 9.2.2 Terminál – Gyakorlati Útmutató és Munkalapok
Verzió: 1.0-stable
Forrás: UNICAGD-Core Analízis
Státusz: HASZNÁLHATÓ (Terepi Útmutató)

---

## 1. Hogyan Legyen Terminálod egy Mac OS 9.2.2 Rendszeren?

Ha fizikai PowerPC Macen (G3, G4, PowerBook) vagy emulátorban (SheepShaver, QEMU-PPC) dolgozol, három bevált módszer létezik a terminál azonnali aktiválására:

### Módszer A: Az Apple MPW Shell Telepítése (A Teljes Parancssor)
1. Töltsd le az Apple ingyenessé tett **MPW-GM (Macintosh Programmer's Workshop Gold Master)** csomagját.
2. Másold az `MPW` mappát a merevlemez gyökerébe (`Macintosh HD:MPW:`).
3. Indítsd el az `MPW Shell` alkalmazást.
4. Megnyílik a **Worksheet (Munkalap)** ablak:
   - Írj be egy parancsot, például: `Directory` vagy `Files -l`
   - Jelöld ki a sort, majd nyomd le a **`NumPad Enter`** vagy **`Cmd + Return`** gombot!
   - A parancs lefut, és a kimenet közvetlenül a kurzor alá íródik!

### Módszer B: Autonóm Háttérfuttatás (ToolServer & AppleScript)
Ha nem akarsz ablakokkal bíbelődni, és azt szeretnéd, hogy "magától működjön":
Készíts egy egyszerű AppleScriptet (`System Folder:Startup Items:` mappába téve):
```applescript
tell application "ToolServer"
    DoScript "Backup_Script"
end tell
```
A ToolServer csendben, a háttérben elvégzi az összes fájlmozgatást és feladatot.

### Módszer C: C/C++ Konzolprogram (SIOUX Használata)
Ha CodeWarriorban fordítasz C kódot:
1. Állítsd be a projekt célját: **MacOS PPC C Console**.
2. A projekt automatikusan hozzácsatolja a `SIOUX.PPC.Lib` állományt.
3. Bármikor, amikor a kódod `printf()` vagy `getchar()` hívást végez, egy elegáns, monospaced szöveges terminálablak jelenik meg a képernyőn!

---
*Dokumentum státusz: STABIL · UNICAGD-Core Terepi Kézikönyv*
