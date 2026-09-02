# Windows NT Kernel – Gyakorlati Tudás és Ismertetők
Verzió: 1.0-stable
Forrás: UNICAGD-Core Analízis
Státusz: TUDNIVALÓ

## 1. Miért különbözik a Windows kernel a Linux kerneltől?
A Windows NT kernel hibrid mikrokernel/monolitikus architektúrát követ. A HAL réteg leválasztja a hardvertől, de a nagy rész (executive, I/O, memory manager) még mindig kernel módban fut.

## 2. A legfontosabb rétegek
- **HAL:** Hardver absztrakció, nem kell tudnod a lapozási egységeket vagy I/O portokat, ha driver írsz.
- **Executive:** Object Manager, Process Manager, Memory Manager, I/O Manager – ez a "magasabb" szint, de még mindig kernelben van.
- **Win32 API:** A felhasználói térbe nyújtott interfész, nem része a kernelen, de rajta keresztül éri el az alkalmazásokat.

## 3. Ha te is beleakartál volna nézni korábban
A Microsoft Research egy ideig elérhetővé tette a Windows Research Kernel (WRK) forráskódját. Bár már nem aktív, a ReactOS projekt hasonló forráskódú, és nyílt forráskódú. Az is a NT kernel architektúrája.

## 4. Driver fejlesztés Windows alatt
- **KMDF (Kernel-Mode Driver Framework):** Az új, ajánlott driver keretrendszer.
- **UMDF (User-Mode Driver Framework):** A driver a felhasználói térben fut, a kernel károsodása esetén a rendszer nem omlik össze.
- **WDM (Windows Driver Model):** Régebbi, de még használt.
- Az eszközmeghajtók nem a `/dev` alatt jelennek meg, hanem a `\Device\` vagy `\DosDevices\` névterében.

## 5. Hibakeresés és monitorozás
- **WinDbg:** Ez a Windows kernel debugolásának eszköze. Először a `kdump` és a `windbg` kombinációjával kell ismerkedni.
- **Windows Performance Toolkit:** Teljesítmény elemzéshez.
- **Event Tracing for Windows (ETW):** Rendszeresemények naplózása, a `logman` vagy `wpr` parancsokkal kezelhető.

## 6. A Windows kernel stabilitása
A nagy verzióváltások (pl. XP → Vista → 7 → 10) között a kernel nagyon stabilizálódott. A PatchGuard megakadályozza, hogy harmadik felek módosítsák a kernel memóriáját futás közben, így a rootkit-ek nehezebben kapcsolódnak be.

## 7. Virtualizáció
A Hyper-V a Windows Server 2008 óta beépített hypervisor. A WSL2 egy teljes Linux kernelt futtat virtualizáció alatt, ami azt mutatja, hogy a Microsoft már elfogadta, hogy a saját kernelje nem mindenre jó.

## 8. Ha ReactOS-t akarnád használni
A ReactOS célja, hogy teljesen kompatibilis Windows NT API-t biztosítson. A fejlesztők gyakran a WRK dokumentációval és a ReactOS forráskódjával együtt dolgoznak, mert a Windows forráskódja zárt.

## 9. Összefoglalás
A Windows NT kernel egy hosszú életű, jól finanszírozott, de zárt rendszer. A legfontosabb különbség a Linux kernelhez képest: az Object Manager, az IRP-alapú I/O, a Registry, és a hibrid mikrokernel/monolitikus szerkezet. Ha driver fejlesztésbe akarsz belevágni, a KMDF a legjobb kezdőpont.

---

*Dokumentum státusz: STABIL. Nincs félreértés. Nincs feltételezés bizonyítás nélkül.*
