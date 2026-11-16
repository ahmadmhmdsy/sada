//! Arabic post-processing for MCP transcript output.
//!
//! This is the Rust twin of desktop/src/lib/arabic-text.ts and must stay byte-for-byte
//! equivalent: the app normalises every transcript it shows, saves or exports, so an agent
//! reading through MCP must see the same polished text — Arabic punctuation instead of ASCII
//! commas, no space before Arabic punctuation, and common Latin acronyms restored from the
//! spellings whisper.cpp produces.
//!
//! The rules are deliberately lossless and idempotent: no words are added, removed or reordered,
//! and Latin text, numbers and URLs are left alone. The JavaScript tests in
//! arabic-text.test.ts are reproduced here so the two implementations cannot drift silently.

const ARABIC_RANGES: [(u32, u32); 5] = [
    (0x0600, 0x06FF),
    (0x0750, 0x077F),
    (0x08A0, 0x08FF),
    (0xFB50, 0xFDFF),
    (0xFE70, 0xFEFF),
];

/// Keep in sync with ARABIC_CHAR in desktop/src/lib/arabic-text.ts.
pub fn is_arabic_char(character: char) -> bool {
    let code = character as u32;
    ARABIC_RANGES.iter().any(|(start, end)| code >= *start && code <= *end)
}

/// Whether a string contains any Arabic character. Text without Arabic is returned untouched.
pub fn contains_arabic(text: &str) -> bool {
    text.chars().any(is_arabic_char)
}

