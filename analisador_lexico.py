# Alunos:
# Guilherme Brunassi Nogima (nUSP: 9771629)
# João Pedro Silva Mambrini Ruiz (nUSP: 9771675)

import os.path
import getopt, sys 

invalid_chars = ['@']
special_chars = ['-', '+', ':', '=', ';', '.', '(', ')', ',', '*', '/']
relational_ops = ['>', '=', '<']

# Dicionário contendo as palavras e símbolos reservados, com seus respectivos tokens
reserved = {
"program": "simb_program",
"begin": "simb_begin",
"end": "simb_end",
"const": "simb_const",
"var": "simb_var",
"real": "simb_real",
"integer": "simb_int",
"procedure": "simb_procedure",
"if": "simb_if",
"then": "simb_then",
"else": "simb_else",
"read": "simb_read",
"write": "simb_write",
"while": "simb_while",
"for": "simb_for",
"to": "simb_to",
"do": "simb_do",
",": "simb_v",
";": "simb_pv",
":": "simb_dp",
"(": "simb_apar",
")": "simb_fpar",
":=": "simb_atrib",
"=": "simb_igual",
"<>": "simb_dif",
">=": "simb_mai",
"<=": "simb_mei",
">": "simb_ma",
"<": "simb_me",
"+": "simb_ad",
"-": "simb_sub",
"*": "simb_mult",
"/": "simb_div",
".": "simb_pf"
} 

i = 0 # variável global, indica a posição atual da leitura do programa
line_count = 1 # indica linha atual da leitura
lexical_errors = []
chcnt = 0 # variável utilizada para rastrear a posição na linha


def print_errors():
    print("Erros léxicos: ")
    line = -1
    for error in lexical_errors:
        if(error[0] == line):
            print("\t Pos. {}: {} -> {}".format(error[1], error[2], error[3]))
        else:
            line = error[0]
            print("\nLinha {}:".format(line))
            print("\t Pos. {}: {} -> {}".format(error[1], error[2], error[3]))


def update_line(c):
    global line_count, chcnt
    if c == '\n':
        line_count+=1
        chcnt = i

        

def handle_error(string, msg):
    global lexical_errors
    lexical_errors.append(tuple((line_count, i-chcnt-1, msg, string)))


# Checa se o número excede o tamanho máximo
def check_num_size(string, token):
    MAX_NUM_SIZE = 10
    if(len(string) > MAX_NUM_SIZE):
        handle_error(string, "Tamanho de número excedeu limite.")
        return "ERRO"
    else:
        return token


# Checa se o id excede o tamanho máximo
def check_id_size(string, token):
    MAX_ID_SIZE = 20
    if(len(string) > MAX_ID_SIZE):
        handle_error(string, "Tamanho de identificador excedeu limite.")
        return "ERRO"
    else:
        return token


# Autômato para identificar strings
def aut_string(program, string, state):
    global i
    # ESTADO 0
    if state == 0:
        string += program[i]
        i+=1
        return aut_string(program, string, 1)
    
    # ESTADO 1
    elif state == 1:
        while(program[i] != '"'):
            update_line(program[i])
            string += program[i]
            i+=1
            if i == len(program):
                handle_error(string, "Fim de arquivo inesperado. String não finalizada.")
                return string, "ERRO"
        string += program[i]
        i+=1
        return string, "string"


# Autômato para chars
def aut_char(program, string, state):
    global i
    # ESTADO 0
    if state == 0:
        string += program[i]
        i+=1
        return aut_char(program, string, 1)
    
    # ESTADO 1
    elif state == 1:
        string += program[i]
        i+=1
        return aut_char(program, string, 2)
    
    # ESTADO 2
    elif state == 2:
        if program[i] == "'":
            string += program[i]
            i+=1
            return string, "char"
        else:
            string += program[i]
            handle_error(string, "Char inválido. Esperava-se '''.")
            print("{} -> ERRO: char inválido.".format(string))
            return string, "ERRO"
    

