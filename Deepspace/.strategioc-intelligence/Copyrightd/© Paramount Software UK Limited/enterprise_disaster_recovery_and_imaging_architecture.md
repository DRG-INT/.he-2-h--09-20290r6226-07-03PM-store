# Enterprise Disaster Recovery & Bare-Metal Imaging Architecture
Copyright: © Paramount Software UK Limited 2026 Macrium Reflect®
Source: Strategic Intelligence / UNICAGD-Core Critical Infrastructure Framework
Classification: USABLE (Enterprise & Defense Disaster Recovery Reference)

---

## 1. Strategic Role of Bare-Metal Imaging in Critical Infrastructure

In mission-critical, defense, and industrial control environments (SCADA/ICS, telemetry stations, electrical substations), recovery speed and data fidelity are paramount. Conventional file-by-file backup tools cannot restore an operating system that suffers from corrupted boot sectors, bricked kernel drivers, or storage controller failures.

**Bare-metal image-based recovery** captures the exact physical state of storage media—including partition tables (MBR/GPT), volume boot records (VBR), hidden OEM recovery partitions, system states, and block-level filesystem structures.

```
+───────────────────────────────────────────────────────────────────+
|               ENTERPRISE IMAGING ARCHITECTURAL STACK              |
+───────────────────────────────────────────────────────────────────+
|  [ MANAGEMENT & ORCHESTRATION ]                                   |
|  • Central Management Console (CMC) · Scripted API / PowerShell   |
+───────────────────────────────────────────────────────────────────+
|  [ VSS (VOLUME SHADOW COPY) COORDINATION LAYER ]                  |
|  • VSS Requestor (Macrium Engine)                                 |
|  • VSS Writers (SQL, Active Directory, Hyper-V consistency)       |
|  • VSS Kernel Provider (Point-in-time snapshot lock)              |
+───────────────────────────────────────────────────────────────────+
|  [ KERNEL FILTER DRIVERS ]                                        |
|  • Changed Block Tracker (CBT / mrcbt.sys)                        |
|  • Volume Snapshot Driver (mrfs.sys / mrxsmb.sys)                 |
+───────────────────────────────────────────────────────────────────+
|  [ STORAGE & NETWORK TARGETS ]                                    |
|  • AES-256 Encrypted Image (.mrimg / .mrbak) · Air-Gapped WORM    |
+───────────────────────────────────────────────────────────────────+
```

---

## 2. Kernel Filter Driver Architecture: Changed Block Tracking (CBT)

Traditional differential and incremental backups require mounting the filesystem and reading every file's metadata (MFT or directory entries) to identify changes, a process that can take hours on multi-terabyte drives.

### 2.1 The `mrcbt.sys` Driver Mechanism
Paramount Software's **Changed Block Tracker (CBT)** is an upper volume filter driver inserted directly into the Windows storage stack:
1. **Real-Time Sector Interception:** As write I/O Request Packets (IRPs) travel down the driver stack from the filesystem to the disk controller driver (`storport.sys`), `mrcbt.sys` intercepts the starting sector and sector count.
2. **In-Memory Tracking Bitmap:** Maintains a high-speed bitmask where each bit represents a block (typically 64 KB). Any modified sector sets the corresponding bit to 1.
3. **Instantaneous Delta Identification:** When an incremental backup is triggered, the backup engine queries `mrcbt.sys` via `DeviceIoControl()`. The bitmap is retrieved in milliseconds, reducing backup initiation time to near-zero.

---

## 3. Volume Shadow Copy Service (VSS) Point-in-Time Cohesion

Backing up an active system without locking the filesystem leads to crash-inconsistent states ("torn writes"). Macrium Reflect interacts with Microsoft VSS through a strict four-phase synchronization protocol:

```
                  ┌─────────────────────┐
                  │ 1. FREEZE PHASE     │ (Flush buffers, pause writes)
                  └──────────┬──────────┘
                             │ VSS Writers Flush Transaction Logs
                             ▼
                  ┌─────────────────────┐
                  │ 2. SNAPSHOT CREATION│ (COW redirect to diff area)
                  └──────────┬──────────┘
                             │ Snapshot Committed in Hardware/Kernel
                             ▼
                  ┌─────────────────────┐
                  │ 3. THAW PHASE       │ (Resume active disk writes)
                  └──────────┬──────────┘
                             │ Normal I/O Restored (< 10 ms)
                             ▼
                  ┌─────────────────────┐
                  │ 4. STREAM EXTRACTION│ (Engine reads frozen view)
                  └─────────────────────┘
```

**Result:** Backups are 100% application-consistent and transaction-safe without requiring services or VMs to stop.

---

## 4. Macrium ReDeploy: Hardware-Independent Disaster Recovery

When a critical substation server or military ruggedized PC experiences catastrophic motherboard, chipset, or storage controller failure, restoring an image directly to replacement hardware often results in a Blue Screen of Death (`INACCESSIBLE_BOOT_DEVICE` / Stop code `0x0000007B`).

### 4.1 ReDeploy Injection Protocol
**Macrium ReDeploy** operates inside the WinPE rescue environment:
1. **Offline Registry Hive Mounting:** Loads the offline `SYSTEM` registry hive (`C:\Windows\System32\config\SYSTEM`).
2. **Hardware ID Discovery:** Queries the replacement machine's PCI bus for new mass storage and AHCI/NVMe/RAID controllers.
3. **Driver Inf Injection & Critical Service Enablement:**
   - Injects the appropriate `.inf` / `.sys` controller drivers into `C:\Windows\System32\drivers`.
   - Modifies the offline registry to set the start type of the new controller drivers to `SERVICE_BOOT_START` (Value `0`).
   - Disables conflicting legacy IDE/SCSI drivers.
4. **Clean Boot Restoration:** The repaired system boots seamlessly on completely foreign silicon.

---

## 5. Air-Gapped Verification & Immutable Storage Defense

In defense and SCADA networks, backups must be safeguarded against adversarial ransomware that attempts to delete shadow copies or encrypt archives:
- **AES-256 Cryptographic Sealing:** Images are encrypted using AES-256 CBC or XTS algorithms with password and PKCS certificate validation.
- **Macrium Image Guardian (MIG):** A kernel driver (`mig.sys`) that blocks all unauthorized file writes, modifications, or deletions targeting `.mrimg` files on attached storage, allowing only the trusted, signed Macrium backup engine access.
- **Automated Virtual Verification:** Boot testing using Hyper-V or viBoot to prove within minutes that an image will successfully boot without human intervention.

---
*Document status: CERTIFIED ENTERPRISE BLUEPRINT · © Paramount Software UK Limited 2026*
