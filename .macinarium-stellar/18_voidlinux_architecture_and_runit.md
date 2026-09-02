# Void Linux Architecture and Runit Supervision Engine
Version: 1.0-stable
Source: UNICAGD-Core Systems Engineering / DRG-INT Defense Framework
Classification: USABLE (Critical Infrastructure Technical Reference)

---

## 1. Architectural Philosophy: The Non-Monolithic Linux Model

Void Linux is an operating system engineered around strict architectural decoupling. Unlike contemporary general-purpose distributions that assimilate networking, logging, device management, and service orchestration into a centralized daemon ecosystem (systemd), Void adheres to the classical Unix modularity principle:

```
+───────────────────────────────────────────────────────────────────+
|               VOID LINUX ARCHITECTURAL DECOUPLING                 |
+───────────────────────────────────────────────────────────────────+
|  [ USERSPACE APPLICATIONS & DAEMONS ]                             |
+───────────────────────────────────────────────────────────────────+
|  [ SERVICE SUPERVISION: RUNIT ]                                   |
|  • Stage 1: One-time system boot script (/etc/runit/1)            |
|  • Stage 2: Supervision tree via runsvdir (/etc/runit/2)          |
|  • Stage 3: Controlled teardown & emergency halt (/etc/runit/3)   |
+───────────────────────────────────────────────────────────────────+
|  [ C STANDARD LIBRARY: MUSL LIBC ]                                |
|  • Lightweight, clean mathematical standard adherence             |
|  • Zero dynamic allocator bloat · Predictable stack frame margins |
+───────────────────────────────────────────────────────────────────+
|  [ PACKAGE ECOSYSTEM: XBPS (X Binary Package System) ]            |
|  • Native C implementation · SHA-256 package verification         |
+───────────────────────────────────────────────────────────────────+
|  [ LINUX KERNEL: MONOLITHIC RUNTIME ]                             |
|  • Vanilla / Hardened patchsets · Minimal initramfs generation    |
+───────────────────────────────────────────────────────────────────+
```

### Why Critical Infrastructure Prefers Void Linux:
1. **Minimal TCB (Trusted Computing Base):** Fewer lines of executable code in PID 1 means mathematically reduced vulnerability surfaces.
2. **Zero Socket Activation Race Conditions:** Daemons start deterministically; services do not hang on unhandled D-Bus signals.
3. **Reproducible Air-Gapped Operation:** The entire package management and runtime state can be verified offline via cryptographic hash databases (`pkgdb`).

---

## 2. Runit Supervision Tree & Finite State Machine

The `runit` init system replaces conventional SysV init and systemd with a deterministic three-stage state machine.

### 2.1 The Three-Stage Lifecycle
1. **Stage 1 (`/etc/runit/1`):**
   - Executed once at machine power-on.
   - Mounts `/proc`, `/sys`, and `/dev` (devtmpfs).
   - Initializes local hardware clock (hwclock) and random seed.
   - Activates swap and checks local filesystems (`fsck`).
   - Hands execution directly to Stage 2 upon exit code 0.
2. **Stage 2 (`/etc/runit/2`):**
   - The operational core. Runs `/usr/bin/runsvdir /var/service`.
   - Periodically scans `/var/service` for new symlinks.
   - For every symlink, spawns an individual `runsv` supervisor process.
   - If a managed daemon crashes or exits, `runsv` immediately restarts it according to policy without rebooting the system.
3. **Stage 3 (`/etc/runit/3`):**
   - Triggered on shutdown, reboot, or emergency halt.
   - Terminates all active `runsv` processes via SIGTERM and SIGKILL.
   - Syncs all buffer caches, unmounts filesystems, and remounts root as read-only.
   - Powers off the CPU via `halt -p` or reboots.

### 2.2 The Service Directory Model
Every service in Void is defined as a directory containing an executable script named `run`:

```text
/etc/sv/isolated-sensor/
├── run           # The daemon launch script (must run in foreground)
├── finish        # Optional cleanup script executed after daemon exit
└── log/
    └── run       # Dedicated logging supervisor (svlogd pipe)
```

**Key Architectural Invariant:** Daemons under `runit` must **never fork into the background**. The `exec` syscall is used to replace the shell process with the target daemon binary, ensuring PID 1 / `runsv` maintains direct process ownership and signal delivery.

---

## 3. Musl Libc vs Glibc: Internals for Safety-Critical Systems

Void Linux provides native first-class tier-1 support for both `glibc` and `musl libc`. In defense and SCADA installations, `musl` is the preferred target:

| Architectural Metric | Glibc (GNU C Library) | Musl Libc | Critical Impact |
| :--- | :--- | :--- | :--- |
| **Binary Static Footprint** | ~2.5 MB minimum static base | **~40 KB minimum static base** | Vital for deeply embedded flash ROMs |
| **Memory Allocator** | Ptmalloc (complex, multi-arena) | **Mallocng (lightweight, hardened)** | Prevents heap exploitation & UAF reuse |
| **Thread Stack Size** | 2 MB to 8 MB default | **128 KB default (customizable)** | Massive density for multi-threaded RTUs |
| **NSS / Dynamic Modules** | Heavy `/etc/nsswitch.conf` dlopen | **Zero runtime dynamic loading** | Deterministic DNS/User lookup, no injection |
| **Standards Adherence** | GNU Extensions + POSIX | **Strict POSIX.1-2008 & ISO C99/C11** | Clean portability, zero undocumented behavior |

### Deep Dive: Thread Stack Determinism
In `glibc`, the default thread stack allocation is large (typically 8MB on x86_64), leading to virtual memory fragmentation in constrained embedded micro-servers. `musl` allocates small, tightly bound guard pages with predictable stack memory layouts, exposing hidden stack overflows early in development rather than intermittently in production.

---

## 4. Deterministic Packaging with XBPS

The **X Binary Package System (XBPS)** was designed from scratch in C99. Key internal design principles:
- **No Interpreted Dependencies:** Unlike RPM (often tied to Python) or APT (heavy C++ templates), XBPS is a compact, statically linkable C library (`libxbps`).
- **Cryptographic Merkle Signatures:** Every package archive (`.xbps`) contains an embedded RSA/SHA-256 signature block.
- **Transactional State Database:** Package metadata is stored in a structured property list format. Failed updates roll back cleanly without leaving half-configured state files.

```bash
# Verifying repository and package integrity in air-gapped environments:
xbps-pkgdb -a          # Complete filesystem verification against package database
xbps-query -R -p shlib # Inspect exact shared library dependencies
```

---

## 5. Defense Invariant: Read-Only Root & Volatile Memory Topology

For critical infrastructure deployment, Void Linux is paired with an immutable storage architecture:

```
[ PHYSICAL FLASH / SSD ] (Read-Only)
   └── /dev/sda2: Squashfs / Ext4 (mount -o ro)
          ├── /bin
          ├── /sbin
          └── /usr
                ▲
                │ (Upperdir Overlay)
[ VOLATILE RAM DRIVE ] (Tmpfs)
   └── /dev/shm: RAM-backed filesystem
          ├── /etc (overlay writeable delta)
          ├── /var/run
          └── /tmp
```

**Failure Mode Containment:** If an attacker compromises a user-space daemon or an unexpected power failure hits the substation, the underlying storage media is never modified. A hardware power-cycle guarantees 100% restoration to the clean, certified baseline image.

---
*Document status: STABLE · UNICAGD-Core Architecture Standard*
