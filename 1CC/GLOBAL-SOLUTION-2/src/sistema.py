from datetime import date, timedelta
# ===== CONFIGURAÇÕES =====
HOJE = date.today()                 # o sistema usa a data do dia em que é aberto
# HOJE = date(2026, 11, 19)         # para reproduzir os testes, troque pela linha de cima
PRAZOS = {"iluminacao": 15, "acessibilidade": 30, "limpeza": 30, "conservacao": 30}
DIAS_CONTESTACAO = 30
FORMATO_DATA = "%d/%m/%y"
CATEGORIAS = ["iluminacao", "acessibilidade", "limpeza", "conservacao"]
STATUS = ["aberta", "em_analise", "concluida"]
PRAZO_REABERTURA = 60
MOTIVOS = ["tentativa_sem_sucesso", "sem_tentativa"]
ULTIMOS_EVENTOS = 10
# Como cada valor aparece na tela (nos arquivos continuam sem acento)
TEXTO_TELA = {"aberta": "aberta", "em_analise": "em análise", "concluida": "concluída",
              "iluminacao": "iluminação", "acessibilidade": "acessibilidade", "limpeza": "limpeza", "conservacao": "conservação",
              "tentativa_sem_sucesso": "houve tentativa, mas não resolveu", "sem_tentativa": "não houve tentativa"}


# Porteiro: confere a ocorrência antes de entrar no sistema; devolve "" ou o motivo do problema
def validar_ocorrencia(ocorrencia, base_ceps):
    if ocorrencia["descricao"] == "" or ocorrencia["cep"] == "":
        return "campo obrigatório vazio"
    elif not ocorrencia["categoria"] in PRAZOS:
        return "categoria desconhecida"
    elif not ocorrencia["cep"] in base_ceps:
        return "CEP " + ocorrencia["cep"] + " não existe na base"
    else:
        return ""

# Lê o ocorrencias.csv, monta uma ficha por linha e só guarda as aprovadas pelo porteiro
def carregar_ocorrencias(base_ceps):
    with open("data/ocorrencias.csv", encoding="utf-8") as arquivo:

        cabecalho = arquivo.readline() 
        limpa_cabeclho = cabecalho.strip()        # tira o \n (e espaços) das pontas
        cabecalho_pedacos = limpa_cabeclho.split(";") 
        #teste:  print(cabecalho_pedacos) 
        lista_ocorrencias = []
        for linha in arquivo:
            limpa = linha.strip()        # tira o \n (e espaços) das pontas
            pedacos = limpa.split(";")   # corta onde tem ; e devolve uma lista
            if len(pedacos) != len(cabecalho_pedacos):
                if limpa != "":
                    print("Linha ignorada em ocorrencias.csv (incompleta):", limpa)
                continue
            ocorrencia = {}
                    
            for i in range(len(cabecalho_pedacos)):
                ocorrencia[cabecalho_pedacos[i]] = pedacos[i]
            #teste:  print(ocorrencia)
            ocorrencia["data_abertura"] = date.fromisoformat(ocorrencia["data_abertura"])
            problema = validar_ocorrencia(ocorrencia, base_ceps)
            if problema == "":
                lista_ocorrencias.append(ocorrencia)
            else:
                print("Ocorrência", ocorrencia["codigo"], "barrada:", problema)
        #teste:  print(lista_ocorrencias)
        #teste: print(len(lista_ocorrencias))
        #teste: print(lista_ocorrencias[0])
                #teste:  print(cabecalho_pedacos[i], ":", pedacos[i])
        return lista_ocorrencias

# Lê o locais.csv e monta o dicionário CEP -> bairro e rua
def carregar_base_ceps():
    with open("data/locais.csv", encoding="utf-8") as arquivo:
        cabecalho = arquivo.readline()
        base_ceps = {}
        for linha in arquivo:
            limpa = linha.strip()        # tira o \n (e espaços) das pontas
            pedacos = limpa.split(";")   # corta onde tem ; e devolve uma lista
            if len(pedacos) != 3:
                continue
            base_ceps[pedacos[0]] = {"bairro": pedacos[1], "rua": pedacos[2]}
        return base_ceps    

