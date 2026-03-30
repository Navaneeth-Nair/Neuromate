use std::env;
use std::path::Path;
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::Arc;
use std::time::Instant;
use tokio::io::{AsyncBufReadExt, AsyncReadExt, AsyncWriteExt};
use tokio::net::{TcpListener, TcpStream};
use tokio_util::io::StreamReader;
use futures_util::TryStreamExt;
use serde_json::json;
use std::sync::Mutex;

type DynError = Box<dyn std::error::Error + Send + Sync>;

const REPLY_STYLE: &str = "";
mod logging;
mod mood_engine;
mod filter;
mod ollama_http;
use monika_middleware::{encrypt_message, decrypt_message};

fn load_dotenv() {
    let repo_env = Path::new(env!("CARGO_MANIFEST_DIR")).join("../.env");
    let _ = dotenv::from_path(&repo_env);
    let _ = dotenv::dotenv();
}



static SESSION_POOL: once_cell::sync::Lazy<Arc<Mutex<std::collections::HashMap<String, Instant>>>> =
    once_cell::sync::Lazy::new(|| Arc::new(Mutex::new(std::collections::HashMap::new())));



async fn session_heartbeat_task(ollama_url: String, interval_secs: u64) {
    let mut interval = tokio::time::interval(std::time::Duration::from_secs(interval_secs));
    loop {
        interval.tick().await;

        let model = env::var("OLLAMA_MODEL").unwrap_or_else(|_| "qwen2.5:7b".to_string());
        let payload = serde_json::json!({
            "model": model,
            "prompt": ".",
            "stream": false,
            "options": { "num_predict": 1 }
        });

        match ollama_http::client()
            .post(&ollama_url)
            .json(&payload)
            .send()
            .await
        {
            Ok(r) if r.status().is_success() => {
                eprintln!("[monika] heartbeat: model kept alive in Ollama memory");
            }
            Ok(r) => {
                eprintln!("[monika] heartbeat failed: HTTP {}", r.status());
            }
            Err(e) => {
                eprintln!("[monika] heartbeat error: {}", e);
            }
        }
    }
}


#[tokio::main]
async fn main() -> Result<(), DynError> {
    load_dotenv();

    let enable_encryption = env::var("ENABLE_ENCRYPTION")
        .map(|v| v == "1" || v.to_lowercase() == "true")
        .unwrap_or(false);

    let ollama_url = ollama_http::resolve_ollama_generate_url();
    let server_host = env::var("SERVER_HOST").unwrap_or_else(|_| "127.0.0.1".to_string());
    let server_port = env::var("SERVER_PORT").unwrap_or_else(|_| "12345".to_string());
    let bind_addr = format!("{}:{}", server_host, server_port);

    eprintln!(
        "[monika] listening on {} | encryption: {} | effective Ollama: {}",
        bind_addr,
        if enable_encryption { "enabled" } else { "disabled" },
        ollama_url
    );
    if ollama_url.contains("127.0.0.1") || ollama_url.contains("localhost") {
        eprintln!("[monika] Local Ollama — sub-second latency when model is loaded.");
    } else {
        eprintln!("[monika] Remote Ollama at {} — RTT + remote inference time.", ollama_url);
    }

    let listener = TcpListener::bind(&bind_addr).await?;

    let url_ping = ollama_url.clone();
    tokio::spawn(async move {
        ollama_http::log_rtt_to_ollama(&url_ping).await;
    });

    let url_warm = ollama_url.clone();
    tokio::spawn(async move {
        if let Err(e) = ollama_http::warmup_generate(&url_warm).await {
            eprintln!("[monika] Ollama warmup: {}", e);
        }
    });

    
    let url_heartbeat = ollama_url.clone();
    let heartbeat_interval = env::var("OLLAMA_HEARTBEAT_SECS")
        .ok()
        .and_then(|s| s.parse().ok())
        .unwrap_or(60);
    tokio::spawn(async move {
        session_heartbeat_task(url_heartbeat, heartbeat_interval).await;
    });

    let server_running = Arc::new(AtomicBool::new(true));
    let running_clone = server_running.clone();

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
            listener.accept(),
        )
        .await
        {
            Ok(Ok((socket, addr))) => {
                let ollama_url = ollama_url.clone();
                tokio::spawn(async move {
                    eprintln!("[monika] client connected from {}", addr);
                    let client_id = addr.to_string();

                    
                    {
                        let mut pool = SESSION_POOL.lock().unwrap();
                        pool.insert(client_id.clone(), Instant::now());
                    }

                    let _ = handle_client(socket, &ollama_url, &client_id).await;
                });
            }
            Ok(Err(_)) => {}
            Err(_) => {}
        }
    }

    eprintln!("[monika] shutting down...");
    Ok(())
}




