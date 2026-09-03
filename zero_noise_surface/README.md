# 🔇 Zero-Noise Application Surfaces
### Zéró-Telemetria, Zárt Helyi IPC és Független ANSI TUI
### UNICAGD-Core / DRG-INT Critical Infrastructure Framework

---

## 1. A Rendszer Célja és Működése

A **Zero-Noise Application Surface** egy olyan felhasználói felület és vezérlőréteg, amely:
1. **Kiiktat minden háttérzajt:** Nincsenek futó telemetriai háttérdémonok, nincs böngészőmotor, nincs automatikus csomagfrissítés.
2. **Kizárólag helyi IPC-t használ:** A folyamatok `AF_UNIX` fájlrendszer-socketeken kommunikálnak, sosem nyitnak TCP portot a külvilág felé.
3. **Közvetlen TUI és DRM/KMS keretpuffer:** Tiszta ANSI/VT100 szekvenciákkal jeleníti meg a műszerfalat bármilyen terminálon, villogásmentesen.

---

## 2. Fordítás és Tesztelés

```bash
make -C zero_noise_surface test
```

---
*Status: VERIFIED & SILENT · UNICAGD-Core*