# Lê o contestacoes.csv; guarda a data da contestação mais recente de cada código
def carregar_contestacoes():
    contestacoes = {}
    with open("data/contestacoes.csv", encoding="utf-8") as arquivo:
        arquivo.readline()
        for linha in arquivo:
            pedacos = linha.strip().split(";")
            if len(pedacos) != 3:
                continue
            contestacoes[pedacos[0]] = date.fromisoformat(pedacos[1])
    return contestacoes

# Calcula o status de cada ocorrência pelas datas (prazo da prefeitura + 30 dias para contestar)
def atualizar_status(ocorrencias, contestacoes):
    for ficha in ocorrencias:
        if ficha["codigo"] in contestacoes:
            ficha["contestada"] = True
            inicio = contestacoes[ficha["codigo"]]
            prazo = PRAZO_REABERTURA
        else:
            ficha["contestada"] = False
            inicio = ficha["data_abertura"]
            prazo = PRAZOS[ficha["categoria"]]
        ficha["vencimento"] = inicio + timedelta(days=prazo)
        ficha["fim_contestacao"] = ficha["vencimento"] + timedelta(days=DIAS_CONTESTACAO)
        if HOJE < ficha["vencimento"]:
            ficha["status"] = "aberta"
        elif HOJE >= ficha["vencimento"] and HOJE < ficha["fim_contestacao"]:
            ficha["status"] = "em_analise"
        else:
            ficha["status"] = "concluida"

# Pausa: segura a tela até a pessoa digitar 0
def voltar_ao_menu():
    resposta = ""
    while resposta != "0":
        resposta = input("\nDigite 0 para voltar ao menu principal: ")

# Mostra o menu e chama a função de cada opção, até escolher 0
def menu_principal():
    opcao = ""
    while opcao != "0":                    # repete até a pessoa escolher sair
        print("\n===== PAINEL DE OCORRÊNCIAS · BORDA DO CAMPO =====")
        print("Hoje:", HOJE.strftime(FORMATO_DATA))
        print("Como funciona: a ocorrência fica aberta durante o prazo da prefeitura (15 dias para iluminação,")
        print("30 para as demais). Depois fica em análise por 30 dias, quando você pode contestar se o problema")
        print("continua. Se ninguém contestar, ela é concluída.\n")
        print("1. Listar todas as ocorrências")
        print("2. Buscar uma ocorrência pelo código")
        print("3. Filtrar por categoria ou por status")
        print("4. Registrar uma nova ocorrência")
        print("5. Contestar uma ocorrência")
        print("6. Ver as últimas atualizações")
        print("7. Ver a fila de ocorrências abertas")
        print("8. Painel de indicadores")
        print("9. Ver ocorrências por bairro e rua")
        print("0. Sair")

        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            print("__________LISTANDO OCORRENCIAS__________")
            mostrar_ocorrencias(ocorrencias, base_ceps)
            voltar_ao_menu()
        elif opcao == "2":
            print("__________BUSCAR OCORRÊNCIA__________")
            buscar_ocorrencia(por_codigo, base_ceps)
            voltar_ao_menu()
        elif opcao == "3":
            print("__________FILTRAR OCORRÊNCIAS__________")
            filtrar_ocorrencias(ocorrencias, base_ceps)
            voltar_ao_menu()
        elif opcao == "4":
            print("__________REGISTRAR OCORRÊNCIA__________")
            registrar_ocorrencia(ocorrencias, por_codigo, base_ceps, contestacoes)
            voltar_ao_menu()
        elif opcao == "5":
            print("__________CONTESTAR OCORRÊNCIA__________")
            contestar_ocorrencia(ocorrencias, por_codigo, contestacoes)
            voltar_ao_menu()
        elif opcao == "6":
            print("__________ÚLTIMAS ATUALIZAÇÕES__________")
            mostrar_historico(ocorrencias, base_ceps)
            voltar_ao_menu()
        elif opcao == "7":
            print("__________FILA DE OCORRÊNCIAS ABERTAS__________")
            mostrar_fila(ocorrencias, base_ceps)
            voltar_ao_menu()
        elif opcao == "8":
            print("__________PAINEL DE INDICADORES__________")
            mostrar_indicadores(ocorrencias, base_ceps)
            voltar_ao_menu()
        elif opcao == "9":
            print("__________OCORRÊNCIAS POR BAIRRO E RUA__________")
            mostrar_hierarquia(ocorrencias, base_ceps)
            voltar_ao_menu()
        elif opcao == "0":
            print("__________Até logo!__________")
        else:
            print("Opção inválida. Digite um número do menu.")

