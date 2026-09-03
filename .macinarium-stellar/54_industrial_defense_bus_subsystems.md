# Industrial & Defense Hardware Bus Subsystems
Version: 1.0-stable
Source: UNICAGD-Core Systems Engineering / DRG-INT Defense Framework
Classification: USABLE (Critical Infrastructure Technical Reference)

---

## 1. The Critical Hardware Bus Hierarchy

In mission-critical, defense, and industrial automation platforms (SCADA, avionics, armored vehicles, electrical grid substations), standard consumer communication buses (USB, Bluetooth, Wi-Fi) are prohibited due to non-deterministic latencies, lack of galvanic isolation, and vulnerability to electromagnetic pulse (EMP) interference.

```
+───────────────────────────────────────────────────────────────────+
|                  DEFENSE & INDUSTRIAL BUS TOPOLOGY                |
+───────────────────────────────────────────────────────────────────+
|  AEROSPACE & COMBAT PLATFORMS   |  FIELD & EMBEDDED AUTOMATION    |
|  • MIL-STD-1553B (Command/Resp) |  • CAN / CAN-FD (Vehicle RTUs)  |
|  • ARINC 429 (Avionics Simplex) |  • RS-485 / Modbus (Substations)|
+─────────────────────────────────┴─────────────────────────────────+
|  HIGH-SPEED COMPUTE & RADAR SENSORS                               |
|  • PCI Express (PCIe Gen3-Gen5): High-throughput DMA / FPGA       |
+───────────────────────────────────────────────────────────────────+
```

---

## 2. MIL-STD-1553B: Dual-Redundant Avionics & Defense Bus

Published by the United States Department of Defense, MIL-STD-1553B is the global benchmark for flight control, weapons integration, and mission computers.

```
                   PRIMARY BUS A (Shielded Twisted Pair, 78 Ohm)
═════════════════════════════════════════════════════════════════════════
   │                   │                   │                   │
┌──┴──┐             ┌──┴──┐             ┌──┴──┐             ┌──┴──┐
│ BC  │             │ RT1 │             │ RT2 │             │ BM  │
│(Bus │             │(Sens│             │(Actu│             │(Bus │
│Ctrl)│             │ or) │             │ator)│             │ Mon)│
└──┬──┘             └──┬──┘             └──┬──┘             └──┬──┘
   │                   │                   │                   │
═════════════════════════════════════════════════════════════════════════
                  SECONDARY BUS B (Hot Standby Redundant)
```

### 2.1 Technical Specifications
- **Data Rate:** 1.0 Mbps.
- **Modulation:** Manchester II bi-phase.
- **Topology:** Dual-redundant balanced differential twisted pair terminated at 78 Ohms.
- **Deterministic TDM:** Szigorú időosztásos multiplexelés. No collision detection needed because only the Bus Controller (BC) initiates traffic.

### 2.2 Word Structure (20 Bits Total)
Every word on the wire contains exactly 20 bit-times:
- **Sync Field (3 bit-times):** Unique hardware waveform invalid in normal data.
- **Payload (16 bits):** Command, Data, or Status word.
- **Parity (1 bit):** Odd parity bit for instantaneous single-bit error detection.

```text
[ Sync (3b) ] [ Remote Terminal Addr (5b) ] [ T/R (1b) ] [ Subaddress (5b) ] [ Data Word Count (5b) ] [ Parity (1b) ]
```

---

## 3. CAN & CAN-FD: Automotive, Defense Vehicle & Robotics Bus

Controller Area Network (CAN) is an asynchronous, multi-master broadcast bus utilizing CSMA/CD with Non-Destructive Bitwise Arbitration.

### 3.1 Bitwise Arbitration Mechanism
Dominant bits (logic 0) overwrite Recessive bits (logic 1). When two nodes transmit simultaneously, the node transmitting the lower numerical Identifier wins the bus with zero transmission delay.

### 3.2 Linux SocketCAN Architecture
Linux implements CAN interfaces not as serial character devices, but as first-class network devices (`can0`, `vcan0`):

```bash
# CAN csatolófelület beállítása és sebesség konfigurációja
sudo ip link set can0 type can bitrate 500000 dbitrate 2000000 fd on
sudo ip link set up can0

# Valós idejű forgalom figyelése
candump can0

# Telemetria keret küldése (ID: 0x123, Adat: DE AD BE EF)
cansend can0 123#DEADBEEF
```

### 3.3 CAN-FD (Flexible Data-Rate)
While classic CAN limits payloads to 8 bytes at 1 Mbps, CAN-FD expands payloads to **64 bytes** and dynamically switches the bit rate up to **5-8 Mbps** during the data phase.

---

## 4. ARINC 429: Civil & Military Avionics Standard

ARINC 429 governs commercial and military aircraft navigation, guidance, and engine sensors.
- **Topology:** Point-to-point simplex (one transmitter, up to 20 receivers).
- **Modulation:** Bipolar Return-to-Zero (BPRZ) signaling (+10V, 0V, -10V).
- **Word Length:** 32-bit words containing:
  - Label (8 bits, specifies parameter type: altitude, airspeed, heading).
  - SDI (Source/Destination Identifier, 2 bits).
  - Data payload (19 bits: BCD or Two's Complement BNR binary).
  - SSM (Sign/Status Matrix, 2 bits: Normal, Failure Warning, Test).
  - Parity (1 bit, Odd parity).

---

## 5. PCI Express (PCIe) in Mission Systems

For high-bandwidth telemetry, software-defined radio (SDR), and phased-array radar, PCIe is the primary interconnect.

### 5.1 Configuration Space & TLP Routing
- Every PCIe device implements a 4,096-byte configuration space accessible via ECAM (Enhanced Configuration Access Mechanism).
- Communication is packetized via **Transaction Layer Packets (TLPs)**:
  - Memory Read/Write (MRd, MWr) for DMA.
  - I/O Read/Write.
  - Message Requests (MSI/MSI-X, PME, AER interrupts).

### 5.2 Advanced Error Reporting (AER)
Critical infrastructure requires containment of physical bus degradations. PCIe AER classifies errors into:
- **Correctable Errors:** Automatically resolved by physical layer retry buffers (bad TLP CRC).
- **Uncorrectable Non-Fatal:** The specific transaction failed, but the PCIe link and device remain operational.
- **Uncorrectable Fatal:** Loss of link or internal device buffer overflow; triggers kernel hardware exception (AER panic or root port containment).

---

## 6. RS-485 and Industrial Telemetry

Used in power generation substations, valve controllers, and nuclear sensor arrays:
- **Differential Signaling:** High common-mode noise rejection across 1,200 meters.
- **Multi-Drop:** Up to 32 unit loads on a single pair.
- **Modbus-RTU Protocol:** Deterministic polling state machine using cyclic redundancy checks (CRC-16).

---
*Document status: STABLE · UNICAGD-Core Architecture Standard*
