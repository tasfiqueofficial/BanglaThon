"""
Lexer (Tokenizer) for Bangla Programming Language
====================================================
Kaj: Raw Bangla (Banglish o Unicode Bangla) source code ke chotto
chotto meaningful token e bhaga.

Example:
    dhori x = 10
    dekhao x
    ধরি নাম = "তাসফিক"
    দেখাও "তুমি কেমন আছো"

Token stream:
    [DHORI, IDENTIFIER(x), ASSIGN, NUMBER(10), NEWLINE, DEKHAO, IDENTIFIER(x)]
"""

import unicodedata


# ---------------------------------------------------------
# 1. KEYWORDS — Banglish & Bangla word -> Token type mapping
# ---------------------------------------------------------
_RAW_KEYWORDS = {
    # Banglish keywords (original syntax)
    "dhori":     "DHORI",       # var/let  -> variable declare
    "jodi":      "JODI",        # if
    "nahole":    "NAHOLE",      # else
    "jotokkhon": "JOTOKKHON",   # while
    "jonno":     "JONNO",       # for
    "kaj":       "KAJ",         # function definition
    "ferot":     "FEROT",       # return
    "dekhao":    "DEKHAO",      # print
    "nao":       "NAO",         # input (take user input)
    "shotti":    "TRUE",        # true
    "mittha":    "FALSE",       # false
    "khali":     "NULL",        # null/none
    "thamo":     "BREAK",       # break
    "cholo":     "CONTINUE",    # continue
    "talika":    "TALIKA",      # list/array
    "ebong":     "AND",         # and
    "ba":        "OR",          # or
    "noy":       "NOT",         # not

    # Native Bangla (বাংলা) keywords
    "ধরি":       "DHORI",       # var/let
    "ধরো":       "DHORI",       # var/let alias
    "যদি":       "JODI",        # if
    "নাহলে":     "NAHOLE",      # else
    "নয়তো":     "NAHOLE",      # else alias
    "যতক্ষণ":    "JOTOKKHON",   # while
    "জন্য":      "JONNO",       # for
    "কাজ":       "KAJ",         # function definition
    "ফেরত":      "FEROT",       # return
    "দেখাও":     "DEKHAO",      # print
    "নাও":       "NAO",         # input
    "সত্যি":     "TRUE",        # true
    "সত্য":      "TRUE",        # true alias
    "মিথ্যা":    "FALSE",       # false
    "খালি":      "NULL",        # null/none
    "থামো":      "BREAK",       # break
    "থাম":       "BREAK",       # break alias
    "চলো":       "CONTINUE",    # continue
    "চল":        "CONTINUE",    # continue alias
    "তালিকা":    "TALIKA",      # list/array
    "এবং":       "AND",         # and
    "বা":        "OR",          # or
    "অথবা":      "OR",          # or alias
    "নয়":       "NOT",         # not (NFC matches both নয় and নয়)
}

# Normalize keys to NFC so decomposed/composed keyboard variants (e.g. য় vs য+়) always match.
KEYWORDS = {unicodedata.normalize("NFC", k): v for k, v in _RAW_KEYWORDS.items()}


# ---------------------------------------------------------
# 2. TOKEN class
# ---------------------------------------------------------
class Token:
    def __init__(self, type_, value, line, col):
        self.type = type_
        self.value = value
        self.line = line
        self.col = col

    def __repr__(self):
        return f"Token({self.type}, {self.value!r}, line={self.line}, col={self.col})"


# ---------------------------------------------------------
# 3. LEXER ERROR
# ---------------------------------------------------------
class LexerError(Exception):
    def __init__(self, message, line, col):
        super().__init__(f"Lexer Error at line {line}, col {col}: {message}")
        self.line = line
        self.col = col


