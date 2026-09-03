# FreeBSD Kernel Architecture and Industrial Subsystems
Version: 1.0-stable
Source: UNICAGD-Core Systems Engineering / DRG-INT Defense Framework
Classification: USABLE (Critical Infrastructure Technical Reference)

---

## 1. Monolithic Core Philosophy & Locking Architecture

FreeBSD implements a classical, highly optimized monolithic Unix kernel. Unlike microkernels, all core abstractions—virtual memory (VM), scheduler, virtual filesystem (VFS), networking stack, and device drivers—operate in the privileged supervisor address space (Ring-0).

```
+───────────────────────────────────────────────────────────────────+
|                     FREEBSD SUBSYSTEM TOPOLOGY                    |
+───────────────────────────────────────────────────────────────────+
|  [ USERSPACE: POSIX ABI / CAPSICUM SANDBOX ]                      |
+───────────────────────────────────┬───────────────────────────────+
                                    │ System Call Table (sysent[])
+───────────────────────────────────▼───────────────────────────────+
|  [ KERNEL LOCKING & SYNCHRONIZATION CORE ]                         |
|  • Mutexes (Adaptive & Spin) · Sleep Locks (sx, lockmgr)          |
|  • Read-Write Locks (rwlock) · Turnstiles (Priority Inversion Fix)|
+───────────────────────────────────────────────────────────────────+
|  [ VFS LAYER & GEOM FRAMEWORK ]      [ NETWORKING: NETGRAPH & BPF]|
|  • OpenZFS / UFS2 Softupdates        • Zero-copy packet filter    |
|  • Modular Block Transforms (GELI)   • Modular TCP Congestion     |
+──────────────────────────────────────┴────────────────────────────+
|  [ NEWBUS DRIVER INFRASTRUCTURE ]                                 |
|  • Hierarchical bus tree (nexus -> acpi -> pci -> device)         |
+───────────────────────────────────────────────────────────────────+
|  [ HARDWARE / CPU HAL ]                                           |
+───────────────────────────────────────────────────────────────────+
```

### Elimination of the Giant Lock (Fine-Grained SMP)
Historical BSD systems utilized a single global lock (`Giant`) protecting kernel reentrancy. Modern FreeBSD is completely fine-grained:
- **Adaptive Mutexes:** If the lock holder is running on another CPU core, the requesting thread spins; if the lock holder is sleeping, the requesting thread yields and sleeps.
- **Spin Mutexes:** Used strictly in interrupt handlers where sleeping is prohibited.
- **Turnstiles:** Mechanism tracking lock ownership to implement **Priority Inheritance Protocols**, preventing low-priority background worker threads from causing starvation in real-time or defense sensor pipelines.

---

## 2. GEOM Storage Architecture: Modular Block Geometry

The FreeBSD storage layer is abstracted by **GEOM**, a modular, plug-and-play block transformation framework developed by Poul-Henning Kamp.

### 2.1 The Provider-Consumer Model
GEOM models storage as a directed acyclic graph (DAG) composed of three entities:
1. **Geom (Class):** An instance of a transformation algorithm (e.g., encryption, mirroring, partitioning).
2. **Provider:** An entity producing block services (e.g., a physical disk `/dev/da0`, a slice `/dev/da0p1`, or a decrypted volume `/dev/da0p1.eli`).
3. **Consumer:** An entity attaching to a provider to read and write blocks.

```
[ Physical Disk Driver: da0 ] (Provider)
             │
             ▼
      [ GEOM_PART (GPT) ] (Geom)
             │
             ▼
     da0p1 (Swap)      da0p2 (Data Provider)
                             │
                             ▼
                    [ GEOM_ELI (GELI) ] (Geom Encryption)
                             │
                             ▼
                    da0p2.eli (Secure Provider)
                             │
                             ▼
                    [ OpenZFS / UFS2 ] (Filesystem Consumer)
```

