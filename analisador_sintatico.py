# Alunos:
# Guilherme Brunassi Nogima (nUSP: 9771629)
# João Pedro Silva Mambrini Ruiz (nUSP: 9771675)

import os.path
import getopt, sys
import analisador_lexico as lexical

parser_errors = []
string = None
token = None
numero = ['num_real', 'num_int']
relacao = ['simb_igual', 'simb_dif', 'simb_mai', 'simb_mei', 'simb_ma', 'simb_me']
simb_comandos = ['simb_read', 'simb_write', 'simb_while', 'simb_if', 'simb_begin', 'id', 'simb_for']


#################################################################################################################################################
# Funções auxiliares

# Escreve no arquivo saída a listagem de todos os erros identificados, tanto na etapa do analisador léxico quanto do analisador sintático
def write_output(fout):
    if(lexical.lexical_errors):
        fout.write("Erros léxicos: ")
        line = -1
        for error in lexical.lexical_errors:
            if(error[0] == line):
                fout.write("\n\tPos. {}: {} -> {}".format(error[1], error[2], error[3]))
            else:
                line = error[0]
                fout.write("\nLinha {}:".format(line))
                fout.write("\n\tPos. {}: {} -> {}".format(error[1], error[2], error[3]))
        fout.write("\n\n")

    if(parser_errors):
        fout.write("Erros sintáticos: ")
        line = -1
        for error in parser_errors:
            if(error[0] == line):
                fout.write("\n\tPos. {}: {} -> {}".format(error[1], error[2], error[3]))
            else:
                line = error[0]
                fout.write("\nLinha {}:".format(line))
                fout.write("\n\tPos. {}: {} -> {}".format(error[1], error[2], error[3]))

# Imprime os erros identificados no analisador sintático
def print_errors():
    print("Erros sintáticos: ")
    line = -1
    for error in parser_errors:
        if(error[0] == line):
            print("\t Pos. {}: {} -> {}".format(error[1], error[2], error[3]))
        else:
            line = error[0]
            print("\nLinha {}:".format(line))
            print("\t Pos. {}: {} -> {}".format(error[1], error[2], error[3]))

# Função de tratamento de erros.
# Parâmetros:
# string: trecho onde foi identificado o erro
# msg: mensagem de erro
# sync: tokens de sincronização
# follow: seguidores do pai 
# max_errors: se for < 0, limite de erros foi excedido e a sincronização segue para o seguidor do pai
def handle_error(program, string, msg, sync=[], follow=[], max_errors=0):
    global parser_errors
    parser_errors.append(tuple((lexical.line_count, lexical.i-lexical.chcnt-1, msg, string)))
    
    if(max_errors < 0):
        sync = follow

    if(token == 'id'):
        update_token(program)
    while(token not in sync+follow and lexical.i < len(program)):
        update_token(program)
    
    if(lexical.i < len(program)):
        print(token)
        if(max_errors < 0) or token in follow:
            return True
        else:
            return False
    else:
        print_errors()
        exit(1)
    
# Faz requisição do próximo token ao analisador léxico
def update_token(program):
    global string, token
    string, token = lexical.get_token(program)


#################################################################################################################################################
# Análise sintática: cada função corresponde a um não-terminal da gramática da linguagem P-
# O parâmetro 'follow' corresponde ao seguidor do pai

def argumentos(program):
    if(token == 'id'):
        update_token(program)       
        while(token == 'simb_v'):
            update_token(program)    
            if(token == 'id'):
                update_token(program)
            else:
                if handle_error(program, string, "Esperava-se identificador", ['simb_fpar']):
                    return False
    else: 
        if handle_error(program, string, "Esperava-se identificador", ['simb_fpar']):
            return False


def variaveis(program, follow=['simb_dp']):
    if(token == 'id'):
        update_token(program)       
        while(token == 'simb_v'):
            update_token(program)    
            if(token == 'id'):
                update_token(program)
            else:
                
                if handle_error(program, string, "Esperava-se identificador de variável", follow):
                    return False
    else: 
        if handle_error(program, string, "Esperava-se identificador de variável", follow):
            return False


def op_mul(program):
    if(token == 'simb_mult'):
        update_token(program)
        return True
    
    elif(token == 'simb_div'):
        update_token(program)
        return True
    else:
        return False


def op_ad(program):
    if(token == 'simb_ad'):
        update_token(program)
        return True
    
    elif(token == 'simb_sub'):
        update_token(program)
        return True
    else:
        return False