#  "1. Listar todas as ocorrências" / lista todas as ocorrências com a rua
def mostrar_ocorrencias(ocorrencias, base_ceps):        #recebe a lista de ococrrencias 
    for mostrar in ocorrencias:
        rua = base_ceps[mostrar["cep"]]["rua"]

        print(mostrar["codigo"], "|", TEXTO_TELA[mostrar["categoria"]], "|", rua, "|", TEXTO_TELA[mostrar["status"]])
    print("\naberta: dentro do prazo da prefeitura; em análise: dá para contestar; concluída: encerrada")
    print("Para ver os detalhes e os prazos de uma ocorrência, use a opção 2.")

#  "2. Buscar uma ocorrência pelo código" / Monta o dicionário código -> ficha, para achar uma ocorrência direto (tabela hash
def montar_por_codigo(ocorrencias):
    por_codigo = {}
    for ficha in ocorrencias:
        por_codigo[ficha["codigo"]] = ficha
    return por_codigo

# mostra a ficha completa de um código
def buscar_ocorrencia(por_codigo, base_ceps):
    codigo = input("Digite o código da ocorrência (ex.: I006): ").strip().upper()
    if codigo in por_codigo:
        ficha = por_codigo[codigo]
        local = base_ceps[ficha["cep"]]
        print("Código:", ficha["codigo"])
        print("Categoria:", TEXTO_TELA[ficha["categoria"]])
        print("Descrição:", ficha["descricao"])
        print("Local:", local["rua"], ficha["numero"], "|", local["bairro"])
        print("Aberta em:", ficha["data_abertura"].strftime(FORMATO_DATA))
        print("Status:", TEXTO_TELA[ficha["status"]])
        vencimento = ficha["vencimento"].strftime(FORMATO_DATA)
        ultimo_dia = (ficha["fim_contestacao"] - timedelta(days=1)).strftime(FORMATO_DATA)
        if ficha["status"] == "aberta" and ficha["contestada"]:
            print("\nFoi contestada e está atrasada. O novo prazo da prefeitura vence em", vencimento + ".")
            print("Se o problema continuar depois disso, você poderá contestar de novo até", ultimo_dia, "(opção 5).")
        elif ficha["status"] == "aberta":
            print("\nAinda está no prazo da prefeitura, que vence em", vencimento + ".")
            print("Se o problema continuar depois disso, você poderá contestar até", ultimo_dia, "(opção 5).")
        elif ficha["status"] == "em_analise":
            print("\nO prazo da prefeitura venceu em", vencimento, "e o sistema considera o problema resolvido.")
            print("Se o problema continua, conteste até", ultimo_dia, "(opção 5).")
        else:
            print("\nConcluída: ninguém contestou dentro do prazo.")
            print("Se o problema voltou ou continua, registre uma nova ocorrência (opção 4).")
    else:
        print("Ocorrência", codigo, "não encontrada. Confira o código ou veja todos na opção 1.")

# Mostra uma lista numerada e devolve o valor escolhido, ou "" se a escolha for inválida
def escolher_opcao(opcoes):
    for i in range(len(opcoes)):
        print(i + 1, "-", TEXTO_TELA[opcoes[i]])
    escolha = input("Digite o número: ").strip()
    for i in range(len(opcoes)):
        if escolha == str(i + 1):
            return opcoes[i]
    return ""

