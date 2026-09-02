# Kernel Energiakezelés (Power Management)
Verzió: 1.0-stable
Forrás: UNICAGD-Core Analízis
Státusz: HASZNÁLHATÓ

## 1. Mi az a Kernel Energiakezelés?

A kernel energiakezelése az a rendszer, amely kezeli a hardver energiafogyasztását. Célja az energia megtakarítása anélkül, hogy a teljesítmény jelentősen csökkenne.

## 2. Energiakezelési Alapfogalmak

### 2.1 CPU Frekvencia
- **CPU frekvencia:** A processzor órajelének sebessége
- **Alap frekvencia:** Normál működés során használt frekvencia
- **Turbo frekvencia:** Rövid időszakra növelt frekvencia
- **Alacsony frekvencia:** Energiatakarékosság, alacsony teljesítmény

### 2.2 CPU Allapotok (C-states)
- **C0:** Aktív állapot (CPU fut)
- **C1:** Halt állapot (CPU pihen, gyors felébresztés)
- **C2:** Clock-gating (órajel kikapcsolva, hosszabb felébresztés)
- **C3+:** Deep sleep (több órajel kikapcsolva, hosszabb felébresztés)

### 2.3 CPU Teljesítmény Állapotok (P-states)
- **P0:** Maximális teljesítmény
- **P1-Pn:** Növekvő energiahatékonyság, csökkenő teljesítmény
- **P-states frekvencia alapján:** Alacsonyabb frekvencia = alacsonyabb energiafogyasztás

## 3. CPU Frekvencia Szabályozás

### 3.1 CPU Governor Típusok
- **performance:** Mindig maximális frekvencia
- **powersave:** Mindig minimális frekvencia
- **ondemand:** Dinamikusan változtatja a frekvenciát a terhelés alapján
- **conservative:** Hasonló az ondemand-hoz, de lassabban változtat
- **schedutil:** Ütemező alapú, a kernel ütemezője dönti a frekvenciát
- **userspace:** Felhasználói szintű beállítás

### 3.2 CPU Governor Beállítás
```bash
# CPU governor beállítása
echo performance > /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor
echo powersave > /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor
echo schedutil > /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor

# CPU frekvencia megtekintése
cat /proc/cpuinfo | grep "cpu MHz"
cat /sys/devices/system/cpu/cpu*/cpufreq/scaling_cur_freq
```

## 4. Energiakezelési Technikák

### 4.1 CPU Idle
- **CPU idle:** CPU nem fut, amikor nincs munka
- **Idle states:** C-states (C1, C2, C3, stb.)
- **Idle injection:** CPU-t feleslegesen foglaljuk, hogy alacsonyabb állapotba kerüljön

### 4.2 CPU Hotplug
- **CPU ki/be kapcsolása:** Nem használt CPU-k kikapcsolása
- **CPU affinity:** Folyamatok CPU-khoz kötése
- **CPU isolation:** CPU-k dedikálása specifikus feladatokhoz

### 4.3 Perifériák Energiakezelése
- **USB autosuspend:** USB eszközök automatikus kikapcsolása
- **PCIe ASPM:** PCIe Active State Power Management
- **SATA Aggressive Link Power Management:** Lemez energiahatékonyság

## 5. Energiakezelési Konfiguráció

### 5.1 CPU Governor Konfiguráció
```bash
# /etc/default/cpufrequtils
GOVERNOR="ondemand"
MAX_SPEED="2.5GHz"
MIN_SPEED="800MHz"
```

### 5.2 CPU Idle Konfiguráció
```bash
# /etc/default/grub (GRUB_CMDLINE_LINUX_DEFAULT)
# A nohz_full és rcu_nocbs kernel boot paraméterek (nem sysctl fájlok):
GRUB_CMDLINE_LINUX_DEFAULT="quiet splash nohz_full=2-3 rcu_nocbs=2-3"
```

### 5.3 Perifériák Energiakezelése
```bash
# USB autosuspend bekapcsolása
echo auto > /sys/bus/usb/devices/*/power/control

# PCIe ASPM bekapcsolása
echo powersave > /sys/module/pcie_aspm/parameters/policy
```

