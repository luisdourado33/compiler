"""
Universidade Federal de Mato Grosso - UFMT

Aluno: Luis Antonio da Silva Dourado
RGA: 201621901003
<luis_dourado33@hotmail.com>

"""

from semantico import Semantico
from lexico import TipoToken as tt, Lexico


class Sintatico:

    def __init__(self, gerar_tokens: bool):
        self.lex = None
        self.tokenAtual = None
        self.gerar_tokens = gerar_tokens
        self.tokens = []
        self.tabela_simbolos = []
        self.tabela_tipo = []
        self.values = []
        self.operadores = []
        self.tipo = None
        self.is_declarando = False
        self.is_atribuindo = False
        
        # Codigo intermediario
        self.temp = 0
        self.codigo = 'operador;arg1;arg2;result\n'
        self.codigo_gerado = ''
        
    def interprete(self, nomeArquivo):
        if not self.lex is None:
            print('ERRO: Ja existe um arquivo sendo processado.')
        else:
            self.lex = Lexico(nomeArquivo)
            self.lex.abreArquivo()
            self.tokenAtual = self.lex.getToken()

            if self.gerar_tokens:
                self.tokens.append(self.tokenAtual)

            self.programa()

            self.lex.fechaArquivo()

    def atualIgual(self, token):
        (const, _) = token
        return self.tokenAtual.const == const

    def consome(self, token):
        print(self.tokenAtual.lexema)
        if self.atualIgual(token):
            self.tokenAtual = self.lex.getToken()
            if self.gerar_tokens:
                self.tokens.append(self.tokenAtual)
        else:
            (_, msg) = token
            print('ERRO DE SINTAXE [linha %d]: era esperado "%s" mas veio "%s"'
                  % (self.tokenAtual.linha, msg, self.tokenAtual.lexema))
            quit()

    def programa(self):
        self.consome(tt.PROGRAM)
        self.consome(tt.ID)
        self.corpo()

        self.consome(tt.PONTO)
        self.consome(tt.EOF)
        print('Tudo certo!')

    def corpo(self):
        print('<corpo>')
        self.dc()

        self.consome(tt.BEGIN)
        self.comandos()
        self.consome(tt.END)

    def dc(self):
        print('<dc>')
        if self.atualIgual(tt.REAL) or self.atualIgual(tt.INTEGER):
            self.dc_v()
            self.mais_dc()

    def mais_dc(self):
        print('<mais_dc>')
        if self.atualIgual(tt.PVIRG):
            self.consome(tt.PVIRG)
            self.dc()

    def dc_v(self):
        print('<dc_v>')
        self.tipo_var()

        self.consome(tt.DPONTOS)
        self.variaveis()

    def tipo_var(self):
        print('<tipo_var>')
        if self.atualIgual(tt.REAL):
            self.tipo = Semantico('INTEGER', tt.REAL)
            self.is_declarando = True
            self.consome(tt.REAL)

        elif self.atualIgual(tt.INTEGER):
            self.tipo = Semantico('INTEGER', tt.INTEGER)
            self.is_declarando = True
            self.consome(tt.INTEGER)
        else:
            print('Erro sintático era esperado INTEGER ou REAL ', self.tokenAtual.lexema ,' dado')

    def variaveis(self):
        print('<variaveis>')
        if self.is_declarando:
            # checa se existe o lexema
            if self.tokenAtual.lexema in self.tabela_simbolos:
                print('Erro semântico identificador ', self.tokenAtual.lexema, ' já declarado.\n')
                quit()
            else:
                self.tabela_simbolos.append(self.tokenAtual.lexema)
                self.is_declarando = False
                self.consome(tt.ID)
        else:
            self.consome(tt.ID)
        self.mais_var()

    def mais_var(self):
        print('<mais_var>')
        if self.atualIgual(tt.VIRG):
            self.consome(tt.VIRG)
            self.is_declarando = True
            self.variaveis()

    def comandos(self):
        print('<comandos>')
        self.comando()
        self.mais_comandos()

    def mais_comandos(self):
        print('<mais_comandos>')
        if self.atualIgual(tt.PVIRG):
            self.consome(tt.PVIRG)
            self.comandos()

    def comando(self):
        print('<comando>')
        if self.atualIgual(tt.READ):
            self.consome(tt.READ)
            if self.atualIgual(tt.ABREPAR):
                
                self.consome(tt.ABREPAR)
                self.consome(tt.ID)
                if self.atualIgual(tt.FECHAPAR):
                    self.consome(tt.FECHAPAR)

        elif self.atualIgual(tt.WRITE):
            self.consome(tt.WRITE)

            if self.atualIgual(tt.ABREPAR):
                self.consome(tt.ABREPAR)
                self.consome(tt.ID)
                if self.atualIgual(tt.FECHAPAR):
                    self.consome(tt.FECHAPAR)

        elif self.atualIgual(tt.IF):
            self.consome(tt.IF)
            self.condicao()

            self.consome(tt.THEN)
            self.comandos()
            self.falsa_condicao()

            self.consome(tt.CIF)

        elif self.atualIgual(tt.ID):
            self.consome(tt.ID)

            self.consome(tt.ATRIB)
            self.expressao()

    def condicao(self):
        print('<condicao>')
        self.expressao()
        self.relacao()
        self.expressao()

    def relacao(self):
        print('<relacao>')
        if self.atualIgual(tt.IGUAL):
            self.consome(tt.IGUAL)
        if self.atualIgual(tt.DIFERENTE):
            self.consome(tt.DIFERENTE)
        if self.atualIgual(tt.MAIORIGUAL):
            self.consome(tt.MAIORIGUAL)
        if self.atualIgual(tt.MENORIGUAL):
            self.consome(tt.MENORIGUAL)
        if self.atualIgual(tt.MAIOR):
            self.consome(tt.MAIOR)
        if self.atualIgual(tt.MENOR):
            self.consome(tt.MENOR)

    def expressao(self):
        print('<expressao>')
        self.termo()
        self.outros_termos()

    def termo(self):
        print('<termo>')
        self.subtracao()
        self.fator()
        self.mais_fatores()

    def subtracao(self):
        print('<op_un>')
        if self.atualIgual(tt.SUBTRACAO):
            self.consome(tt.SUBTRACAO)

    def fator(self):
        print('<fator>')
        if self.atualIgual(tt.ID):
            if self.tokenAtual.lexema not in self.values:
                self.values.append(self.tokenAtual.lexema)
            self.consome(tt.ID)
        elif self.atualIgual(tt.ABREPAR):
            self.consome(tt.ABREPAR)
            self.expressao()

            if self.atualIgual(tt.FECHAPAR):
                self.consome(tt.FECHAPAR)

    def outros_termos(self):
        print('<outros_termos>')
        if self.atualIgual(tt.SOMA) or self.atualIgual(tt.SUBTRACAO):
            self.op_ad()
            self.termo()
            self.outros_termos()

    def op_ad(self):
        print('<op_ad>')
        if self.atualIgual(tt.SOMA):
            self.operadores.append(self.tokenAtual.lexema)
            self.consome(tt.SOMA)

        if self.atualIgual(tt.SUBTRACAO):
            self.operadores.append(self.tokenAtual.lexema)
            self.consome(tt.SUBTRACAO)
            
    def mais_fatores(self):
        print('<mais_fatores>')
        if self.atualIgual(tt.MULTIPLICACAO) or self.atualIgual(tt.DIVISAO):
            self.op_mul()
            self.fator()
            self.mais_fatores()

    def op_mul(self):
        print('<op_mul>')
        if self.atualIgual(tt.MULTIPLICACAO):
            self.operadores.append(self.tokenAtual.lexema)
            self.consome(tt.MULTIPLICACAO)
        else:
            self.operadores.append(self.tokenAtual.lexema)
            self.consome(tt.DIVISAO)

    def falsa_condicao(self):
        print('<p_falsa>')
        self.consome(tt.ELSE)
        self.comandos()

    def busca(self, id):
        return id in self.tabela_simbolos

    def gera_temp(self):
        return "t" + str(self.temp + 1)

    def code(self, op, arg1, arg2, result):
        self.codigo.join(op + ";" + arg1 + ";" + arg2 + ";" + result + "\n")