#  "3. Filtrar por categoria ou por status" / Mostra só as ocorrências de uma categoria ou de um status
def filtrar_ocorrencias(ocorrencias, base_ceps):
    print("1. Por categoria")
    print("2. Por status")
    tipo = input("Escolha 1 ou 2: ").strip()
    if tipo == "1":
        campo = "categoria"
        valor = escolher_opcao(CATEGORIAS)
    elif tipo == "2":
        campo = "status"
        valor = escolher_opcao(STATUS)
    else:
        print("Opção inválida.")
        return
    if valor == "":
        print("Opção inválida.")
        return
    quantidade = 0
    for ficha in ocorrencias:
        if ficha[campo] == valor:
            rua = base_ceps[ficha["cep"]]["rua"]
            print(ficha["codigo"], "|", TEXTO_TELA[ficha["categoria"]], "|", rua, "|", TEXTO_TELA[ficha["status"]])            
            quantidade = quantidade + 1
    print("Encontradas:", quantidade)
    if quantidade == 0:
        print("Nenhuma ocorrência com essa escolha no momento.")

#  "4. Registrar uma nova ocorrência" / Cria o próximo código: inicial da categoria + maior número + 1
def gerar_codigo(categoria, ocorrencias):
    maior = 0
    for ficha in ocorrencias:
        numero = int(ficha["codigo"][1:])
        if numero > maior:
            maior = numero
    return categoria[0].upper() + str(maior + 1).zfill(3)

# Acrescenta a ocorrência nova no fim do ocorrencias.csv
def gravar_ocorrencia(nova):
    linha = (nova["codigo"] + ";" + nova["categoria"] + ";" + nova["descricao"] + ";"
        + nova["cep"] + ";" + nova["numero"] + ";" + nova["data_abertura"].isoformat())
    with open("data/ocorrencias.csv", "a", encoding="utf-8") as arquivo:
        arquivo.write(linha + "\n")

# Cadastra uma ocorrência nova, passando pelo porteiro
def registrar_ocorrencia(ocorrencias, por_codigo, base_ceps, contestacoes):
    print("Registre um problema da sua rua. Você não precisa se identificar.")
    print("Escolha a categoria:")
    categoria = escolher_opcao(CATEGORIAS)
    if categoria == "":
        print("Opção inválida. Nada foi registrado.")
        return
    descricao = input("Descreva o problema: ").strip().replace(";", ",")
    cep = input("CEP do local (ex.: 00110-040): ").strip()
    numero = input("Número mais próximo (ou s/n): ").strip()
    nova = {
        "codigo": gerar_codigo(categoria, ocorrencias),
        "categoria": categoria,
        "descricao": descricao,
        "cep": cep,
        "numero": numero,
        "data_abertura": HOJE,

    }
    problema = validar_ocorrencia(nova, base_ceps)
    if problema == "":
        ocorrencias.append(nova)
        por_codigo[nova["codigo"]] = nova
        gravar_ocorrencia(nova)
        atualizar_status(ocorrencias, contestacoes)
        local = base_ceps[cep]
        print("Ocorrência registrada com o código", nova["codigo"])
        print("Local:", local["rua"], numero, "|", local["bairro"])
        print("\nGuarde esse código: com ele você acompanha o pedido (opção 2) e contesta, se precisar (opção 5).")
        print("A prefeitura tem", PRAZOS[categoria], "dias para resolver, até", nova["vencimento"].strftime(FORMATO_DATA) + ".") 
        ultimo_dia = nova["fim_contestacao"] - timedelta(days=1)
        print("Se o problema continuar depois disso, você pode contestar de", nova["vencimento"].strftime(FORMATO_DATA), "a", ultimo_dia.strftime(FORMATO_DATA) + ".")
    elif "CEP" in problema:
        print("O CEP", cep, "não existe em Borda do Campo. Nada foi gravado.")
        print("Confira o CEP do local e registre de novo, digitando um CEP correspondente, no formato 00110-040.")
    else:
        print("Não foi possível registrar:", problema)
        print("Nada foi gravado. Confira os dados e registre de novo.")

#  "5. Contestar uma ocorrência" / Acrescenta a contestação no fim do contestacoes.csv
def gravar_contestacao(codigo, data, motivo):
    with open("data/contestacoes.csv", "a", encoding="utf-8") as arquivo:
        arquivo.write(codigo + ";" + data.isoformat() + ";" + motivo + "\n")

