# The Driver Architect: Universal Device Driver Paradigms & Patterns
Version: 1.0-stable
Source: UNICAGD-Core Systems Engineering / DRG-INT Defense Framework
Classification: USABLE (Critical Infrastructure Technical Reference)

---

## 1. The Architectural Role of the Device Driver

Device drivers bridge the gap between abstract operating system primitives (files, sockets, block devices) and asynchronous, untrusted physical hardware. In high-reliability and critical infrastructure systems, driver architecture determines overall system survivability: over **70% of production kernel crashes** originate in driver-space due to memory corruption, improper synchronization, or hardware race conditions.

```
+───────────────────────────────────────────────────────────────────+
|               DEVICE DRIVER PARADIGM COMPARISON                   |
+───────────────────────────────────────────────────────────────────+
|  MONOLITHIC KERNEL (Linux / FreeBSD)                              |
|  • Driver runs in Ring-0 supervisor space                         |
|  • Direct MMIO & Physical DMA access                              |
|  • Single fault -> Fatal Panic / Oops / Kernel Crash              |
+───────────────────────────────────────────────────────────────────+
|  HYBRID KERNEL (Windows NT WDF)                                   |
|  • KMDF (Kernel-Mode Driver Framework, Ring-0)                    |
|  • UMDF (User-Mode Driver Framework, Ring-3, isolated crash)      |
|  • Standardized IRP (I/O Request Packet) packet switching         |
+───────────────────────────────────────────────────────────────────+
|  CAPABILITY MICROKERNEL (Genode / seL4)                           |
|  • 100% of drivers reside in Ring-3 isolated address spaces       |
|  • Hardware access strictly mediated via IOMMU capability pages   |
|  • Driver fault -> Zero kernel impact; driver restarts in microsec|
+───────────────────────────────────────────────────────────────────+
```

---

## 2. Universal Driver Lifecycle State Machine

Regardless of the host operating system, every production driver adheres to a canonical lifecycle state machine:

```
                  ┌───────────────────┐
                  │ 1. INITIALIZATION │ (Module Load / OS Boot)
                  └─────────┬─────────┘
                            │ Register Bus Driver
                            ▼
                  ┌───────────────────┐
                  │     2. PROBE      │ (Match Vendor/Device ID)
                  └─────────┬─────────┘
                            │ Match Success
                            ▼
                  ┌───────────────────┐
                  │     3. ATTACH     │ (Allocate MMIO, IRQ, DMA)
                  └─────────┬─────────┘
                            │
               ┌────────────┴────────────┐
               ▼                         ▼
     ┌───────────────────┐     ┌───────────────────┐
     │ 4. ACTIVE RUNTIME │ ◄───┤    5. SUSPEND     │ (Power Mgt / PM)
     │ (Handle I/O & IRQ)│ ───►│ (Drain DMA/Sleep) │
     └─────────┬─────────┘     └───────────────────┘
               │ Device Removal / System Teardown
               ▼
     ┌───────────────────┐
     │    6. DETACH      │ (Release IRQs, Free Buffers, Unmap BAR)
     └───────────────────┘
```

---

## 3. Hardware Communication: MMIO, Port I/O & BARs

Hardware devices expose internal control registers through two primary mechanisms:

### 3.1 Port-Mapped I/O (PMIO / x86 In/Out)
- Legacy x86 mechanism (`inb`, `outb` instructions).
- Separate 16-bit I/O address space (0x0000 - 0xFFFF).
- Non-cacheable, strictly synchronized, low performance.

### 3.2 Memory-Mapped I/O (MMIO & PCI BARs)
- Contemporary high-speed standard.
- Hardware registers are mapped directly into the physical address space of the processor via **Base Address Registers (BARs)** in the PCI configuration header.
- Handled by the CPU as memory loads and stores (`readl()`, `writel()` in Linux; `bus_space_read_4()` in FreeBSD).

```c
// Linux Kernel MMIO leképezési minta
void __iomem *reg_base;
resource_size_t mmio_start = pci_resource_start(pdev, 0);
resource_size_t mmio_len = pci_resource_len(pdev, 0);

// Virtuális lapozás leképezése nem-gyorsítótárazott (uncached) módban
reg_base = ioremap(mmio_start, mmio_len);

// Regiszter írása szigorú memóriakorláttal
writel(HARDWARE_RESET_CMD, reg_base + REG_CONTROL);
```

---

## 4. DMA Architectures: Coherent vs Streaming & Scatter-Gather

Direct Memory Access (DMA) allows hardware controllers to transfer data directly to and from system RAM without CPU intervention.

```
+───────────────────+                    +───────────────────+
|   CPU & CACHES    |                    |  PHYSICAL MEMORY  |
|  (L1/L2/L3 Cache) |                    |       (RAM)       |
+─────────┬─────────+                    +─────────┬─────────+
          │ Cache Flush / Invalidate               │
          ▼                                        ▼
    [ CACHE COHERENCE ENGINE / MEMORY CONTROLLER BUS ]
                           ▲
                           │ Direct Bus Read / Write
                  +────────┴────────+
                  |  PCIe DEVICE /  |
                  |   DMA ENGINE    |
                  +─────────────────+
```

### 4.1 Coherent (Consistent) DMA
- Memory region is guaranteed to be coherent between CPU caches and the device.
- Allocated via `dma_alloc_coherent()`.
- Used for persistent, bi-directional control structures (ring buffer descriptors, command queues).

### 4.2 Streaming DMA & Scatter-Gather (SG)
- Used for ephemeral, large-scale data transfers (packet buffers, disk blocks).
- Allocated from standard page memory, then explicitly mapped via `dma_map_single()` or `dma_map_sg()`.
- **Cache Synchronization Invariant:**
  - Before device write: `dma_sync_single_for_device()` (flushes CPU cache).
  - Before CPU read: `dma_sync_single_for_cpu()` (invalidates CPU cache).
- **Scatter-Gather:** Allows chaining discontiguous physical memory pages into a single hardware transaction via linked descriptors.

---

## 5. Modern Interrupt Handling: MSI-X and Lockless Ring Buffers

### 5.1 The Evolution: Pin IRQ -> MSI -> MSI-X
1. **Legacy Pin IRQs (INTA-INTD):** Shared physical lines, high latency, interrupt storms on shared PCI buses.
2. **MSI (Message Signaled Interrupts):** Device writes a specific 32-bit DWORD to a memory address (`0xFEE00000` on x86). No physical pin required; up to 32 vectors per device.
3. **MSI-X (Extended MSI):** Up to 2,048 independent vectors. Crucial for multi-core scaling: each CPU core is assigned an independent queue and interrupt line, eliminating cross-core lock contention.

### 5.2 Lockless Single-Producer Single-Consumer (SPSC) Ring Buffer
Critical sensor pipelines and telemetry drivers must avoid spinlocks in the interrupt path:

```c
struct spsc_ring {
    uint32_t head; // Csak a Producer (Hardware IRQ) módosítja
    uint32_t tail; // Csak a Consumer (Kernel Worker) módosítja
    uint32_t size;
    struct telemetry_sample buffer[RING_SIZE];
};

// Producer (IRQ handler)
void ring_enqueue(struct spsc_ring *r, struct telemetry_sample data) {
    uint32_t current_head = r->head;
    uint32_t next_head = (current_head + 1) & (r->size - 1);
    
    if (next_head != smp_load_acquire(&r->tail)) {
        r->buffer[current_head] = data;
        smp_store_release(&r->head, next_head); // Memóriakorlát
    }
}
```

---
*Document status: STABLE · UNICAGD-Core Architecture Standard*
