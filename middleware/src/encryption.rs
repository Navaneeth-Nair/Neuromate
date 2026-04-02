use aes_gcm::aead::{Aead, KeyInit};
use aes_gcm::Aes256Gcm;
use rand::Rng;
use sha2::{Sha256, Digest};
use std::error::Error;
use std::sync::OnceLock;

static CIPHER: OnceLock<Aes256Gcm> = OnceLock::new();
const NONCE_SIZE: usize = 12;

fn init_cipher() -> Aes256Gcm {
    dotenv::dotenv().ok();
    let secret = std::env::var("MONIKA_SHARED_SECRET")
        .unwrap_or_else(|_| "monika-e2e-shared-secret-v1-default".to_string());
    
    let mut hasher = Sha256::new();
    hasher.update(secret.as_bytes());
    let key_bytes = hasher.finalize();
    
    let key = aes_gcm::Key::<Aes256Gcm>::from_slice(&key_bytes);
    Aes256Gcm::new(key)
}

fn get_cipher() -> &'static Aes256Gcm {
    CIPHER.get_or_init(init_cipher)
}

pub fn encrypt_message(message: &str) -> Result<Vec<u8>, Box<dyn Error>> {
    let cipher = get_cipher();
    let mut rng = rand::thread_rng();
    let mut nonce_bytes = [0u8; NONCE_SIZE];
    rng.fill(&mut nonce_bytes);
    
    let nonce = aes_gcm::Nonce::from_slice(&nonce_bytes);
    let ciphertext = cipher.encrypt(nonce, message.as_bytes())
        .map_err(|e| format!("Encryption failed: {}", e))?;
    
    let mut result = nonce_bytes.to_vec();
    result.extend(ciphertext);
    Ok(result)
}

pub fn decrypt_message(encrypted: &[u8]) -> Result<String, Box<dyn Error>> {
    if encrypted.len() < NONCE_SIZE {
        return Err("Encrypted data too short".into());
    }
    
    let cipher = get_cipher();
    let nonce = aes_gcm::Nonce::from_slice(&encrypted[..NONCE_SIZE]);
    let ciphertext = &encrypted[NONCE_SIZE..];
    
    let plaintext = cipher.decrypt(nonce, ciphertext)
        .map_err(|e| format!("Decryption failed: {}", e))?;
    
    Ok(String::from_utf8(plaintext)?)
}
