import Lexer as lex


def init_Variables()->dict:
    variables = {}
    return variables
 
def add_Variable(variables, variable, valor, funciones)-> None:
    funciones.pop(variable, None) 
    variables[variable] = valor

def del_Variable(variables, variable):
    variables.pop(variable, None)

def get_Value(variables, variable):
    return variables[variable]

def exist_Variable(variables, variable):
    return variable in variables

def init_Funciones():
    funciones = {}
    return funciones

def add_Funcion(funciones, funcion, params, variables)-> None:
    variables.pop(funcion, None)
    funciones[funcion] = params

def del_Funcion(funciones, funcion):
    funciones.pop(funcion, None)

def get_NumberParams(funciones, funcion):
    n = len(funciones[funcion])
    return n

def get_Params(funciones, funcion):
    return funciones[funcion]

def exist_Funcion(funciones, funcion):
    return funcion in funciones

def init_Keywords()->list:
    keywords = ["turnToMy", "turnToThe", "walk", "jump", "drop", "pick", "grab", "letGo", "pop",
                "moves", "nop", "safeExe"]
    return keywords



def recorrer_Lista(lista, variables, keywords, funciones, 
                    inside_if=False, inside_block=False, inside_func=False):
    """
    Hace el recorrido por la lista de tokens
    """
    correcto = True
    newCommand = True
    stop = False
    
    if inside_block:
        minimo_1Command = False

    i = 0
    while i < len(lista) and correcto and not stop:
        
        
        if lista[i][0] == "EXEC":
            if lista[i+1][0]!="LBRACE":
                correcto=False
                stop=True
        
        elif inside_block and lista[i][0] == ")":
            i -= 1
            stop = True
            if not minimo_1Command:
                correcto = False
        
        elif inside_func and lista[i][0] == "END":
            i -= 1
            stop = True
        
        elif lista[i][0] == "EXEC":
            newCommand = True
        
        elif newCommand == True :
            CommandName = lista[i]
            correcto, termina_en = isCommand(CommandName, i, lista, variables, keywords, funciones)
            if inside_block and not minimo_1Command and correcto:
                minimo_1Command = True
                
            i = termina_en
            newCommand = False

        else:
            correcto = False
        
        #print("correcto:",correcto)
        i+=1

    return correcto, i