def op_un(program):
    if(token == 'simb_ad'):
        update_token(program)
        return True
    
    elif(token == 'simb_sub'):
        update_token(program)
        return True
    else:
        return False


def mais_fatores(program, follow):
    if(op_mul(program)):
        fator(program, follow)
        mais_fatores(program, follow)
    else:
        return False


def fator(program, follow):
    if(token == 'id'):
        update_token(program)
    
    elif(token in numero):
        update_token(program)
    
    elif(token == 'simb_apar'):
        update_token(program)

        expressao(program, ['simb_fpar'])

        if(token == 'simb_fpar'):
            update_token(program)
        else: 
            if handle_error(program, string, "Esperava-se ')'", follow):
                return False
        
    else:
        if handle_error(program, string, "Esperava-se expressão", follow):
            return False
        

def outros_termos(program, follow):
    if(op_ad(program)):
        termo(program, follow)
        outros_termos(program, follow)
    else:
        return False


def termo(program, follow):
    op_un(program)
    fator(program, follow)
    mais_fatores(program, follow)


def expressao(program, follow):
    termo(program, follow)
    outros_termos(program, follow)


def cmd(program):
    max_errors = 2
    follow = ['simb_pv']

    # READ
    if(token == 'simb_read'):
        update_token(program)
        if(token == 'simb_apar'):
            update_token(program)
        else:
            max_errors-=1
            if handle_error(program, string, "Esperava-se '('", ['id', 'simb_fpar'], follow, max_errors):
                return False

        variaveis(program, ['simb_fpar'] + follow)    

        if(token == 'simb_fpar'):
            update_token(program)
            return True
        else:
            max_errors-=1 
            if handle_error(program, string, "Esperava-se ')'", follow):
                return False
        
    # WRITE
    elif(token == 'simb_write'):
        update_token(program)
        if(token == 'simb_apar'):
            update_token(program)
        else:
            max_errors-=1
            if handle_error(program, string, "Esperava-se '('", ['id', 'simb_fpar'], follow, max_errors):
                return False

        variaveis(program, ['simb_fpar'] + follow)   

        if(token == 'simb_fpar'):
            update_token(program)
        else:
            max_errors-=1 
            if handle_error(program, string, "Esperava-se ')'", follow):
                return False

    # WHILE
    elif(token == 'simb_while'):
        update_token(program)
        if(token == 'simb_apar'):
            update_token(program)
        else:
            max_errors-=1
            if handle_error(program, string, "Esperava-se '('", ['simb_ad', 'simb_sub', 'id', 'simb_apar']+numero, follow, max_errors):
                return False

        expressao(program, relacao)
    
        if (token in relacao):
            update_token(program)
        else:
            if handle_error(program, string, "Esperava-se uma relação", ['simb_ad', 'simb_sub', 'id', 'simb_apar']+numero, follow, max_errors):
                return False

        expressao(program, ['simb_fpar'])   

        if(token == 'simb_fpar'):
            update_token(program)
        else:
            max_errors-=1 
            if handle_error(program, string, "Esperava-se ')'", ['simb_do'], follow, max_errors):
                return False
        
        if(token == 'simb_do'):
            update_token(program)
        else:
            max_errors-=1 
            if handle_error(program, string, "Esperava-se 'do'", simb_comandos, follow, max_errors):
                return False

        if cmd(program) == 'None':
            if handle_error(program, string, "Esperava-se algum comando", follow):
                return False
    
    # IF
    elif(token == 'simb_if'):
        update_token(program)

        expressao(program, relacao)
    
        if (token in relacao):
            update_token(program)
        else:
            if handle_error(program, string, "Esperava-se uma relação", ['simb_ad', 'simb_sub', 'id', 'simb_apar']+numero, follow, max_errors):
                return False    

        expressao(program, ['simb_then'])  

        if(token == 'simb_then'):
            update_token(program)
        else:
            max_errors-=1 
            if handle_error(program, string, "Esperava-se 'then'", simb_comandos, follow, max_errors):
                return False

        if cmd(program) == 'None':
            if handle_error(program, string, "Esperava-se algum comando", ['simb_else'], follow, max_errors):
                return False

        if(token == 'simb_else'):
            update_token(program)
        else:
            max_errors-=1 
            if handle_error(program, string, "Esperava-se 'else'", simb_comandos, follow, max_errors):
                return False

        if cmd(program) == 'None':
            if handle_error(program, string, "Esperava-se algum comando", follow):
                return False

    # IDENT
    elif(token == 'id'):
        update_token(program)
        if(token == 'simb_atrib'):
            update_token(program)
            expressao(program, ['simb_pv'])

        elif(token == 'simb_apar'):

            update_token(program)
        
            argumentos(program)    

            if(token == 'simb_fpar'):
                update_token(program)
            else:
                max_errors-=1 
                if handle_error(program, string, "Esperava-se ')'", follow):
                    return False
        
        else:
            max_errors-=1 
            if handle_error(program, string, "Esperava-se '(' ou ':='", follow):
                return False
        
    # BEGIN
    elif(token == 'simb_begin'):
        update_token(program)
        comandos(program)
        if(token == 'simb_end'):
                update_token(program)
        else:
            max_errors-=1 
            if handle_error(program, string, "Esperava-se 'end'", follow):
                return False
    
    # FOR
    elif(token == 'simb_for'):
        update_token(program)
        if(token == 'id'):
            
            update_token(program)
        else:
            max_errors-=1 
            if handle_error(program, string, "Esperava-se identificador", ['simb_atrib'], follow, max_errors):
                return False

        if(token == 'simb_atrib'):
            update_token(program)
        else:
            max_errors-=1 
            if handle_error(program, string, "Esperava-se ':='", numero, follow, max_errors):
                return False

        if(token in numero):
            update_token(program)
        else:
            max_errors-=1            
            if handle_error(program, string, "Esperava-se número", ['simb_to'], follow, max_errors):
                return False

        if(token == 'simb_to'):
            update_token(program)
        else:
            max_errors-=1 
            if handle_error(program, string, "Esperava-se 'to'", numero, follow, max_errors):
                return False

        if(token in numero):
            update_token(program)
        else:
            max_errors-=1 
            if handle_error(program, string, "Esperava-se número", ['simb_do'], follow, max_errors):
                return False

        if(token == 'simb_do'):
            update_token(program)
        else:
            max_errors-=1 
            if handle_error(program, string, "Esperava-se 'do'", ['simb_begin'], follow, max_errors):
                return False

        if cmd(program) == 'None':
            if handle_error(program, string, "Esperava-se algum comando", follow):
                return False

    else:
        return "None"