## 6. Energiamegtakarítási Eszközök

### 6.1 powertop
- **Energiafogyasztás elemzése**
- **Energiamaradványok felismerése**
- **Javítási javaslatok**
```bash
# powertop futtatása
sudo powertop

# Energiajavaslatok alkalmazása
sudo powertop --auto-tune
```

### 6.2 turbostat
- **CPU teljesítmény és energiafogyasztás elemzése**
- **CPU frekvencia és C-state információk**
```bash
# turbostat futtatása
sudo turbostat --interval 1
```

### 6.3 tlp
- **Energiakezelési eszköz laptopokhoz**
- **Automatikus energiamegtakarítás**
```bash
# tlp telepítése és futtatása
sudo tlp start
sudo tlp-stat
```

## 7. Energiakezelés Hibakeresés

### 7.1 Energiafogyasztási Problémák
- **CPU túlterhelés:** CPU folyamatos maximális frekvencián
- **Perifériák energiafogyasztása:** USB eszközök folyamatos aktívak
- **Szervezeti problémák:** Nem optimalizált konfiguráció

### 7.2 Hibakeresési Eszközök
```bash
# Energiafogyasztás elemzése
sudo powertop
sudo turbostat

# CPU állapot megtekintése
cat /proc/acpi/processor/CPU*/power
cat /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor

# C-state információk
cat /proc/acpi/processor/CPU*/info
```

### 7.3 Energiafogyasztás csökkentése
1. **CPU governor beállítása:** Ondemand vagy schedutil
2. **CPU idle engedélyezése:** C-states használata
3. **Perifériák kikapcsolása:** USB autosuspend
4. **CPU hotplug:** Nem használt CPU-k kikapcsolása

## 8. Energiakezelés és Teljesítmény

### 8.1 Energiahatékonyság vs Teljesítmény
- **High performance:** Mindig maximális frekvencia, magas energiafogyasztás
- **Balanced:** Dinamikus frekvencia, közepes energiafogyasztás
- **Power save:** Minimális frekvencia, alacsony energiafogyasztás, alacsony teljesítmény

### 8.2 Energiahatékonyság Optimalizálás
- **CPU governor:** Ondemand vagy schedutil
- **CPU idle:** C-states engedélyezése
- **Perifériák:** USB autosuspend, PCIe ASPM
- **Szervezeti konfiguráció:** Energiatakarékos beállítások

### 8.3 Teljesítmény Optimalizálás
- **CPU governor:** Performance
- **CPU idle:** C1 állapot (nem mélyebb)
- **Perifériák:** Mindig aktív
- **CPU hotplug:** Minden CPU aktív

## 9. Energiakezelés és Virtualizáció

### 9.1 Virtualizációs Energiakezelés
- **CPU scaling:** VM CPU frekvencia szabályozás
- **CPU hotplug:** VM CPU-k ki/be kapcsolása
- **Memory ballooning:** Memória felesleges VM-ekből visszanyerése

### 9.2 Energiamegtakarítás Virtualizált Rendszerekben
- **VM konszolidálás:** Több VM egy fizikai gépre
- **VM migrálás:** VM-k áthelyezése energiatakarékos gépekhez
- **VM energiahatékonyság:** Energiatakarékos VM konfiguráció

## 10. Összefoglalás

Az energiakezelés:
- **Fontos** a hordozható eszközökön (laptop, telefon)
- **Összetett rendszer** a CPU, perifériák, és kernel részekből
- **Teljesítmény és energiafogyasztás** egyensúlyát kell megtartani
- **Konfigurálható** a felhasználói igények alapján

A kernel energiakezelés megértése:
- **CPU frekvencia** és **C-states** fogalmak ismerete
- **CPU governor** típusok és használati esetek ismerete
- **Energiamegtakarítási eszközök** ismerete
- **Hibakeresési technikák** ismerete

---

*Dokumentum státusz: STABIL. Nincs félreértés. Nincs feltételezés bizonyítás nélkül.*
