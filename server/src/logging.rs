use chrono::Local;
use tokio::fs::OpenOptions;
use tokio::io::AsyncWriteExt;

pub async fn log_entry(question: &str, answer: &str) -> Result<(), Box<dyn std::error::Error>> {
    let timestamp = Local::now().format("%Y-%m-%d %H:%M:%S").to_string();
    let log_line = format!("[{}] Q: {}\nA: {}\n\n", timestamp, question, answer);
    
    let mut file = OpenOptions::new()
        .create(true)
        .append(true)
        .open("logging.log")
        .await?;
    
    file.write_all(log_line.as_bytes()).await?;
    Ok(())
}