# Autômato para identificar comentários
def comment(program, string, state):
    global i
    # ESTADO 0
    if state == 0:
        string += program[i]
        i+=1
        return comment(program, string, 1)
    
    # ESTADO 1
    elif state == 1:
        while(program[i] != '}'):
            update_line(program[i])
            string += program[i]
            i+=1
            if i == len(program):
                handle_error(string, "Fim de arquivo inesperado. Comentário não finalizado.")
                return string, "ERRO"
        string += program[i]
        i+=1
        return string, "comment"


# Autômato para operadores relacionais >, >=, <, <=, = e <>
def rel_ops(program, string, state):
    global i
    # ESTADO 0
    if state == 0:
        if program[i] == '<':
            string += program[i]
            i+=1
            return rel_ops(program, string, 1)
        
        elif program[i] == '=':
            string += program[i]
            i+=1
            return rel_ops(program, string, 5)
        
        elif program[i] == '>':
            string += program[i]
            i+=1
            return rel_ops(program, string, 6)
    
    # ESTADO 1
    elif state == 1:
        if program[i] == '=':
            string += program[i]
            i+=1
            return rel_ops(program, string, 2)
        
        elif program[i] == '>':
            string += program[i]
            i+=1
            return rel_ops(program, string, 3)
        
        else:
            return string

    # ESTADO 6
    elif state == 6:
        if program[i] == '=':
            string += program[i]
            i+=1
            return rel_ops(program, string, 7)
        
        else:
            return string
    
    else:
        return string    
    

# Autômato para := e :
def colon(program, string, state):
    global i
    if program[i] == ':' and state == 0:
        string += program[i]
        i+=1
        return colon(program, string, state+1)
    elif program[i] == '=' and state == 1:
        string += program[i]
        i+=1
        return colon(program, string, state+1)
    else:
        return string


# Autômato para palavras, podendo ser palavras reservadas ou identificadores
def words(program, string, state):
    global i
    # ESTADO 0
    if state == 0:
        string += program[i]
        i+=1
        return words(program, string, 1)
    
    # ESTADO 1
    elif state == 1:
        if program[i] in invalid_chars or program[i] == "'" or program[i] == '"':
            string += program[i]
            i+=1
            handle_error(string, "Caractere inválido para identificadores.")
            return string, "ERRO"

        elif program[i] in special_chars or program[i] in relational_ops or program[i].isspace():
            return string, ""

        else:
            string += program[i]
            i+=1
            return words(program, string, state)


# Autômato para números, podendo ser número inteiro ou real
def numbers(program, string, state):
    global i
    # ESTADO 0
    if state == 0:
        if program[i] == '+' or program[i] == '-':
            string += program[i]
            i+=1
            return numbers(program, string, 1)

        elif program[i].isdigit():
            string += program[i]
            i+=1
            return numbers(program, string, 2)
    
    elif state == 1:
        if program[i].isdigit():
            string += program[i]
            i+=1
            return numbers(program, string, 2)

        elif program[i] in special_chars or program[i] in relational_ops or program[i].isspace():
            return string, check_num_size(string, "num_int")

        else:
            string += program[i]
            i+=1
            handle_error(string, "Número mal formado. Esperava-se algum dígito.")
            return string, "ERRO"

    elif state == 2:
        if program[i] == '.':
            string += program[i]
            i+=1
            return numbers(program, string, 3)
        
        if program[i].isdigit():
            string += program[i]
            i+=1
            return numbers(program, string, 2)

        elif program[i] in special_chars or program[i] in relational_ops or program[i].isspace():
            return string, check_num_size(string, "num_int")

        else:
            string += program[i]
            i+=1
            handle_error(string, "Número mal formado. Esperava-se '.' ou dígito.")
            return string, "ERRO"
    
    elif state == 3:
        if program[i].isdigit():
            string += program[i]
            i+=1
            return numbers(program, string, 2)

        elif program[i] in special_chars or program[i] in relational_ops or program[i].isspace():
            return string, check_num_size(string, "num_real")
        
        else:
            string += program[i]
            i+=1
            handle_error(string, "Número mal formado. Esperava-se algum dígito.")
            return string, "ERRO"
        

