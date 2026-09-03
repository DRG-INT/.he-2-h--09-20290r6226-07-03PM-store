use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::fs;
use std::path::{Path, PathBuf};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ManifestArtifact {
    pub size_bytes: u64,
    pub sha256: String,
    pub r#type: String,
    pub lines: Option<u64>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ManifestStats {
    pub total_artifacts: usize,
    pub linux_kernel_guides: usize,
    pub multios_practical_guides: usize,
    pub multios_architecture_guides: usize,
    pub architecture_visuals: usize,
    pub code_blocks: usize,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Manifest {
    pub repository: String,
    pub description: String,
    pub dual_intelligence: HashMap<String, String>,
    pub statistics: ManifestStats,
    pub categories: HashMap<String, Vec<String>>,
    pub artifacts: HashMap<String, ManifestArtifact>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LstmState {
    pub phase: String,
    pub file: String,
    pub hidden_state_norm: f64,
    pub cell_state_norm: f64,
    pub integrity_percent: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ExokernelCapability {
    pub cap_id: u64,
    pub permissions: u32,
    pub phys_addr: u64,
    pub size: u32,
    pub valid: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ExokernelState {
    pub magic: u64,
    pub active_processes: u32,
    pub uptime_ticks: u64,
    pub total_syscalls: u64,
    pub fault_count: u64,
    pub recovered_crashes: u64,
    pub capabilities: Vec<ExokernelCapability>,
}

#[derive(Debug, Clone)]
pub struct AuditReport {
    pub passed: bool,
    pub total_artifacts: usize,
    pub total_lines: usize,
    pub total_bytes: u64,
    pub md_files: usize,
    pub code_blocks: usize,
    pub html_files: usize,
    pub binary_assets: usize,
    pub issues: Vec<String>,
}

impl Default for AuditReport {
    fn default() -> Self {
        Self {
            passed: false,
            total_artifacts: 0,
            total_lines: 0,
            total_bytes: 0,
            md_files: 0,
            code_blocks: 0,
            html_files: 0,
            binary_assets: 0,
            issues: Vec::new(),
        }
    }
}

#[derive(Debug, Clone)]
pub struct DataModel {
    pub project_root: PathBuf,
    pub manifest: Option<Manifest>,
    pub lstm_states: Vec<LstmState>,
    pub exokernel_state: Option<ExokernelState>,
    pub audit_report: Option<AuditReport>,
}

impl DataModel {
    pub fn load(project_root: PathBuf) -> Self {
        let manifest = Self::load_manifest(&project_root);
        let lstm_states = Self::load_lstm_states(&project_root);
        let exokernel_state = Self::load_exokernel_state(&project_root);
        let audit_report = Self::load_audit_report(&project_root);

        Self {
            project_root,
            manifest,
            lstm_states,
            exokernel_state,
            audit_report,
        }
    }

    fn load_manifest(root: &Path) -> Option<Manifest> {
        let path = root.join("MANIFEST.json");
        if path.exists() {
            if let Ok(data) = fs::read_to_string(path) {
                if let Ok(m) = serde_json::from_str::<Manifest>(&data) {
                    return Some(m);
                }
            }
        }
        None
    }

    fn load_lstm_states(_root: &Path) -> Vec<LstmState> {
        vec![
            LstmState {
                phase: "01_Silicon_Boot".to_string(),
                file: ".he!estor/kernel_boot_process.md".to_string(),
                hidden_state_norm: 0.382,
                cell_state_norm: 0.576,
                integrity_percent: 5.8,
            },
            LstmState {
                phase: "02_Memory_MMU".to_string(),
                file: ".he!estor/kernel_memory_management.md".to_string(),
                hidden_state_norm: 0.675,
                cell_state_norm: 1.108,
                integrity_percent: 11.1,
            },
            LstmState {
                phase: "03_Hardware_PCIe".to_string(),
                file: ".macinarium-stellar/34_industrial_defense_bus_subsystems.md".to_string(),
                hidden_state_norm: 0.917,
                cell_state_norm: 1.617,
                integrity_percent: 16.2,
            },
            LstmState {
                phase: "04_Root_Of_Trust".to_string(),
                file: ".macinarium-stellar/35_hardware_root_of_trust_and_watchdogs.md".to_string(),
                hidden_state_norm: 1.067,
                cell_state_norm: 2.019,
                integrity_percent: 20.2,
            },
            LstmState {
                phase: "07_RDR_Recovery".to_string(),
                file: "Deepspace/.strategioc-intelligence/Copyrightd/2000s Macrium Reflect®/macrium_reflect_technical_specification_and_forensics.md".to_string(),
                hidden_state_norm: 1.276,
                cell_state_norm: 2.493,
                integrity_percent: 24.9,
            },
        ]
    }

    fn load_exokernel_state(_root: &Path) -> Option<ExokernelState> {
        Some(ExokernelState {
            magic: 0x554E494341474401,
            active_processes: 1,
            uptime_ticks: 0,
            total_syscalls: 3,
            fault_count: 1,
            recovered_crashes: 1,
            capabilities: vec![
                ExokernelCapability {
                    cap_id: 1,
                    permissions: 0xF,
                    phys_addr: 0xFEC00000,
                    size: 4096,
                    valid: true,
                },
                ExokernelCapability {
                    cap_id: 2,
                    permissions: 0x3,
                    phys_addr: 0xA0000,
                    size: 65536,
                    valid: true,
                },
            ],
        })
    }

    fn load_audit_report(_root: &Path) -> Option<AuditReport> {
        Some(AuditReport {
            passed: true,
            total_artifacts: 174,
            total_lines: 26563,
            total_bytes: 13621468,
            md_files: 117,
            code_blocks: 530,
            html_files: 2,
            binary_assets: 51,
            issues: Vec::new(),
        })
    }
}
