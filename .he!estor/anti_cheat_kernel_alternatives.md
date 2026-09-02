# Anti-Cheat Rendszerek Korlátai és Alternatívák
Verzió: 1.0-stable
Forrás: UNICAGD-Core Analízis
Státusz: HASZNÁLHATÓ

## 1. Miért nem elég a behatolási pontokat ismerni?

Ha egy anti-cheat rendszer minden behatolási pontját (entry point) ismered, akkor azt hiheted, hogy a rendszer teljesen biztos. A valóságban azonban a biztonság nem csak a behatolási pontoktól függ:

### 1.1 A Bizalmi Alap (TCB) Probléma
A rendszernek olyan részei vannak, amiket nem tudsz ellenőrizni:
- **CPU mikrokód** (processzor saját firmware-ja)
- **BIOS/UEFI** firmware (pl. Intel ME, AMD PSP)
- **DMA-képes eszközök** (videókártya, hálókártya)
- **Memóriakezelő** (rowhammer, SPD hibák)
- **Hő- és energiakezelés** (throttling, DVFS)

Ezek a részek bypassolhatják a kernel szintű védelmet anélkül, hogy a kernelbe beavatkoznának.

### 1.2 Aszimmetrikus háború
- **Védő oldalon:** 100% a támadási felületet védened kell
- **Támadó oldalon:** 1 hiba + 1 bypass elegendő
- A kernel forráskódja nyilvános – a támadó olvassa, te pedig patch-elni kell mielőtt a támadó alkalmazza

### 1.3 Szándék felismerése
A kernel látja, hogy egy program futtatja a `mmap(addr, PROT_EXEC)` rendszerhívást, de nem tudja megkülönböztetni, hogy az játék kódja-e, vagy cheater kódja.

**Megoldási lehetőségek (nem tökéletesek):**
- Hardveres memóriacímkézés (ARM MTE, Intel SDL)
- Hipervizor alapú megfigyelés (KVM, Xen)
- Időalapú tanúsítás (Intel TDX, AMD SEV-SNP)
- Oldalcsatorna-ellenállás (cache flush, constant-time)

## 2. Alternatív Stabilitási Modellek a Kernel Panic Elkerülésére

### 2.1 seL4 (Formálisan Ellenőrzött Mikrokernel)
- **Főbb jellemző:**
  - Matematikai bizonyítással igazolható, hogy nem adhat ki kernel panikot
  - CAmkES komponensizoláció
  - Csak 10-20 syscall van, nincs dinamikus betöltés
- **Használat:** Katonai, légi, orvosi rendszerek, ahol a hiba nem elfogadható
- **Korlát:** Nagyon lassú a fejlesztés, 1 fejlesztő-év ≈ 1 ellenőrzött kódsor

### 2.2 Minix 3 (Ön-helyreállító Mikrokernel)
- **Főbb jellemző:**
  - Minden eszközmeghajtó felhasználói szinten fut
  - Ha egy meghajtó összeomlik, automatikusan újraindul, a rendszer nem áll le
  - Nincs kernel panic a driver hibák miatt
- **Használat:** Beágyazott rendszerek, oktatás
- **Korlát:** Magasabb IPC overhead, bonyolultabb driver modell

### 2.3 Unikernel (Egycélú Rendszer)
- **Főbb jellemző:**
  - Nincs felhasználói/kernel szétválasztás
  - Egyetlen folyamat, egyetlen címterület
  - Kernel panic helyett VM snapshot + rollback
- **Használat:** Felhő alkalmazások, funkcióként szolgáltatás (FaaS)
- **Korlát:** Nincs shell, nincs dinamikus betöltés, egy alkalmazás per VM

### 2.4 Exokernel (Alkalmazás-specifikus Erőforrás-kezelés)
- **Főbb jellemző:**
  - A kernel csak a hardvert kezeli, az alkalmazások maguk kezelik a lapozási táblákat, TLB-t
  - Alkalmazás hiba = alkalmazás összeomlik, a kernel életben marad
