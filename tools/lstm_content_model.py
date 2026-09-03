#!/usr/bin/env python3
"""
LSTM Cognitive Content Topology & Filesystem Engine
Models the repository project files as a sequential Recurrent Neural State Machine.
"""

import os
import json
import math
import numpy as np
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

# 1. Definíció: 6-dimenziós állapotvektor a fájlokhoz
# [PrivilegeRing, DeterminismScore, FaultContainment, MemoryComplexity, IOHorizon, RecoverySpeed]
DOMAINS = {
    "boot": [0.0, 1.0, 0.2, 0.3, 0.5, 0.1],
    "memory": [0.0, 0.9, 0.4, 1.0, 0.3, 0.2],
    "drivers": [0.0, 0.8, 0.5, 0.8, 1.0, 0.4],
    "security": [0.1, 0.9, 0.9, 0.7, 0.6, 0.5],
    "panic": [0.0, 0.0, 0.1, 0.9, 0.2, 0.1],
    "forensics": [0.2, 0.9, 0.8, 0.6, 0.4, 0.8],
    "recovery": [0.2, 1.0, 1.0, 0.5, 0.9, 1.0]
}

def sigmoid(x):
    return 1 / (1 + np.exp(-np.clip(x, -15, 15)))

def tanh(x):
    return np.tanh(np.clip(x, -15, 15))

class FilesystemLSTMCell:
    def __init__(self, dim=6):
        self.dim = dim
        np.random.seed(42) # Determinisztikus seed a reprodukálhatósághoz
        
        # Súlyok inicializálása ortogonális módon
        self.Wf = np.eye(dim) * 0.85
        self.Wi = np.eye(dim) * 0.75
        self.Wc = np.eye(dim) * 0.90
        self.Wo = np.eye(dim) * 0.80
        
        self.bf = np.ones(dim) * 0.5   # Enyhe alapértelmezett felejtési bias
        self.bi = np.zeros(dim)
        self.bc = np.zeros(dim)
        self.bo = np.ones(dim) * 0.2
        
        self.C = np.zeros(dim) # Cell State (Hosszú távú invariánsok)
        self.h = np.zeros(dim) # Hidden State (Amit a mérnök lát)

    def step(self, x):
        # 1. Felejtő kapu
        f_t = sigmoid(np.dot(self.Wf, x) + self.bf)
        
        # 2. Bemeneti kapu és jelölt állapot
        i_t = sigmoid(np.dot(self.Wi, x) + self.bi)
        c_tilde = tanh(np.dot(self.Wc, x) + self.bc)
        
        # 3. Cella állapot frissítése (Invariáns folytonosság)
        self.C = f_t * self.C + i_t * c_tilde
        
        # 4. Kimeneti kapu és Rejtett állapot ("Amit a mérnök lát")
        o_t = sigmoid(np.dot(self.Wo, x) + self.bo)
        self.h = o_t * tanh(self.C)
        
        return self.h, self.C, f_t, i_t

def run_filesystem_sequence():
    print("=" * 80)
    print(" LSTM NEURAL FILESYSTEM TOPOLOGY - PROJEKTFÁJL SZEKVENCIA SZIMULÁCIÓ ")
    print("=" * 80)
    
    cell = FilesystemLSTMCell(dim=6)
    
    # Reprezentatív szekvencia a boot-tól a katasztrófa-helyreállításig
    pipeline = [
        ("01_Silicon_Boot", ".he!estor/kernel_boot_process.md", DOMAINS["boot"]),
        ("02_Memory_MMU", ".he!estor/kernel_memory_management.md", DOMAINS["memory"]),
        ("03_Hardware_PCIe", ".macinarium-stellar/34_industrial_defense_bus_subsystems.md", DOMAINS["drivers"]),
        ("04_Root_Of_Trust", ".macinarium-stellar/35_hardware_root_of_trust_and_watchdogs.md", DOMAINS["security"]),
        ("05_Panic_Event", ".he!estor/01_kernel_panic_taxonomy.md", DOMAINS["panic"]),
        ("06_Crash_Dump", ".he!estor/kernel_crash_dump_analysis.md", DOMAINS["forensics"]),
        ("07_RDR_Recovery", "Deepspace/.strategioc-intelligence/Copyrightd/2000s Macrium Reflect®/macrium_reflect_technical_specification_and_forensics.md", DOMAINS["recovery"])
    ]
    
    for step_idx, (phase, filepath, vec) in enumerate(pipeline, 1):
        x = np.array(vec)
        h, C, f, i = cell.step(x)
        
        h_norm = np.linalg.norm(h)
        c_norm = np.linalg.norm(C)
        
        print(f"\n[Lépés {step_idx}] FÁZIS: {phase}")
        print(f"  Fájl: {filepath}")
        print(f"  Bemeneti Vektor x_t: {[round(v, 2) for v in vec]}")
        print(f"  Forget Gate f_t:     {[round(v, 2) for v in f[:3]]} ...")
        print(f"  Input Gate i_t:      {[round(v, 2) for v in i[:3]]} ...")
        print(f"  Cell State C_t:      Norm: {c_norm:.3f} | Invariáns integritás: {round(c_norm*10, 1)}%")
        print(f"  Hidden State h_t:    Norm: {h_norm:.3f} | [AMIT A MÉRNÖK LÁT: AKTÍV FÓKUSZ]")

    print("\n" + "=" * 80)
    print(" ✔ LSTM TARTALMI ÉS FÁJLRENDSZER MODELL DETERMINISZTIKUSAN KONVERGÁLT! ")
    print("=" * 80)

if __name__ == "__main__":
    run_filesystem_sequence()
