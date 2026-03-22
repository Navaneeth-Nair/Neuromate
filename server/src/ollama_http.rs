use std::env;
use std::time::Duration;
use once_cell::sync::Lazy;
use reqwest::Client;

type DynError = Box<dyn std::error::Error + Send + Sync>;

static OLLAMA_HTTP: Lazy<Client> = Lazy::new(|| {
    let timeout_secs: u64 = env::var("OLLAMA_HTTP_TIMEOUT_SECS")
        .ok()
        .and_then(|s| s.parse().ok())
        .unwrap_or(300);
    Client::builder()
        .connect_timeout(Duration::from_secs(15))
        .timeout(Duration::from_secs(timeout_secs))
        .pool_max_idle_per_host(16)
        .pool_idle_timeout(Duration::from_secs(120))
        .tcp_keepalive(Duration::from_secs(60))
        .tcp_nodelay(true)
        .build()
        .expect("reqwest client for Ollama")
});

/// Get the persistent, pooled HTTP client for Ollama requests.
/// 
/// The client reuses TCP connections across all requests via keep-alive,
/// reducing handshake overhead and improving throughput.
pub fn client() -> &'static Client {
    &OLLAMA_HTTP
}

/// Resolve the Ollama generate endpoint URL from environment variables.
/// 
/// Priority:
/// 1. If OLLAMA_USE_LOCAL=1, use OLLAMA_LOCAL_BASE (default: http://100.86.220.9:11434)
/// 2. Otherwise, use OLLAMA_URL (default: http://100.86.220.9:11434/api/generate)
pub fn resolve_ollama_generate_url() -> String {
    if env::var("OLLAMA_USE_LOCAL").unwrap_or_default() == "1" {
        let base = env::var("OLLAMA_LOCAL_BASE")
            .unwrap_or_else(|_| "http://100.86.220.9:11434".to_string());
        let base = base.trim_end_matches('/').to_string();
        eprintln!("[monika] OLLAMA_USE_LOCAL=1 — using {}/api/generate", base);
        return format!("{}/api/generate", base);
    }
    let url = env::var("OLLAMA_URL")
        .unwrap_or_else(|_| "http://100.86.220.9:11434/api/generate".to_string());
    eprintln!("[monika] using OLLAMA_URL: {}", url);
    url
}

/// GET /api/tags round-trip time to diagnose slow Tailscale vs slow inference.
/// 
/// If RTT > 500ms, suggests running Ollama locally via OLLAMA_USE_LOCAL=1.
pub async fn log_rtt_to_ollama(generate_url: &str) {
    let tags_url = generate_url.replace("/api/generate", "/api/tags");
    let t = std::time::Instant::now();
    match client().get(&tags_url).send().await {
        Ok(r) if r.status().is_success() => {
            let ms = t.elapsed().as_secs_f64() * 1000.0;
            eprintln!(
                "[monika] Ollama RTT (GET /api/tags via {}): {:.0} ms",
                tags_url, ms
            );
            if ms > 500.0 {
                eprintln!(
                    "[monika] hint: RTT >500ms often means remote Ollama over VPN. For local speed, set OLLAMA_USE_LOCAL=1 and run Ollama on this machine."
                );
            }
        }
        Ok(r) => eprintln!(
            "[monika] Ollama {} returned HTTP {} — check URL and firewall",
            tags_url,
            r.status()
        ),
        Err(e) => eprintln!(
            "[monika] Ollama not reachable at {} ({}) — fix OLLAMA_URL or start Ollama",
            tags_url, e
        ),
    }
}

/// Optional one-token generation to pre-load the model before the first user message.
/// 
/// Enabled by setting OLLAMA_WARMUP=1. Useful for reducing latency on first request.
pub async fn warmup_generate(ollama_url: &str) -> Result<(), DynError> {
    if env::var("OLLAMA_WARMUP").unwrap_or_default() != "1" {
        return Ok(());
    }
    let model = env::var("OLLAMA_MODEL").unwrap_or_else(|_| "qwen2.5:7b".to_string());
    let payload = serde_json::json!({
        "model": model,
        "prompt": ".",
        "stream": false,
        "options": { "num_predict": 1 }
    });
    eprintln!("[monika] OLLAMA_WARMUP=1 — priming model at {} …", ollama_url);
    let t = std::time::Instant::now();
    let r = client()
        .post(ollama_url)
        .json(&payload)
        .send()
        .await?;
    let _ = r.error_for_status()?;
    eprintln!(
        "[monika] warmup finished in {:.2}s (model should stay loaded on Ollama)",
        t.elapsed().as_secs_f64()
    );
    Ok(())
}