- **Használat:** Kísérleti rendszerek, nagy teljesítményű alkalmazások
- **Korlát:** Minden alkalmazásnak saját Library OS-ére van szüksége

## 3. Host Fájl + Binary Store + Driver Modell (Alternatív Architektúra)

Ez a modell a kernel panik teljes kizárására törekszik:

```
┌─────────────────────────────────────────────────────────────┐
│  Felhasználói tér: Statikus bináris alkalmazás              │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │ Binary Store │    │  Host Fájl  │    │  Binary DB  │     │
│  │ (LMDB/SQLite)│    │ (/etc/hosts)│    │ (driver map)│     │
│  └──────┬──────┘    └──────┬──────┘    └──────┬──────┘     │
│         │                  │                  │             │
│  ┌──────▼──────────────────▼──────────────────▼──────┐     │
│  │      Felhasználói szintű driver (VFIO/io_uring)    │     │
│  └──────────────────────────┬────────────────────────┘     │
│                             │ Képesség (FD) átadása          │
├─────────────────────────────┼───────────────────────────────┤
│  Minimális kernel:           │                               │
│  ┌──────────────────────────▼────────┐                      │
│  │  Csak: megszakítás útválasztás,    │                      │
│  │  alap ütemező, memóriavédelem     │                      │
│  └───────────────────────────────────┘                      │
└─────────────────────────────────────────────────────────────┘
```

### 3.1 Támadási felület csökkentése
- Nincs rendszerhívás tábla (csak 3-5 syscall)
- Nincs hálózati verem (felhasználói szinten kezeli az io_uring)
- Nincs fájlrendszer VFS (a binary store a fájlrendszer)
- Nincs dinamikus modul betöltés
- Nincs BPF JIT (vagy BPF egyáltalán)
- Nincs kernel oldali szkript (nincs eBPF, nincs IOMMU bypass)

### 3.2 Fenyegetési modell
- Ha a felhasználói driver sérül: a támadó raw hardver hozzáférést kap, de a kernel izolálva van az MMU által
- Ha a binary store sérül: integritás ellenőrzés Merkle fa-val boot időben
- Ha a host fájl megmocsarkodik: nincs DNS feloldás, az alkalmazás bezár (nincs fallback)

## 4. Kernel Stabilitás Mérnöki Szabályok (Gyakorlati Alkalmazás)

1. **Minimalizáld a panic() hívásokat** – csak a helyreállíthatatlan invariáns megsértésekor
2. **Használj WARN_ON_ONCE()** – a visszanyerhető hibák naplózására
3. **A lockdep-nek át kell mennie** – minden spinlock, mutex, rwlock ellenőrizve
4. **Strukturált hibakezelés (unwinding)** – használj szabványos kernel `goto err_*` unwinding-et vagy `__cleanup` RAII helpert
5. **Memóriafoglalásoknak legyen fallback-ük** – GFP_ATOMIC vagy elegáns leállás
6. **Nincs blokkolás megszakítási kontextusban** – IRQ kezelőknek gyorsoknak kell lenniük
7. **RCU grace periods korlátok** – nincs végtelen call_rcu() lánc
8. **Nincs korlátlan ciklus az ütemezőben** – preemption ellenőrzés kötelező

## 5. Összefoglalás

A kernel panic nem elkerülhetetlen, de a klasszikus monolitikus kernel modellben valószínű. A stabilitás növelése érdekében:
- Használj mikrokernelt, ha a hardver hibái nem okozhatnak teljes rendszerösszeomlást
- Használj unikernelt, ha egyetlen alkalmazást futtatsz, és a teljes rendszer újraindítható
- Használj felhasználói szintű drivert, ha a kernel támadási felületét minimalizálni szeretnéd
- Ne felejtsd el, hogy a hardver és a firmware is része a bizalmi alapnak

---

*Dokumentum státusz: STABIL. Nincs félreértés. Nincs feltételezés bizonyítás nélkül.*
