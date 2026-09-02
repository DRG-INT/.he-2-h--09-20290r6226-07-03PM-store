# Kernel IOMMU Kezelés
Verzió: 1.0-stable
Forrás: UNICAGD-Core Analízis
Státusz: HASZNÁLHATÓ

## 1. Mi az az IOMMU?

Az IOMMU (Input-Output Memory Management Unit) egy hardveres egység, amely kezeli az eszközök memória hozzáféréseit. Hasonló a CPU MMU-jához, de az IOMMU az eszközök számára biztosítja a memóriakezelést.

## 2. IOMMU Működése

### 2.1 Cél
- **Memóriavédelem:** Eszközök csak engedélyezett memóriaterületeket érhetik el
- **Címátirás:** Eszközök által használt címek leképezése a fizikai memóriára
- **Elkülönítés:** Eszközök elkülönítése egymástól

### 2.2 IOMMU és DMA
- IOMMU közvetlenül a DMA folyamatot érinti
- Eszközök által generált DMA címeket átirányítja a fizikai memóriára
- Ha nincs IOMMU, az eszközök közvetlenül a fizikai címeket használják

## 3. IOMMU Típusok

### 3.1 AMD-Vi (AMD IOMMU)
- AMD processzorokon elérhető
- Támogatja a virtualizációt (SR-IOV)
- IOMMU csoportok (I/O virtualization)

### 3.2 Intel VT-d
- Intel processzorokon elérhető
- Támogatja a virtualizációt
- DMA remapping, interrupt remapping

### 3.3 ARM SMMU
- ARM processzorokon elérhető
- Stage-1 és Stage-2 fordítás
- Stage-1: Guest物理 cím -> Host fizikai cím
- Stage-2: Eszköz cím -> Host fizikai cím

## 4. IOMMU Konfiguráció

### 4.1 Kernel Parancssor
```bash
# Intel VT-d bekapcsolása
GRUB_CMDLINE_LINUX_DEFAULT="intel_iommu=on iommu=pt"

# AMD IOMMU bekapcsolása
GRUB_CMDLINE_LINUX_DEFAULT="amd_iommu=on iommu=pt"

# IOMMU naplózás bekapcsolása
GRUB_CMDLINE_LINUX_DEFAULT="intel_iommu=on iommu=pt dmar=on"
```

### 4.2 Szigorú IOMMU és DMAR Boot Paraméterek
```bash
# /etc/default/grub (GRUB_CMDLINE_LINUX_DEFAULT)
# Szigorú leképezés (strict TLB invalidation) DMA támadások ellen:
GRUB_CMDLINE_LINUX_DEFAULT="intel_iommu=on iommu.strict=1 iommu=force"
```

### 4.3 IOMMU Ellenőrzés
```bash
# IOMMU státusz ellenőrzése
dmesg | grep -i dmar
dmesg | grep -i iommu

# IOMMU csoportok
ls /sys/kernel/iommu_groups/

# IOMMU információk
cat /sys/kernel/iommu_groups/*/devices/*/config
```

## 5. IOMMU és Virtualizáció

### 5.1 SR-IOV (Single Root I/O Virtualization)
- Egy fizikai eszközből több virtuális eszköz létrehozása
- IOMMU lehetővé teszi a virtuális eszközök elkülönítését
- Magas teljesítményű virtualizáció

### 5.2 VFIO (Virtual Function I/O)
- Eszközök átadása virtuális gépeknek
- IOMMU biztosítja a biztonságos hozzáférést
- KVM/QEMU virtualizációban használatos

### 5.3 IOMMU és KVM
- **KVM IOMMU:** Virtuális gépek IOMMU támogatása
- **VFIO PCI:** PCI eszközök átadása VM-nek
- **VFIO platform:** Platform eszközök átadása

## 6. IOMMU Hibakeresés

### 6.1 Gyakori Hibák
- **IOMMU fault:** IOMMU hiba
- **DMA address error:** Hibás DMA cím
- **IOMMU timeout:** IOMMU időtúllépés
- **Device not attached:** Eszköz nem csatlakozik IOMMU-hoz

### 6.2 Hibakeresési Eszközök
```bash
# IOMMU hibák keresése
dmesg | grep -i dmar
dmesg | grep -i iommu
dmesg | grep -i dma

# IOMMU információk
cat /sys/kernel/iommu_groups/*/devices/*/status
```

### 6.3 IOMMU Tesztelés
```bash
# IOMMU tesztek futtatása
dmaengine_test
stress --dma 4 --timeout 60
```

## 7. IOMMU és Biztonság

### 7.1 IOMMU Védelem
- **DMA védelem:** Eszközök csak engedélyezett memóriaterületeket érhetik el
- **Eszköz elkülönítés:** Eszközök nem érintik egymás memóriáját
- **Kernel memóriavédelem:** Eszközök nem írhatják a kernel memóriát

### 7.2 IOMMU és Tűzfal
- **IOMMU tűzfal:** Eszközök hozzáférési szabályok
- **DMA ACL:** Access Control List
- **IOMMU naplózás:** Eszközök hozzáférésének naplózása

### 7.3 IOMMU Korlátok
- **Teljesítmény overhead:** IOMMU leképezés költsége
- **Kompatibilitási problémák:** Régi eszközök nem támogatják
- **Konfiguráció bonyolultság:** IOMMU beállítása nehézkes

## 8. IOMMU Optimalizálás

### 8.1 IOMMU Működési Módok
- **Strict mode:** Minden DMA cím ellenőrzése
- **Lazy mode:** Csak az első hozzáférés ellenőrzése
- **Pass-through mode:** IOMMU kikapcsolva

### 8.2 IOMMU Beállítások
```bash
# Strict mode (biztonságosabb)
echo 1 > /sys/kernel/iommu_groups/*/strict

# Lazy mode (gyorsabb)
echo 0 > /sys/kernel/iommu_groups/*/strict

# Pass-through mode (leggyorsabb, de veszélyes)
echo 0 > /sys/kernel/iommu_groups/*/enable
```

### 8.3 IOMMU és Teljesítmény
- **IOMMU cache:** IOMMU cím leképezés cache
- **IOMMU prefetch:** Előre leképezés
- **IOMMU batching:** Csoportos leképezések

## 9. IOMMU és Kernel Verziók

### 9.1 IOMMU Támogatás
- **Kernel 2.6.x:** Kezdeti IOMMU támogatás
- **Kernel 3.x:** Fejlettebb IOMMU támogatás
- **Kernel 4.x+:** Teljes IOMMU támogatás, VFIO integráció

### 9.2 IOMMU és Driver
- **IOMMU API:** Kernel API IOMMU műveletekhez
- **IOMMU driver:** IOMMU vezérlő driverek
- **IOMMU domain:** IOMMU domain kezelés

## 10. Összefoglalás

Az IOMMU kezelés:
- **Fontos** a DMA biztonságához
- **Hardveres támogatás** szükséges
- **Konfiguráció** és **tesztelés** szükséges
- **Virtualizáció** esetén kiváló

A kernel IOMMU kezelés megértése:
- **IOMMU működés** és **célja** ismerete
- **IOMMU típusok** és **konfiguráció** ismerete
- **IOMMU biztonság** és **védelem** ismerete
- **Hibakeresési eszközök** ismerete

---

*Dokumentum státusz: STABIL. Nincs félreértés. Nincs feltételezés bizonyítás nélkül.*
