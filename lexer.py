"""
Lexer (Tokenizer) for Bangla Programming Language
====================================================
Kaj: Raw Bangla source code ke chotto chotto meaningful token e bhaga.

Example:
    dhori x = 10
    dekhao x

Token stream:
    [DHORI, IDENTIFIER(x), ASSIGN, NUMBER(10), NEWLINE, DEKHAO, IDENTIFIER(x)]
"""

# ---------------------------------------------------------
# 1. KEYWORDS — Bangla word -> Token type mapping
# ---------------------------------------------------------
KEYWORDS = {
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
    # word-based logical operators (alternative to && || !)
    "ebong":     "AND",         # and
    "ba":        "OR",          # or
    "noy":       "NOT",         # not
}

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
    def _is_bangla_letter(ch):
        # Bangla Unicode block: U+0980 to U+09FF
        return ch is not None and "\u0980" <= ch <= "\u09FF"

    @staticmethod
    def _is_identifier_start(ch):
        return ch is not None and (
            Lexer._is_bangla_letter(ch) or ch.isalpha() or ch == "_"
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

            # Skip whitespace (except newline, which we treat as a token
            # so the parser can use it as a statement separator)
            if ch in (" ", "\t", "\r"):
                self._advance()
                continue

            if ch == "\n":
                line, col = self.line, self.col
                self._advance()
                self._add_token("NEWLINE", "\\n", line, col)
                continue

            # Comments: # eita comment
            if ch == "#":
                while self._peek() is not None and self._peek() != "\n":
                    self._advance()
                continue

            # String literals: "..."
            if ch == '"':
                self._read_string()
                continue

            # Numbers: 123, 45.6
            if ch.isdigit():
                self._read_number()
                continue

            # Identifiers / Keywords (Bangla or English letters)
            if self._is_identifier_start(ch):
                self._read_identifier()
                continue

            # Two-char operators: == != <= >= &&  ||
            two = self.source[self.pos:self.pos + 2]
            if two in ("==", "!=", "<=", ">=", "&&", "||"):
                line, col = self.line, self.col
                self._advance()
                self._advance()
                mapping = {
                    "==": "EQ", "!=": "NEQ", "<=": "LTE",
                    ">=": "GTE", "&&": "AND", "||": "OR",
                }
                self._add_token(mapping[two], two, line, col)
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
    def _read_string(self):
        line, col = self.line, self.col
        self._advance()  # skip opening quote
        chars = []
        while self._peek() is not None and self._peek() != '"':
            c = self._advance()
            if c == "\\" and self._peek() is not None:
                nxt = self._advance()
                escape_map = {"n": "\n", "t": "\t", '"': '"', "\\": "\\"}
                chars.append(escape_map.get(nxt, nxt))
            else:
                chars.append(c)
        if self._peek() != '"':
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
        word = "".join(chars)
        token_type = KEYWORDS.get(word, "IDENTIFIER")
        self._add_token(token_type, word, line, col)


# ---------------------------------------------------------
# 5. Quick manual test (run: python lexer.py)
# ---------------------------------------------------------
if __name__ == "__main__":
    sample_code = '''
dhori x = 10
dhori naam = "Tasfique"
dhori nums = talika(1, 2, 3)
jodi (x > 5 ebong x < 100) {
    dekhao "boro shongkha"
} nahole {
    dekhao "choto shongkha"
}
'''
    lexer = Lexer(sample_code)
    for tok in lexer.tokenize():
        print(tok)