### 2.2 Classified Forensics: Encrypted Panic Dumps (`dumpon -k`)
When a kernel panics, it must dump physical RAM to non-volatile storage. In military/classified deployments, dumping raw RAM exposes unencrypted encryption keys and sensitive signals. GEOM solves this via native public-key kernel dump encryption:
- At boot time, only the **public RSA key** is loaded into the kernel memory.
- During panic execution, the kernel generates a one-time random AES key, encrypts the memory dump, encrypts the AES key using the RSA public key, and writes the stream to the swap partition.
- The dump can only be decrypted offline in an isolated forensic lab possessing the RSA private key.

---

## 3. Capsicum: Capability-Based Security in the Kernel

Capsicum is a lightweight, mathematically sound capability and sandboxing framework integrated directly into the FreeBSD kernel.

### 3.1 The Vulnerability of POSIX Access Control
Conventional Unix permissions (DAC / MAC) operate at file open time. Once an application is compromised (e.g., via buffer overflow), it can invoke `open()`, `socket()`, or `execve()` to move laterally across the system.

### 3.2 Capability Mode (`cap_enter()`)
Capsicum addresses this by decoupling rights from the process identity and binding them to individual **file descriptors**:

```c
#include <sys/capsicum.h>

void enter_defense_enclave(int data_fd) {
    cap_rights_t rights;

    // 1. Definiáljuk a szigorúan megengedett műveleteket az FD-re
    cap_rights_init(&rights, CAP_READ, CAP_SEEK);
    cap_rights_limit(data_fd, &rights);

    // 2. Belépés a visszafordíthatatlan képesség-módba
    cap_enter();

    // Invariáns: A cap_enter() után az open(), socket(), connect(), execve()
    // rendszerhívások automatikusan ECAPMODE hibával elbuknak!
    // A folyamat KIZÁRÓLAG a már megnyitott data_fd-t tudja olvasni.
}
```

**Security Invariant:** Capability mode is one-way. A process cannot escalate privileges or restore normal system call access even with full shellcode execution.

---

## 4. The Newbus Device Driver Framework

FreeBSD structures all hardware devices in an explicit hierarchical tree managed by the **Newbus** subsystem.

### 4.1 Driver Tree Structure
- **Root (nexus0):** The top-level platform bus representing the physical CPU/chipset boundary.
- **Buses (nexus -> acpi -> pci -> usb):** Container devices that enumerate child devices.
- **Leaf Drivers:** Actual hardware controllers (e.g., `em0` Intel NIC, `nvme0` SSD).

### 4.2 Resource Allocation Protocol
Drivers never hardcode physical memory addresses or interrupt lines. Instead, they negotiate with Newbus via standardized methods:

```c
// Erőforrás-foglalási minta Newbus driverben
struct resource *res;
int rid = PCIR_BAR(0); // PCI Base Address Register 0

res = bus_alloc_resource_any(dev, SYS_RES_MEMORY, &rid, RF_ACTIVE);
if (res == NULL) {
    device_printf(dev, "Nem sikerült az MMIO BAR leképezése!\n");
    return (ENXIO);
}

// Biztonságos hozzáférés a regiszterekhez bus-space műveletekkel:
bus_write_4(res, REG_COMMAND, CMD_START);
```

---

## 5. DTrace: Dynamic Tracing in Production Operations

DTrace enables real-time instrumentation of the FreeBSD kernel and userland without recompiling or restarting.

### Strategic SRE / Defense Incident Use Cases:
1. **Interrupt Latency Profiling:** Identifying hardware spikes and noisy neighbors on shared PCI lines.
2. **Lock Contention Heatmaps:** Pinpointing exact kernel lock collisions during high-throughput network ingestion.
3. **Tracepoints at Failure:** Capturing stack traces precisely at the millisecond when a driver returns an error code.

---
*Document status: STABLE · UNICAGD-Core Architecture Standard*