def comandos(program):
    follow = ['simb_end']
    if cmd(program) == 'None':
        return 
    if(token == 'simb_pv'):
        update_token(program)
        comandos(program)
    else:
        if handle_error(program, string, "Esperava-se ';'", follow):
            return False


def lista_par(program):
    max_errors = 2
    follow = ['simb_fpar']

    variaveis(program)     
    

    if(token == 'simb_dp'):
        update_token(program)
    else:
        max_errors-=1
        if handle_error(program, string, "Esperava-se ':'", ['simb_int', 'simb_real'], follow, max_errors):
            return False

    if(token in ['simb_int', 'simb_real']):
        update_token(program)
    else:
        max_errors-=1
        if handle_error(program, string, "Esperava-se o tipo da variável", follow):
            return False
    
    if(token == 'simb_pv'):
        update_token(program)
        lista_par(program)
    

def parametros(program):
    max_errors = 2
    follow = ['simb_pv']

    if(token == 'simb_apar'):
        update_token(program)
    else:
        return False


    lista_par(program)
 

    if(token == 'simb_fpar'):
        update_token(program)
    else:
        max_errors-=1 
        if handle_error(program, string, "Esperava-se ')'", follow):
            return False


def dc_p(program):
    max_errors = 2
    follow = ['simb_begin']

    if(token == 'simb_procedure'):
        update_token(program)
    else:
        return False

    if(token == 'id'):
        update_token(program)
    else: 
        max_errors-=1
        if handle_error(program, string, "Esperava-se identificador de procedimento", ['simb_apar', 'simb_pv'], follow, max_errors):
            return False

    parametros(program)
    
    if(token == 'simb_pv'):
        update_token(program)
    else:
        max_errors-=1 
        if handle_error(program, string, "Esperava-se ';' ou '('", ['simb_var', 'simb_begin'], [], max_errors):
            return False

    dc_v(program)
        
    if(token == 'simb_begin'):
        update_token(program)
    else:
        max_errors-=1 
        if handle_error(program, string, "Esperava-se 'begin'", simb_comandos, follow, max_errors):
            return False
    
    comandos(program)

    if(token == 'simb_end'):
        update_token(program)
    else:
        max_errors-=1 
        if handle_error(program, string, "Esperava-se 'end'", ['simb_pv'], follow, max_errors):
            return False

    if(token == 'simb_pv'):
        update_token(program)
    else:
        max_errors-=1 
        if handle_error(program, string, "Esperava-se ';'", follow):
            return False
    
    if(token == 'simb_procedure'):
        dc_p(program)


