use command_engine::{Command, Engine};
use colored::Colorize;
use std::io::{self, Write};
use std::path::PathBuf;
use std::sync::Arc;
use tokio::io::AsyncReadExt;
use tokio::sync::Mutex;

fn run_repl(project_root: PathBuf) {
    let mut engine = Engine::new(project_root);

    println!(
        "{}",
        r#"
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   ██╗   ██╗███████╗██████╗ ███╗   ██╗███████╗██╗   ██╗    ║
║   ██║   ██║██╔════╝██╔══██╗████╗  ██║██╔════╝██║   ██║    ║
║   ██║   ██║█████╗  ██████╔╝██╔██╗ ██║█████╗  ██║   ██║    ║
║   ╚██╗ ██╔╝██╔══╝  ██╔══██╗██║╚██╗██║██╔══╝  ╚██╗ ██╔╝    ║
║    ╚████╔╝ ███████╗██║  ██║██║ ╚████║███████╗ ╚████╔╝     ║
║     ╚═══╝  ╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝╚══════╝  ╚═══╝      ║
║                                                              ║
║           COMMAND ENGINE - PHP-RUST HYBRID SYSTEM            ║
║              "Data Model Competitive Interface"              ║
╚══════════════════════════════════════════════════════════════╝
"#
    );

    if let Ok(data) = engine.execute("help") {
        println!("{}", data);
    }

    println!(
        "{} Type 'help' for commands, 'exit' to quit.\n",
        "Ready.".bold().green()
    );

    loop {
        print!("{}", "unicagd-engine> ".bold().cyan());
        io::stdout().flush().unwrap();

        let mut input = String::new();
        io::stdin().read_line(&mut input).unwrap();

        let input = input.trim();
        if input.is_empty() {
            continue;
        }
        if input == "exit" || input == "quit" || input == "q" {
            println!("{}", "Exiting UNICAGD Command Engine.".yellow());
            break;
        }

        match engine.execute(input) {
            Ok(result) => println!("{}\n", result),
            Err(err) => println!("{} {}\n", "✗ Error:".red(), err),
        }
    }
}

async fn run_http(project_root: PathBuf, port: u16) {
    use std::net::SocketAddr;
    use tokio::net::TcpListener;
    
    let engine = Arc::new(Mutex::new(Engine::new(project_root)));
    
    println!("{} HTTP server starting on port {}", "✔".green(), port);
    println!("{} POST /command with JSON {{\"command\": \"...\"}}", "  Endpoint:".cyan());
    println!("{} GET  /status for engine status", "  Endpoint:".cyan());
    
    let addr = SocketAddr::from(([0, 0, 0, 0], port));
    let listener = TcpListener::bind(addr).await.unwrap();
    
    loop {
        let (socket, _) = listener.accept().await.unwrap();
        let engine = Arc::clone(&engine);
        
        tokio::spawn(async move {
            use tokio::io::{AsyncBufReadExt, AsyncWriteExt, BufReader};
            let mut reader = BufReader::new(socket);
            let mut request_line = String::new();
            
            if reader.read_line(&mut request_line).await.is_err() {
                return;
            }
            
            let parts: Vec<&str> = request_line.trim().split_whitespace().collect();
            if parts.len() < 2 {
                return;
            }
            
            let method = parts[0];
            let path = parts[1];
            
            let mut headers = String::new();
            loop {
                let mut line = String::new();
                if reader.read_line(&mut line).await.is_err() {
                    return;
                }
                if line.trim().is_empty() {
                    break;
                }
                headers.push_str(&line);
            }
            
            let mut response = String::new();
            let mut status = "200 OK";
            
            if method == "POST" && path == "/command" {
                let mut body = String::new();
                let _ = reader.read_to_string(&mut body).await;
                
                if let Ok(json) = serde_json::from_str::<serde_json::Value>(&body) {
                    let command = json["command"].as_str().unwrap_or("");
                    let mut engine = engine.lock().await;
                    match engine.execute(command) {
                        Ok(output) => {
                            response = serde_json::json!({
                                "success": true,
                                "output": output
                            }).to_string();
                        }
                        Err(err) => {
                            status = "400 Bad Request";
                            response = serde_json::json!({
                                "success": false,
                                "error": err
                            }).to_string();
                        }
                    }
                } else {
                    status = "400 Bad Request";
                    response = serde_json::json!({
                        "success": false,
                        "error": "Invalid JSON body"
                    }).to_string();
                }
            } else if method == "GET" && path == "/status" {
                let engine = engine.lock().await;
                let data = engine.data_model();
                response = serde_json::json!({
                    "manifest": data.manifest.is_some(),
                    "lstm_phases": data.lstm_states.len(),
                    "exokernel": data.exokernel_state.is_some(),
                    "audit_passed": data.audit_report.as_ref().map(|a| a.passed).unwrap_or(false)
                }).to_string();
            } else {
                status = "404 Not Found";
                response = serde_json::json!({
                    "success": false,
                    "error": "Not found"
                }).to_string();
            }
            
            let http_response = format!(
                "HTTP/1.1 {}\r\nContent-Type: application/json\r\nContent-Length: {}\r\nConnection: close\r\n\r\n{}",
                status,
                response.len(),
                response
            );
            
            let _ = reader.get_mut().write_all(http_response.as_bytes()).await;
        });
    }
}

#[tokio::main]
async fn main() {
    let args: Vec<String> = std::env::args().collect();
    let project_root = std::env::current_dir().unwrap_or_else(|_| PathBuf::from("."));
    
    let mode = args.get(1).map(|s| s.as_str()).unwrap_or("repl");
    let port = args.get(2).and_then(|s| s.parse().ok()).unwrap_or(8089);
    
    match mode {
        "http" => run_http(project_root, port).await,
        "repl" | _ => run_repl(project_root),
    }
}
