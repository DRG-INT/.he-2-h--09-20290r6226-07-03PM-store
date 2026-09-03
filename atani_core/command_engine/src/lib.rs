pub mod command_parser;
pub mod data_model;
pub mod executor;

pub use command_parser::Command;
pub use command_parser::CommandParser;
pub use data_model::DataModel;
pub use executor::Executor;
use std::path::PathBuf;

pub struct Engine {
    data_model: DataModel,
    executor: Executor,
}

impl Engine {
    pub fn new(project_root: PathBuf) -> Self {
        let data_model = DataModel::load(project_root);
        let executor = Executor::new();
        Self {
            data_model,
            executor,
        }
    }

    pub fn execute(&mut self, input: &str) -> Result<String, String> {
        let cmd = CommandParser::parse(input)?;
        match cmd {
            Command::Audit => self.executor.run_audit(&self.data_model),
            Command::Manifest { filter } => self.executor.run_manifest(&self.data_model, filter),
            Command::Lstm => self.executor.run_lstm(&self.data_model),
            Command::Exokernel => self.executor.run_exokernel(&self.data_model),
            Command::Search { query } => self.executor.run_search(&self.data_model, &query),
            Command::Execute { command } => self.executor.run_system_command(command),
            Command::Help => Ok(Engine::help_text()),
            Command::Status => self.executor.run_status(&self.data_model),
        }
    }

    pub fn data_model(&self) -> &DataModel {
        &self.data_model
    }

    fn help_text() -> String {
        r#"
╔══════════════════════════════════════════════════════════════╗
║          UNICAGD COMMAND ENGINE - AVAILABLE COMMANDS         ║
╠══════════════════════════════════════════════════════════════╣
║  audit              Run full dual-intelligence audit         ║
║  manifest [filter]  Show file manifest (optionally filter)   ║
║  lstm               Show LSTM neural topology state          ║
║  exokernel          Show exokernel capabilities & state      ║
║  search <query>     Search data model for query              ║
║  status             Show system/data model status             ║
║  execute <cmd>      Execute arbitrary system command          ║
║  help               Show this help text                       ║
╚══════════════════════════════════════════════════════════════╝
"#.to_string()
    }
}