def dc_v(program):
    max_errors = 2
    follow = ['simb_procedure', 'simb_begin']
    if(token == 'simb_var'):
        update_token(program)
    else:
        return False

    variaveis(program)       

    if(token == 'simb_dp'):
        update_token(program)
    else:
        max_errors-=1 
        if handle_error(program, string, "Esperava-se ':'", ['simb_real', 'simb_int'], follow, max_errors):
            return False
        
    if(token == 'simb_real' or token == 'simb_int'):
        update_token(program)
    else:
        max_errors-=1 
        if handle_error(program, string, "Esperava-se o tipo do identificador", [';'], follow, max_errors):
            return False

    if(token == 'simb_pv'):
        update_token(program)
    else:
        max_errors-=1 
        if handle_error(program, string, "Esperava-se ';'", follow):
            return False

    if(token == 'simb_var'):
        dc_v(program)


def dc_c(program):
    max_errors = 2
    follow = ['simb_var', 'simb_procedure', 'simb_begin']

    if(token == 'simb_const'):
        update_token(program)
    else:
        return False

    if(token == 'id'):
        update_token(program)
    else: 
        max_errors-=1
        if handle_error(program, string, "Esperava-se identificador de constante", ['simb_igual'], follow, max_errors):
            return False

    if(token == 'simb_igual'):
        update_token(program)
    else:
        max_errors-=1
        if handle_error(program, string, "Esperava-se '='", numero, follow, max_errors):
            return False
    
    if(token in numero):
        update_token(program)
    else:
        max_errors-=1
        if handle_error(program, string, "Esperava-se número", ['simb_pv'], follow, max_errors):
            return False
        
    if(token == 'simb_pv'):
        update_token(program)
    else:
        max_errors-=1
        if handle_error(program, string, "Esperava-se ';'", follow):
            return False

    if(token == 'simb_const'):
        dc_c(program)


def corpo(program):
    max_errors = 2
    follow = ['simb_pf']

    dc_c(program)
    dc_v(program)
    dc_p(program)

    if(token == 'simb_begin'):
        update_token(program)
    else:
        handle_error(program, string, "Esperava-se 'begin'", ['id'], follow, max_errors)
    
    comandos(program)

    if(token == 'simb_end'):
        update_token(program)
    else:
        
        handle_error(program, string, "Esperava-se 'end'", [';'], follow, max_errors)    


def programa(program):
    if(token == 'simb_program'):
        update_token(program)
    else:
        handle_error(program, string, "Esperava-se 'program'", ['id'])

    if(token == 'id'):
        update_token(program)
    else:
        handle_error(program, string, "Esperava-se identificador do programa", ['simb_pv'])
    
    if(token == 'simb_pv'):
        update_token(program)
    else:
        handle_error(program, string, "Esperava-se ';'", ['simb_const', 'simb_var', 'simb_procedure', 'simb_begin'])

    corpo(program)

    # if(token == 'simb_pf'):
    #     print("Fim")


# Realiza a chamada do analisador sintático
def parser(program):
    update_token(program)
    programa(program)
        
# Recebe a entrada e inicializa o arquivo de saída
def main(argumentList): 
    global i
    input_file = ""
    output_file = "saida.txt"

    try:
        opts, args = getopt.getopt(argumentList,"hi:o:",["ifile=","ofile="])
        
        for opt, arg in opts:
            
            if opt == '-h':
                print("usage: python3 analisador_sintatico.py -i <programa_entrada> [-o <arquivo_saída>]")
                print("Se não especificado, o arquivo saída será 'saida.txt'")
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
        
        parser(program)

        write_output(fout)
        
        fout.close()

        if(parser_errors):
            print_errors()
            return False
        
        else:
            return True


    else:
        print("Erro ao abrir carregar programa. Insira um arquivo existente.")
        print("Para ajuda, utilize '-h'")
        return False    


if __name__ == '__main__':
    main(sys.argv[1:])