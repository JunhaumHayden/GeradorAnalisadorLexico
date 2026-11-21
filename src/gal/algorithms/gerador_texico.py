
from arvore_binaria import NoArvore
from collections import deque

class GeradorLexico:
    def __init__(self, caminho_arquivo):
        self.caminho_arquivo = caminho_arquivo
        self.expressoes = {}
        self.mapa_simbolos = {}
        self.followpost = {}   
        self.contador = 0
        self.afds = {}
        self.automato_completo = {}


#############################################################################################################
# Conversão de Expressão Regular para Autômato Finito Determinístico (algoritmo apresentado no livro do Aho);
#############################################################################################################


    #########################################################################
    # 1.1) ARRUMAR EXPRESSÃO (EXPANDIR [], COLOCAR CONCATENAÇÃO, TIRAR ESPAÇOS
    #########################################################################

    def arrumar_arquivo(self):
        with open(self.caminho_arquivo, 'r', encoding='utf-8') as arquivo: # abre arquivo
            for linha in arquivo: # passa linha por linha

                # LIMPAR A EXPRESSÃO
                linha = linha.strip() # retira espaços vazios inicio e fim
                if not linha or ':' not in linha: # se a linha está vazia ou não tem ":"
                    continue # vai para próxima linha do arquivo

                nome_token, padrao_er = linha.split(':', 1) # separa expressão em dois (1 é para fazer uma vez (se veio dois :: então pega e divide só no primeiro))
                padrao_er = padrao_er.strip().replace(" ", "") # tirar espaços

                while ('**' in padrao_er or '++' in padrao_er or '??' in padrao_er or '*+' in padrao_er or '+*' in padrao_er or '?*' in padrao_er or '*?' in padrao_er or '?+' in padrao_er or '+?' in padrao_er):
                    padrao_er = padrao_er.replace('**', '*') 
                    padrao_er = padrao_er.replace('++', '+')
                    padrao_er = padrao_er.replace('??', '?')

                    padrao_er = padrao_er.replace('*+', '*')
                    padrao_er = padrao_er.replace('+*', '*')
                    padrao_er = padrao_er.replace('?*', '*')
                    padrao_er = padrao_er.replace('*?', '*')
                    padrao_er = padrao_er.replace('?+', '*') 
                    padrao_er = padrao_er.replace('+?', '*')
                
                # ABRIR COLCHETES
                while '[' in padrao_er: # enquanto tiver "["
                    inicio_colchete = padrao_er.find('[') # busca onde começa colchete
                    fim_colchete = padrao_er.find(']') # onde termina o colchete
                    if fim_colchete == -1: # se não achou "]" então para
                        break

                    entre_colchete = padrao_er[inicio_colchete + 1: fim_colchete] # mostrar o que tem no meio do colchete 

                    como_deixar_colchete = [] # como fica o [] no final
                    
                    i = 0
                    while i < len(entre_colchete): # passa pelos caraceres que tem no colchete
                        if i + 2 < len(entre_colchete) and entre_colchete[i + 1] == '-': # vê se está ainda dentro do colchete e ter '-' no meio
                            for valor in range(ord(entre_colchete[i]), ord(entre_colchete[i + 2]) + 1): # pega o primeiro caracter e depois final caracter (logo depois de '-') Valor ASCCI
                                como_deixar_colchete.append(chr(valor)) # transforma em caracter o número ASCII
                            i += 3 # passa para próximo conjunto (A-Z)
                        else:
                            como_deixar_colchete.append(entre_colchete[i]) # como o caso de A-Zx
                            i += 1 # próximo conjunto

                    novo_trecho = "(" + "|".join(como_deixar_colchete) + ")" # join coloca '|' sempre no meio e coloca nos extremos '(' e ')'
                    padrao_er = padrao_er[:inicio_colchete] + novo_trecho + padrao_er[fim_colchete + 1:] # coloca dentro da expressão esse novo trecho

                # COMO FICA A CONCATENAÇÃO 
                como_fica_concatenacao = "" 
                for i in range(len(padrao_er)): # passa por toda a expressão 
                    caracter_atual = padrao_er[i] # pega o caracter atual
                    como_fica_concatenacao += caracter_atual # colcocar o carater atual
                    if i + 1 < len(padrao_er): # vê se está no final da expressão 
                        caracter_futuro = padrao_er[i + 1] # pega o próximo caracter
                        lado_esq = caracter_atual.isalnum() or caracter_atual in [')', '*', '+', '?'] # ele é está "padrão"
                        lado_dir = caracter_futuro.isalnum() or caracter_futuro == '(' # ele está no padrão?
                        if lado_esq and lado_dir: # colocar explicitamente a concatenação 
                            como_fica_concatenacao += '.' 

                self.expressoes[nome_token.strip()] = "(" + como_fica_concatenacao + ").#" # finalizar a ordenação

        return self.expressoes

    #########################################################
    # 1.2) EXPRESSÃO REGULAR -> "PÓS-FIXA" -> ÁRVORE SINTÁTICA
    #########################################################

    def criar_arvore(self, expressao):
        # ORDENAR PARA LER POS FIXA (Algoritmo de Shunting-Yard)
        prioridade = {'*': 3, '+': 3, '?': 3, '.': 2, '|': 1, '(': 0} # prioridade das operações
        posfixa = "" # ordenação para ler
        pilha_operadores = [] 
        for char in expressao:
            if char.isalnum() or char == '#': # numero, letra ou # já são inseridos
                posfixa += char
            elif char == '(': # uma lista de espera (para analizar o que tem entre os colchetes)
                pilha_operadores.append(char)
            elif char == ')': # retirar da lista de espera 
                while pilha_operadores and pilha_operadores[-1] != '(':
                    posfixa += pilha_operadores.pop()
                pilha_operadores.pop()
            else:
                while (pilha_operadores and prioridade.get(pilha_operadores[-1], 0) >= prioridade[char]): # vê qual é mais forte de operadorquando vem '*', '+', etc
                    posfixa += pilha_operadores.pop()
                pilha_operadores.append(char)
        while pilha_operadores: # se ainda tem algo na pilha então adiciona
            posfixa += pilha_operadores.pop()

        arvore_no = [] # guarda a árvore ()
        for char in posfixa: # passa por todos os caracteres
            if char.isalnum() or char == '#': # numero, letra ou # 
                arvore_no.append(NoArvore(char)) # adiciona direto o nó
            elif char in ['*', '+', '?']: # operador mas afeta 1 elemento só
                no = NoArvore(char)
                no.no_esquerda = arvore_no.pop()
                arvore_no.append(no)
            elif char in ['.', '|']: # operador mas afeta 2 elementos
                no = NoArvore(char)
                no.no_direita = arvore_no.pop()
                no.no_esquerda = arvore_no.pop()
                arvore_no.append(no)
        return arvore_no.pop() 

    ########################################################
    # 1.3) CONSTRUIR AS "FUNÇÕES" ANULÁVEL, PRIMEIRA-POST, ...
    ########################################################
    
    def construir_funcoes(self, no):
        if no is None:
            return
        self.construir_funcoes(no.no_esquerda)
        self.construir_funcoes(no.no_direita)

        if no.valor.isalnum() or no.valor == '#': # se é int, num ou #
            self.contador += 1 # qual é o seu número (colocar posição dele)
            no.posicao = self.contador
            self.mapa_simbolos[no.posicao] = no.valor
            self.followpost[no.posicao] = []
            no.anulavel = False # não dá para anular
            no.firstpos = [no.posicao] # ele mesmo 
            no.lastpos = [no.posicao] # ele mesmo

        elif no.valor == '|':
            no.anulavel = no.no_esquerda.anulavel or no.no_direita.anulavel # verifica se algum deles é anulável
            no.firstpos = no.no_esquerda.firstpos + no.no_direita.firstpos # união dos firstposts
            no.lastpos = no.no_esquerda.lastpos + no.no_direita.lastpos # união de lastposts

        elif no.valor == '.':
            no.anulavel = no.no_esquerda.anulavel and no.no_direita.anulavel # verifica se os dois são 
            no.firstpos = no.no_esquerda.firstpos + no.no_direita.firstpos if no.no_esquerda.anulavel else list(no.no_esquerda.firstpos)
            no.lastpos = no.no_esquerda.lastpos + no.no_direita.lastpos if no.no_direita.anulavel else list(no.no_direita.lastpos)
            for i in no.no_esquerda.lastpos: # colocar na tabela qual é followpost
                for j in no.no_direita.firstpos:
                    if j not in self.followpost[i]:
                        self.followpost[i].append(j)

        elif no.valor in ['*', '+', '?']:
            no.anulavel = (no.valor != '+') or no.no_esquerda.anulavel
            no.firstpos = list(no.no_esquerda.firstpos)
            no.lastpos = list(no.no_esquerda.lastpos)
            if no.valor in ['*', '+']:
                for i in no.no_esquerda.lastpos:
                    for j in no.no_esquerda.firstpos:
                        if j not in self.followpost[i]:
                            self.followpost[i].append(j)
        return no

    ###########################################################
    # 1.4) CRIAR AUTOMATO FINITO POR MEIO DE EXPRESSÕES REGULARES
    ###########################################################
    
    def construir_estados_d(self, raiz):
        # VER ALFABETO 
        simbolos_de_entrada = []
        for s in self.mapa_simbolos.values():
            if s != '#' and s not in simbolos_de_entrada:
                simbolos_de_entrada.append(s)
        
        # ALGORÍTIMO AHO EM SI
        inicial = sorted(raiz.firstpos)
        estados_d = [inicial] # lista com todos os estados descobertos
        nao_marcados = [inicial] 
        dtran = [] # tabela de transições: dtran[i][a] = número do estado destino

        while nao_marcados: 
            T = nao_marcados.pop(0) # marcar T (retira o primeiro elemento da lista)
            transicoes = {} # transições de T
            for a in simbolos_de_entrada: # para cada símbolo de entrada a
                U = [] # U = lista vazia
                for p in T: # para cada posição p que está em T
                    if self.mapa_simbolos[p] == a: # só interessa se o símbolo da posição p for a
                        for destino in self.followpost[p]: # faz o papel do U.update()
                            if destino not in U:
                                U.append(destino)
                if U: # se U não é vazio, existe transição com a
                    U.sort() # ordena U 
                    if U not in estados_d: # se U ainda não está em Destados
                        estados_d.append(U) # adiciona U em Destados
                        nao_marcados.append(U) # U entra na fila como não marcado
                    transicoes[a] = estados_d.index(U) 
            dtran.append(transicoes)

        # DESCOBRIR ESTADOS FINAIS
        # 1. descobrir posição do '#'
        pos_hashtag = -1
        for posicao, simbolo in self.mapa_simbolos.items():
            if simbolo == '#':
                pos_hashtag = posicao
                break 
        # 2. descobrir quais estados são finais
        finais = []
        for i in range(len(estados_d)):
            estado_atual = estados_d[i]
            # Se o número do '#' estiver dentro desse estado, ele é um estado final!
            if pos_hashtag in estado_atual: 
                finais.append(i)        
        return estados_d, dtran, finais, simbolos_de_entrada

    #########################################################################
    # 2.1) MINIMIZAÇÃO DE AUTÔMATOS FINITOS
    #########################################################################

    def _eliminar_estados_inalcancaveis(self, n, dtran, simbolos):
        alcancaveis = {0}
        fila = deque([0])

        # BFS para identificação dos estados alcançáveis
        while fila:
            atual = fila.popleft()
            for s in simbolos:
                dest = dtran[atual].get(s)
                if dest is not None and dest not in alcancaveis:
                    alcancaveis.add(dest)
                    fila.append(dest)

        return [s for s in range(n) if s in alcancaveis]
        
    def _eliminar_estados_mortos(self, estados_validos, finais_set, dtran):
        validos_set = set(estados_validos)
        reverso = {s: [] for s in validos_set}

        # transições reversas para facilitar a busca
        for origem in validos_set:
            for dest in dtran[origem].values():
                if dest in reverso:
                    reverso[dest].append(origem)

        vivos = {f for f in finais_set if f in validos_set}
        fila = deque(vivos)

        # BFS para identificação dos estados vivos
        while fila:
            atual = fila.popleft()
            for ant in reverso[atual]:
                if ant not in vivos:
                    vivos.add(ant)
                    fila.append(ant)

        return [s for s in estados_validos if s in vivos]
        
    def _construir_classes_equivalencia(self, estados_ativos, finais_set, dtran, simbolos):
        ativos_set = set(estados_ativos)
        SEM_DESTINO = -1

        def prox(estado, sym):
            dest = dtran[estado].get(sym)
            return dest if dest in ativos_set else SEM_DESTINO

        grupo_finais = [s for s in estados_ativos if s in finais_set]
        grupo_nao_finais = [s for s in estados_ativos if s not in finais_set]

        particoes = []
        if grupo_finais:
            particoes.append(grupo_finais)
        if grupo_nao_finais:
            particoes.append(grupo_nao_finais)

        mudou = True
        while mudou:
            mudou = False
            id_ce = {SEM_DESTINO: len(particoes)}
            for idx_ce, ce in enumerate(particoes):
                for s in ce:
                    id_ce[s] = idx_ce

            novas_particoes = []
            for ce in particoes:
                if len(ce) <= 1:
                    novas_particoes.append(ce)
                    continue

                assinaturas = {}
                for s in ce:
                    chave = tuple(id_ce[prox(s, sym)] for sym in simbolos)
                    assinaturas.setdefault(chave, []).append(s)

                if len(assinaturas) > 1:
                    mudou = True
                novas_particoes.extend(assinaturas.values())

            particoes = novas_particoes

        return particoes
        
    def _construir_afd_minimo(self, particoes, estados, finais_set, dtran, simbolos):
        idx_q0 = next((i for i, ce in enumerate(particoes) if 0 in ce), 0)
        if idx_q0 != 0:
            particoes[0], particoes[idx_q0] = particoes[idx_q0], particoes[0]

        ce_de_estado = {}
        for idx_ce, ce in enumerate(particoes):
            for s in ce:
                ce_de_estado[s] = idx_ce

        novos_estados = [
            sorted({pos for s in ce for pos in estados[s]})
            for ce in particoes
        ]

        novo_dtran = []
        for ce in particoes:
            representante = ce[0]
            trans = {}
            for sym in simbolos:
                dest = dtran[representante].get(sym)
                if dest is not None and dest in ce_de_estado:
                    trans[sym] = ce_de_estado[dest]
            novo_dtran.append(trans)

        novos_finais = sorted({
            idx_ce for idx_ce, ce in enumerate(particoes)
            if any(s in finais_set for s in ce)
        })

        return novos_estados, novo_dtran, novos_finais, simbolos
        
    def minimizar_afd(self, estados, dtran, finais, simbolos):
        n = len(estados)
        if n == 0:
            return estados, dtran, finais, simbolos

        finais_set = set(finais)

        alcancaveis = self._eliminar_estados_inalcancaveis(n, dtran, simbolos)
        estados_vivos = self._eliminar_estados_mortos(alcancaveis, finais_set, dtran)

        if not estados_vivos:
            return [], [], [], simbolos

        particoes = self._construir_classes_equivalencia(
            estados_vivos, finais_set, dtran, simbolos
        )

        return self._construir_afd_minimo(
            particoes, estados, finais_set, dtran, simbolos
        )

    def minimizar_afds(self):
        for nome, (estados, dtran, finais, simbolos) in self.afds.items():
            self.afds[nome] = self.minimizar_afd(estados, dtran, finais, simbolos)
        return self.afds

    #########################################################################
    # 3.1) UNIÃO DE AUTÔMATOS VIA E-TRANSIÇÃO
    #########################################################################
    def unir_afds_com_epsilon(self):
        qtd_estado = 1 
        novo_dtran = {0: {'&': []}}         
        novos_finais = {} 
        simbolos_totais = ['&']
        for nome_token, (estados, dtran, finais, simbolos_de_entrada) in self.afds.items():
            qtd_estados = len(estados)            
            estado_inicial_afd = 0 + qtd_estado
            novo_dtran[0]['&'].append(estado_inicial_afd)

            # ADICIONA NA TABELA DE ALFABETO NOVO SIMBOLO
            for simbolo in simbolos_de_entrada:
                if simbolo not in simbolos_totais:
                    simbolos_totais.append(simbolo)
            
            # COPIA TODAS AS TRANSIÇÕES MAS PARA NÃO FICAR VARIAS ESTADO 1, 1 E 1 RENUMERA 
            for estado_antigo in range(qtd_estados):
                novo_estado = estado_antigo + qtd_estado
                novo_dtran[novo_estado] = {}
                
                transicoes = dtran[estado_antigo]
                for simbolo, destino_antigo in transicoes.items():
                    novo_dtran[novo_estado][simbolo] = [destino_antigo + qtd_estado]
                    
            # RENUMERAR ESTADO FINAIS
            for f in finais:
                novos_finais[f + qtd_estado] = nome_token

            qtd_estado += qtd_estados
            
        return novo_dtran, novos_finais, simbolos_totais

    
    ##########################
    # 0) UMA AFD POR EXPRESSÃO
    ##########################
    def gerar_afd(self):
        for nome, er in self.expressoes.items():
            self.mapa_simbolos = {}       
            self.followpost = {}
            self.contador = 0

            raiz = self.criar_arvore(er)
            self.construir_funcoes(raiz)
            estados, dtran, finais, simbolos_de_entrada = self.construir_estados_d(raiz)

            self.afds[nome] = (estados, dtran, finais, simbolos_de_entrada)
        return self.afds


if __name__ == "__main__":
    analisador = GeradorLexico("arquivo.txt")
    analisador.arrumar_arquivo()
    analisador.gerar_afd()
    analisador.minimizar_afds()

    dtran_afnd, finais_afnd, simbolos = analisador.unir_afds_com_epsilon()

    print("Transições (AFND):", dtran_afnd)
    print("Finais:", finais_afnd)
    print("Alfabeto:", simbolos)
