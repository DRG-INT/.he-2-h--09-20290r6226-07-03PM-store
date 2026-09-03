# Classic Mac OS 9.2.2 System Architecture & PowerPC Nanokernel Internals
Version: 1.0-stable (Final Classic Architecture)
Source: UNICAGD-Core Systems Engineering / DRG-INT Defense Framework
Classification: USABLE (Operating Systems Architecture Reference)

---

## 1. Historical Architecture Overview: The 1984–2001 Heritage

Classic Mac OS (culminating in version **9.2.2**, released in December 2001) represents one of the most distinctive operating system architectures in computing history. Designed originally in 1984 for the Motorola 68000 CPU with 128 KB of RAM, it evolved over nearly two decades into a PowerPC multiprocessor-capable system while maintaining binary backwards compatibility with early 68k software.

```
+───────────────────────────────────────────────────────────────────+
|               CLASSIC MAC OS 9.2.2 SUBSYSTEM TOPOLOGY             |
+───────────────────────────────────────────────────────────────────+
|  [ APPLICATION LAYER ]                                            |
|  • Carbon Apps · 68k Legacy Binaries · PowerPC CFM Shared Libs    |
+───────────────────────────────────────────────────────────────────+
|  [ MACINTOSH TOOLBOX & USER INTERFACE ]                           |
|  • Event Manager (WaitNextEvent) · Window / Menu / Dialog Mgr     |
|  • QuickDraw (2D Vector Graphics Core) · Appearance Manager       |
+───────────────────────────────────────────────────────────────────+
|  [ OPERATING SYSTEM CORE (No MMU Protection) ]                    |
|  • Memory Manager (Master Pointers & Handles) · Process Manager   |
|  • File Manager (HFS / HFS+ B-Trees) · Open Transport (Networking)|
+───────────────────────────────────────────────────────────────────+
|  [ POWERPC NANOKERNEL & 68k EMULATION CORE ]                      |
|  • Mixed Mode Manager (PowerPC <-> 68k Thunking) · Nanokernel     |
+───────────────────────────────────────────────────────────────────+
|  [ HARDWARE / OPEN FIRMWARE ] (PowerPC G3, G4, PCI, SCSI)         |
+───────────────────────────────────────────────────────────────────+
```

---

## 2. The PowerPC Nanokernel & The Mixed Mode Manager

When Apple transitioned from Motorola 680x0 processors to the PowerPC architecture in 1994, rewriting the millions of lines of 68k assembly in the operating system overnight was impossible.

### 2.1 The Nanokernel
On PowerPC hardware, Mac OS 9 does not boot a standard monolithic kernel. Instead, a lightweight **Nanokernel** boots directly from Open Firmware:
- Handles low-level CPU interrupt dispatching and hardware context switching.
- Implements basic preemptive threads used by internal device drivers (Multi-Processing API).
- Runs the **68LC040 Dynamic Recompiler (Emulator)** as a top-priority task.

### 2.2 The Mixed Mode Manager
To allow native PowerPC code to transparently call 68k code and vice versa, Apple engineered the **Mixed Mode Manager**:
- **Routine Descriptors:** Data structures describing whether a function is 68k or native PowerPC, its calling convention, and its parameter types.
- **Transition Vectors:** When native PowerPC code calls a legacy 68k Toolbox routine, the CPU saves PowerPC registers, transitions into the emulator, executes the 68k trap, and returns the result back to PowerPC.

---

## 3. Cooperative Scheduling & Lack of Memory Protection

### 3.1 The Cooperative Process Model
Classic Mac OS user-space applications are strictly cooperative:
- The **Process Manager** schedules applications based on an event-driven model.
- Each application runs an internal event loop revolving around `WaitNextEvent()`:
```c
// Klasszikus Mac OS eseményhurok
EventRecord event;
while (!gQuitFlag) {
    if (WaitNextEvent(everyEvent, &event, sleepTicks, NULL)) {
        switch (event.what) {
            case mouseDown:
                HandleMouseDown(&event);
                break;
            case keyDown:
                HandleKeyDown(&event);
                break;
        }
    }
    // Az alkalmazás CSAK a WaitNextEvent() meghívásakor adja át a vezérlést
    // a Process Managernek a többi alkalmazás számára!
}
```
**Architectural Consequence:** If an application enters an infinite loop without calling `WaitNextEvent()`, the entire computer freezes. The cursor may still move (handled via hardware interrupt), but all other applications and background networking halt.

### 3.2 Flat Memory Model Without Protection
Although PowerPC processors featured sophisticated Memory Management Units (MMUs), Classic Mac OS operated with **paging disabled or running in flat physical translation**:
- Applications could read and write anywhere in physical RAM, including the System Zone, interrupt vectors, and other running applications' heaps.
- This allowed blazing-fast inter-application communication, but meant that a single wild pointer instantly corrupted operating system structures, precipitating a "Bomb" error.

---

## 4. The Macintosh Memory Manager: Pointers vs Handles

Because early Macs lacked an MMU, physical memory fragmentation was fatal. The original Macintosh engineers solved memory relocation using **Handles**:

```
[ APPLICATION VARIABLE ]
          │
          ▼
   Handle (Ptr*) ───► [ MASTER POINTER ] (Fixed, Non-Relocatable Table Entry)
                             │
                             ▼
                      [ MEMORY BLOCK ] (Can be moved during compaction)
```

1. **Pointers (`Ptr`):** Direct memory addresses pointing to non-relocatable blocks. Excessive pointer allocation caused fragmentation ("islands" in the heap).
2. **Handles (`Handle`):** Pointers to Master Pointers. When the Memory Manager needs to allocate memory and lacks contiguous space, it performs **Heap Compaction**: it slides relocatable blocks across memory and updates the single Master Pointer. The application's `Handle` remains valid!
3. **Locking Invariant:** If an application dereferences a handle to work with raw bytes, it must explicitly invoke `HLock(handle)` to prevent the Memory Manager from moving the block during compaction, followed by `HUnlock(handle)`.

---

## 5. HFS & HFS+ File System Internals

Mac OS 9.2.2 popularized the **Hierarchical File System Plus (HFS+)**, characterized by:
- **Dual-Fork File Model:**
  - **Data Fork:** Unstructured byte stream (equivalent to a standard Unix file).
  - **Resource Fork:** Structured binary database containing compiled icons, dialog layouts, string tables, and executable code (`CODE` resources).
- **Balanced B-Tree Catalog:** Metadata (file names, directory hierarchies, permissions) is stored in a dynamically balancing B-Tree (`Catalog File`), providing instantaneous file lookup regardless of directory depth.

---

## 6. The Bridge to the Future: Carbon & The Classic Environment

To ease developer migration to Mac OS X, Apple introduced the **Carbon API**:
- A cleaned-up subset of the Macintosh Toolbox APIs that eliminated direct struct member access (forcing accessor functions).
- Allowed a single binary executable to run natively on both Classic Mac OS 9.2.2 and modern Mac OS X.
- In early OS X (10.0 Cheetah through 10.4 Tiger), Mac OS 9.2.2 served as the engine of the **Classic Environment**, running inside an isolated Mach task.

---
*Document status: STABLE · UNICAGD-Core Architecture Standard*