async fn send_framed_message(socket: &mut TcpStream, body: &[u8]) -> Result<(), DynError> {
    socket.write_all(&(body.len() as u32).to_le_bytes()).await?;
    socket.write_all(body).await?;
    socket.flush().await?;
    Ok(())
}


async fn handle_client(mut socket: TcpStream, ollama_url: &str, client_id: &str) -> Result<(), DynError> {
    match handle_request(&mut socket, ollama_url, client_id).await {
        Ok(()) => Ok(()),
        Err(e) => {
            let msg = format!("Server error: {}", e);
            eprintln!("[monika] request error: {}", e);
            let _ = send_framed_message(&mut socket, msg.as_bytes()).await;
            let _ = send_framed_message(&mut socket, &[]).await;
            Ok(())
        }
    }
}


fn fmt_timing_rows(rows: &[(&str, f64)]) -> String {
    let mut out = String::new();
    for (k, v) in rows {
        out.push_str(&format!("  {:<26} {:>10.2}\n", k, v));
    }
    out
}


async fn handle_request(socket: &mut TcpStream, ollama_url: &str, client_id: &str) -> Result<(), DynError> {
    let wall = Instant::now();

    
    let t = Instant::now();
    let mut length_bytes = [0u8; 4];
    socket.read_exact(&mut length_bytes).await?;
    let question_length = u32::from_le_bytes(length_bytes) as usize;
    let mut question_bytes = vec![0u8; question_length];
    socket.read_exact(&mut question_bytes).await?;
    let question = String::from_utf8(question_bytes)?;
    let read_tcp_ms = t.elapsed().as_secs_f64() * 1000.0;

    
    let t = Instant::now();
    let (mood, elo) = mood_engine::record_interaction(client_id, &question).await;
    let mood_ms = t.elapsed().as_secs_f64() * 1000.0;

    eprintln!("[monika] streaming from Ollama (mood={} elo={:.1}) …", mood, elo);

    
    {
        let mut pool = SESSION_POOL.lock().unwrap();
        pool.insert(client_id.to_string(), Instant::now());
    }

    
    let (raw_answer, om) =
        query_ollama_streaming(ollama_url, &question, &mood, socket).await?;

    let ollama_sum_ms = om.post_send_ms + om.stream_drain_ms;

    
    let t = Instant::now();
    let answer = filter::sanitize_response(&raw_answer);
    let filter_ms = t.elapsed().as_secs_f64() * 1000.0;

    
    let t = Instant::now();
    send_framed_message(socket, &[]).await?;
    let send_eof_ms = t.elapsed().as_secs_f64() * 1000.0;

    
    let timings_before_disk = format!(
        "{}{}",
        fmt_timing_rows(&[
            ("read_tcp", read_tcp_ms),
            ("mood_engine", mood_ms),
            ("ollama_http_send", om.post_send_ms),
            ("ollama_stream_drain", om.stream_drain_ms),
            ("ollama_http_sum", ollama_sum_ms),
            ("filter", filter_ms),
            ("send_eof", send_eof_ms),
        ]),
        format!(
            "  (Ollama API) prompt_tokens:     {:>10}\n  (Ollama API) output_tokens:    {:>10}\n  (Ollama API) reported_wall_s:  {:>10.3}\n",
            om.prompt_tokens,
            om.output_tokens,
            om.ollama_reported_wall_ns as f64 / 1e9
        )
    );

    let disk_log_ms = logging::log_entry(
        &format!("{} [mood={} elo={:.1}]", question, mood, elo),
        &answer,
        &timings_before_disk,
        wall,
    )
    .await?;

    let total_wall_ms = wall.elapsed().as_secs_f64() * 1000.0;

    eprintln!(
        "[monika] bottleneck profile (ms for phases; tokens/duration from Ollama):\n{}",
        format!(
            "{}{}",
            fmt_timing_rows(&[
                ("read_tcp", read_tcp_ms),
                ("mood_engine", mood_ms),
                ("ollama_http_send", om.post_send_ms),
                ("ollama_stream_drain", om.stream_drain_ms),
                ("ollama_http_sum", ollama_sum_ms),
                ("filter", filter_ms),
                ("send_eof", send_eof_ms),
                ("disk_log", disk_log_ms),
                ("total_server_wall_ms", total_wall_ms),
            ]),
            format!(
                "  (Ollama API) prompt_tokens:     {:>10}\n  (Ollama API) output_tokens:    {:>10}\n  (Ollama API) reported_wall_s:  {:>10.3}\n",
                om.prompt_tokens,
                om.output_tokens,
                om.ollama_reported_wall_ns as f64 / 1e9
            )
        )
    );

    Ok(())
}

