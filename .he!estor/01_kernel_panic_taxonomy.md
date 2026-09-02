# Kernel Panic Taxonomy - Operational Field Guide
Version: 1.0-stable
Classification: USABLE

## 1. Panic Vectors (What actually kills the kernel)

| Vector | Root Cause | Detection | Recovery |
|--------|-----------|-----------|----------|
| NULL deref | Bad pointer, missing bounds check | OOPS dump, stack trace | kexec/kdump, NMI watchdog |
| Stack overflow | Deep recursion, IRQ storm | Stack canary failure | Boot with `irqpoll` |
| BUG_ON trigger | Invariant violation | Immediate halt | Boot parameter `panic=N` |
| OOM killer panic | Memory pressure + !__GFP_FS | dmesg tail | `vm.overcommit_memory` tuning |
| Hardware exception | MCE, ECC, PCIe AER | EDAC logs, mcelog | RAS injection, CMC handler |
| Spinlock deadlock | IRQ context + preempt | lockdep splat | lockdep boot flag |
| RCU stall | CPU stuck in kernel | rcu_cpu_stall_warn | rcu_cpu_stall_timeout |
| TLB shootdown | IPI timeout | IPI send failed | smp_call_function timeout |

## 2. Panic vs Oops vs BUG

- **BUG()**: Compile-time / assert-time halt. Kernel intentionally stops. Traceback available.
- **Oops**: Non-fatal exception. Kernel may continue in degraded mode. `panic_on_oops=1` makes it fatal.
- **Panic**: Fatal. `panic()` called explicitly. `panic_timeout` controls auto-reboot.

**Key insight**: The boundary between oops and panic is `panic_on_oops`. Most production kernels set this to 0 (continue) or 1 (halt) with kdump.

## 3. Practical: Reading a Panic Dump

```
[    0.000000] Booting Linux on physical CPU 0x0
[    0.000000] Linux version 5.15.0-78-generic
[    0.000000] Command line: BOOT_IMAGE=/vmlinuz...
[    0.000000] KERNEL supported:
[    0.000000] CPU: U4200 @ 2.4GHz
[    0.000000] Memory: 4096MB = 4096MB available
[   12.345678] BUG: unable to handle kernel NULL pointer dereference
[   12.345689] IP: ffffffff810a3b2a [ext4_find_entry+0x3a/0x1f0]
[   12.345690] PGD 0 P4D 0 
[   12.345691] Oops: 0002 [#1] SMP NOPTI
[   12.345692] CPU: 0 PID: 1234 Comm: myprocess Tainted: G
[   12.345693] RIP: 0010:ext4_find_entry+0x3a/0x1f0
[   12.345694] RSP: 0018:ffffc90001ab3d88 EFLAGS: 00010246
[   12.345695] RAX: 0000000000000000 RBX: ffff88801a1b8000
[   12.345696] RCX: 0000000000000000 RDX: 0000000000000001
[   12.345697] RSI: ffff88801a1b8000 RDI: ffff88801a1b8000
[   12.345698] RBP: ffffc90001ab3de0 R8: 0000000000000000
[   12.345699] R9: ffff88801a1b8000 R10: 0000000000000000
[   12.345700] R11: 0000000000000000 R12: ffff88801a1b8000
[   12.345701] R13: ffff88801a1b8000 R14: ffffc90001ab3e80
[   12.345702] R15: ffffc90001ab3e90
[   12.345703] FS:  0000000000000000(0000) GS:ffff888039800000(0000)
[   12.345704] knlGS:0000000000000000
[   12.345705] CS:  0010 DS: 0000 ES: 0000 CR0: 0000000080050033
[   12.345706] CR2: 0000000000000000 CR3: 0000000001a0a000 CR4: 00000000000006f0
[   12.345707] Call Trace:
[   12.345708]  ext4_lookup+0x8a/0x1b0
[   12.345709]  __lookup_hash+0x25/0x40
[   12.345710]  lookup_fast+0xa5/0x150
[   12.345711]  walk_component+0x11b/0x290
[   12.345712]  path_lookupat+0x6e/0x140
[   12.345713]  filename_lookup+0x6e/0x140
[   12.345714]  vfs_statx+0x7d/0x140
[   12.345715]  __do_sys_newstat+0x34/0x50
[   12.345716]  do_syscall_64+0x3e/0x90
[   12.345717]  entry_SYSCALL_64_after_hwframe+0x61/0xc6
[   12.345718] RIP: 0033:0x7f3a4c5b1e7a
[   12.345719] RSP: 002b:00007ffd9a1b3d80 EFLAGS: 00000246
[   12.345720] RAX: 0000000000000401 RBX: 0000000000000000
[   12.345721] RCX: 0000000000000000 RDX: 0000000000000000
[   12.345722] RSI: 00007ffd9a1b3e80 RDI: 0000000000000000
[   12.345723] RBP: 00007ffd9a1b3e80 R8: 00007ffd9a1b3f00
[   12.345724] R9: 00007f3a4c5b1e7a R10: 0000000000000000
[   12.345725] R11: 0000000000000246 R12: 0000000000000000
[   12.345726] R13: 0000000000000000 R14: 00007ffd9a1b3f00
[   12.345727] R15: 0000000000000000
[   12.345728] Modules linked in: ext4(O) crc32c_generic
```

