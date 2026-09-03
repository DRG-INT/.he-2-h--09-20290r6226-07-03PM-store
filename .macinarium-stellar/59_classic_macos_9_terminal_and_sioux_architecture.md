# Classic Mac OS 9.2.2 Terminál Architektúra & SIOUX Konzol Belsők
Verzió: 1.0-stable
Forrás: UNICAGD-Core / DRG-INT Történeti & Ipari Rendszertan
Státusz: HASZNÁLHATÓ (Macintosh Toolbox & Terminál Emuláció)

---

## 1. A Klasszikus Macintosh Paradoxon: Hol a Terminál?

A modern mérnök számára megdöbbentő tény: **a klasszikus Mac OS-nek (System 1.0-tól egészen a Mac OS 9.2.2-ig) gyárilag SOHA NEM VOLT parancssori terminálja!**

Steve Jobs és az eredeti 1984-es Macintosh csapat (Andy Hertzfeld, Bill Atkinson, Jef Raskin) filozófiája az volt, hogy a parancssor a múlté, és a Finder asztala az egyetlen shell. Nincs `/bin/sh`, nincs DOS `COMMAND.COM`, és nincs Windows `cmd.exe`.

### Hogyan oldották meg a mérnökök a terminált Mac OS 9-en régen?
A rendszermérnökök négy fő technológiával hoztak létre terminált és TUI-t:

```
+─────────────────────────────────────────────────────────────────────────────+
|               TERMINÁL MEGOLDÁSOK CLASSIC MAC OS 9.2.2 ALATT                |
+─────────────────────────────────────────────────────────────────────────────+
|                                                                             |
|   [ 1. MPW SHELL (Macintosh Programmer's Workshop) ]                        |
|   • Az Apple hivatalos Unix-szerű parancssora (csővezetékek, szkriptek)     |
|   • Munkalap (Worksheet) felület: bárhová kattintasz és Entert ütsz, lefut  |
|                                                                             |
|   [ 2. METROWERKS SIOUX (Simple Input Output User eXchange) ]               |
|   • A CodeWarrior zseniális C konzol-könyvtára                              |
|   • Ha a C kód meghívja a printf()-et, a SIOUX automatikusan terminál-      |
|     ablakot nyit QuickDraw és TextEdit alapon!                              |
|                                                                             |
|   [ 3. TOOLSERVER (Fej nélküli / Autonóm Végrehajtó) ]                      |
|   • Háttérben futó démon ablakok nélkül                                     |
|   • AppleEvents csomagokon keresztül fogad parancsokat és önállóan dolgozik |
|                                                                             |
|   [ 4. MACSSH & NIFTYTELNET ]                                               |
|   • Open Transport TCP/IP alapú VT100 terminál emulátor külső Unix felé     |
|                                                                             |
+─────────────────────────────────────────────────────────────────────────────+
```

---

## 2. A SIOUX (Simple Input Output User eXchange) Működési Mechanizmusa

A Metrowerks CodeWarrior azért hódította meg a Macintosh fejlesztői piacot a '90-es években, mert a szabványos ANSI C programok nem fordultak le Macen a terminál hiánya miatt.

### A SIOUX Megoldása:
Amikor a fordító elérte a `main()` függvényt, a háttérben linkelt **SIOUX runtime**:
1. Inicializálta a Macintosh Toolboxot: `InitGraf`, `InitFonts`, `InitWindows`, `InitMenus`, `TEInit`.
2. Létrehozott egy lebegő dokumentumablakot (`NewWindow`).
3. Példányosított egy **TextEdit Recordot (`TEHandle`)** a monospaced **Monaco 9 pt** betűtípussal.
4. Átirányította az `stdout`, `stdin` és `stderr` fájlleírókat a TextEdit memóriapufferébe.
5. Az eseményhurkot (`WaitNextEvent`) folyamatosan futtatta, biztosítva a görgetést, kijelölést és másolást.

---

## 3. Az Autonóm Végrehajtás: AppleEvents és ToolServer

Ha azt akarjuk, hogy a terminál "magától működjön", ne kérdezzen vissza, és autonóm módon hajtsa végre a műveleteket:
- A Classic Mac OS az **Inter-Process Communication (IPC)** réteget az **AppleEvents** objektumorientált üzenetkezelőn keresztül valósította meg.
- A **ToolServer** nevű Apple eszköz képes volt arra, hogy a háttérben fusson:
  - Figyelt egy beérkező eseménysorozatra.
  - Végrehajtotta a fordítást vagy adatfeldolgozást.
  - A kimenetet visszaküldte vagy fájlba írta.
  - Mindezt felhasználói beavatkozás nélkül!

---
*Dokumentum státusz: STABIL · UNICAGD-Core Történeti & Ipari Rendszertan*