# Contesta uma ocorrência em análise; ela volta a ficar aberta com novo prazo
def contestar_ocorrencia(ocorrencias, por_codigo, contestacoes):
    print("Use esta opção se o prazo da prefeitura já venceu e o problema continua.")
    print("A contestação é aceita enquanto a ocorrência está em análise, nos 30 dias depois do prazo.")
    codigo = input("Digite o código da ocorrência (ex.: I006): ").strip().upper()
    if not codigo in por_codigo:
        print("Ocorrência", codigo, "não encontrada.")
        return
    ficha = por_codigo[codigo]
    ultimo_dia = ficha["fim_contestacao"] - timedelta(days=1)
    if ficha["status"] == "aberta" and ficha["contestada"]:
        print("Já foi contestada e está atrasada. Novo prazo da prefeitura:", ficha["vencimento"].strftime(FORMATO_DATA))
        print("A partir dessa data, se o problema continuar, você poderá contestar até", ultimo_dia.strftime(FORMATO_DATA) + ".")
    elif ficha["status"] == "aberta":
        print("Ainda está no prazo da prefeitura. Vence em", ficha["vencimento"].strftime(FORMATO_DATA))
        print("A partir dessa data, se o problema continuar, você poderá contestar até", ultimo_dia.strftime(FORMATO_DATA) + ".")
    elif ficha["status"] == "concluida":
        print("O prazo para contestar terminou em", ficha["fim_contestacao"].strftime(FORMATO_DATA))
        print("Se o problema continua, registre uma nova ocorrência (opção 4).")
    else:
        print("Está em análise: o prazo da prefeitura venceu em", ficha["vencimento"].strftime(FORMATO_DATA) + ". Você pode contestar até", ultimo_dia.strftime(FORMATO_DATA) + ".")
        print("Qual o motivo da contestação?")
        motivo = escolher_opcao(MOTIVOS)
        if motivo == "":
            print("Opção inválida. Nada foi contestado.")
            return
        gravar_contestacao(codigo, HOJE, motivo)
        contestacoes[codigo] = HOJE
        atualizar_status(ocorrencias, contestacoes)
        print("Contestação registrada. A ocorrência voltou para aberta e está atrasada.")
        print("Novo prazo da prefeitura:", ficha["vencimento"].strftime(FORMATO_DATA))
        print("Atrasada quer dizer que a prefeitura já perdeu um prazo para esse problema.")
        print("Se o novo prazo vencer e o problema continuar, você poderá contestar de novo.")

#  "6. Ver as últimas atualizações" / Junta registros e contestações em ordem de data (o mais novo fica no topo da pilha)
def montar_historico(ocorrencias, base_ceps):
    historico = []
    for ficha in ocorrencias:
        rua = base_ceps[ficha["cep"]]["rua"]
        historico.append([ficha["data_abertura"], ficha["codigo"] + " registrada: " + ficha["descricao"] + " (" + rua + ")"])
        primeiro_vencimento = ficha["data_abertura"] + timedelta(days=PRAZOS[ficha["categoria"]])
        if primeiro_vencimento <= HOJE:
            historico.append([primeiro_vencimento, ficha["codigo"] + " entrou em análise (prazo da prefeitura venceu)"])
        if ficha["contestada"] and ficha["vencimento"] <= HOJE:
            historico.append([ficha["vencimento"], ficha["codigo"] + " entrou em análise de novo (venceu o novo prazo)"])
        if ficha["status"] == "concluida":
            historico.append([ficha["fim_contestacao"], ficha["codigo"] + " concluída (ninguém contestou em 30 dias)"])
    with open("data/contestacoes.csv", encoding="utf-8") as arquivo:
        arquivo.readline()
        for linha in arquivo:
            pedacos = linha.strip().split(";")
            if len(pedacos) != 3:
                continue
            historico.append([date.fromisoformat(pedacos[1]), pedacos[0] + " contestada: " + TEXTO_TELA[pedacos[2]]])
    historico.sort()
    return historico

# Tira da pilha e mostra os eventos mais recentes
def mostrar_historico(ocorrencias, base_ceps):
    pilha = montar_historico(ocorrencias, base_ceps)
    print("Total de eventos:", len(pilha), "| mostrando os", ULTIMOS_EVENTOS, "mais recentes")
    mostrados = 0
    while len(pilha) > 0 and mostrados < ULTIMOS_EVENTOS:
        evento = pilha.pop()
        print(evento[0].strftime(FORMATO_DATA), "|", evento[1])
        mostrados = mostrados + 1

