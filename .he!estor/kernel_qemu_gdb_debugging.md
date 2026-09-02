# Kernel QEMU és GDB Kombinált Hibakeresés
Verzió: 1.0-stable
Forrás: UNICAGD-Core Analízis
Státusz: HASZNÁLHATÓ

## 1. Miért Használjunk QEMU-t Kernel Hibakereséshez?

A QEMU lehetővé teszi a kernel virtuális környezetben történő futtatását, ahol biztonságosan kísérletezhetünk, anélkül hogy a valódi hardvert veszélyeztetnénk.

## 2. QEMU Kernel Debug Beállítás

### 2.1 Kernel Build Debug Információkkal
```bash
cd /usr/src/linux
make menuconfig

# Kernel hacking -> Compile-time checks and compiler options
# -> Compile the kernel with debug info
CONFIG_DEBUG_INFO=y

# Kernel hacking -> KGDB: kernel debugger
CONFIG_KGDB=y
CONFIG_KGDB_SERIAL_CONSOLE=y

make -j$(nproc) KCFLAGS=-g
sudo make modules_install install
```

### 2.2 QEMU Indítás Debug Módban
```bash
# QEMU indítása GDB szerverrel
qemu-system-x86_64 \
  -kernel /boot/vmlinuz-$(uname -r) \
  -initrd /boot/initrd.img-$(uname -r) \
  -append "root=/dev/sda1 console=ttyS0 kgdboc=ttyS0,115200 kgdbwait" \
  -hda kernel-debug.qcow2 \
  -serial stdio \
  -monitor telnet:127.0.0.1:4444,server,nowait \
  -s -S
```

### 2.3 GDB Kapcsolódás
```bash
# GDB indítása
gdb vmlinux

# Kapcsolódás QEMU-hoz
(gdb) target remote :1234

# Vagy
(gdb) target remote localhost:1234
```

## 3. GDB Kernel Debug Parancsok

### 3.1 Alap Parancsok
```bash
# Breakpoint
(gdb) break do_fork
(gdb) break *0xffffffff810a3b2a
(gdb) break *0xffffffff810a3b2a if $rax == 0

# Futtatás
(gdb) continue
(gdb) step
(gdb) next
(gdb) finish

# Stack trace
(gdb) bt
(gdb) bt full
(gdb) thread apply all bt
```

### 3.2 Kernel Specifikus Parancsok
```bash
# Kernel napló
(gdb) p *(char *)0xffffffff82200000

# Processzek listája
(gdb) p *(struct task_struct *)0xffffffff82200000

# Memória dump
(gdb) x/16x 0xffffffff810a3b2a

# Regiszterek
(gdb) info registers
(gdb) p/x $rax
```

### 3.3 Kernel Helper Scriptek
```bash
# ~/.gdbinit kernel debughez
define psinfo
    p ((struct task_struct *)$arg0)->comm
    p ((struct task_struct *)$arg0)->pid
    p ((struct task_struct *)$arg0)->state
end

define btall
    thread apply all bt
end
```

## 4. Kernel Boot Problémák Hibakeresése

### 4.1 Kernel Nem Indul
```bash
# Boot paraméterek hozzáadása
GRUB_CMDLINE_LINUX_DEFAULT="debug initcall_debug earlyprintk=serial,ttyS0,115200"
```

### 4.2 Kernel Panic Debug
```bash
# Kernel panic információ
dmesg | grep -A 20 "Kernel panic"

# Kernel oops elemzés
scripts/decode_stacktrace.sh /path/to/vmlinux < /var/log/kern.log
```

### 4.3 Early Boot Hibakeresés
```bash
# Early printk bekapcsolása
earlyprintk=serial,ttyS0,115200

# Debug információk
debug initcall_debug
```

## 5. Kernel Module Debugolása QEMU-ban

