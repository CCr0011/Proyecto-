import re
import Lexer as lex

# Lists of valid commands
commands_list_1 = ["walk", "jump", "drop", "pick", "grab", "letgo", "pop"]
commands_list_2 = ["turnToMy", "turnToThe"]
commands_list_3 = ["moves", "safeExe"]

valid_turnToMy_vars = ["left", "right", "back"]
valid_turnToThe_vars = ["north", "south", "east", "west"]
valid_moves_vars = ["forward", "right", "left", "backwards"]

def parse(tokens):
    tokens = list(tokens)  # Convert the tokens iterator to a list for easy access
    current_index = -1  # Start before the first token

    def advance():
        nonlocal current_index
        current_index += 1
        if current_index < len(tokens):
            return tokens[current_index]
        return None
    
    def goback():
        nonlocal current_index
        if current_index > 0:
            current_index -= 1
        return tokens[current_index] if current_index >= 0 else None

    def current_token():
        if 0 <= current_index < len(tokens):
            return tokens[current_index]
        return None

    def get_token_slice(index, before=3, after=3):
        start = max(0, index - before)
        end = min(len(tokens), index + after + 1)
        return tokens[start:end]

    def expect(token_type, value=None):
        token = current_token()
        if token is None:
            raise SyntaxError(f"Expected {token_type} but found end of input")
        if token[0] != token_type or (value is not None and token[1] != value):
            surrounding_tokens = get_token_slice(current_index)
            raise SyntaxError(f"Expected {token_type}{' with value ' + value if value else ''} but found {token}. Context: {surrounding_tokens}")
        advance()

    def parse_condition():
        if current_token()[0] == "NOT":
            advance()
            expect("LPAREN")
            parse_condition()
            expect("RPAREN")
        elif current_token()[0] in ["BLOCKED", "ISFACING", "ZERO"]:
            advance()
            expect("LPAREN")
            expect("VAR")
            expect("RPAREN")
        else:
            surrounding_tokens = get_token_slice(current_index, before=3, after=3)
            raise SyntaxError(f"Invalid token following '{current_token()}'. Context: {surrounding_tokens}")

    def parse_if_statement():
        expect("IF")
        parse_condition()
        expect("THEN")
        parse_block()
        if current_token() and current_token()[0] == "ELSE":
            advance()
            parse_block()
        expect("FI")
        expect("SEMICOLON")

    def parse_do_statement():
        expect("DO")
        if current_token()[0] =="NOT":
            advance()
            parse_condition()
        parse_block()
        expect("OD")
        expect("SEMICOLON")

    def parse_repeat_statement():
        expect("REPEAT")
        if current_token()[0] == "NUMBER" or current_token()[0] == "VAR":
                advance()
        else:
            surrounding_tokens = get_token_slice(current_index, before=3, after=3)
            raise SyntaxError(f"Invalid token following '{current_token()}'. Expected 'NUMBER' or 'VAR'. Context: {surrounding_tokens}")
        expect("TIMES")
        parse_block()

    def parse_exec_block():
        expect("EXEC")
        parse_block()

    def parse_var_declaration():
        expect("NEW_VAR")
        expect("VAR")
        expect("EQUAL")
        if current_token()[0] == "NUMBER" or current_token()[0] == "VAR":
                advance()
        else:
            surrounding_tokens = get_token_slice(current_index, before=3, after=3)
            raise SyntaxError(f"Invalid token following '{current_token()}'. Expected 'NUMBER' or 'VAR'. Context: {surrounding_tokens}")
    macros=[]
    def parse_macro_declaration():
        expect("NEW_MACRO")
        macros.append(current_token()[1])
        expect("VAR")
        expect("LPAREN")
        while current_token() and current_token()[0] != "RPAREN":
            expect("VAR")
            if current_token()[0] == "COMMA":
                advance()
        expect("RPAREN")
        parse_block()

    def parse_command(command):
        if command in commands_list_1:
            # Commands from list 1 must be followed by a number inside parentheses
            expect("LPAREN")
            if current_token()[0] == "NUMBER" or current_token()[0] == "VAR":
                advance()
            else:
                surrounding_tokens = get_token_slice(current_index, before=3, after=3)
                raise SyntaxError(f"Invalid token following '{command}'. Expected 'NUMBER' or 'VAR'. Context: {surrounding_tokens}")
            expect("RPAREN")
        elif command in commands_list_2:
            # Commands from list 2 have different requirements
            expect("LPAREN")
            if command == "turnToMy":
                #expect("VAR")
                direction = current_token()[1]
                if direction not in valid_turnToMy_vars:
                    surrounding_tokens = get_token_slice(current_index, before=3, after=3)
                    raise SyntaxError(f"Invalid direction '{direction}' for command 'turnToMy'. Expected one of {valid_turnToMy_vars}. Context: {surrounding_tokens}")
            elif command == "turnToThe":
                #expect("VAR")
                direction = current_token()[1]
                if direction not in valid_turnToThe_vars:
                    surrounding_tokens = get_token_slice(current_index, before=3, after=3)
                    raise SyntaxError(f"Invalid direction '{direction}' for command 'turnToThe'. Expected one of {valid_turnToThe_vars}. Context: {surrounding_tokens}")
            advance()  # Move past the VAR
            expect("RPAREN")
        elif command in commands_list_3:
            expect("LPAREN")
            if command == "moves":
                while current_token() and current_token()[0] != "RPAREN":
                    token_type, token_value = current_token()
                    if token_type == "VAR" and token_value in valid_moves_vars:
                        advance()
                    elif token_type == "COMMA":
                        advance()
                    else:
                        surrounding_tokens = get_token_slice(current_index, before=3, after=3)
                        raise SyntaxError(f"Invalid token '{current_token()}' in 'moves' command. Context: {surrounding_tokens}")        
                    
            elif command == "safeExe":
                sub_command = current_token()[1]
                expect("VAR")
                if sub_command not in commands_list_1:
                    surrounding_tokens = get_token_slice(current_index, before=3, after=3)
                    raise SyntaxError(f"Invalid command '{sub_command}' for 'safeExe'. Expected one of {commands_list_1}. Context: {surrounding_tokens}")
                parse_command(sub_command)  # Recursively parse the sub-command
            expect("RPAREN")

    def parse_statement():
        token = current_token()
        if token is None:
            return
        if token[0] == "IF":
            parse_if_statement()
        elif token[0] == "DO":
            parse_do_statement()
        elif token[0] == "REPEAT":
            parse_repeat_statement()
        elif token[0] == "EXEC":
            parse_exec_block()
        elif token[0] == "NEW_VAR":
            parse_var_declaration()
        elif token[0] == "NEW_MACRO":
            parse_macro_declaration()
        elif token[0] == "VAR":
            command = token[1]
            if command in commands_list_1 or command in commands_list_2 or command in commands_list_3:
                advance()
                parse_command(command)
            elif command in macros:
                # Handle macro invocation
                advance()
                expect("LPAREN")
                while current_token() and current_token()[0] != "RPAREN":
                    if current_token()[0] == "VAR":
                        advance()
                    elif current_token()[0] == "COMMA":
                        advance()
                    elif current_token()[0] == "NUMBER":
                        advance()
                    else:
                        surrounding_tokens = get_token_slice(current_index, before=3, after=3)
                        raise SyntaxError(f"Invalid token '{current_token()}' in macro call. Context: {surrounding_tokens}")
                expect("RPAREN")
            else:
                advance()
                if current_token()[0] == "EQUAL":
                    expect("EQUAL")
                    expect("NUMBER")
            expect("SEMICOLON")
        elif token[0]=="SEMICOLON":
            advance()
        else:
            raise SyntaxError(f"Unexpected token in statement: {token}. Context: {get_token_slice(current_index)}")
        
    def parse_block():
        expect("LBRACE")
        while current_token() and current_token()[0] != "RBRACE":
            parse_statement()
        expect("RBRACE")

    # Start parsing
    advance()
    while current_token():
        parse_statement()

tokens = lex.lexer_funcioamiento("prueba.txt")
try:
    parse(tokens)
    print("Code parsed successfully.")
except SyntaxError as e:
    print(f"Parsing failed: {e}")
