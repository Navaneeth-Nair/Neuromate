use chrono::Local;
use std::time::Instant;
use tokio::fs::OpenOptions;
use tokio::io::AsyncWriteExt;

/// Writes Q/A plus timings; measures file I/O and appends `disk_log` + `total_wall_ms`.
pub async fn log_entry(
    question: &str,
    answer: &str,
    timings_before_disk: &str,
    wall: Instant,
) -> Result<f64, Box<dyn std::error::Error + Send + Sync>> {
    let timestamp = Local::now().format("%Y-%m-%d %H:%M:%S").to_string();
    let body = format!(
        "[{}] Q: {}\nA: {}\nTimings (ms):\n{}",
        timestamp, question, answer, timings_before_disk
    );

    let t_disk = Instant::now();
    let mut file = OpenOptions::new()
        .create(true)
        .append(true)
        .open("logging.log")
        .await?;

    file.write_all(body.as_bytes()).await?;
    let disk_log_ms = t_disk.elapsed().as_secs_f64() * 1000.0;

    let tail_disk = format!("  {:<26} {:>10.2}\n", "disk_log", disk_log_ms);
    file.write_all(tail_disk.as_bytes()).await?;

    let total_wall_ms = wall.elapsed().as_secs_f64() * 1000.0;
    let tail_total = format!("  {:<26} {:>10.2}\n\n", "total_wall_ms", total_wall_ms);
    file.write_all(tail_total.as_bytes()).await?;
    Ok(disk_log_ms)
}
