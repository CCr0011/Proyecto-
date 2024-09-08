import re

# Token definitions
tokens = [
    ("EXEC", r'EXEC\b'),
    ("NEW_VAR", r'NEW VAR\b'),
    ("NEW_MACRO", r'NEW MACRO\b'),
    ("IF", r'if\b'),
    ("ELSE", r'else\b'),
    ("THEN", r'then\b'),
    ("FI", r'fi\b'),
    ("DO", r'do\b'),
    ("OD", r'od\b'),
    ("REPEAT", r'rep\b'),
    ("TIMES", r'times\b'),
    ("PER", r'per\b'),
    ("BLOCKED", r'isBlocked\?'),
    ("ZERO", r'zero\?'),
    ("NOT", r'not\b'),
    ("ISFACING", r'isFacing\?'),
    ("VAR", r'[a-zA-Z_][a-zA-Z0-9_]*'),
    ("NUMBER", r'\d+'),
    ("LBRACE", r'\{'),
    ("RBRACE", r'\}'),
    ("LPAREN", r'\('),
    ("RPAREN", r'\)'),
    ("SEMICOLON", r';'),
    ("EQUAL", r'='),
    ("COMMA", r','),
    ("WHITESPACE", r'\s+'),
    ("COMMENT", r'//[^\n]*')
]

# Lexer function
def lexer(code):
    pos = 0
    while pos < len(code):
        match = None
        for token_type, regex in tokens:
            pattern = re.compile(regex)
            match = pattern.match(code, pos)
            if match:
                text = match.group(0)
                if token_type != "WHITESPACE" and token_type != "COMMENT":
                    yield (token_type, text)
                pos = match.end(0)
                break
        if not match:
            raise SyntaxError(f"Unexpected character: {code[pos]}")

# Simplified parsing function
def parse_tokens(tokens):
    i = 0
    length = len(tokens)

    def expect(expected_type):
        nonlocal i
        if i < length and tokens[i][0] == expected_type:
            i += 1
        else:
            print(tokens[i-2][1])
            print(tokens[i-1][1])
            print(tokens[i][1])
            print(tokens[i+1][1])
            print(print(tokens[i+2][1]))
            raise SyntaxError(f"Expected {expected_type} but found {tokens[i]}")

    def parse_exec():
        expect("EXEC")
        expect("LBRACE")
        while tokens[i][0] != "RBRACE":
            parse_statement()
        expect("RBRACE")

    def parse_new_var():
        expect("NEW_VAR")
        expect("VAR")
        expect("EQUAL")
        expect("NUMBER")
        expect("SEMICOLON")

    def parse_new_macro():
        expect("NEW_MACRO")
        expect("VAR")  # Macro name
        expect("LPAREN")
        while tokens[i][0] != "RPAREN":
            expect("VAR")
            if tokens[i][0] == "COMMA":
                expect("COMMA")
        expect("RPAREN")
        expect("LBRACE")
        while tokens[i][0] != "RBRACE":
            parse_statement()
        expect("RBRACE")

    def parse_statement():
        if tokens[i][0] == "IF":
            parse_if()
        elif tokens[i][0] == "DO":
            parse_do()
        elif tokens[i][0] == "REPEAT":
            parse_repeat()
        elif tokens[i][0] == "VAR":
            if i + 1 < length and tokens[i + 1][0] == "EQUAL":
                parse_assignment()
            else:
                parse_function_call()
        else:
            raise SyntaxError(f"Unexpected statement start {tokens[i]}")

    def parse_assignment():
        expect("VAR")
        expect("EQUAL")
        expect("NUMBER")
        expect("SEMICOLON")

    def parse_function_call():
        expect("VAR")
        expect("LPAREN")
        while tokens[i][0] != "RPAREN":
            if tokens[i][0] == "VAR" or tokens[i][0] == "NUMBER":
                expect(tokens[i][0])
            if tokens[i][0] == "COMMA":
                expect("COMMA")
        expect("RPAREN")
        expect("SEMICOLON")

    def parse_if():
        expect("IF")
        expect("NOT")
        expect("LPAREN")
        expect("BLOCKED")
        expect("LPAREN")
        expect("VAR")
        expect("RPAREN")
        expect("RPAREN")
        expect("THEN")
        expect("LBRACE")
        while tokens[i][0] != "RBRACE":
            parse_statement()
        expect("RBRACE")
        if tokens[i][0] == "ELSE":
            expect("ELSE")
            expect("LBRACE")
            while tokens[i][0] != "RBRACE":
                parse_statement()
            expect("RBRACE")
        expect("FI")

    def parse_do():
        expect("DO")
        expect("NOT")
        expect("ZERO")
        expect("LPAREN")
        expect("VAR")
        expect("RPAREN")
        expect("LBRACE")
        while tokens[i][0] != "RBRACE":
            parse_statement()
        expect("RBRACE")
        expect("OD")

    def parse_repeat():
        expect("REPEAT")
        expect("VAR")
        expect("TIMES")
        expect("LBRACE")
        while tokens[i][0] != "RBRACE":
            parse_statement()
        expect("RBRACE")

    while i < length:
        token_type = tokens[i][0]
        if token_type == "EXEC":
            parse_exec()
        elif token_type == "NEW_VAR":
            parse_new_var()
        elif token_type == "NEW_MACRO":
            parse_new_macro()
        else:
            raise SyntaxError(f"Unexpected token {tokens[i]}")

    print("Parsing complete: no errors found.")

# Function to execute lexer and parser
def lexer_and_parser(file_path):
    with open(file_path, 'r') as file:
        code = file.read()
    
    tokens = list(lexer(code))
    parse_tokens(tokens)

# Run the lexer and parser on a sample file
lexer_and_parser("prueba.txt")

