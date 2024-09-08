import re


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
    ("TIMES",r'times\b'),
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
    #("STRING", r'"[^"]*"')
    #,("?",r"\?")  
]


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


#Ejemplo:

def lexer_funcioamiento(txt):
    with open(txt, 'r') as file:
        code = file.read()
    lista_tokens=[]
    for token in lexer(code):
        #print(token)
        lista_tokens.append(token)
    #print(lista_tokens)
    return lista_tokens

lexer_funcioamiento("prueba3.txt")