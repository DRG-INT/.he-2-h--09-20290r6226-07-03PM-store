# macOS XNU Kernel Architecture & Darwin Operating System Internals
Version: 1.0-stable
Source: UNICAGD-Core Systems Engineering / DRG-INT Defense Framework
Classification: USABLE (Operating Systems Architecture Reference)

---

## 1. The XNU Hybrid Architecture: Mach, BSD & I/O Kit

The macOS operating system kernel is called **XNU** (a recursive acronym for "X is Not Unix"). XNU is an engineering hybrid combining the message-passing flexibility of the **Mach 3.0 microkernel**, the mature POSIX compliance and networking of the **FreeBSD monolithic kernel**, and the object-oriented hardware abstraction of **I/O Kit**:

```
+───────────────────────────────────────────────────────────────────+
|               MACOS / DARWIN APPLICATION LAYER (RING-3)           |
|  • Cocoa / AppKit / SwiftUI · POSIX C Runtime (libSystem)         |
+─────────────────────────────────┬─────────────────────────────────+
                                  │ System Calls / Mach Traps
+─────────────────────────────────▼─────────────────────────────────+
|                     XNU HYBRID KERNEL (RING-0)                    |
+───────────────────────────────────────────────────────────────────+
|  [ BSD LAYER ]                                                    |
|  • POSIX Process Model (struct proc) · BSD Credentials & Auditing |
|  • VFS (Virtual File System) · BSD Sockets & Packet Filter (PF)   |
+───────────────────────────────────────────────────────────────────+
|  [ I/O KIT & DRIVERKIT ]                                          |
|  • Object-Oriented C++ Driver Framework · IORegistry Tree         |
|  • User-Space DriverKit (.dext) Boundary                          |
+───────────────────────────────────────────────────────────────────+
|  [ MACH 3.0 MICROKERNEL CORE ]                                    |
|  • Mach Tasks & Threads · Mach IPC (Ports & Messages)             |
|  • Virtual Memory (vm_map) · Real-Time Microkernel Scheduling     |
+───────────────────────────────────────────────────────────────────+
|  [ PLATFORM EXPERT / HARDWARE ABSTRACTION LAYER (HAL) ]           |
|  • ARM64 (Apple Silicon) / x86_64 Support                         |
+───────────────────────────────────────────────────────────────────+
```

---

## 2. Mach 3.0 Core Abstractions

At the lowest layer, XNU treats the operating system not in terms of traditional Unix processes, but through fundamental Mach primitives:

### 2.1 Tasks vs Threads
- **Mach Task:** A passive resource allocation container holding an address space (`vm_map`), a port namespace, and security credentials. A task performs no execution on its own.
- **Mach Thread:** The actual schedulable execution context. A single Mach task contains one or more threads.
- *Bridge to BSD:* A standard Unix process (`pid_t`) in XNU is implemented as a BSD process wrapper around an underlying Mach task.

### 2.2 Mach IPC: Ports, Messages & Rights
Inter-Process Communication in Mach is strictly message-based:
- **Mach Port:** A unidirectional, kernel-protected message queue referenced by integer handles.
- **Port Rights:**
  - `Receive Right:` Held by exactly one task that can read messages from the port.
  - `Send Right:` Held by tasks authorized to transmit messages into the port.
  - `Send-Once Right:` Single-use reply ticket for synchronous RPC exchanges.

```c
// Alacsony szintű Mach üzenetküldési minta
mach_msg_header_t msg;
msg.msgh_bits = MACH_MSGH_BITS(MACH_MSG_TYPE_COPY_SEND, 0);
msg.msgh_size = sizeof(msg);
msg.msgh_remote_port = target_service_port; // Send joggal felruházott port
msg.msgh_local_port = MACH_PORT_NULL;
msg.msgh_id = 0x1001; // Szolgáltatás metódus azonosító

// Kernel hívás: atomikus Mach üzenet átadás
mach_msg(&msg, MACH_SEND_MSG, sizeof(msg), 0, MACH_PORT_NULL,
         MACH_MSG_TIMEOUT_NONE, MACH_PORT_NULL);
```

---

## 3. I/O Kit: Object-Oriented C++ Driver Model

Unlike the monolithic C function-pointer structs of Linux (`struct file_operations`) or FreeBSD (`struct cdevsw`), macOS implements device drivers using a restricted subset of C++ known as **I/O Kit**:

### 3.1 Restricted C++ Environment (libkern)
To guarantee kernel stability, I/O Kit enforces:
- **No C++ RTTI (Run-Time Type Information):** Replaced by lightweight `OSMetaClass`.
- **No C++ Exceptions:** All memory allocation and initialization returns explicit error codes (`IOReturn`).
- **No Multiple Inheritance:** Strictly single inheritance rooted in `OSObject`.

### 3.2 The IORegistry Tree
Hardware devices and drivers are cataloged in a real-time, self-updating graph called the **IORegistry**, organized into multiple parallel planes:
1. **Service Plane:** Functional relationships (controllers -> buses -> devices).
2. **Power Plane:** Power management and sleep-state dependency graphs.
3. **Device Tree Plane:** Physical ACPI / Open Firmware hardware topology.

---

## 4. Modern macOS Security Architecture

macOS implements the most aggressive hardware-enforced security posture among mainstream commercial operating systems:

```
[ APFS Signed System Volume (SSV) ] (Read-Only Merkle Tree)
   │
   ▼ Verified via Hardware Root of Trust at Boot
[ Secure Enclave Processor (SEP) ] (Isolated Silicon)
   │
   ▼ Cryptographic Key Management & Biometrics
[ Pointer Authentication Codes (PAC) ] (Hardware ARM64e)
   │
   ▼ Cryptographic Signatures on Function Return Addresses
[ System Integrity Protection (SIP) & AMFI ] (Kernel Entitlements)
```

1. **Signed System Volume (SSV):**
   - The root filesystem (`/`) is an immutable, read-only APFS snapshot cryptographically sealed with a SHA-256 Merkle root tree hash signed by Apple.
   - Any physical tampering with system files causes the cryptographic seal to break, immediately halting the bootloader.
2. **Pointer Authentication (PAC / ARM64e):**
   - Cryptographically signs pointers in memory using CPU registers (`pacia`, `autia`).
   - Completely neutralizes Return-Oriented Programming (ROP) and Jump-Oriented Programming (JOP) kernel exploits.
3. **DriverKit (User-Space Drivers):**
   - Third-party drivers run in Ring-3 as isolated user-space daemon processes (`.dext`). If an Ethernet or USB driver crashes, the system survives without kernel panic.

---
*Document status: STABLE · UNICAGD-Core Architecture Standard*