#  "7. Ver a fila de ocorrências abertas" / Monta a fila com as ocorrências abertas, na ordem em que chegaram
def montar_fila(ocorrencias):
    fila = []
    for ficha in ocorrencias:
        if ficha["status"] == "aberta":
            fila.append(ficha)
    return fila

# Atende a fila do começo, mostrando quanto falta para vencer
def mostrar_fila(ocorrencias, base_ceps):
    fila = montar_fila(ocorrencias)
    print("Ocorrências abertas na fila:", len(fila), "(a mais antiga é a primeira)")
    if len(fila) == 0:
        print("Nenhuma ocorrência aberta no momento.")
    else:
        print("ATRASADA quer dizer que a ocorrência já foi contestada: a prefeitura perdeu o primeiro prazo.\n")
    posicao = 1
    while len(fila) > 0:
        ficha = fila.pop(0)
        rua = base_ceps[ficha["cep"]]["rua"]
        dias = (ficha["vencimento"] - HOJE).days
        if ficha["contestada"]:
            aviso = "| ATRASADA (contestada)"
        else:
            aviso = ""
        print(str(posicao) + "º |", ficha["codigo"], "|", rua, "| vence em", dias, "dias", aviso)
        posicao = posicao + 1

#  "8. Painel de indicadores" / Monta a matriz categoria x status, contando as ocorrências de cada casa
def montar_matriz(ocorrencias):
    matriz = []
    for categoria in CATEGORIAS:
        linha = []
        for status in STATUS:
            linha.append(0)
        matriz.append(linha)
    for ficha in ocorrencias:
        i = CATEGORIAS.index(ficha["categoria"])
        j = STATUS.index(ficha["status"])
        matriz[i][j] = matriz[i][j] + 1
    return matriz

# Conta quantas contestações há de cada motivo
def contar_motivos():
    motivos = {}
    for motivo in MOTIVOS:
        motivos[motivo] = 0
    with open("data/contestacoes.csv", encoding="utf-8") as arquivo:
        arquivo.readline()
        for linha in arquivo:
            pedacos = linha.strip().split(";")
            if len(pedacos) != 3:
                continue
            if pedacos[2] in motivos:
                motivos[pedacos[2]] = motivos[pedacos[2]] + 1
    return motivos

# Calcula parte / total x 100, com proteção para total zero
def porcentagem(parte, total):
    if total == 0:
        return 0
    return round(parte / total * 100, 1)
# Calcula a média (soma / quantidade), com proteção para quantidade zero
def media(soma, quantidade):
    if quantidade == 0:
        return 0
    return round(soma / quantidade, 1)


