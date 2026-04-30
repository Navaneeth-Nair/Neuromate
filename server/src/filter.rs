


const HARMFUL_PATTERNS: &[&str] = &[
    "kill yourself",
    "suicide",
    "hurt yourself",
    "harm yourself",
    "cut yourself",
    "end your life",
    "worthless",
    "no one cares",
    "better off dead",
    "die",
    "should die",
    "nobody loves you",
    "hopeless",
    "give up",
    "useless",
    "hate yourself",
    "self-harm",
    "take your life",
    "you should not exist",
    
];

pub fn sanitize_response(response: &str) -> String {
    let lower = response.to_lowercase();
    for pattern in HARMFUL_PATTERNS {
        if lower.contains(pattern) {
            return "Sorry, I can't assist with that.".to_string();
        }
    }
    response.to_string()
}