# Função que retorna o par cadeia, token conforme forem solicitados
def lexical_analyser(program):
    global i, line_count
    # Caractere atual é número
    if program[i].isdigit():
        return numbers(program, "", 0)

    # Caractere atual é letra
    elif program[i].isalpha():
        string, token = words(program, "", 0)
        if(token != "ERRO"):
            # Se não for palavra reservada é um ident
            if(string in reserved):
                token = reserved[string]
            else:
                token = check_id_size(string, "id")
        return string, token

    # Caractere atual é ':'
    elif(program[i] == ':'):
        string = colon(program, "", 0)
        token = reserved[string]
        return string, token

    # Caractere atual é <, =, >
    elif program[i] in relational_ops:
        string = rel_ops(program, "", 0)
        token = reserved[string]
        return string, token
    
    # Caractere atual é {
    elif program[i] == '{':
        return comment(program, "", 0)

    # Caractere atual é '
    elif program[i] == "'":
        return aut_char(program, "", 0)
    
    # Caractere atual é '
    elif program[i] == '"':
        return aut_string(program, "", 0)

    # Caractere atual é -, +, :, =, ;, ., (, )
    elif program[i] in special_chars:
        string = program[i]
        i+=1
        token = reserved[string]
        return string, token
    

    # Caractere atual é espaço em branco
    elif program[i].isspace():
        update_line(program[i])
        i+=1
        return "None", "None"

    # Caractere atual é inválido
    elif program[i] in invalid_chars:
        string = program[i]
        i+=1
        handle_error(string, "Caractere inválido.")
        # print("{} -> ERRO: caractere inválido.".format(string))
        return string, "ERRO"

    else:
        i+=1
        return "None", "None"


def get_token(program):
    string, token = lexical_analyser(program)

    while(i < len(program) and (string == 'None' or token == 'comment')):
        string, token = lexical_analyser(program)
    

    
    return string, token


def generate_token_list(input_file, output_file="token_list.txt"):
    global i

    if (os.path.isfile(input_file)):
        fin = open(input_file, "r")
        fout = open(output_file, "w")
    
        program = fin.read()
        fin.close()
        program += ' '
        table = []
        

        while(i < len(program)):
            string, token = lexical_analyser(program)
            if(string != "None"):
                table.append(tuple((string, token)))

        for i in table:
            fout.write("{} - {}\n".format(i[0], i[1]))

        fout.close()

        if(lexical_errors):
            print_errors()
            return False
        
        else:
            return True


    else:
        print("Erro ao abrir carregar programa. Insira um arquivo existente.")
        print("Para ajuda, utilize '-h'")
        return False
    

def main(argumentList): 
    global i

    input_file = ""
    output_file = "token_list.txt"

    try:
        opts, args = getopt.getopt(argumentList,"hi:o:",["ifile=","ofile="])
        
        for opt, arg in opts:
            
            if opt == '-h':
                print("usage: python3 analisador_lexico.py -i <programa_entrada> [-o <programa_saída>]")
                print("Se não especificado, o arquivo saída será 'token_list.txt'")
                sys.exit()
            
            elif opt in ("-i", "--ifile"):
                input_file = arg
            
            elif opt in ("-o", "--ofile"):
                output_file = arg

    except getopt.GetoptError:
        print("Erro. Para ajuda, utilize '-h'.")
        sys.exit(2)

    
    if (os.path.isfile(input_file)):
        fin = open(input_file, "r")
        fout = open(output_file, "w")
    
        program = fin.read()
        fin.close()
        program += ' '
        table = []
        

        while(i < len(program)):
            string, token = lexical_analyser(program)
            if(string != "None"):
                table.append(tuple((string, token)))

        for i in table:
            fout.write("{} - {}\n".format(i[0], i[1]))

        fout.close()

        if(lexical_errors):
            print_errors()
            print(False)
            return False
        
        else:
            print(True)
            return True


    else:
        print("Erro ao abrir carregar programa. Insira um arquivo existente.")
        print("Para ajuda, utilize '-h'")
        print(False)
        return False
   

if __name__ == '__main__':
    main(sys.argv[1:])