# Painel com a matriz, as porcentagens, as atrasadas, os motivos e as ruas
def mostrar_indicadores(ocorrencias, base_ceps):
    total = len(ocorrencias)
    matriz = montar_matriz(ocorrencias)
    print("Total de ocorrências válidas:", total)

    print("\n--- Matriz: categoria x status ---")
    print("categoria".ljust(16), "aberta".ljust(8), "em análise".ljust(11), "concluída".ljust(10), "total")
    for i in range(len(CATEGORIAS)):
        linha = matriz[i]
        total_categoria = linha[0] + linha[1] + linha[2]
        print(TEXTO_TELA[CATEGORIAS[i]].ljust(16), str(linha[0]).ljust(8), str(linha[1]).ljust(11), str(linha[2]).ljust(10), total_categoria)

    print("\n--- Por status (quantidade / total x 100) ---")
    for j in range(len(STATUS)):
        quantidade = 0
        for i in range(len(CATEGORIAS)):
            quantidade = quantidade + matriz[i][j]
        print(TEXTO_TELA[STATUS[j]].ljust(12), quantidade, "de", total, "=", porcentagem(quantidade, total), "%")

    print("\n--- Por categoria (quantidade / total x 100) ---")
    for i in range(len(CATEGORIAS)):
        quantidade = matriz[i][0] + matriz[i][1] + matriz[i][2]
        print(TEXTO_TELA[CATEGORIAS[i]].ljust(16), quantidade, "de", total, "=", porcentagem(quantidade, total), "%")

    abertas = 0
    atrasadas = 0
    por_rua = {}
    for ficha in ocorrencias:
        if ficha["status"] == "aberta":
            abertas = abertas + 1
            if ficha["contestada"]:
                atrasadas = atrasadas + 1
        if ficha["status"] != "concluida":
            rua = base_ceps[ficha["cep"]]["rua"]
            if rua in por_rua:
                por_rua[rua] = por_rua[rua] + 1
            else:
                por_rua[rua] = 1

    print("\n--- Pendências atrasadas (contestadas) ---")
    print("Atrasadas:", atrasadas, "de", abertas, "abertas =", porcentagem(atrasadas, abertas), "%")

    print("\n--- Tempo de acompanhamento (em dias) ---")
    dias_pendentes = 0
    pendentes = 0
    dias_concluidas = 0
    concluidas = 0
    for ficha in ocorrencias:
        if ficha["status"] == "concluida":
            dias_concluidas = dias_concluidas + (ficha["fim_contestacao"] - ficha["data_abertura"]).days
            concluidas = concluidas + 1
        else:
            dias_pendentes = dias_pendentes + (HOJE - ficha["data_abertura"]).days
            pendentes = pendentes + 1
    print("Não concluídas: soma", dias_pendentes, "dias /", pendentes, "=", media(dias_pendentes, pendentes), "dias em acompanhamento, em média")
    print("Concluídas: soma", dias_concluidas, "dias /", concluidas, "=", media(dias_concluidas, concluidas), "dias da abertura até a conclusão, em média")

    print("\n--- Motivos das contestações ---")
    motivos = contar_motivos()
    for motivo in MOTIVOS:
        print(TEXTO_TELA[motivo].ljust(35), motivos[motivo])

    print("\n--- Ruas com mais de uma ocorrência não concluída ---")
    mais_ocorrencias = ""
    maior = 0
    for rua in por_rua:
        if por_rua[rua] > 1:
            print(rua.ljust(26), por_rua[rua])
        if por_rua[rua] > maior:
            maior = por_rua[rua]
            mais_ocorrencias = rua
    print("Rua com mais problemas em aberto:", mais_ocorrencias, "(" + str(maior) + ")")
#  "9. Ver ocorrências por bairro e rua" / Monta a árvore bairro -> rua -> códigos com as ocorrências não concluídas
def montar_hierarquia(ocorrencias, base_ceps):
    hierarquia = {}
    for ficha in ocorrencias:
        if ficha["status"] != "concluida":
            local = base_ceps[ficha["cep"]]
            bairro = local["bairro"]
            rua = local["rua"]
            if not bairro in hierarquia:
                hierarquia[bairro] = {}
            if not rua in hierarquia[bairro]:
                hierarquia[bairro][rua] = []
            hierarquia[bairro][rua].append(ficha["codigo"])
    return hierarquia

# Mostra a árvore por bairro e rua
def mostrar_hierarquia(ocorrencias, base_ceps):
    hierarquia = montar_hierarquia(ocorrencias, base_ceps)
    print("Ocorrências não concluídas, por bairro e rua:")
    print("O número entre parênteses é quantas ocorrências o bairro tem em aberto.")
    if len(hierarquia) == 0:
        print("Nenhuma ocorrência em aberto no momento.")
    for bairro in hierarquia:
        total_bairro = 0
        for rua in hierarquia[bairro]:
            total_bairro = total_bairro + len(hierarquia[bairro][rua])
        print("\n" + bairro, "(" + str(total_bairro) + ")")
        for rua in hierarquia[bairro]:
            codigos = hierarquia[bairro][rua]
            print("   -", rua + ":", ", ".join(codigos))


# ===== PROGRAMA PRINCIPAL =====
base_ceps = carregar_base_ceps()
ocorrencias = carregar_ocorrencias(base_ceps)
contestacoes = carregar_contestacoes()
atualizar_status(ocorrencias, contestacoes)
por_codigo = montar_por_codigo(ocorrencias)

# Teste: print(base_ceps["00110-040"]["rua"])  
menu_principal()


   