struct OllamaMeta {
    post_send_ms: f64,
    stream_drain_ms: f64,
    prompt_tokens: u64,
    output_tokens: u64,
    ollama_reported_wall_ns: u64,
}











async fn query_ollama_streaming(
    ollama_url: &str,
    question: &str,
    culture: &str,
    socket: &mut TcpStream,
) -> Result<(String, OllamaMeta), DynError> {
    let model = env::var("OLLAMA_MODEL").unwrap_or_else(|_| "qwen2.5:7b".to_string());

    let prompt = format!(
        "{}\n\nUser mood: {}\nUser: {}\nAssistant:",
        REPLY_STYLE, culture, question
    );

    
    let mut payload = json!({
        "model": model,
        "prompt": prompt,
        "stream": true
    });

    let num_predict: i64 = env::var("OLLAMA_NUM_PREDICT")
        .ok()
        .and_then(|s| s.parse().ok())
        .unwrap_or(280);

    let mut options = json!({ "num_predict": num_predict });
    if let Ok(n) = env::var("OLLAMA_NUM_CTX") {
        if let Ok(v) = n.parse::<u64>() {
            if let Some(o) = options.as_object_mut() {
                o.insert("num_ctx".to_string(), json!(v));
            }
        }
    }
    if let Ok(extra) = env::var("OLLAMA_OPTIONS_JSON") {
        let patch: serde_json::Value = serde_json::from_str(&extra)?;
        if let (Some(po), Some(o)) = (patch.as_object(), options.as_object_mut()) {
            for (k, v) in po {
                o.insert(k.clone(), v.clone());
            }
        }
    }
    if let Some(obj) = payload.as_object_mut() {
        obj.insert("options".to_string(), options);
    }

    
    let t_post = Instant::now();
    let response = ollama_http::client()
        .post(ollama_url)
        .json(&payload)
        .send()
        .await?
        .error_for_status()?;
    let post_send_ms = t_post.elapsed().as_secs_f64() * 1000.0;

    
    let byte_stream = response
        .bytes_stream()
        .map_err(|e| std::io::Error::new(std::io::ErrorKind::Other, e));
    let stream_reader = StreamReader::new(byte_stream);
    let mut lines = stream_reader.lines();

    
    let t_drain = Instant::now();
    let mut full_text = String::new();
    let mut prompt_tokens: u64 = 0;
    let mut output_tokens: u64 = 0;
    let mut ollama_reported_wall_ns: u64 = 0;

    let mut chunk_count = 0;
    while let Some(line) = lines.next_line().await? {
        let line = line.trim().to_owned();
        if line.is_empty() {
            continue;
        }

        
        let chunk: serde_json::Value = match serde_json::from_str(&line) {
            Ok(v) => v,
            Err(e) => {
                eprintln!("[monika] NDJSON parse error (skipping): {}: {:?}", e, line);
                continue;
            }
        };

        chunk_count += 1;
        let is_done = chunk["done"].as_bool().unwrap_or(false);

        
        let fragment = chunk["response"].as_str().unwrap_or("").to_string();
        if !fragment.is_empty() {
            eprintln!("[monika] chunk #{}: got '{}' (done={})", chunk_count, fragment, is_done);
            full_text.push_str(&fragment);
            
            send_framed_message(socket, fragment.as_bytes()).await?;
        } else {
            eprintln!("[monika] chunk #{}: empty response (done={})", chunk_count, is_done);
        }

        
        if is_done {
            prompt_tokens = chunk["prompt_eval_count"].as_u64().unwrap_or(0);
            output_tokens = chunk["eval_count"].as_u64().unwrap_or(0);
            ollama_reported_wall_ns = chunk["total_duration"].as_u64().unwrap_or(0);
            eprintln!(
                "[monika] stream done after {} chunks. tokens: prompt={}, output={}",
                chunk_count, prompt_tokens, output_tokens
            );
            break;
        }
    }

    let stream_drain_ms = t_drain.elapsed().as_secs_f64() * 1000.0;

    if full_text.is_empty() {
        full_text = "No response from Ollama".to_string();
    }

    Ok((
        full_text,
        OllamaMeta {
            post_send_ms,
            stream_drain_ms,
            prompt_tokens,
            output_tokens,
            ollama_reported_wall_ns,
        },
    ))
}