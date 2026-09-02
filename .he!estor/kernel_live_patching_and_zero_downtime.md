# Kernel Live Patching és Zero-Downtime Frissítés
Verzió: 1.0-stable
Forrás: UNICAGD-Core Analízis
Státusz: HASZNÁLHATÓ

## 1. Mi az a Kernel Live Patching?

A kernel live patching lehetővé teszi, hogy a futó kernelbe biztonsági javításokat alkalmazzunk újraindítás nélkül. Ez kritikus fontosságú a magas rendelkezésre állású rendszerekhez.

## 2. Live Patching Típusok

### 2.1 kpatch (Red Hat)
- **Technológia:** ftrace alapú
- **Működés:** Függvényhívások átirányítása
- **Előny:** Nem igényel speciális kernel verziót
- **Hátrány:** Csak egyszerű patch-eket támogat

### 2.2 kgraft (SUSE)
- **Technológia:** ftrace alapú, kpatch alternatíva
- **Működés:** Hívási gráf frissítése
- **Előny:** Open Source, szélesebb kernel támogatás
- **Hátrány:** Komplexebb implementáció

### 2.3 livepatch (Canonical/Ubuntu)
- **Technológia:** ftrace és kexec kombináció
- **Működés:** Függvényhívások átirányítása, kexec kernel újratöltés
- **Előny:** Ubuntu integráció, Canonical támogatás
- **Hátrány:** Csak Ubuntu rendszereken

## 3. Live Patching Működése

### 3.1 Alap Elv
1. **Eredeti függvény:** A kernelben lévő eredeti függvény
2. **Javított függvény:** A javított kód új verziója
3. **Átirányítás:** Az eredeti függvényhívások átirányítása a javított függvényre
4. **Atomic update:** Az átirányítás atomikus művelet

### 3.2 Ftrace Alapú Live Patching
```c
// Eredeti függvény
int vulnerable_function(int arg) {
    // Hibás kód
    return arg * 2;
}

// Javított függvény
int fixed_function(int arg) {
    // Javított kód
    if (arg < 0) return -EINVAL;
    return arg * 2;
}

// Live patch
struct kpatch_patch patch = {
    .name = "vulnerable_function",
    .new_func = fixed_function,
};
```

## 4. Live Patching Beállítás

### 4.1 RHEL/CentOS
```bash
# kpatch telepítése
sudo yum install kpatch

# Kernel live patch telepítése
sudo kpatch install kernel-3.10.0-1160.el7.x86_64

# Patch Ellenőrzés
sudo kpatch list
```

### 4.2 SUSE
```bash
# kgraft telepítése
sudo zypper install kgraft

# Patch alkalmazása
sudo kgraft apply patch.kpatch

# Patch állapot
sudo kgraft status
```

### 4.3 Ubuntu
```bash
# livepatch telepítése
sudo apt install ubuntu-advantage-tools
sudo ua attach <token>

# Live patch engedélyezése
sudo ua enable livepatch

# Patch állapot
sudo canonical-livepatch status
```

## 5. Live Patching Korlátai

### 5.1 Mit Támogat?
- **Egyszerű függvénycserék:** A függvény teljes kódjának cseréje
- **Adatstruktúra változások:** Nem támogatott
- **Új funkciók:** Nem támogatott
- **Belső API változások:** Nem támogatott

### 5.2 Mit Nem Támogat?
- **Adatstruktúra módosítások:** A patch nem módosíthatja a globális adatokat
- **Új syscall-ok:** Nem adhat hozzá új rendszerhívásokat
- **Komplex logika:** Összetett változások nem lehetségesek
- **Memóriakezelés:** Nem módosíthatja a memóriakezelést

### 5.3 Korlátok
- **Teljesítmény overhead:** Az átirányítás költsége
- **Memória használat:** Mindkét verziót kell tárolni
- **Stabilitás:** Hibás patch újabb problémákhoz vezethet

