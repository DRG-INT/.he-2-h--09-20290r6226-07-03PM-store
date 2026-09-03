use clap::Parser;
use std::str::FromStr;

#[derive(Debug, Parser, Clone)]
#[command(author, version, about = "UNICAGD Command Engine", long_about = None)]
pub enum Command {
    /// Run full dual-intelligence audit
    Audit,
    /// Show file manifest with optional filter
    Manifest {
        /// Filter artifacts by name substring
        filter: Option<String>,
    },
    /// Show LSTM neural topology state
    Lstm,
    /// Show exokernel capabilities and state
    Exokernel,
    /// Search data model for query string
    Search {
        /// Query string to search for
        query: String,
    },
    /// Execute arbitrary system command
    Execute {
        /// System command to execute
        command: SystemCommand,
    },
    /// Show system status
    Status,
    /// Show help text
    Help,
}

#[derive(Debug, Clone)]
pub struct SystemCommand {
    pub program: String,
    pub args: Vec<String>,
}

impl FromStr for SystemCommand {
    type Err = String;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        let mut parts = s.split_whitespace();
        let program = parts.next().ok_or("Empty command")?.to_string();
        let args = parts.map(|s| s.to_string()).collect();
        Ok(SystemCommand { program, args })
    }
}

pub struct CommandParser;

impl CommandParser {
    pub fn parse(input: &str) -> Result<Command, String> {
        let input = input.trim();
        if input.is_empty() {
            return Ok(Command::Help);
        }

        let parts: Vec<&str> = input.split_whitespace().collect();
        let cmd = parts[0].to_lowercase();

        match cmd.as_str() {
            "audit" => Ok(Command::Audit),
            "manifest" | "ls" | "list" => {
                let filter = parts.get(1).map(|s| s.to_string());
                Ok(Command::Manifest { filter })
            }
            "lstm" | "neural" | "topology" => Ok(Command::Lstm),
            "exokernel" | "exo" | "kernel" => Ok(Command::Exokernel),
            "search" | "find" | "grep" | "query" => {
                let query = parts.get(1..).unwrap_or(&[]).join(" ");
                if query.is_empty() {
                    return Err("Search requires a query. Usage: search <query>".to_string());
                }
                Ok(Command::Search { query })
            }
            "execute" | "run" | "exec" | "!" => {
                let cmd_str = parts.get(1..).unwrap_or(&[]).join(" ");
                if cmd_str.is_empty() {
                    return Err("Execute requires a command. Usage: execute <command>".to_string());
                }
                let command = SystemCommand::from_str(&cmd_str)
                    .map_err(|e| format!("Invalid command: {}", e))?;
                Ok(Command::Execute { command })
            }
            "status" | "info" | "state" => Ok(Command::Status),
            "help" | "?" | "--help" | "-h" => Ok(Command::Help),
            _ => {
                // Try to execute as system command directly
                let command = SystemCommand::from_str(input)
                    .map_err(|_| format!("Unknown command: {}. Type 'help' for available commands.", cmd))?;
                Ok(Command::Execute { command })
            }
        }
    }
}