/// Spellings whisper.cpp produces for terms that are normally written in Latin inside Arabic
/// text. Order matters only for overlapping spellings; keep it identical to the TypeScript list.
type Acronym = (&'static [&'static [&'static str]], &'static str);

const ACRONYMS: [Acronym; 9] = [
    (&[&["جي", "جى"], &["بي", "بى"], &["يو", "يوا"]], "GPU"),
    (&[&["سي", "سى"], &["بي", "بى"], &["يو", "يوا"]], "CPU"),
    (&[&["بي", "بى"], &["دي", "دى"], &["إف", "اف", "أف"]], "PDF"),
    (&[&["إس", "اس", "أس"], &["آر", "ار", "أر"], &["تي", "تى"]], "SRT"),
    (&[&["في", "فى"], &["تي", "تى"], &["تي", "تى"]], "VTT"),
    (&[&["جيسون", "جسون", "جيسُن"]], "JSON"),
    (&[&["إيه", "ايه", "إي"], &["بي", "بى"], &["آي", "اي", "أي"]], "API"),
    (
        &[
            &["إف", "اف", "أف"],
            &["إف", "اف", "أف"],
            &["إم", "ام", "أم"],
            &["بيغ", "بيج", "بغ"],
        ],
        "FFmpeg",
    ),
    (&[&["ويسبر", "ويسپر", "ويسْبر"]], "Whisper"),
];

/// Match one token (a fixed Arabic spelling) at position; returns the position after it.
fn match_token(characters: &[char], position: usize, token: &str) -> Option<usize> {
    let token: Vec<char> = token.chars().collect();
    if token.is_empty() || position + token.len() > characters.len() {
        return None;
    }
    (characters[position..position + token.len()] == token[..]).then_some(position + token.len())
}

/// Try every acronym spelling starting at start; returns the end position and replacement.
fn match_acronym(characters: &[char], start: usize) -> Option<(usize, &'static str)> {
    for (pattern, replacement) in ACRONYMS {
        let mut position = start;
        let mut matched = true;
        for (index, alternatives) in pattern.iter().enumerate() {
            if index > 0 {
                while position < characters.len()
                    && (characters[position] == ' ' || characters[position] == '\t')
                {
                    position += 1;
                }
            }
            match alternatives
                .iter()
                .find_map(|alternative| match_token(characters, position, alternative))
            {
                Some(end) => position = end,
                None => {
                    matched = false;
                    break;
                }
            }
        }
        if !matched {
            continue;
        }
        let starts_cleanly = start == 0 || !is_arabic_char(characters[start - 1]);
        let ends_cleanly = position >= characters.len() || !is_arabic_char(characters[position]);
        if starts_cleanly && ends_cleanly {
            return Some((position, replacement));
        }
    }
    None
}

/// Collapse runs of spaces and tabs to one space, exactly like the TypeScript rule.
fn collapse_horizontal_whitespace(text: &str) -> String {
    let mut collapsed = String::with_capacity(text.len());
    let mut run = 0usize;
    for character in text.chars() {
        if character == ' ' || character == '\t' {
            run += 1;
            continue;
        }
        if run > 0 {
            collapsed.push(' ');
            run = 0;
        }
        collapsed.push(character);
    }
    if run > 0 {
        collapsed.push(' ');
    }
    collapsed
}

/// Trim trailing spaces and tabs on every line, like the multiline end-of-line rule.
fn trim_line_ends(text: &str) -> String {
    text.split('\n')
        .map(|line| line.trim_end_matches([' ', '\t']))
        .collect::<Vec<_>>()
        .join("\n")
}

/// Normalise Arabic transcript text. Returns the input untouched when it contains no Arabic.
pub fn normalize_arabic(text: &str) -> String {
    if text.is_empty() || !contains_arabic(text) {
        return text.to_string();
    }

    let characters: Vec<char> = text.chars().collect();
    let mut output = String::with_capacity(text.len());
    let mut index = 0usize;

    while index < characters.len() {
        if let Some((end, replacement)) = match_acronym(&characters, index) {
            output.push_str(replacement);
            index = end;
            continue;
        }

        let character = characters[index];
        match character {
            // ASCII punctuation after Arabic becomes Arabic punctuation, with exactly one space
            // after it. The single space is trimmed again by the line-end rule.
            ',' | '?' | ';' => {
                let end = output.trim_end_matches([' ', '\t']).len();
                let previous_is_arabic = output[..end].chars().next_back().is_some_and(is_arabic_char);
                if previous_is_arabic {
                    output.truncate(end);
                    output.push(match character {
                        ',' => '،',
                        '?' => '؟',
                        _ => '؛',
                    });
                    let mut next = index + 1;
                    while next < characters.len()
                        && (characters[next] == ' ' || characters[next] == '\t')
                    {
                        next += 1;
                    }
                    output.push(' ');
                    index = next;
                    continue;
                }
            }
            // Arabic punctuation hugs the word before it; whisper often leaves a space.
            '،' | '؛' | '؟' => {
                while output.ends_with(' ') || output.ends_with('\t') {
                    output.pop();
                }
                output.push(character);
                index += 1;
                continue;
            }
            _ => {}
        }

        output.push(character);
        index += 1;
    }

    trim_line_ends(&collapse_horizontal_whitespace(&output))
}

#[cfg(test)]
mod tests {
    use super::normalize_arabic;

    #[test]
    fn leaves_english_text_untouched() {
        let text = "Hello, world? Yes; fine.";
        assert_eq!(normalize_arabic(text), text);
    }

    #[test]
    fn rewrites_ascii_punctuation_that_follows_arabic() {
        let text = "مرحبا , كيف حالك? بخير; شكرا";
        assert_eq!(normalize_arabic(text), "مرحبا، كيف حالك؟ بخير؛ شكرا");
    }

    #[test]
    fn removes_the_space_whisper_leaves_before_arabic_punctuation() {
        assert_eq!(normalize_arabic("نص عربي ، ثم سؤال ؟"), "نص عربي، ثم سؤال؟");
    }

    #[test]
    fn restores_common_latin_acronyms() {
        assert_eq!(
            normalize_arabic("استخدم جي بي يو لتسريع تحسين الصوت"),
            "استخدم GPU لتسريع تحسين الصوت"
        );
        assert_eq!(normalize_arabic("ملف بي دي إف جاهز"), "ملف PDF جاهز");
        assert_eq!(normalize_arabic("حفظ بصيغة إس آر تي"), "حفظ بصيغة SRT");
        assert_eq!(normalize_arabic("رابط إيه بي آي محلي"), "رابط API محلي");
        assert_eq!(normalize_arabic("حفظ بصيغة في تي تي"), "حفظ بصيغة VTT");
        assert_eq!(normalize_arabic("مخرجات جيسون"), "مخرجات JSON");
        assert_eq!(normalize_arabic("أداة إف إف إم بيغ"), "أداة FFmpeg");
        assert_eq!(normalize_arabic("نموذج ويسبر"), "نموذج Whisper");
        assert_eq!(normalize_arabic("المعالج سي بي يو"), "المعالج CPU");
    }

    #[test]
    fn does_not_touch_the_inside_of_latin_words_or_urls() {
        let text = "افتح https://example.com/a,b ثم اقرأ الملف";
        assert_eq!(normalize_arabic(text), text);
    }

    #[test]
    fn is_idempotent() {
        let once = normalize_arabic("مرحبا ، هذا جي بي يو ؟");
        assert_eq!(normalize_arabic(&once), once);
    }

    #[test]
    fn keeps_empty_and_whitespace_only_text() {
        assert_eq!(normalize_arabic(""), "");
        assert_eq!(normalize_arabic("   "), "   ");
    }

    #[test]
    fn leaves_arabic_punctuation_without_a_preceding_space_alone() {
        assert_eq!(normalize_arabic("مرحبا، كيف حالك؟"), "مرحبا، كيف حالك؟");
    }

    #[test]
    fn collapses_double_spaces_only_when_arabic_is_present() {
        assert_eq!(normalize_arabic("مرحبا  بك"), "مرحبا بك");
        assert_eq!(normalize_arabic("hello  there"), "hello  there");
    }
}
