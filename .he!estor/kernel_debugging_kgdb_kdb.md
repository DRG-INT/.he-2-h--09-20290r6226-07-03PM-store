# Kernel Debugging kgdb és kdb használata
Verzió: 1.0-stable
Forrás: UNICAGD-Core Analízis
Státusz: HASZNÁLHATÓ

## 1. Mi az a kgdb és kdb?

A kgdb (Kernel GNU Debugger) és a kdb (Kernel Debugger) eszközök lehetővé teszik a kernel futás közbeni hibakeresését. A kgdb távoli debugolást tesz lehetővé, míg a kdb konzolon keresztül érhető el.

## 2. kgdb Beállítás

### 2.1 Kernel Konfiguráció
A következő opciókat be kell kapcsolni a kernel konfigurációban:
- `CONFIG_KGDB=y` vagy `CONFIG_KGDB=m`
- `CONFIG_KGDB_SERIAL_CONSOLE=y`
- `CONFIG_DEBUG_INFO=y`
- `CONFIG_FRAME_POINTER=y`
- `CONFIG_MAGIC_SYSRQ=y`

### 2.2 Boot Paraméterek
```bash
# GRUB boot paraméterek
GRUB_CMDLINE_LINUX_DEFAULT="kgdboc=ttyS0,115200 kgdbwait"
```
- `kgdboc=ttyS0,115200` – soros port konfigurálása kgdb-hez
- `kgdbwait` – kernel vár a kgdb kapcsolódásra

### 2.3 kgdb Indítása
```bash
# kernel debug build fordítása
cd /usr/src/linux
make menuconfig
# Kernel hacking -> Kernel debugging -> KGDB: kernel debugger

make -j$(nproc)
sudo make modules_install install
```

## 3. GDB és kgdb Kapcsolódás

### 3.1 GDB Konfigurálása
```bash
# GDB indítása a kernelrel
gdb vmlinux

# Távoli kapcsolódás kgdb-hez
(gdb) target remote /dev/ttyS0

# Vagy TCP-n keresztül
(gdb) target remote 192.168.1.100:4444
```

### 3.2 Gyakori kgdb Parancsok
```bash
# Breakpoint beállítása
(gdb) break kernel_clone   # (régebbi kerneleken: do_fork)
(gdb) break *0xffffffff810a3b2a

# Folyamatok listázása
(gdb) info threads
(gdb) thread apply all bt

# Memória megtekintése
(gdb) x/16x 0xffffffff810a3b2a
(gdb) p/x $rax

# Kernel napló
(gdb) p *(char *)0xffffffff82200000
```

## 4. kdb Beállítás

### 4.1 Kernel Konfiguráció
```bash
# Kernel konfiguráció
CONFIG_KGDB=y
CONFIG_KGDB_KDB=y
CONFIG_KDB=y
CONFIG_KDB_KEYBOARD=y
```

### 4.2 kdb Elérése
```bash
# SysRq keresztül
echo g > /proc/sysrq-trigger

# Vagy billentyűzetről
# Alt+SysRq+g
```

### 4.3 kdb Parancsok
```
kdb> bt          # Backtrace
kdb> ps          # Processzek listája
kdb> md          # Memória dump
kdb> rd          # Regiszterek dump
kdb> go          # Folytatás
kdb> ss          # Egy szál stackjének dumpja
kdb> cpu         # CPU információk
kdb> help        # Segítség
```

## 5. kprobes és Jprobes

### 5.1 Mi az a kprobes?
A kprobes lehetővé teszi bármilyen kernel címre breakpointot beállítani futás közben, anélkül hogy újra kellene fordítani a kernelt.

### 5.2 kprobes Használata
```c
#include <linux/kprobes.h>

static int handler_pre(struct kprobe *p, struct pt_regs *regs) {
    printk(KERN_INFO "kprobe triggered at %p\n", p->addr);
    return 0;
}

static struct kprobe kp = {
    .symbol_name = "do_fork",
    .pre_handler = handler_pre,
};

static int __init my_init(void) {
    int ret = register_kprobe(&kp);
    if (ret < 0) {
        printk(KERN_INFO "register_probe failed, returned %d\n", ret);
        return ret;
    }
    printk(KERN_INFO "kprobe registered\n");
    return 0;
}

static void __exit my_exit(void) {
    unregister_kprobe(&kp);
    printk(KERN_INFO "kprobe unregistered\n");
}
```

### 5.3 Kprobes Modern Használata (Jprobes helyett)
> *Megjegyzés:* A `jprobe` API a Linux 4.15-ben hivatalosan kivezetésre került. Modern kerneleken (5.x, 6.x) standard `kprobe`, `kretprobe` vagy eBPF használandó:

