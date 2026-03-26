use std::collections::HashMap;
use chrono::{DateTime, Duration, Utc};
use once_cell::sync::Lazy;
use tokio::sync::Mutex;

const DECAY_HOURS: i64 = 62;
const BASE_ELO: f64 = 1600.0;
const MIN_ELO: f64 = 1000.0;
const MAX_ELO: f64 = 2200.0;
const K_FACTOR: f64 = 32.0;

pub enum Mood {
    VeryNegative,
    Negative,
    Neutral,
    Positive,
    VeryPositive,
}

impl Mood {
    pub fn as_str(&self) -> &'static str {
        match self {
            Mood::VeryNegative => "very negative",
            Mood::Negative => "negative",
            Mood::Neutral => "neutral",
            Mood::Positive => "positive",
            Mood::VeryPositive => "very positive",
        }
    }

    pub fn as_score(&self) -> i32 {
        match self {
            Mood::VeryNegative => -2,
            Mood::Negative => -1,
            Mood::Neutral => 0,
            Mood::Positive => 1,
            Mood::VeryPositive => 2,
        }
    }

    pub fn from_score(score: i32) -> Self {
        match score.clamp(-2, 2) {
            -2 => Mood::VeryNegative,
            -1 => Mood::Negative,
            0 => Mood::Neutral,
            1 => Mood::Positive,
            2 => Mood::VeryPositive,
            _ => Mood::Neutral,
        }
    }

    pub fn from_elo(elo: f64) -> Self {
        match elo {
            e if e < 1200.0 => Mood::VeryNegative,
            e if e < 1400.0 => Mood::Negative,
            e if e < 1800.0 => Mood::Neutral,
            e if e < 2000.0 => Mood::Positive,
            _ => Mood::VeryPositive,
        }
    }
}

pub struct MoodState {
    pub elo_rating: f64,
    pub last_seen: DateTime<Utc>,
}

impl MoodState {
    pub fn new() -> Self {
        MoodState {
            elo_rating: BASE_ELO,
            last_seen: Utc::now(),
        }
    }

    pub fn maybe_decay(&mut self) {
        let now = Utc::now();
        if now.signed_duration_since(self.last_seen) > Duration::hours(DECAY_HOURS) {
            self.elo_rating = BASE_ELO;
        }
    }

    pub fn get_mood(&self) -> Mood {
        Mood::from_elo(self.elo_rating)
    }

    pub fn update_from_sentiment(&mut self, sentiment_delta: i32) {
        let expected_rating = BASE_ELO;
        let actual_performance = if sentiment_delta > 0 { 1.0 } else if sentiment_delta < 0 { 0.0 } else { 0.5 };

        let expected = 1.0 / (1.0 + 10.0_f64.powf((expected_rating - self.elo_rating) / 400.0));
        let rating_change = K_FACTOR * (actual_performance - expected);

        self.elo_rating = (self.elo_rating + rating_change).clamp(MIN_ELO, MAX_ELO);
        self.last_seen = Utc::now();
    }
}

static MOOD_STORE: Lazy<Mutex<HashMap<String, MoodState>>> = Lazy::new(|| Mutex::new(HashMap::new()));

fn analyze_sentiment(input: &str) -> i32 {
    let lowercase = input.to_lowercase();
    let positives = [
        "good", "great", "happy", "glad", "joy", "joyful", "love", "lovely", "awesome",
        "fantastic", "yay", "nice", "cool", "excellent", "wonderful", "amazing", "pleased",
        "excited", "thrilled", "cheerful", "delighted", "grateful", "blessed", "perfect",
    ];
    let negatives = [
        "bad", "sad", "angry", "hate", "terrible", "awful", "upset", "worst", "hated",
        "depressed", "miserable", "horrible", "no", "not",
    ];
    let mut score = 0;

    for word in lowercase.split_whitespace() {
        let token: String = word
            .trim_matches(|c: char| !c.is_alphanumeric())
            .chars()
            .filter(|c| c.is_alphanumeric())
            .collect::<String>()
            .to_lowercase();
        if token.is_empty() {
            continue;
        }
        if positives.iter().any(|p| *p == token) {
            score += 1;
        }
        if negatives.iter().any(|n| *n == token) {
            score -= 1;
        }
    }

    score
}

pub async fn record_interaction(client_id: &str, message: &str) -> (String, f64) {
    let sentiment = analyze_sentiment(message);

    let mut store = MOOD_STORE.lock().await;
    let state = store.entry(client_id.to_string()).or_insert_with(MoodState::new);

    state.maybe_decay();
    state.update_from_sentiment(sentiment);

    let mood = if sentiment != 0 {
        Mood::from_score(sentiment.clamp(-2, 2))
    } else {
        state.get_mood()
    };
    let label = mood.as_str().to_string();
    let elo = state.elo_rating;
    (label, elo)
}

pub async fn current_mood(client_id: &str) -> String {
    let store = MOOD_STORE.lock().await;
    if let Some(state) = store.get(client_id) {
        state.get_mood().as_str().to_string()
    } else {
        Mood::Neutral.as_str().to_string()
    }
}
