# Kernel Hardening és Biztonság Erősítés
Verzió: 1.0-stable
Forrás: UNICAGD-Core Analízis
Státusz: HASZNÁLHATÓ

## 1. Mi az a Kernel Hardening?

A kernel hardening az a folyamat, amely során a kernel biztonsági réseit csökkentjük, és a támadási felületet minimalizáljuk. Célja, hogy a kernel ellenálljon a támadásoknak, és ne könnyítsen a behatolást.

## 2. Kernel Hardening Technikák

### 2.1 Memória Védelme
- **KASLR (Kernel Address Space Layout Randomization):** Kernel címek randomizálása
- **KPTI (Kernel Page Table Isolation):** Kernel és felhasználói címterek szétválasztása
- **SMEP (Supervisor Mode Execution Prevention):** Kernel nem futtathat felhasználói kódot
- **SMAP (Supervisor Mode Access Prevention):** Kernel nem férhet hozzá a felhasználói memóriához
- **Stack Protector:** Veremvédelem a buffer overflow ellen
- **FORTIFY_SOURCE:** Bounds checking a standard C függvényekhez

### 2.2 Access Control
- **SELinux (Security-Enhanced Linux):** Mandatory Access Control
- **AppArmor:** Profil alapú hozzáférési szabályok
- **Seccomp:** Syscall szűrés
- **Capabilities:** Részleges root jogosultságok

### 2.3 Kernel Konfiguráció
- **Strict kernel mode:** Kernel futtatása védett módban
- **Module signature verification:** Kernel modulok aláírás ellenőrzése
- **Lockdown mode:** Kernel módosítások korlátozása
- **Read-only kernel:** Kernel írásvédett

## 3. Hardening Beállítások

### 3.1 Kernel Paraméterek
```bash
# /etc/sysctl.conf
kernel.kptr_restrict = 2
kernel.dmesg_restrict = 1
kernel.printk = 3 3 1 4
kernel.modules_disabled = 1
kernel.randomize_va_space = 2
```

### 3.2 Boot Parancssor
```bash
# GRUB_CMDLINE_LINUX_DEFAULT
"slab_nomerge slub_debug=FZP page_owner=on init_on_alloc=1 init_on_free=1"
```

### 3.3 LSM (Linux Security Modules)
```bash
# SELinux bekapcsolása
SELINUX=enforcing

# AppArmor bekapcsolása
apparmor=1 security=apparmor
```

## 4. KASLR (Kernel Address Space Layout Randomization)

### 4.1 Működés
- A kernel betöltési címe minden boot során véletlenszerű
- Nehézségi szintek: alapértelmezett, erősített, maximális
- KASLR megkerülés: Információiszivárgás + ROP chaining

### 4.2 Konfiguráció
```bash
# Userspace ASLR bekapcsolása (2 = full randomization: stack, mmap, heap)
echo 2 > /proc/sys/kernel/randomize_va_space

# KASLR (Kernel-szintű) boot paraméter ellenőrzése (kikapcsolás: nokaslr)
dmesg | grep -i "kernel text base"
cat /proc/kallsyms | head -1
```

## 5. KPTI (Kernel Page Table Isolation)

### 5.1 Működés
- Kernel és felhasználói lapozási táblák szétválasztása
- Meltdown (Rogue Data Cache Load, Variant 3) elleni alapvető védelem
- Kernel oldali adat eléréshez kernel lapozási táblák betöltése

### 5.2 Teljesítmény Hatás
- 5-30% teljesítménycsökkenés (CPU és munkaterhelés függő)
- CPU specifikus: régebbi Intel processzorokon jelentősebb

### 5.3 Konfiguráció
```bash
# KPTI boot paraméter
pti=on   # vagy: pti=auto

# KPTI ellenőrzése (Meltdown státusz)
dmesg | grep -i "Kernel/User page tables isolation"
cat /sys/devices/system/cpu/vulnerabilities/meltdown
```

## 6. SMEP és SMAP

### 6.1 SMEP (Supervisor Mode Execution Prevention)
- CPU nem futtathat felhasználói térben lévő kódot
- Megakadályozza, hogy a kernel véletlenül futtasson felhasználói kódot