def isCommand(CommandName, i, lista, variables, keywords, funciones):
    "Verifica si el comando es correcto y regresa en qué parte de la lista termina este comando"

    correcto = False
    termina_en = i

    tipo1 = ["MOVE", "RIGHT", "LEFT", "ROTATE", "DROP", "FREE", "PICK", "POP"]
    if CommandName in tipo1:
        #print("T1. lista[i="+str(i)+"] " +lista[i])
        if is_Type(variables, lista[i+1], "numero"):
            termina_en = i+1
            correcto = True

    elif CommandName == "LOOK":
        #print("T2. lista[i="+str(i)+"] " +lista[i])
        if is_Type(variables, lista[i+1], "direccion"):
            termina_en = i+1
            correcto = True

    elif CommandName == "CHECK":
        #print("T3. lista[i="+str(i)+"] " +lista[i])
        if is_Type(variables, lista[i+1], "opcion"):
            if is_Type(variables, lista[i+2], "numero"):
                termina_en = i+2
                correcto = True

    elif CommandName == "BLOCKEDP" or CommandName == "NOP":
        #print("T4. lista[i="+str(i)+"] " +lista[i])
        termina_en = i
        correcto = True
    
    elif CommandName == "DEFINE":
        #print("T5. lista[i="+str(i)+"] " +lista[i])
        if lista[i+1].islower():    
            if is_Type(variables, lista[i+2], "numero"):
                add_Variable(variables, lista[i+1], lista[i+2], funciones)
                termina_en = i+2
                correcto = True
            else:
                print("Debe ingresar un número entero como valor de la variable")
        else:
            print("El nombre de la variable debe ser un string en minúsculas")

    elif CommandName == "IF":
        #print("T6. lista[i="+str(i)+"] " +lista[i])
        if lista[i+1] == "BLOCKEDP" or lista[i+2] == "!BLOCKEDP":
            if lista[i+2] == "[":
                correcto, j = recorrer_Lista(lista[i+3:], variables, keywords, funciones, inside_if=True)
                termina_en = i+3+j
        else:
            print("La expresión del IF debe ser booleana")  

    elif CommandName == "(":
        #print("T7. lista[i="+str(i)+"] " +lista[i])

        if lista[i+1] == "BLOCK":
            correcto, j = recorrer_Lista(lista[i+2:], variables, keywords, funciones, inside_block=True)
            termina_en = i+2+j
        
        elif lista[i+1] == "REPEAT":
            if is_Type(variables, lista[i+2], "numero"):
                if lista[i+3] == "[":
                    correcto, j = recorrer_Lista(lista[i+4:], variables, keywords, funciones, inside_if=True)
                    i += 4+j
                    if correcto:
                        i, correcto = ignore_Newlines(i+1, lista)
                        if lista[i] == ")" and correcto:
                            termina_en = i

    elif CommandName == "TO":
        #print("T8. lista[i="+str(i)+"] " +lista[i])
        if lista[i+1] not in keywords:
            j = 2
            parametros = []
            while ":" == lista[i+j][0]:  
                parametros.append(lista[i+j])
                add_Variable(variables, lista[i+j], None, funciones)
                j += 1
            add_Funcion(funciones, lista[i+1], parametros, variables)
            i, correcto = ignore_Newlines(i+j, lista)
            if lista[i] == "OUTPUT":
                correcto, k = recorrer_Lista(lista[i+1:], variables, keywords, funciones, inside_func=True)
                if correcto:
                    termina_en = i+1+k
                    correcto = True
                    for variable in parametros:
                        del_Variable(variables, variable)

    else:
        if CommandName in funciones:
            n = get_NumberParams(funciones, CommandName)

            params_validos = True
            if i+n <= len(lista)-1:
                for j in range(1, n+1):
                    if not is_Type(variables, lista[i+j], "numero"):
                        params_validos = False
            else: 
                params_validos = False

            if params_validos:
                correcto = True
                termina_en = i+n
            
    return correcto, termina_en

def is_Type(variables, string, tipo):
    """
    Verifica si es del tipo correcto
    """
    es_tipo = False
    if tipo == "numero":
        if string.isdigit() or (exist_Variable(variables,string) and (get_Value(variables,string) == None or get_Value(variables,string).isdigit())):
            es_tipo = True
    
    elif tipo == "direccion":
        direcciones = ["N", "S", "W", "E"]
        if string in direcciones or (exist_Variable(variables,string) and (get_Value(variables,string) in direcciones or get_Value(variables,string) == None)):
            es_tipo = True
    
    elif tipo == "opcion":
        opciones = ["C", "B"]
        if string in opciones or (exist_Variable(variables,string) and (get_Value(variables,string) in opciones or get_Value(variables,string) == None)):
            es_tipo = True
        
    return es_tipo


def ignore_Newlines(i, lista):
    """
    i: posición desde la cual debe empezar a ignorar los newlines (primer newline)
    retorna: posición del último newline
    """
    correcto = True
    if lista[i] == "NEWLINE":
        while lista[i+1] == "NEWLINE":
            i+=1
            if i == len(lista)-1:
                correcto = False
                break
        i += 1          

    return i, correcto

def iniciar_Programa():

    variables = init_Variables()
    keywords = init_Keywords()
    funciones = init_Funciones()

    tokens = lex.lexer_funcioamiento("prueba.txt")

    #resultado, _ = recorrer_Lista(tokens, variables, keywords, funciones)
    #if resultado:
    #    print("The syntax is CORRECT.")
    ##else:
    #    print("The syntax is INCORRECT.")

iniciar_Programa()