**Quick diagnosis:**
- `BUG: unable to handle kernel NULL pointer dereference` = classic NULL deref
- `IP: ffffffff810a3b2a` = instruction pointer (kernel space)
- `CR2: 0000000000000000` = faulting address (NULL confirmed)
- `ext4_find_entry+0x3a/0x1f0` = corrupt inode or journal replay issue
- `PID: 1234 Comm: myprocess` = user-space process triggered it

## 4. Alternative Stability Models

### 4.1 seL4 (Formal Verification)
- Proof: CAmkES component isolation
- Kernel panic? Impossible by construction (proof assistant verified)
- Cost: 1 developer-year ≈ 1 verified LOC (very slow to write)
- Use case: Defense, medical, aerospace (where failure is not an option)

### 4.2 Minix 3 (Self-healing Microkernel)
- Drivers run in user space
- Driver crash → re-executed by reincarnation server
- Panic? System continues, driver restarts
- Cost: Higher IPC overhead, complex driver model

### 4.3 Unikernel (Single Address Space)
- No userspace/kernel split
- One process, one address space
- Panic? VM snapshot + rollback (oracles like MirageOS)
- Cost: No shell, no dynamic loading, single app per VM

### 4.4 Exokernel (Application-Specific Resource Management)
- Kernel exposes raw hardware
- Application manages its own page tables, TLB
- Panic? Application bug = application crash, kernel stays alive
- Cost: Library OS (LibOS) complexity per app

## 5. Host File + Binary Store + Driver Model (Your Proposed Architecture)

```
┌─────────────────────────────────────────────────────────────┐
│  User Space: Application (static binary blob)               │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │ Binary Store │    │  Host File  │    │  Binary DB  │     │
│  │ (LMDB/SQLite)│    │ (/etc/hosts)│    │ (driver map)│     │
│  └──────┬──────┘    └──────┬──────┘    └──────┬──────┘     │
│         │                  │                  │             │
│  ┌──────▼──────────────────▼──────────────────▼──────┐     │
│  │           Userspace Driver (VFIO/io_uring)         │     │
│  └──────────────────────────┬────────────────────────┘     │
│                             │ Capability Passed (FD)         │
├─────────────────────────────┼───────────────────────────────┤
│  Kernel (minimal):           │                               │
│  ┌──────────────────────────▼────────┐                      │
│  │  Only: interrupt routing, basic    │                      │
│  │  scheduler, memory protection (if any)│                   │
│  └───────────────────────────────────┘                      │
└─────────────────────────────────────────────────────────────┘
```

**Attack surface reduction:**
- No system call table (no syscalls except 3-5)
- No network stack (userspace handles via io_uring)
- No filesystem VFS (binary store is the FS)
- No dynamic module loading
- No BPF JIT (or BPF at all)
- No kernel-side scripting (no eBPF, no IOMMU bypass)

**Threat model:**
- If userspace driver is compromised: attacker gets raw hardware access, but kernel is isolated by MMU
- If binary store is corrupted: integrity check via Merkle tree at boot
- If host file is poisoned: no DNS resolution, app fails closed (no fallback)

