# Hardware Root of Trust and Physical Watchdog Engineering
Version: 1.0-stable
Source: UNICAGD-Core Systems Engineering / DRG-INT Defense Framework
Classification: USABLE (Critical Infrastructure Technical Reference)

---

## 1. The Physical Substrate of Trust

In hostile electronic environments and critical infrastructure (substations, air-defense radar stations, remote SCADA RTUs), software-based security guarantees are insufficient. If the underlying hardware or firmware is compromised, all higher-level security assertions (cryptographic hashes, LSMs, sandboxes) collapse.

```
+───────────────────────────────────────────────────────────────────+
|               HARDWARE ROOT OF TRUST (RoT) LAYERS                 |
+───────────────────────────────────────────────────────────────────+
|  LEVEL 4: APPLICATION OS RUNTIME                                  |
|  • Kernel Integrity / eBPF / Seccomp BPF                          |
+───────────────────────────────────────────────────────────────────+
|  LEVEL 3: MEASURED BOOT & KERNEL VERIFICATION                     |
|  • TPM 2.0 PCR Validation · dm-verity Merkle Tree Verification    |
+───────────────────────────────────────────────────────────────────+
|  LEVEL 2: FIRMWARE & SECURE BOOT CHAIN                            |
|  • UEFI / Coreboot Signed Bootloader · Hardware Keys in ROM       |
+───────────────────────────────────────────────────────────────────+
|  LEVEL 1: PHYSICAL HARDWARE ROOT OF TRUST                         |
|  • Hardware Security Module (HSM) · Discrete TPM 2.0 (SPI/I2C)    |
|  • External Watchdog IC (Physical Timer) · Tamper-Zeroization Wire|
+───────────────────────────────────────────────────────────────────+
```

---

## 2. TPM 2.0: Architecture, PCRs & Measured Boot

The **Trusted Platform Module (TPM 2.0)** is a dedicated, tamper-resistant cryptographic coprocessor connected via SPI or I2C.

### 2.1 Platform Configuration Registers (PCRs)
PCRs are 256-bit registers that can never be overwritten directly. They can only be **extended** using cryptographic hashes:
$$\text{PCR}_{\text{new}} = \text{SHA256}(\text{PCR}_{\text{old}} \parallel \text{Measurement})$$

| PCR Index | Measured Component | Critical Defense Role |
| :--- | :--- | :--- |
| **PCR 0 - 3** | UEFI Firmware, ROM code, CPU Microcode | Detects firmware rootkits and SMM implants |
| **PCR 4** | Bootloader (GRUB, systemd-boot) | Guarantees bootloader binary has not been modified |
| **PCR 5** | GPT Partition Table, Boot Configuration | Prevents physical disk substitution |
| **PCR 8 - 9** | Kernel Command Line & Kernel Binary (`vmlinuz`) | Validates kernel boot parameters (e.g. `nokaslr` tampering) |
| **PCR 10** | Initramfs Image (`initrd.img`) | Protects early user-space and storage drivers |
| **PCR 15** | Defense Enclave Runtime Policy | Protects local air-gapped security state |

### 2.2 Key Sealing & Unsealing
Disk encryption keys (e.g., LUKS master key or GELI passphrase) are sealed inside the TPM. The TPM will only release the key if and only if **the current PCR values exactly match the certified platform baseline**:

```bash
# Titkosítási kulcs lepecsételése a PCR 0, 2, 7 állapotokhoz kötve (tpm2-tools):
tpm2_createprimary -C o -g sha256 -G rsa -c primary.ctx
tpm2_pcrread "sha256:0,2,7" -o pcr_digest.bin
tpm2_create -C primary.ctx -u key.pub -r key.priv -L pcr_policy.bin -i raw_secret.bin

# Feloldás a boot során (csak tiszta, nem módosított rendszeren sikeres):
tpm2_unseal -c key.ctx -p pcr:sha256:0,2,7
```

---

## 3. Physical Hardware Watchdogs (WDT)

A software hang, kernel deadlock, or memory latchup caused by radiation / EMP cannot be resolved by software. A physical **Watchdog Timer (WDT)** is required.

### 3.1 External Discrete Watchdog ICs vs Internal SoC Timers
- **SoC Internal Watchdogs:** Susceptible to internal power rail failures and clock tree halts.
- **Discrete External Watchdogs (e.g., Texas Instruments TPS3823, Maxim MAX6369):** Independent silicon chips wired to the CPU reset line with physical capacitors determining the timeout period.

```
┌─────────────────────────┐                   ┌─────────────────────────┐
│     CPU / CONTROLLER    │                   │   DISCRETE WATCHDOG IC  │
│                         │   Strobe / Kick   │   (e.g., TI TPS3823)    │
│  GPIO Pin / /dev/watchdog ──────────────────► WDI (Input Pin)         │
│                         │   (Periodic Pulse)│                         │
│                         │                   │   Internal RC Timer:    │
│                         │   Hardware Reset  │   Timeout = 1.6 seconds │
│  RESET# Line (Active Low) ◄────────────────── RESET Pin               │
└─────────────────────────┘                   └─────────────────────────┘
```

### 3.2 The Linux `/dev/watchdog` Protocol
The kernel exposes the watchdog via an ioctl-driven character device:
- The user-space daemon opens `/dev/watchdog`.
- The daemon must periodically write a byte (`\0`) or issue `WDIOC_KEEPALIVE` every $N$ seconds.
- **The Magic Close Invariant:** If the daemon crashes, the device file is closed abruptly. The kernel detects the absence of the "magic character" (`V`) and refuses to disable the timer, forcing a physical hardware reboot.

```c
#include <linux/watchdog.h>
#include <fcntl.h>
#include <unistd.h>

void watchdog_loop(void) {
    int wdt_fd = open("/dev/watchdog", O_WRONLY);
    int timeout = 10; // 10 másodperces időzítés

    ioctl(wdt_fd, WDIOC_SETTIMEOUT, &timeout);

    while (system_healthy()) {
        // Időzítő "rugdosása" (strobe / heartbeat)
        ioctl(wdt_fd, WDIOC_KEEPALIVE, 0);
        sleep(2);
    }

    // Ha a rendszer integritása sérül, nem küldünk heartbeat-et:
    // A hardveres watchdog 10 másodpercen belül fizikailag újraindítja a gépet.
}
```

---

## 4. Fail-Safe vs Fail-Secure in Critical Systems

In military and critical infrastructure engineering, system halts are governed by two distinct philosophies:

1. **Fail-Safe (Életvédelmi Elv):**
   - In transportation and nuclear cooling: upon failure, valves open, signals turn red, and power shuts down to prevent physical catastrophe.
2. **Fail-Secure (Biztonsági Elv):**
   - In cryptosystems and defense perimeters: upon physical tampering or memory compromise, zeroization circuits discharge capacitors to wipe cryptographic keys from RAM, and communication interfaces permanently lock down.

---
*Document status: STABLE · UNICAGD-Core Architecture Standard*