### 6.2 SMAP (Supervisor Mode Access Prevention)
- CPU nem férhet hozzá a felhasználói memóriához kernel módban
- Megakadályozza, hogy a kernel véletlenül írjon a felhasználói memóriába

### 6.3 Ellenőrzés
```bash
# SMAP/SMEP ellenőrzése
grep smap /proc/cpuinfo
grep smep /proc/cpuinfo

# CPU védelmei
cat /proc/cpuinfo | grep -E "smep|smap|smap"
```

## 7. Capabilities

### 7.1 Mi az a Capability?
- Részleges root jogosultságok
- Minden folyamatnak van egy capability halmaza
- Pl. CAP_NET_ADMIN (hálózati adminisztráció), CAP_SYS_ADMIN (rendszergazda)

### 7.2 Gyakori Capabilities
- **CAP_SYS_ADMIN:** Rendszergazda jogok (mintegy root)
- **CAP_NET_ADMIN:** Hálózati konfiguráció
- **CAP_NET_RAW:** Raw socket használata
- **CAP_SYS_RAWIO:** Raw I/O műveletek
- **CAP_DAC_OVERRIDE:** Fájljogosultságok felülbírálása

### 7.3 Capability Kezelés
```bash
# Capability megtekintése
getcap /usr/bin/ping
getcap /usr/bin/tcpdump

# Capability beállítása
setcap CAP_NET_RAW+ep /usr/bin/ping
setcap CAP_NET_ADMIN+ep /usr/bin/ip
```

## 8. Seccomp

### 8.1 Mi az a Seccomp?
- Syscall szűrés
- Alkalmazások korlátozása csak bizonyos syscall-okat használják
- Csak olvasható, nem módosítható (BPF alapú)

### 8.2 Seccomp Profilok
```c
// Seccomp példa C-ben
#include <linux/seccomp.h>
#include <linux/filter.h>
#include <sys/prctl.h>

// Csak read, write, exit syscall-ok engedélyezése
struct sock_filter filter[] = {
    BPF_STMT(BPF_LD | BPF_W | BPF_ABS, offsetof(struct seccomp_data, nr)),
    BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_read, 3, 0),  // ha egyezik -> ugrás ALLOW-ra (3 utasítás előre)
    BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_write, 2, 0), // ha egyezik -> ugrás ALLOW-ra (2 utasítás előre)
    BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_exit, 1, 0),  // ha egyezik -> ugrás ALLOW-ra (1 utasítás előre)
    BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_KILL_PROCESS),   // nem engedélyezett syscall -> leállítás
    BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ALLOW),          // engedélyezett syscall -> továbbengedés
};
```

## 9. Kernel Lockdown

### 9.1 Mi az a Kernel Lockdown?
- Kernel módosítások korlátozása
- Nem lehet kernel modulokat betölteni
- Nem lehet kernel memóriát módosítani

### 9.2 Lockdown Beállítások
```bash
# Lockdown módok
0: Disabled (nincs lockdown)
1: Integrity (csak aláírt modulok betöltése)
2: Confidentiality (csak aláírt modulok, kernel memória védett)

# Lockdown ellenőrzése
cat /sys/kernel/security/lockdown
```

## 10. Hardening Eszközök

### 10.1 Lynis
- Rendszer biztonsági audit eszköz
- Kernel hardening ellenőrzés
- Konfiguráció javaslatok

### 10.2 kconfig-hardening-check
- Kernel konfiguráció hardening ellenőrzés
- Hiányzó védelmi mechanizmusok felismerése

### 10.3 grsecurity/PaX
- Hardening patch a kernelhez
- Memory protection, access control
- Nem elérhető minden kernel verzióban

## 11. Összefoglalás

A kernel hardening:
- **Fontos** a rendszer biztonságához
- **Több rétegű védelem** szükséges
- **Teljesítmény költséggel** járhat
- **Rendszeres ellenőrzés** szükséges

A kernel hardening megértése:
- **KASLR, KPTI, SMEP, SMAP** működésének ismerete
- **Capabilities** és **Seccomp** használata
- **Lockdown mód** és **konfiguráció** ismerete
- **Hardening eszközök** ismerete

---

*Dokumentum státusz: STABIL. Nincs félreértés. Nincs feltételezés bizonyítás nélkül.*
