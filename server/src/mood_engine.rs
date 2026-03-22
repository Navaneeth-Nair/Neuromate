use std::collections::HashMap;
use chrono::{DateTime, Duration, Utc};
use once_cell::sync::Lazy;
use tokio::sync::Mutex;

const _x1: i64 = 62;
const _x2: f64 = 1600.0;
const _x3: f64 = 1000.0;
const _x4: f64 = 2200.0;
const _x5: f64 = 32.0;

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum _M {
    VeryNegative,
    Negative,
    Neutral,
    Positive,
    VeryPositive,
}

impl _M {
    pub fn _a(&self) -> &'static str {
        match self {
            _M::VeryNegative => "very negative",
            _M::Negative => "negative",
            _M::Neutral => "neutral",
            _M::Positive => "positive",
            _M::VeryPositive => "very positive",
        }
    }

    pub fn _b(&self) -> i32 {
        match self {
            _M::VeryNegative => -2,
            _M::Negative => -1,
            _M::Neutral => 0,
            _M::Positive => 1,
            _M::VeryPositive => 2,
        }
    }

    pub fn _c(score: i32) -> Self {
        match score.clamp(-2, 2) {
            -2 => _M::VeryNegative,
            -1 => _M::Negative,
            0 => _M::Neutral,
            1 => _M::Positive,
            2 => _M::VeryPositive,
            _ => _M::Neutral,
        }
    }

    pub fn _d(elo: f64) -> Self {
        match elo {
            e if e < 1200.0 => _M::VeryNegative,
            e if e < 1400.0 => _M::Negative,
            e if e < 1800.0 => _M::Neutral,
            e if e < 2000.0 => _M::Positive,
            _ => _M::VeryPositive,
        }
    }
}

#[derive(Clone, Debug)]
pub struct _S {
    pub elo_rating: f64,
    pub last_seen: DateTime<Utc>,
}

impl _S {
    pub fn _e() -> Self {
        _S {
            elo_rating: _x2,
            last_seen: Utc::now(),
        }
    }

    pub fn _f(&mut self) {
        let now = Utc::now();
        if now.signed_duration_since(self.last_seen) > Duration::hours(_x1) {
            self.elo_rating = _x2;
        }
    }

    pub fn _g(&self) -> _M {
        _M::_d(self.elo_rating)
    }

    pub fn _h(&mut self, sentiment_delta: i32) {
        let expected_rating = _x2;
        let actual_performance = if sentiment_delta > 0 { 1.0 } else if sentiment_delta < 0 { 0.0 } else { 0.5 };
        
        let expected = 1.0 / (1.0 + 10.0_f64.powf((expected_rating - self.elo_rating) / 400.0));
        let rating_change = _x5 * (actual_performance - expected);
        
        self.elo_rating = (self.elo_rating + rating_change).clamp(_x3, _x4);
        self.last_seen = Utc::now();
    }
}

static _z: Lazy<Mutex<HashMap<String, _S>>> = Lazy::new(|| Mutex::new(HashMap::new()));

fn _i(input: &str) -> i32 {
    let lowercase = input.to_lowercase();
    let positives = ["good", "great", "happy", "love", "awesome", "fantastic", "yay", "nice", "cool", "excellent"];
    let negatives = ["bad", "sad", "angry", "hate", "terrible", "awful", "upset", "worst", "no", "not"];
    let mut score = 0;

    for word in lowercase.split_whitespace() {
        let token = word.trim_matches(|c: char| !c.is_alphanumeric());
        if positives.contains(&token) {
            score += 1;
        }
        if negatives.contains(&token) {
            score -= 1;
        }
    }

    score
}

pub async fn _j(client_id: &str, message: &str) -> String {
    let sentiment = _i(message);

    let mut store = _z.lock().await;
    let state = store.entry(client_id.to_string()).or_insert_with(_S::_e);

    state._f();
    state._h(sentiment);

    state._g()._a().to_string()
}

pub async fn _k(client_id: &str) -> String {
    let store = _z.lock().await;
    if let Some(state) = store.get(client_id) {
        state._g()._a().to_string()
    } else {
        _M::Neutral._a().to_string()
    }
}