## 6. Anti-Cheat: Why Knowing All Entry Points Is Not Enough

### 6.1 The Trusted Computing Base (TCB) Problem

Even if you audit every kernel entry point, the TCB includes:
1. **Microcode** (CPU itself)
2. **Firmware** (BIOS/UEFI, SMM, ME, PSP)
3. **DMA-capable devices** (GPU, NIC, storage controller)
4. **Memory controller** (rowhammer, SPD)
5. **Thermal/power management** (throttling, DVFS)

**Example:** Spectre/Meltdown bypassed kernel isolation entirely via CPU speculation. No entry point was needed.

### 6.2 Kernel Knowledge is Asymmetric

- **Defender** must protect 100% of the attack surface
- **Attacker** needs 1 exploit + 1 bypass
- Kernel source is open. Attacker reads it freely.
- Defender must patch before weaponization.

### 6.3 The Behavioral Gap

Kernel sees: `mmap(addr, PROT_EXEC)` → allows
Kernel does NOT see: "this is game code vs cheat code"

**Solution space (not foolproof):**
- Hardware-enforced memory tagging (ARM MTE, Intel SDL)
- Hypervisor-based introspection (KVM, Xen)
- Time-based attestation (Intel TDX, AMD SEV-SNP)
- Side-channel resistance (cache flushing, constant-time)

### 6.4 Your "Pattern Language" Approach

If you know the patterns (not the assembly), you can:
- Detect anomalous control flow graphs
- Identify hidden modules via entropy + section analysis
- Map behavioral signatures (not signature matching)

But: **adversarial ML** can mutate patterns to evade detection. The game is eternal.

## 7. Kernel Stability Engineering (Practical Rules)

1. **Minimize panic() calls** - only for unrecoverable invariant violations
2. **Use WARN_ON_ONCE()** for recoverable issues with logging
3. **Lockdep must pass** - every spinlock, mutex, rwlock verified
4. **Structured unwinding in error paths** - use canonical kernel `goto err_*` unwinding or modern `__cleanup` helpers
5. **Memory allocations must have fallbacks** - GFP_ATOMIC or fail gracefully
6. **No blocking in interrupt context** - IRQ handlers must be fast
7. **RCU grace periods bounded** - no infinite call_rcu() chains
8. **No unbounded loops in scheduler** - preemption checks mandatory

## 8. Transferable Knowledge for 9-Language Study

| Language | Kernel-Relevant Concept | School Architecture Analogy |
|----------|------------------------|----------------------------|
| C | Memory layout, struct packing, function pointers | Foundation (concrete) |
| Assembly | Calling conventions, stack frames, interrupts | Blueprint (low-level) |
| Rust | Ownership, lifetimes, unsafe blocks | Structural integrity (verifiable) |
| Python | Dynamic dispatch, GIL, coroutines | Scheduling (high-level) |
| Go | Goroutines, channels, GC tuning | Multi-tenancy (lightweight) |
| Zig | Comptime, allocator config, no hidden control flow | Explicit construction |
| Haskell | Pure functions, ST monad, immutability | Formal proof (ideal) |
| Lisp | Macros, homoiconicity, REPL | Metaprogramming (self-modifying) |
| Prolog | Logic programming, unification, backtracking | Policy engine (declarative) |

**Key insight**: The kernel is just a very efficient, very unsafe, very real-time Prolog interpreter with side effects and no GC. If you understand logic programming, you understand scheduling.

## 9. Immediate Action Items (Next 48 Hours)

1. Boot a Linux kernel with `debugfs` mounted
2. Read `/proc/kallsyms` and `/proc/modules`
3. Trigger a controlled Oops: `echo c > /proc/sysrq-trigger` (in VM only!)
4. Analyze the crash dump with `crash` utility or `gdb` vmlinux
5. Map syscall table: `cat /proc/kallsyms | grep sys_call_table`
6. Read `Documentation/admin-guide/sysrq.rst` from kernel source
7. Write a null kernel module (no-op) and insmod/rmmod it
8. Check `dmesg` for module load/unload messages

---

*Document status: STABLE. No half-measures. No assumptions without proof.*
