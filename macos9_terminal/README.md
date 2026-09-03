# 🖥️ Classic Mac OS 9.2.2 SIOUX Terminal & Autonomous Engine
### "Magától működik, mint a Macintoshok régen" — SIOUX Konzol & ToolServer Autonómia
### UNICAGD-Core / DRG-INT Történeti & Ipari Rendszertan

---

## 1. A Rendszer Lényege

A klasszikus Mac OS-nek (System 1.0 -> Mac OS 9.2.2) nem volt beépített terminálja. A fejlesztők a **Metrowerks SIOUX (Simple Input Output User eXchange)** könyvtárával hoztak létre automatikus terminálablakokat a C nyelvű `printf()` hívásokhoz, míg az Apple **ToolServer** és **AppleEvents** rendszere tette lehetővé az autonóm, felhasználói beavatkozás nélküli feladatvégrehajtást.

Ez a modul reprodukálja ezt a viselkedést:
- Monospaced **Monaco 9 pt** képernyőpuffer.
- Kooperatív `WaitNextEvent` eseményhurok.
- Autonóm feladatfuttató állapotgép, ami önállóan elvégzi a diagnosztikát és a feladatokat.

---

## 2. Fordítás és Tesztelés

```bash
make -C macos9_terminal test
```

---
*Status: VERIFIED & AUTONOMOUS · UNICAGD-Core*