## 6. Zero-Downtime Frissítés Stratégiák

### 6.1 Kernel Rolling
```bash
# Rendszeres kernel frissítés
sudo apt update && sudo apt upgrade

# Kernel verzió követése
uname -r
apt list --upgradable | grep linux-image
```

### 6.2 Kernel Hot Reboot
```bash
# Kernel újratöltés kexec-tel
sudo kexec -l /boot/vmlinuz-$(uname -r) --initrd=/boot/initrd.img-$(uname -r) --command-line="$(cat /proc/cmdline)"
sudo systemctl kexec

# Vagy
sudo kexec -e
```

### 6.3 Virtualizációs Megközelítés
```bash
# VM snapshot
virsh snapshot-create myvm

# VM migrateálás
virsh migrate myvm qemu+tcp://newhost/system

# VM újraindítás
virsh reboot myvm
```

## 7. Live Patching Hibakeresés

### 7.1 Hibák Okaik
- **Hibás patch:** Nem megfelelően írt javítás
- **Kompatibilitási probléma:** A patch nem illeszkedik a kernelhez
- **Teljesítmény probléma:** Az átirányítás túl költséges

### 7.2 Hibakeresési Lépések
1. **Patch ellenőrzése:** A patch helyességének ellenőrzése
2. **Kernel napló:** `dmesg` hibakeresése
3. **Patch napló:** `kpatch` vagy `kgraft` naplók
4. **Visszafejtés:** Ha a patch hibás, azonnali visszafejtés

### 7.3 Patch Visszafejtés
```bash
# Patch eltávolítása
sudo kpatch uninstall kernel-3.10.0-1160.el7.x86_64

# Vagy
sudo kgraft remove patch.kpatch
```

## 8. Live Patching és Biztonság

### 8.1 Biztonsági Előnyök
- **Gyors javítás:** Kritikus sérülékenységek azonnali javítása
- **Nincs downtime:** Nincs szükség újraindításra
- **Környezet:** Ideális a 24/7 rendszerekhez

### 8.2 Biztonsági Kockázatok
- **Hibás patch:** A patch hibásan íródott, további hibák
- **Nem tesztelt patch:** Nem minden patch tesztelt a live patchinggel
- **Komplexitás:** Az élő rendszer megbízhatatlansága

### 8.3 Biztonsági Best Practices
- **Staging környezet:** Először teszteld a staging környezetben
- **Rollback terv:** Mindig legyen elérhető a visszafejtés
- **Monitorozás:** Folyamatos figyelés a javítás után

## 9. Live Patching és Fejlesztés

### 9.1 Patch Fejlesztés
```c
// Patch struktúra
struct kpatch_patch patch = {
    .name = "vulnerable_function",
    .new_func = fixed_function,
    .old_func = vulnerable_function,
};

// Patch regisztráció
kpatch_register_patch(&patch);
```

### 9.2 Patch Tesztelés
```bash
# Patch tesztelése
sudo kpatch test patch.kpatch

# Patch alkalmazása
sudo kpatch install patch.kpatch

# Patch ellenőrzése
sudo kpatch list
```

## 10. Összefoglalás

A kernel live patching:
- **Kritikus** a 24/7 rendszerekhez
- **Korlátokkal** rendelkezik
- **Rendszeres tesztelést** igényel
- **Biztonsági eszköz** a kritikus javításokhoz

A zero-downtime frissítés:
- **Kernel live patching** egyik módja
- **Virtualizáció** másik megközelítés
- **Kexec** és **kpatch** kombinálása
- **Rendszeres stratégia** szükséges

A kernel frissítési folyamatok:
- **Live patching** azonnali javításokhoz
- **Rendszeres frissítés** a hosszú távú karbantartáshoz
- **Virtualizáció** a rugalmassághoz
- **Monitorozás** a biztonságért

---

*Dokumentum státusz: STABIL. Nincs félreértés. Nincs feltételezés bizonyítás nélkül.*
