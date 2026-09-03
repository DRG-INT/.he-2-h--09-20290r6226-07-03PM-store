# 🧩 UNICAGD Zero-Surface Exokernel & Puzzle Solver Engine
### Megfejtve: A Rendszermag Paradoxon, Zéró Pánik és Immutábilis Bináris Tár
### UNICAGD-Core / DRG-INT Critical Infrastructure Framework

---

## 1. A Megfejtett Rejtvény

Ez a rendszer választ ad a rendszermérnöki alapkérdésekre:
1. **Zéró Pánik Garancia:** A kernel nem tartalmaz eszközmeghajtókat és hálózati vermelet. A rendszerhívások száma pontosan 3 (`Yield`, `MapPage`, `RouteIRQ`). Ha egy felhasználói driver hibázik, nem történik Kernel Panic / Kékhalál, csupán a felhasználói folyamat indul újra tiszta állapotból.
2. **Immutábilis Bináris Tár (Binary Store DB):** A sérülékeny kernel VFS helyett egy Merkle-fával védett, append-only kulcs-érték tároló kezeli a programokat, host fájlokat és driver leképezéseket.
3. **Deklaratív Mintanyelv (Pattern Language):** Minden bináris adatstruktúra ellenőrzése deklaratívan történik a végrehajtás előtt.
4. **TCB Integritás és Anti-Cheat:** A megfigyelői paradoxon feloldása out-of-band Merkle ellenőrzéssel és hardveres root-of-trusttal.

---

## 2. Bővített Funkciók (v2.0)

### Exokernel Core
- **Dinamikus folyamatkezelés:** Több izolált folyamat létrehozása és kezelése
- **Képesség reference counting:** Biztonságos erőforrás-közpénuszámbavétel
- **Képesség revokáció:** Futás közbeni jogosultság visszavonás
- **Rendszerhívás statisztikák:** Részletes számláló minden syscall-re
- **Fault recovery tracking:** Összeomlások számlálása és helyreállítás

### Binary Store
- **Dinamikus tábla növelés:** Nincs fix 256 bejegyzés korlát
- **O(1) kulcs keresés:** Hash table-alapú keresés
- **LRU eviction:** Intelligens kitörlés kevésbé használt bejegyzésekből
- **Pin/Unpin:** Kritikus bejegyzések védeleme kitörlés ellen
- **Referencia számlálás:** Biztonságos megosztott blob-ok
- **Javított Merkle root:** Integritás ellenőrzés összes bejegyzésen
- **Statisztikák:** Részletes használati adatok

### Pattern Language
- **Tartomány ellenőrzés:** Numerikus range validáció
- **Bit mezők:** Egyenletes szintű bit szűrés
- **Endianness támogatás:** Little/Big/Native byte order
- **Változó hosszúságú mezők:** Flexible field definitions
- **Kötegelt ellenőrzés:** Több minta egyszerre
- **Minta leírás:** Automatikus dokumentáció generálás

---

## 3. Fordítás és Futtatás

```bash
# Fordítás
make -C UNICAGD_EXOKERNEL

# Futatás
make -C UNICAGD_EXOKERNEL test

# Debug mód
make -C UNICAGD_EXOKERNEL debug

# Takarítás
make -C UNICAGD_EXOKERNEL clean
```

---

## 4. Adatmodell Architektúra

```
┌─────────────────────────────────────────────────────────────┐
│                    EXOKERNEL STATE                           │
├─────────────────────────────────────────────────────────────┤
│  - Magic: 0x554E494341474401                                 │
│  - Process Table: Dynamic array of exo_process_t            │
│  - Capability Fast-Path: Static 64-entry array              │
│  - Syscall Counters: YIELD / MAP_PAGE / ROUTE_IRQ          │
│  - Fault/Recovery Tracking                                  │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│   PROCESS     │   │  CAPABILITY   │   │   BINARY      │
│   TABLE       │   │   TOKEN       │   │   STORE       │
├───────────────┤   ├───────────────┤   ├───────────────┤
│ - PID         │   │ - cap_id      │   │ - SHA-256     │
│ - Parent PID  │   │ - permissions │   │ - CRC32       │
│ - CPU time    │   │ - phys_addr   │   │ - Merkle root │
│ - Cap array   │   │ - ref_count   │   │ - LRU stats   │
│ - alive flag  │   │ - owner_pid   │   │ - Hash table  │
└───────────────┘   │ - revoked     │   │ - Eviction    │
                     └───────────────┘   └───────────────┘
                            │                   │
                            ▼                   ▼
                   ┌───────────────────────────────────┐
                   │      PATTERN LANGUAGE             │
                   ├───────────────────────────────────┤
                   │ - Magic numbers                   │
                   │ - Range validation                │
                   │ - Bit fields                      │
                   │ - Endianness handling              │
                   │ - Batch verification               │
                   └───────────────────────────────────┘
```

---

## 5. Adatmodell Javítások (Data Model Enhancements)

### 5.1 Exokernel State
- **Process Control Block (PCB):** Minden folyamat saját capability array-vel
- **Reference Counting:** Képességek biztonságos felszabadítása
- **Revocation:** Futás közbeni jogosultság visszavonás
- **Syscall Accounting:** Részletes teljesítmény számlálás

### 5.2 Capability Token
- **Reference Count:** Több folyamat megosztása esetén
- **Owner Tracking:** Ki tulajdonosa a képességnek
- **Timestamp:** Létrehozás időpontja
- **Revoke Flag:** Visszavonás állapot

### 5.3 Binary Store
- **Dynamic Growth:** Nincs fix korlát
- **Hash Table:** O(1) kulcs keresés
- **LRU Eviction:** Intelligens memóriakezelés
- **Pin/Unpin:** Kritikus adatok védelme
- **Compression Flags:** Tömörítési lehetőség
- **Access Tracking:** Hozzáférési statisztikák

### 5.4 Pattern Language
- **Range Validation:** Numerikus intervallumok ellenőrzése
- **Bit Fields:** Egyenletes szintű bit szűrés
- **Endianness:** Little/Big/Native byte order támogatás
- **Batch Verification:** Több minta egyszeres hívásban
- **Auto-description:** Minta dokumentáció generálás

---

## 6. Teljesítmény Jellemzők

| Jellemző | Előny |
|----------|-------|
| Syscall Count | Pontosan 3 (minimális TCB) |
| Kernel Panic Vektorok | 0 (lehetetlen állapot) |
| Capability Lookup | O(1) hash table |
| Binary Store Lookup | O(1) hash table |
| Memory Safety | Reference counting + bounds checking |
| Fault Isolation | Per-process recovery |
| Integrity Verification | SHA-256 + Merkle root |

---

## 7. Integráció a Kernel-LSTM Pipeline-vel

Az UNICAGD Exokernel adatmodellje integrálható a Kernel-LSTM rendszerrel:

```
UNICAGD Exokernel
├── Capability Tokens → Kernel Event Streamer
├── Binary Store → ClickHouse Data Lake
├── Pattern Language → Event Schema Validation
└── Zero-Panic Invariant → Anomaly Detection Baseline
```

---

## 8. Licensz

MIT

---

*Status: VERIFIED & SOLVED · UNICAGD-Core / DRG-INT · v2.0 ENHANCED*
