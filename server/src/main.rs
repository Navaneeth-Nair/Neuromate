use std::env;
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::Arc;
use tokio::io::{AsyncReadExt, AsyncWriteExt};
use tokio::net::{TcpListener, TcpStream};
use serde_json::json;

mod logging;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    dotenv::dotenv().ok();
    
    let ollama_url = env::var("OLLAMA_URL")
        .unwrap_or_else(|_| "http://localhost:11434/api/generate".to_string());
    let server_host = env::var("SERVER_HOST").unwrap_or_else(|_| "0.0.0.0".to_string());
    let server_port = env::var("SERVER_PORT").unwrap_or_else(|_| "12345".to_string());
    let bind_addr = format!("{}:{}", server_host, server_port);
    
    let listener = TcpListener::bind(&bind_addr).await?;
    
    let server_running = Arc::new(AtomicBool::new(true));
    let running_clone = server_running.clone();
    
    // Handle Ctrl+C
    tokio::spawn(async move {
        tokio::signal::ctrl_c().await.ok();
        running_clone.store(false, Ordering::SeqCst);
    });
    
    loop {
        if !server_running.load(Ordering::SeqCst) {
            break;
        }
        
        match tokio::time::timeout(
            std::time::Duration::from_millis(100),
            listener.accept()
        ).await {
            Ok(Ok((socket, addr))) => {
                let ollama_url = ollama_url.clone();
                let running = server_running.clone();
                
                tokio::spawn(async move {
                    let _ = handle_client(socket, &ollama_url).await;
                });
            }
            Ok(Err(_)) => {},
            Err(_) => {} // Timeout, continue looping
        }
    }
    
    Ok(())
}

async fn handle_client(
    mut socket: TcpStream,
    ollama_url: &str,
) -> Result<(), Box<dyn std::error::Error>> {
    // Read question length (4 bytes, little-endian u32)
    let mut length_bytes = [0u8; 4];
    socket.read_exact(&mut length_bytes).await?;
    let question_length = u32::from_le_bytes(length_bytes) as usize;
    
    // Read question
    let mut question_bytes = vec![0u8; question_length];
    socket.read_exact(&mut question_bytes).await?;
    let question = String::from_utf8(question_bytes)?;
    
    // Query Ollama
    let answer = query_ollama(ollama_url, &question).await?;
    
    // Log question and answer
    let _ = logging::log_entry(&question, &answer).await;
    
    // Send response
    let answer_bytes = answer.as_bytes();
    let response_length = answer_bytes.len() as u32;
    socket.write_all(&response_length.to_le_bytes()).await?;
    socket.write_all(answer_bytes).await?;
    
    Ok(())
}

async fn query_ollama(ollama_url: &str, question: &str) -> Result<String, Box<dyn std::error::Error>> {
    let client = reqwest::Client::new();
    
    let payload = json!({
        "model": "qwen2.5:7b",
        "prompt": question,
        "stream": false
    });
    
    let response = tokio::time::timeout(
        std::time::Duration::from_secs(120),
        client.post(ollama_url)
            .json(&payload)
            .send()
    ).await??;
    
    let result: serde_json::Value = response.json().await?;
    
    Ok(result["response"]
        .as_str()
        .unwrap_or("No response from Ollama")
        .to_string())
}
