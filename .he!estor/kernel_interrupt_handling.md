# Kernel Megszakításkezelés (IRQ)
Verzió: 1.0-stable
Forrás: UNICAGD-Core Analízis
Státusz: HASZNÁLHATÓ

## 1. Mi az a Megszakítás (Interrupt)?

A megszakítás az a jel, amelyet a hardver küld a CPU-nak, amikor esemény történik, amire a kernelnek reagálnia kell. A megszakítás lehet:
- **Hardveres megszakítás:** Eszközök (pl. hálókártya, billentyűzet) jelzik, hogy adat érkezett
- **Szoftveres megszakítás:** Kernel által generált jel (pl. timer, syscall)

## 2. IRQ (Interrupt Request) Típusok

### 2.1 Hardveres IRQ
- **Legacy IRQ:** 0-15 között, régi x86 rendszerek
- **APIC IRQ:** Többprocesszoros rendszerek, 0-255 között
- **MSI (Message Signaled Interrupt):** PCIe eszközök, hálózati kártyák

### 2.2 Szoftveres IRQ
- **Timer interrupt:** Rendszeridő frissítése
- **System call:** Felhasználói program kernelbe való belépése
- **IPI (Inter-Processor Interrupt):** CPU-k közötti jelzés

## 3. IRQ Kezelés a Kernelben

### 3.1 IRQ Regisztráció
- Eszközmeghajtók regisztrálják a IRQ kezelőiket
- `request_irq()` függvény hívása
- IRQ szám, kezelő függvény, flags megadása

### 3.2 IRQ Vektorok
- Minden IRQ-hoz tartozik egy vektor (0-255)
- IDT (Interrupt Descriptor Table) tárolja a vektorokat
- A vektor mutatja a kezelő függvény címét

### 3.3 IRQ Kiosztás
- **Static IRQ:** Előre kiosztott IRQ számok
- **Dynamic IRQ:** Futás közben kiosztott IRQ számok
- **IRQ sharing:** Több eszköz ugyanazt az IRQ-t használja

## 4. IRQ Kontextus

### 4.1 IRQ Kontextus
- A kernel megszakítás kezelője fut itt
- **Nincs felhasználói tér:** Nem futtathatók felhasználói programok
- **Nincs blokkolás:** Nem lehet várakozni
- **Rövid és gyors:** Minimalizálni kell a futási időt

### 4.2 Bottom Halves (Softirq, Tasklets, Workqueues)
- A hosszabb munkát felfüggesztik és később végezhetik
- **Softirq:** Magas prioritu, kernel szálakban fut
- **Tasklets:** Softirq alapú, egyszerre futó egységek
- **Workqueues:** Processzekben futó munkafolyamatok

### 4.3 Top Halves vs Bottom Halves
- **Top Half (IRQ handler):** Azonnali, kritikus munka
- **Bottom Half (Softirq/Tasklet):** Késleltetett, nem kritikus munka

## 5. IRQ Monitorozás

### 5.1 IRQ Listázás
```bash
# IRQ információk
cat /proc/interrupts
cat /proc/stat
```

### 5.2 IRQ Statisztikák
```bash
# IRQ számlálók
cat /proc/interrupts
cat /proc/stat | grep intr

# IRQ affinitás
cat /proc/irq/*/smp_affinity
```

### 5.3 IRQ hibakeresés
```bash
# IRQ hibák keresése
dmesg | grep -i irq
dmesg | grep -i error

# IRQ csomagolási hibák
ethtool -S eth0 | grep -i rx_missed
```

## 6. IRQ Beállítások

### 6.1 IRQ Affinity
```bash
# IRQ affinitás beállítása
echo 1 > /proc/irq/XX/smp_affinity

# Minden IRQ egy CPU-ra
for irq in $(cat /proc/interrupts | grep -i eth0 | awk '{print $1}' | sed 's/://'); do
    echo 1 > /proc/irq/$irq/smp_affinity
done
```

### 6.2 IRQ Balancing
```bash
# IRQ balancing be/ki
echo 0 > /proc/irq/default_smp_affinity

# IRQ balancing naplózás
cat /proc/interrupts
```

### 6.3 IRQ Coalescing
```bash
# IRQ coalescing beállítása
ethtool -C eth0 rx-usecs 100
ethtool -C eth0 rx-frames 16
```

## 7. IRQ Hibakeresés

### 7.1 Gyakori Hibák
- **IRQ flood:** Túl sok megszakítás
- **IRQ storm:** Megszakítási hurkok
- **IRQ timeout:** Megszakítás nem érkezett
- **Shared IRQ conflict:** Több eszköz ugyanazt az IRQ-t használja

### 7.2 Hibakeresési Lépések
1. **IRQ listázása:** `cat /proc/interrupts`
2. **Hibás IRQ azonosítása:** `dmesg | grep -i irq`
3. **Eszköözök ellenőrzése:** `lspci`, `lsusb`
4. **Driver frissítés:** Eszközmeghajtó frissítése

## 8. IRQ Biztonság

### 8.1 IRQ Védelem
- **IRQ disable:** Megszakítások ideiglenes letiltása
- **Spinlock:** Kritikus szekciók védelme
- **Local IRQ disable:** CPU-specifikus megszakítások letiltása

### 8.2 IRQ Biztonsági Problémák
- **IRQ flood attack:** Túl sok megszakítás
- **IRQ storm:** Megszakítási hurkok
- **Deadlock:** Zárolási problémák

## 9. IRQ Optimalizálás

### 9.1 IRQ Balancing
- **Manual affinity:** IRQ-k kézi kiosztása
- **irqbalance démon:** Automatikus kiegyensúlyozás
- **CPU isolation:** CPU-k dedikálása

### 9.2 IRQ Coalescing
- **Több megszakítás összevonása**
- **CPU terhelés csökkentése**
- **Átfolyás csökkentése**

### 9.3 IRQ Rate Limiting
- **Megszakítási korlátok beállítása**
- **DoS védelem**
- **Rendszerstabilitás javítása**

## 10. Összefoglalás

Az IRQ kezelés:
- **Kritikus fontosságú** a rendszer kommunikációjához
- **Összetett rendszer** a megszakítási folyamatokkal
- **Teljesítmény érzékeny** a beállításokra
- **Biztonsági szempontok** figyelembevétele szükséges

A kernel megszakításkezelés megértése:
- **IRQ típusok** és **használati esetek** ismerete
- **Top/Bottom halves** különbségének megértése
- **IRQ affinity** és **coalescing** beállítása
- **Hibakeresési eszközök** ismerete

---

*Dokumentum státusz: STABIL. Nincs félreértés. Nincs feltételezés bizonyítás nélkül.*