### 5.1 Modul Betöltés Debugolása
```bash
# Kernel konfiguráció
CONFIG_MODULE_UNLOAD=y
CONFIG_MODULE_FORCE_UNLOAD=y

# Modul betöltés debugolása
insmod mymodule.ko
dmesg | tail -50
```

### 5.2 Modul Hibakeresés
```bash
# Breakpoint a modul inicializálásánál
(gdb) break mymodule_init
(gdb) continue

# Modul betöltése
(gdb) # Amikor a modul betöltődik, a breakpoint aktiválódik
```

## 6. Kernel Crash Dump Elemzés QEMU-ban

### 6.1 Crash Dump Generálása
```bash
# QEMU-ban kernel panic triggered
echo c > /proc/sysrq-trigger

# Vagy: pánik kikényszerítése Oops esetén, 5 másodperces újraindítási késleltetéssel:
echo 1 > /proc/sys/kernel/panic_on_oops
echo 5 > /proc/sys/kernel/panic
```

### 6.2 Crash Dump Elemzése
```bash
# Crash dump elemzés
crash /usr/lib/debug/boot/vmlinux-$(uname -r) /var/crash/$(uname -r)/vmcore

# Vagy GDB-vel
gdb vmlinux /var/crash/$(uname -r)/vmcore
```

## 7. Kernel Teljesítmény Hibakeresése QEMU-ban

### 7.1 CPU Profil Készítése
```bash
# Perf használata QEMU-ban
perf record -g -p $(pidof qemu-system-x86_64)
perf report
```

### 7.2 Ftrace Használata
```bash
# Ftrace bekapcsolása
echo function > /sys/kernel/debug/tracing/current_tracer
echo 1 > /sys/kernel/debug/tracing/tracing_on

# Trace megtekintése
cat /sys/kernel/debug/tracing/trace
```

## 8. Kernel Hibakeresési Módszertan

### 8.1 Hibaeloszlás Stratégia
1. **Hiba reprodukálása:** QEMU-ban reprodukáld a hibát
2. **Naplók összegyűjtése:** dmesg, kern.log, QEMU napló
3. **Kód elemzés:** Forráskód, git log, commitok
4. **Debugolás:** GDB, ftrace, perf használata
5. **Javítás:** Patch készítése és tesztelése

### 8.2 Hibakeresési Eszközök Kombinálása
- **GDB + QEMU:** Interactive debugging
- **Ftrace + perf:** Performance analysis
- **kprobes + SystemTap:** Dynamic tracing
- **kdump + crash:** Post-mortem analysis

## 9. Gyakorlati Tippek

### 9.1 Környezet Előkészítése
```bash
# Virtuális gép kép létrehozása
qemu-img create -f qcow2 kernel-debug.img 20G

# Kernel telepítése
sudo debootstrap --include=linux-image-amd64,linux-headers-amd64,build-essential,gdb \
  stable /mnt http://deb.debian.org/debian
```

### 9.2 Hibakeresési Munkafolyamat
1. **Kernel build debug infóval**
2. **QEMU indítása GDB szerverrel**
3. **GDB kapcsolódása**
4. **Breakpointok beállítása**
5. **Hibát reprodukálni**
6. **Stack trace elemzése**
7. **Javítás készítése**
8. **Újraindítás és tesztelés**

## 10. Összefoglalás

A QEMU és GDB kombinált hibakeresés:
- **Biztonságos** kernel hibakeresést tesz lehetővé
- **Rendszeres** tesztelést és hibakeresést
- **Költséghatékony** – nincs szükség több fizikai gépre
- **Reprodukálható** hibakeresési környezet

A kernel QEMU debugolás megértése:
- **QEMU beállítása** GDB szerverrel
- **GDB kapcsolódás** és parancsok
- **Kernel boot problémák** hibakeresése
- **Crash dump elemzés** virtuális környezetben

---

*Dokumentum státusz: STABIL. Nincs félreértés. Nincs feltételezés bizonyítás nélkül.*
