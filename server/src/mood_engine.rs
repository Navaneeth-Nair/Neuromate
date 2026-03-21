use std::collections::HashMap;
use chrono::{DateTime, Duration, Utc};
use once_cell::sync::Lazy;
use tokio::sync::Mutex;

const DECAY_HOURS: i64 = 62;

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
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
}

#[derive(Clone, Debug)]
pub struct MoodState {
    pub mood: Mood,
    pub last_seen: DateTime<Utc>,
}

impl MoodState {
    pub fn new() -> Self {
        MoodState {
            mood: Mood::Neutral,
            last_seen: Utc::now(),
        }
    }

    pub fn maybe_decay(&mut self) {
        let now = Utc::now();
        if now.signed_duration_since(self.last_seen) > Duration::hours(DECAY_HOURS) {
            self.mood = Mood::Neutral;
        }
    }

    pub fn update_from_sentiment(&mut self, sentiment_delta: i32) {
        let delta = sentiment_delta.signum();
        let new_score = (self.mood.as_score() + delta).clamp(-2, 2);
        self.mood = Mood::from_score(new_score);
        self.last_seen = Utc::now();
    }
}

static MOOD_STORE: Lazy<Mutex<HashMap<String, MoodState>>> = Lazy::new(|| Mutex::new(HashMap::new()));

fn analyze_sentiment(input: &str) -> i32 {
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

pub async fn record_interaction(client_id: &str, message: &str) -> String {
    let sentiment = analyze_sentiment(message);

    let mut store = MOOD_STORE.lock().await;
    let state = store.entry(client_id.to_string()).or_insert_with(MoodState::new);

    state.maybe_decay();
    state.update_from_sentiment(sentiment);

    state.mood.as_str().to_string()
}

pub async fn current_mood(client_id: &str) -> String {
    let store = MOOD_STORE.lock().await;
    if let Some(state) = store.get(client_id) {
        state.mood.as_str().to_string()
    } else {
        Mood::Neutral.as_str().to_string()
    }
}
