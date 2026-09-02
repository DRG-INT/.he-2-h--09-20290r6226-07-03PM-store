# Classic Mac OS 9.2.2 – Gyakorlati Rendszerkezelés és Terepi Ismertetők
Verzió: 1.0-stable (Final Classic Release)
Forrás: UNICAGD-Core Analízis / DRG-INT Védelmi Rendszertan
Státusz: HASZNÁLHATÓ (Történelmi és Ipari Helyreállítási Kézikönyv)

## 1. Történelmi Háttér és Ipari Jelentőség

A **Mac OS 9.2.2** (kódnevén "Moonlight", 2001 decembere) az Apple klasszikus Macintosh operációs rendszerének legutolsó, legstabilabb hivatalos kiadása a Mac OS X (Darwin/XNU) előtti korszakból. Számos régebbi ipari berendezés (nyomdai RIP vezérlők, stúdió DAW hangkártyák, katonai jelfeldolgozó rendszerek) mind a mai napig Mac OS 9.2.2 alatt fut PowerPC (G3, G4) hardvereken vagy az OS X "Classic" környezetében.

Fő mérnöki sajátosságai:
- **Kooperatív multitaszking:** Nincs preemptív időszeletelés a felhasználói térben; az alkalmazások a `WaitNextEvent()` hívással adják át önként a vezérlést.
- **Nincs hardveres memóriavédelem:** Minden alkalmazás és a rendszer egyetlen közös, lapos címtérben osztozik. Egyetlen program hibája azonnal az egész rendszer leállását ("Bomb" doboz) idézi elő.
- **System Folder struktúra:** Nincs registry, nincs csomagkezelő; a rendszer konfigurációja fájlok és kiterjesztések közvetlen mozgatásával történik.

---

## 2. A Rendszermappa (System Folder) Anatómiája

A rendszer működésének szíve az "áldott" (blessed) **System Folder**:
- **System:** A monolitikus rendszermag, fontok és alapvető erőforrások (Mac OS ROM kiegészítések).
- **Finder:** A grafikus shell és asztalkezelő.
- **Extensions (Kiterjesztések):** INIT kódok, eszközmeghajtók (SCSI, USB, FireWire, PCI kártyák), amelyek a boot során közvetlenül betöltődnek a memóriába és patchelik a rendszer ugrótábláit.
- **Control Panels (Vezérlőpultok):** Beállító appletek (TCP/IP, Memory, Sound, AppleTalk).
- **Preferences:** Alkalmazások bináris konfigurációs állományai.

---

## 3. Hibaelhárítás és Kiterjesztés-Konfliktusok

A fagyások és rendszerösszeomlások 90%-át az egymással ütköző INIT kiterjesztések okozzák, mivel mindegyik az operációs rendszer A-Trap ugrási vektorait módosítja.

### 3.1 Tiszta Boot (Safe Boot)
- **Bekapcsoláskor a `Shift` gomb nyomva tartása:**
  - Letiltja az összes harmadik féltől származó kiterjesztést és vezérlőpultot ("Extensions Disabled" felirat jelenik meg).
  - Lehetővé teszi a hibás driver törlését vagy mozgatását.

### 3.2 Extensions Manager Használata
- A boot során tartsuk nyomva a `Szóköz (Space)` billentyűt az **Extensions Manager** előhívásához.
- Válasszuk a "Mac OS 9.2.2 Base" készletet: ez kizárólag a hivatalos Apple kiterjesztéseket tölti be, azonnal azonosítva a külső modulhibákat.

---

## 4. Memóriakezelés Terepi Konfigurációja

Mivel nincs virtuális memóriavédelem, minden alkalmazás számára előre meg kell adni egy fix memóriapartíciót:

### 4.1 "Get Info" Memóriapuffer Beállítása
1. Jelöljük ki az alkalmazás ikonját, majd nyomjuk meg a `Cmd + I` (Get Info) billentyűkombinációt.
2. Válasszuk a legördülő menüből a **Memory** panelt:
   - **Minimum Size:** Az a legkisebb RAM méret, amivel a program még hajlandó elindulni.
   - **Preferred Size:** Az ideális RAM méret. Ha a rendszerben van elég összefüggő szabad memória, ennyit kap.
3. **Mérnöki Szabály:** Kritikus adatfeldolgozó szoftvereknél a Preferred Size értékét a gyári duplájára kell emelni, különben a program out-of-memory hibával azonnal kilép és magával rántja az operációs rendszert.

### 4.2 Memory Control Panel Beállításai
- **Virtual Memory:** Flash vagy merevlemez alapú lapozófájl. Nagy sebességű ipari és valós idejű audio feladatoknál **KIKAPCSOLANDÓ**, mert a merevlemezes lapozás nem-determinisztikus hangpattogást és SCSI időtúllépést okoz.

---

## 5. Hálózat és Tárhelykezelés

### 5.1 Open Transport (TCP/IP és AppleTalk)
- **TCP/IP Control Panel:** Kézi IP, alhálózati maszk és router beállítása.
- **AppleTalk:** Helyi hálózati fájlmegosztás és hálózati nyomtatók elérése a **Chooser** (Kiválasztó) segédprogramon keresztül.

### 5.2 Lemez- és Fájlrendszer Karbantartás
- **Drive Setup:** SCSI és IDE/ATA merevlemezek inicializálása, Apple Partition Map (APM) létrehozása és HFS+ (Mac OS Extended) formázás.
- **Disk First Aid:** B-Tree katalógusfájl és Extents Overflow fájl javítása fizikai leállási hibák után.

---

## 6. Összeomlás Forenzika: A "Bomb" Doboz és a MacsBug

Ha a rendszer összeomlik, a klasszikus bomba ikon jelenik meg egy hibakóddal:

| Hibakód | Jelentés | Okozó |
| :--- | :--- | :--- |
| **Type 1** | Bus Error | Nem létező hardvercímre vagy buszra történő olvasási/írási kísérlet |
| **Type 2** | Address Error | Páratlan memóriacímről történő 16/32-bites szó olvasása (68000 CPU hiba) |
| **Type 3** | Illegal Instruction | Érvénytelen gépi kód végrehajtása (általában sérült kódmemória vagy túlfutás) |
| **Type 10** | Line 1010 Trap | Nem létező A-Trap rendszerhívás meghívása |
| **Type 11** | Hardware Exception | PowerPC natív processzor-kivétel (DSI, ISI, Alignment) |

### 6.1 MacsBug: Alacsony Szintű Rendszerdebugger
A System Folderbe helyezett `MacsBug` kiterjesztés összeomláskor nem bombát dob, hanem közvetlen assembly monitort nyit:
```text
(MacsBug) sc                # Stack crawl (függvényhívási lánc ellenőrzése)
(MacsBug) std               # Stack and Registers (regiszterek és verm állapot)
(MacsBug) heap              # Heap zóna integritás ellenőrzése
(MacsBug) es                # Exit to Shell (megpróbálja bezárni a lefagyott programot a Finderbe mentve a rendszert)
(MacsBug) rb                # Reboot azonnali újraindítás
```

---
*Dokumentum státusz: STABIL · UNICAGD-Core Történeti & Ipari Kézikönyv*
