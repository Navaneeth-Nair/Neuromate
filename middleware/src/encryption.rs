use aes_gcm::aead::{Aead, KeyInit};
use aes_gcm::Aes256Gcm;
use rand::Rng;
use sha2::{Sha256, Digest};
use std::error::Error;

fn get_shared_secret() -> String {
    dotenv::dotenv().ok();
    std::env::var("MONIKA_SHARED_SECRET")
        .unwrap_or_else(|_| "monika-e2e-shared-secret-v1-default".to_string())
}

fn get_nonce_size() -> usize {
    dotenv::dotenv().ok();
    std::env::var("MONIKA_NONCE_SIZE")
        .unwrap_or_else(|_| "12".to_string())
        .parse::<usize>()
        .unwrap_or(12)
}

fn get_cipher_type() -> String {
    dotenv::dotenv().ok();
    std::env::var("MONIKA_CIPHER_TYPE")
        .unwrap_or_else(|_| "aes256gcm".to_string())
}

pub struct EncryptionContext {
    inner: Box<dyn CipherOps>,
}

trait CipherOps: Send + Sync {
    fn encrypt(&self, plaintext: &[u8]) -> Result<Vec<u8>, Box<dyn Error>>;
    fn decrypt(&self, encrypted: &[u8]) -> Result<Vec<u8>, Box<dyn Error>>;
}

struct Aes256GcmCipher {
    cipher: Aes256Gcm,
    nonce_size: usize,
}

impl CipherOps for Aes256GcmCipher {
    fn encrypt(&self, plaintext: &[u8]) -> Result<Vec<u8>, Box<dyn Error>> {
        let mut rng = rand::thread_rng();
        let mut nonce_bytes = vec![0u8; self.nonce_size];
        rng.fill(&mut nonce_bytes[..]);
        
        let nonce = aes_gcm::Nonce::from_slice(&nonce_bytes);
        let ciphertext = self.cipher.encrypt(nonce, plaintext)
            .map_err(|e| format!("Encryption failed: {}", e))?;
        
        let mut result = nonce_bytes.clone();
        result.extend(ciphertext);
        Ok(result)
    }

    fn decrypt(&self, encrypted: &[u8]) -> Result<Vec<u8>, Box<dyn Error>> {
        if encrypted.len() < self.nonce_size {
            return Err("Encrypted data too short".into());
        }
        
        let nonce_bytes = &encrypted[..self.nonce_size];
        let ciphertext = &encrypted[self.nonce_size..];
        
        let nonce = aes_gcm::Nonce::from_slice(nonce_bytes);
        let plaintext = self.cipher.decrypt(nonce, ciphertext)
            .map_err(|e| format!("Decryption failed: {}", e))?;
        
        Ok(plaintext)
    }
}


impl EncryptionContext {
    pub fn new() -> Result<Self, Box<dyn Error>> {
        let secret = get_shared_secret();
        let cipher_type = get_cipher_type();
        let nonce_size = get_nonce_size();
        
        let mut hasher = Sha256::new();
        hasher.update(secret.as_bytes());
        let key_bytes = hasher.finalize();
        
        let inner: Box<dyn CipherOps> = match cipher_type.as_str() {
            "aes256gcm" | _ => {
                let key = aes_gcm::Key::<Aes256Gcm>::from_slice(&key_bytes[..]);
                let cipher = Aes256Gcm::new(key);
                Box::new(Aes256GcmCipher { cipher, nonce_size })
            }
        };
        
        Ok(EncryptionContext { inner })
    }

    pub fn encrypt(&self, plaintext: &[u8]) -> Result<Vec<u8>, Box<dyn Error>> {
        self.inner.encrypt(plaintext)
    }

    pub fn decrypt(&self, encrypted: &[u8]) -> Result<Vec<u8>, Box<dyn Error>> {
        self.inner.decrypt(encrypted)
    }
}

pub fn encrypt_message(message: &str) -> Result<Vec<u8>, Box<dyn Error>> {
    let ctx = EncryptionContext::new()?;
    ctx.encrypt(message.as_bytes())
}

pub fn decrypt_message(encrypted: &[u8]) -> Result<String, Box<dyn Error>> {
    let ctx = EncryptionContext::new()?;
    let plaintext = ctx.decrypt(encrypted)?;
    Ok(String::from_utf8(plaintext)?)
}
