#!/usr/bin/env python3
"""
UNICAGD DUAL-INTELLIGENCE STATIC AUDIT
Fast static + mathematical verification of critical infrastructure.
"""

import hashlib
import json
import math
import os
import sys
from pathlib import Path
from datetime import datetime, timezone

class DualIntelligenceAudit:
    """Static + Mathematical audit engine."""
    
    def __init__(self, root):
        self.root = Path(root)
        self.artifacts = []
        self.stats = {
            'total_files': 0,
            'total_dirs': 0,
            'total_bytes': 0,
            'md_files': 0,
            'code_blocks': 0,
            'rust_crates': 0,
            'php_files': 0,
            'python_files': 0,
            'c_files': 0,
            'docker_files': 0,
            'json_files': 0,
        }
        self.findings = []
        
    def audit(self):
        print("=" * 70)
        print("UNICAGD DUAL-INTELLIGENCE STATIC AUDIT")
        print(f"Target: {self.root}")
        print(f"Time: {datetime.now(timezone.utc).isoformat()}")
        print("=" * 70)
        
        self._static_inventory()
        self._crypto_verify()
        self._math_audit()
        self._doctrine_check()
        self._report()
        
    def _static_inventory(self):
        print("\n[1/4] STATIC INVENTORY")
        print("-" * 70)
        
        # Focus on critical paths only
        critical_paths = [
            "docker-compose.yml",
            "Dockerfile.api",
            "Dockerfile.ui",
            "Cargo.toml",
            "trust_monitor/phalcon_app",
            "trust_monitor/bootstrap_app",
            "unicagd_core",
            "atani_core",
            "hathat",
            "UNICAGD_EXOKERNEL",
            "tools",
            "UNICAGD_DATA_FABRIC_STANDALONE_v2.4",
        ]
        
        for cp in critical_paths:
            p = self.root / cp
            if not p.exists():
                print(f"  ⚠ MISSING: {cp}")
                continue
                
            if p.is_file():
                self._scan_file(p)
            else:
                for f in p.rglob("*"):
                    if f.is_file():
                        self._scan_file(f)
                        
        print(f"  Files scanned: {self.stats['total_files']}")
        print(f"  Total bytes: {self.stats['total_bytes']:,}")
        print(f"  Rust crates: {self.stats['rust_crates']}")
        print(f"  PHP files: {self.stats['php_files']}")
        print(f"  Python files: {self.stats['python_files']}")
        print(f"  Markdown: {self.stats['md_files']}")
        
    def _scan_file(self, path):
        try:
            size = path.stat().st_size
            self.stats['total_files'] += 1
            self.stats['total_bytes'] += size
            
            rel = path.relative_to(self.root)
            ext = path.suffix.lower()
            
            # Skip large binaries
            if size > 10_000_000:
                return
                
            # Compute fast hash
            h = hashlib.sha256()
            with open(path, 'rb') as f:
                while chunk := f.read(65536):
                    h.update(chunk)
            sha256 = h.hexdigest()
            
            if ext == '.md':
                self.stats['md_files'] += 1
                try:
                    content = path.read_text(errors='ignore')
                    self.stats['code_blocks'] += content.count('```')
                except:
                    pass
            elif ext == '.rs':
                self.stats['rust_crates'] += 1
            elif ext == '.php':
                self.stats['php_files'] += 1
            elif ext == '.py':
                self.stats['python_files'] += 1
            elif ext in ['.c', '.h']:
                self.stats['c_files'] += 1
            elif ext == '.json':
                self.stats['json_files'] += 1
            elif 'dockerfile' in path.name.lower():
                self.stats['docker_files'] += 1
                
            self.artifacts.append({
                'path': str(rel),
                'size': size,
                'sha256': sha256,
            })
        except (FileNotFoundError, PermissionError):
            pass
            
    def _crypto_verify(self):
        print("\n[2/4] CRYPTOGRAPHIC VERIFICATION")
        print("-" * 70)
        
        # Check MANIFEST.json
        manifest_path = self.root / "MANIFEST.json"
        if manifest_path.exists():
            print(f"  ✔ MANIFEST.json found")
            try:
                manifest = json.loads(manifest_path.read_text())
                print(f"    Artifacts: {len(manifest.get('artifacts', {}))}")
            except:
                print(f"  ✗ MANIFEST.json invalid")
        else:
            print(f"  ⚠ MANIFEST.json not found")
            
        # Check exokernel magic
        exokernel_main = self.root / "UNICAGD_EXOKERNEL" / "src" / "main.c"
        if exokernel_main.exists():
            content = exokernel_main.read_text()
            if "0x554E494341474401" in content:
                print(f"  ✔ Exokernel magic verified: 0x554E494341474401")
            else:
                print(f"  ✗ Exokernel magic missing")
                
        # Check Rust workspace
        cargo_toml = self.root / "Cargo.toml"
        if cargo_toml.exists():
            print(f"  ✔ Cargo.toml found")
            
        # Check Phalcon app
        phalcon_index = self.root / "trust_monitor" / "phalcon_app" / "public" / "index.php"
        if phalcon_index.exists():
            print(f"  ✔ Phalcon app found")
            
    def _math_audit(self):
        print("\n[3/4] MATHEMATICAL AUDIT")
        print("-" * 70)
        
        # LSTM files
        lstm_files = [
            ".he!estor/kernel_boot_process.md",
            ".he!estor/kernel_memory_management.md",
            ".macinarium-stellar/34_industrial_defense_bus_subsystems.md",
            ".macinarium-stellar/35_hardware_root_of_trust_and_watchdogs.md",
        ]
        print("\n  LSTM Topology:")
        for f in lstm_files:
            p = self.root / f
            if p.exists():
                print(f"    ✔ {f}")
            else:
                print(f"    ✗ {f} MISSING")
                
        # Cube matrix
        print("\n  Cube Matrix:")
        cube = self.root / "unicagd_core" / "cube_matrix.py"
        if cube.exists():
            content = cube.read_text()
            has_accumulate = "accumulate_ids" in content
            has_transform = "transform" in content
            print(f"    ✔ cube_matrix.py")
            print(f"      Entropy accumulation: {'PRESENT' if has_accumulate else 'MISSING'}")
            print(f"      One-way transform: {'PRESENT' if has_transform else 'MISSING'}")
            
        # Exokernel
        print("\n  Exokernel:")
        main_c = self.root / "UNICAGD_EXOKERNEL" / "src" / "main.c"
        if main_c.exists():
            content = main_c.read_text()
            syscalls = content.count("syscall(")
            print(f"    Syscalls: {syscalls}")
            if "YIELD_SYSCALL" in content and "MAP_PAGE_SYSCALL" in content:
                print(f"    ✔ Core syscalls present")
                
        # Vector kernel
        print("\n  Vector Kernel:")
        vk = self.root / "unicagd_core" / "vector_kernel.py"
        if vk.exists():
            content = vk.read_text()
            has_cosine = "_cosine_sim" in content
            has_upsert = "upsert" in content
            print(f"    ✔ vector_kernel.py")
            print(f"      Cosine similarity: {'PRESENT' if has_cosine else 'MISSING'}")
            print(f"      Upsert: {'PRESENT' if has_upsert else 'MISSING'}")
            
    def _doctrine_check(self):
        print("\n[4/4] DOCTRINE CHECK")
        print("-" * 70)
        
        doctrine_files = [
            "IOS_DOCTRINE_AND_LOGIC.md",
            "IOS_SYSTEM_OVERVIEW.md",
            "IOS_TECHNICAL_SPECS.md",
            "COMMANDER_ENGINE.md",
            "CONVERGENCE_PROTOCOL.md",
            "README.md",
        ]
        
        for f in doctrine_files:
            p = self.root / f
            if p.exists():
                print(f"  ✔ {f}")
            else:
                print(f"  ⚠ {f} not found")
                
        # Check license
        license_files = ["LICENSE", "LICENSE.md", "LICENSE.txt"]
        for f in license_files:
            p = self.root / f
            if p.exists():
                print(f"\n  License: {f}")
                break
                
    def _report(self):
        print("\n" + "=" * 70)
        print("AUDIT SUMMARY")
        print("=" * 70)
        print(f"Artifacts scanned: {len(self.artifacts)}")
        print(f"Total bytes: {self.stats['total_bytes']:,}")
        print(f"Rust crates: {self.stats['rust_crates']}")
        print(f"PHP files: {self.stats['php_files']}")
        print(f"Python files: {self.stats['python_files']}")
        print(f"Markdown docs: {self.stats['md_files']}")
        print(f"Dockerfiles: {self.stats['docker_files']}")
        print("=" * 70)
        
        # Save compact report
        report = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'root': str(self.root),
            'stats': self.stats,
            'artifacts': [
                {'path': a['path'], 'sha256': a['sha256'][:16], 'size': a['size']}
                for a in self.artifacts[:50]
            ],
        }
        
        report_path = self.root / ".dual_intelligence_audit.json"
        report_path.write_text(json.dumps(report, indent=2))
        print(f"\nReport saved: {report_path}")

def main():
    if len(sys.argv) > 1:
        root = sys.argv[1]
    else:
        root = "/Volumes/_ARCHIVE/reunited/reunited/ios"
        
    audit = DualIntelligenceAudit(root)
    audit.audit()

if __name__ == "__main__":
    main()