# ---------------------------------------------------------
# 4. LEXER
# ---------------------------------------------------------
class Lexer:
    SINGLE_CHAR_TOKENS = {
        "(": "LPAREN",
        ")": "RPAREN",
        "{": "LBRACE",
        "}": "RBRACE",
        "[": "LBRACKET",
        "]": "RBRACKET",
        ",": "COMMA",
        ";": "SEMICOLON",
        "+": "PLUS",
        "-": "MINUS",
        "*": "STAR",
        "/": "SLASH",
        "%": "PERCENT",
    }

    TWO_CHAR_TOKENS = {
        "==": "EQ",
        "!=": "NEQ",
        "<=": "LTE",
        ">=": "GTE",
        "&&": "AND",
        "||": "OR",
        "**": "POWER",
        "+=": "PLUS_ASSIGN",
        "-=": "MINUS_ASSIGN",
        "*=": "STAR_ASSIGN",
        "/=": "SLASH_ASSIGN",
        "%=": "PERCENT_ASSIGN",
    }

    QUOTE_PAIRS = {
        '"': '"',
        "'": "'",
        "“": "”",
    }

    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.line = 1
        self.col = 1
        self.tokens = []

    # ---- helpers -------------------------------------------------
    def _peek(self, offset=0):
        idx = self.pos + offset
        if idx < len(self.source):
            return self.source[idx]
        return None

    def _advance(self):
        ch = self.source[self.pos]
        self.pos += 1
        if ch == "\n":
            self.line += 1
            self.col = 1
        else:
            self.col += 1
        return ch

    def _add_token(self, type_, value, line, col):
        self.tokens.append(Token(type_, value, line, col))

    @staticmethod
    def _is_bangla_digit(ch):
        # Bengali numerals ০-৯ (U+09E6 to U+09EF)
        return ch is not None and "\u09E6" <= ch <= "\u09EF"

    @staticmethod
    def _is_bangla_letter(ch):
        # Bangla Unicode block (U+0980 to U+09FF) excluding Bengali digits so numbers tokenize cleanly
        return ch is not None and "\u0980" <= ch <= "\u09FF" and not Lexer._is_bangla_digit(ch)

    @staticmethod
    def _is_identifier_start(ch):
        return ch is not None and (
            Lexer._is_bangla_letter(ch)
            or (ch.isalpha() and not Lexer._is_bangla_digit(ch))
            or ch == "_"
        )

    @staticmethod
    def _is_identifier_char(ch):
        return ch is not None and (
            Lexer._is_bangla_letter(ch) or ch.isalnum() or ch == "_"
        )

    # ---- main tokenize loop ---------------------------------------
    def tokenize(self):
        while self.pos < len(self.source):
            ch = self._peek()

            # Skip whitespace and UTF-8 BOM (except newline, which acts as a statement separator)
            if ch in (" ", "\t", "\r", "\ufeff"):
                self._advance()
                continue

            # Newline and Bengali Dari (।) act as statement separators
            if ch in ("\n", "\u0964"):
                line, col = self.line, self.col
                self._advance()
                self._add_token("NEWLINE", "\\n" if ch == "\n" else "।", line, col)
                continue

            # Comments: # eita comment
            if ch == "#":
                while self._peek() is not None and self._peek() != "\n":
                    self._advance()
                continue

            # String literals: "...", '...', or “...”
            if ch in self.QUOTE_PAIRS:
                self._read_string(self.QUOTE_PAIRS[ch])
                continue

            # Numbers: 123, 45.6, ১২৩, ৪৫.৬
            if ch.isdigit():
                self._read_number()
                continue

            # Identifiers / Keywords (Bangla or English letters)
            if self._is_identifier_start(ch):
                self._read_identifier()
                continue

            # Two-char operators
            two = self.source[self.pos:self.pos + 2]
            if two in self.TWO_CHAR_TOKENS:
                line, col = self.line, self.col
                self._advance()
                self._advance()
                self._add_token(self.TWO_CHAR_TOKENS[two], two, line, col)
                continue

            # Single-char operators / punctuation
            if ch in self.SINGLE_CHAR_TOKENS:
                line, col = self.line, self.col
                self._advance()
                self._add_token(self.SINGLE_CHAR_TOKENS[ch], ch, line, col)
                continue

            if ch == "=":
                line, col = self.line, self.col
                self._advance()
                self._add_token("ASSIGN", "=", line, col)
                continue

            if ch == "<":
                line, col = self.line, self.col
                self._advance()
                self._add_token("LT", "<", line, col)
                continue

            if ch == ">":
                line, col = self.line, self.col
                self._advance()
                self._add_token("GT", ">", line, col)
                continue

            if ch == "!":
                line, col = self.line, self.col
                self._advance()
                self._add_token("NOT", "!", line, col)
                continue

            # Unknown character
            raise LexerError(f"Unexpected character {ch!r}", self.line, self.col)

        self._add_token("EOF", None, self.line, self.col)
        return self.tokens

    # ---- sub-readers ------------------------------------------------
    def _read_string(self, close_quote):
        line, col = self.line, self.col
        self._advance()  # skip opening quote
        chars = []
        escape_map = {"n": "\n", "t": "\t", '"': '"', "'": "'", "\\": "\\"}
        while self._peek() is not None and self._peek() != close_quote:
            c = self._advance()
            if c == "\\" and self._peek() is not None:
                nxt = self._advance()
                chars.append(escape_map.get(nxt, nxt))
            else:
                chars.append(c)
        if self._peek() != close_quote:
            raise LexerError("Unterminated string literal", line, col)
        self._advance()  # skip closing quote
        self._add_token("STRING", "".join(chars), line, col)

    def _read_number(self):
        line, col = self.line, self.col
        chars = []
        is_float = False
        while self._peek() is not None and (self._peek().isdigit() or self._peek() == "."):
            c = self._advance()
            if c == ".":
                if is_float:
                    raise LexerError("Invalid number format", line, col)
                is_float = True
            chars.append(c)
        value = float("".join(chars)) if is_float else int("".join(chars))
        self._add_token("NUMBER", value, line, col)

    def _read_identifier(self):
        line, col = self.line, self.col
        chars = []
        while self._is_identifier_char(self._peek()):
            chars.append(self._advance())
        word = unicodedata.normalize("NFC", "".join(chars))
        token_type = KEYWORDS.get(word, "IDENTIFIER")
        self._add_token(token_type, word, line, col)


# ---------------------------------------------------------
# 5. Quick manual test (run: python lexer.py)
# ---------------------------------------------------------
if __name__ == "__main__":
    sample_code = '''
ধরি সংখ্যা = ১০
দেখাও "তুমি কেমন আছো"
যদি (সংখ্যা > ৫ এবং সংখ্যা < ১০০) {
    দেখাও "বড় সংখ্যা"
} নাহলে {
    দেখাও "ছোট সংখ্যা"
}
'''
    lexer = Lexer(sample_code)
    for tok in lexer.tokenize():
        print(tok)