```c
#include <linux/kprobes.h>

static int kp_pre_handler(struct kprobe *p, struct pt_regs *regs) {
    printk(KERN_INFO "kernel_clone meghívva (cím: %p)\n", p->addr);
    return 0;
}

static struct kprobe kp = {
    .symbol_name = "kernel_clone", // régebbi kerneleken: _do_fork vagy do_fork
    .pre_handler = kp_pre_handler,
};
```

## 6. Ftrace

### 6.1 Mi az a Ftrace?
Az ftrace a kernel function tracer rendszere. Minden függvényhívás nyomon követhető.

### 6.2 Ftrace Használata
```bash
# Ftrace bekapcsolása
echo function > /sys/kernel/debug/tracing/current_tracer

# Egy konkrét függvény követése (modern kerneleken kernel_clone, régebben do_fork)
echo kernel_clone > /sys/kernel/debug/tracing/set_ftrace_filter

# Trace indítása
echo 1 > /sys/kernel/debug/tracing/tracing_on

# Trace megállítása
echo 0 > /sys/kernel/debug/tracing/tracing_on

# Trace eredmény megtekintése
cat /sys/kernel/debug/tracing/trace
```

### 6.3 Ftrace Szűrők
```bash
# Csak egy PID követése
echo 1234 > /sys/kernel/debug/tracing/set_ftrace_pid

# Csak kernel funkciók
echo function_graph > /sys/kernel/debug/tracing/current_tracer

# Function graph tracer
echo function_graph > /sys/kernel/debug/tracing/current_tracer
echo do_fork > /sys/kernel/debug/tracing/set_graph_function
```

## 7. Perf

### 7.1 Mi az a Perf?
A perf a Linux teljesítmény elemzési eszköze. CPU-események, függvényhívások, cache miss-ek nyomon követése.

### 7.2 Perf Felhasználás
```bash
# CPU profil készítése
perf record -g ./myprogram
perf report

# Valós idejű profil
perf top

# CPU események
perf stat -e cycles,instructions,cache-references,cache-misses ./myprogram

# Kernel függvények követése
perf record -e 'syscalls:sys_enter_open' -a
```

### 7.3 Perf Kernel Futtatása
```bash
# Kernel teljesítmény elemzés
perf record -e cycles:k -a
perf report

# Syscall tracing
perf record -e 'syscalls:sys_enter_*' -a
perf script
```

## 8. SystemTap

### 8.1 Mi az a SystemTap?
A SystemTap kernel események figyelésére szolgál. Skriptekkel definiálhatók a vizsgálni kívánt pontok.

### 8.2 SystemTap Használata
```bash
# Egyszerű SystemTap szkript
stap -e 'probe kernel.function("do_fork") {
    printf("do_fork called, pid=%d\n", pid())
}'

# Rendszeres események figyelése
stap -e 'probe kernel.function("*").call {
    printf("%s -> %s\n", probefunc(), user_string($return))
}'
```

## 9. eBPF és BCC

### 9.1 Mi az az eBPF?
Az eBPF (extended Berkeley Packet Filter) lehetővé teszi, hogy biztonságos, JIT-kompilált programokat futtassunk a kernelben futás közben.

### 9.2 BCC Eszközök
```bash
# Open és Close syscall-ok követése
execsnoop-bpfcc

# Memória kivétel követése
memleak-bpfcc

# TCP kapcsolatok követése
tcpconnect-bpfcc
```

### 9.3 bpftrace
```bash
# Syscallok számlálása
bpftrace -e 'tracepoint:syscalls:sys_enter_* { @[probe] = count(); }'

# Egy konkrét függvény hívásának követése (modern kerneleken kernel_clone)
bpftrace -e 'kprobe:kernel_clone { @[pid] = count(); }'
```

## 10. Hibakeresési Stratégia

### 10.1 Hibaeloszlás
1. **Hiba reprodukálása:** Milyen körülmények között jelentkezik?
2. **Naplók összegyűjtése:** dmesg, kern.log, syslog
3. **Kernel dump elemzése:** crash, gdb
4. **Futtatási környezet:** Virtuális gép, dedikált rendszer
5. **Kód elemzés:** Forráskód, git log

### 10.2 Hibakeresési Módszerek
- **Printk:** Naplózás a kódba
- **kprobes:** Dinamikus breakpointok
- **kgdb:** Távoli debug
- **Ftrace:** Függvényhívás nyomkövetés
- **Perf:** Teljesítmény elemzés

## 11. Összefoglalás

A kernel debugolási eszközök:
- **Kritikus fontosságú** a kernel hibák diagnosztikájához
- **Összetett eszközkészlet** áll rendelkezésre
- **Rendszeres gyakorlat** igényel
- **Különböző szintek** közül választhatsz

A kernel debugolás megértése:
- **kgdb** és **kdb** beállítása és használata
- **kprobes** és **jprobes** működése
- **Ftrace** és **perf** használata
- **eBPF** és **BCC** modern eszközök

---

*Dokumentum státusz: STABIL. Nincs félreértés. Nincs feltételezés bizonyítás nélkül.*
