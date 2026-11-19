# Neighborhood Action Dashboard · Borda do Campo

Painel comunitário de ocorrências, feito em Python e usado no terminal, para os moradores registrarem problemas da rua e acompanharem a situação de cada um. Projeto da **Global Solution 2026.2 (CitizenTech)** da FIAP.

## Equipe

| Integrante | RM |
|---|---|
| Gabriel Storer Romero | RM575479 |

Projeto individual · Ciência da Computação (On-Line) · turma 1CCOR-2026.

## Sumário

1. [A comunidade, o problema e o público](#1-a-comunidade-o-problema-e-o-público)
2. [Estruturas de dados e por que cada uma](#2-estruturas-de-dados-e-por-que-cada-uma)
3. [Regras lógicas](#3-regras-lógicas)
4. [Indicadores](#4-indicadores)
5. [Como executar](#5-como-executar)
6. [Exemplo de uso](#6-exemplo-de-uso)
7. [Acessibilidade, inclusão e privacidade](#7-acessibilidade-inclusão-e-privacidade)
8. [Vídeo](#8-vídeo)
9. [Conclusões, limitações e aprendizados](#9-conclusões-limitações-e-aprendizados)
10. [Estrutura do repositório e documentos](#10-estrutura-do-repositório-e-documentos)

## 1. A comunidade, o problema e o público

**A comunidade.** Borda do Campo é uma cidade fictícia com 4 bairros e 20 ruas, todos com nomes e CEPs inventados. O nome vem da antiga vila de Santo André da Borda do Campo, fundada em 1553, que deu origem a Santo André. Sou morador do Grande ABC e quis que o projeto tivesse a cara da minha região.

**O problema.** Quando um morador vê um problema na rua, ele faz uma reclamação na prefeitura e, depois disso, perde a referência de como está o pedido. Ele também não sabe se os vizinhos estão reclamando da mesma coisa. Em Santo André, em 2017, só 30 dos 62 pedidos de manutenção de calçada foram respondidos (Diário do Grande ABC, 2018).

**A solução.** O morador registra o problema e recebe um código. Enquanto o prazo da prefeitura corre, a ocorrência fica **aberta**. Quando o prazo vence, o sistema considera que o conserto foi feito e a ocorrência fica **em análise** por 30 dias, que é quando o morador pode contestar se o problema continua. Sem contestação, ela é **concluída**. Com contestação, volta a ficar aberta, marcada como **atrasada**, com um novo prazo de 60 dias. Tudo isso acontece pelas datas, sem ninguém precisar atualizar nada. Uma ferramenta do povo para o povo cobrar.

**O público.** Os moradores de Borda do Campo, com atenção a quem tem pouca familiaridade com tecnologia, como os idosos.

| Situação | Significado |
|---|---|
| aberta | Dentro do prazo da prefeitura (15 dias para iluminação, 30 para as demais categorias) |
| em análise | O prazo venceu; o morador tem 30 dias para contestar se o problema continua |
| concluída | Passaram os 30 dias sem contestação |
| atrasada | Aberta e já contestada: a prefeitura perdeu um prazo para esse problema |

## 2. Estruturas de dados e por que cada uma

| Estrutura | Onde | Por que foi escolhida |
|---|---|---|
| **Lista** de fichas (dicionários) | `ocorrencias` | É o fichário: o sistema percorre a lista para listar, filtrar e calcular os indicadores |
| **Dicionário** pelo código | `por_codigo` | A busca tem uma resposta só, então o dicionário vai direto nela, como a agenda do celular (a ideia de tabela hash da Fase 3). Ele aponta para as mesmas fichas da lista, sem copiar |
| **Dicionários** de apoio | `base_ceps`, `PRAZOS`, `contestacoes`, `TEXTO_TELA` | O CEP leva à rua e ao bairro; cada categoria tem seu prazo num lugar só; cada código guarda a data da última contestação; cada valor guardado sem acento tem seu texto de tela |
| **Pilha** | Últimas atualizações (opção 6) | O último evento que entra é o primeiro que sai: o morador vê primeiro o que aconteceu por último |
| **Fila** | Ocorrências abertas (opção 7) | Quem chegou primeiro é atendido primeiro: a mais antiga aparece no topo |
| **Matriz** 4 × 3 | Painel (opção 8) | Linhas são categorias e colunas são situações. Somar uma linha dá o total da categoria; somar uma coluna, o total da situação |
| **Hierarquia** bairro → rua → códigos | Opção 9 | Mostra em que rua e em que bairro os problemas se acumulam |

**Os dados como um extrato.** Os arquivos `data/ocorrencias.csv` e `data/contestacoes.csv` funcionam como um extrato bancário: só recebem linhas novas no fim e nunca têm uma linha alterada. A situação de cada ocorrência não é gravada; ela é calculada toda vez que o sistema abre, a partir das datas e da data do dia. Assim, o painel nunca fica desatualizado.

**Formato dos arquivos.** Texto com campos separados por `;`. A primeira linha dá o nome de cada campo.

| Arquivo | Campos |
|---|---|
| `data/ocorrencias.csv` | `codigo;categoria;descricao;cep;numero;data_abertura` (data no formato ano-mês-dia) |
| `data/contestacoes.csv` | `codigo;data;motivo` |
| `data/locais.csv` | `cep;bairro;rua` |

Campos obrigatórios: descrição e CEP. Categorias e situações são guardadas em minúsculo e sem acento.

Os dados de demonstração ficam nesses três arquivos da pasta `data/`, no lugar de um único `dados.csv`: um para as ocorrências, um para as contestações e um para as ruas.

## 3. Regras lógicas

**Cadastro (opção 4).** A categoria é escolhida por número; a descrição, o CEP e o número são digitados. O código é criado automaticamente (inicial da categoria + próximo número, como `I013`). A ocorrência passa pela validação e, se aprovada, é gravada no fim do arquivo. O sistema informa o prazo da prefeitura e o período para contestar.

**Validação.** Toda ocorrência, vinda do arquivo ou do cadastro, passa pela mesma validação antes de entrar no sistema:

```python
if ocorrencia["descricao"] == "" or ocorrencia["cep"] == "":
    return "campo obrigatório vazio"
elif not ocorrencia["categoria"] in PRAZOS:
    return "categoria desconhecida"
elif not ocorrencia["cep"] in base_ceps:
    return "CEP " + ocorrencia["cep"] + " não existe na base"
```

O `or` barra o registro se faltar qualquer um dos dois campos. O `not` barra categoria e CEP que não existem. É essa regra que barra a ocorrência **L013**, que está no arquivo com um CEP inexistente, logo ao abrir o sistema. Linhas incompletas no arquivo também são ignoradas, com aviso.

**Consulta.** Busca pelo código (opção 2) direto no dicionário, aceitando minúsculas e espaços; filtro por categoria ou por situação (opção 3), escolhidos por número, percorrendo a lista.

**Atualização de situação.** A situação é calculada pelas datas, com esta expressão booleana:

```python
if HOJE < ficha["vencimento"]:
    ficha["status"] = "aberta"
elif HOJE >= ficha["vencimento"] and HOJE < ficha["fim_contestacao"]:
    ficha["status"] = "em_analise"
else:
    ficha["status"] = "concluida"
```

O `and` garante que só fica em análise quem **já venceu** e **ainda está** dentro dos 30 dias de contestação. A contestação (opção 5) só é aceita em análise: ela grava uma linha no `contestacoes.csv`, a ocorrência volta a ficar aberta com novo prazo de 60 dias, e a mudança aparece no histórico (opção 6). Uma ocorrência **aberta and contestada** é mostrada como atrasada. Cada situação gera uma mensagem diferente: a aberta informa até quando vai o prazo, a concluída orienta a registrar uma nova ocorrência e a em análise pede o motivo da contestação.

## 4. Indicadores

Painel da opção 8. Cada número aparece com a conta usada. Como o sistema usa a data do dia, os resultados mudam com o tempo; os valores abaixo são de **17/11/2026**.

| Indicador | Fórmula | Resultado em 17/11/2026 |
|---|---|---|
| Matriz categoria × situação | Para cada ocorrência, soma 1 na casa da sua categoria e da sua situação | Ver o painel no sistema |
| Por situação | quantidade da situação ÷ total × 100 | Abertas 5 de 12 (41,7%) · em análise 4 de 12 (33,3%) · concluídas 3 de 12 (25,0%) |
| Por categoria | quantidade da categoria ÷ total × 100 | 3 de 12 (25,0%) em cada uma das 4 |
| Pendências atrasadas | abertas já contestadas ÷ abertas × 100 | 1 de 5 (20,0%) |
| Tempo de acompanhamento | média de dias desde a abertura (não concluídas) e da abertura até a conclusão (concluídas) | 26,6 dias (239 ÷ 9) e 55,0 dias (165 ÷ 3) |
| Motivos das contestações | contagem de cada motivo | "não houve tentativa": 1 · "houve tentativa, mas não resolveu": 0 |
| Rua com mais problemas em aberto | contagem por rua das não concluídas, guardando a maior | Rua Principal, com 3 |

**Interpretação.** Os registros estão equilibrados entre as quatro categorias, então nenhum tipo de problema domina. Quase metade das ocorrências ainda está no prazo da prefeitura, e quem espera, espera em média quase um mês. Um ciclo completo leva em média 55 dias: o prazo da prefeitura somado aos 30 dias de contestação. A Rua Principal concentra 3 dos 9 problemas não resolvidos, informação que pode virar cobrança coletiva. Por serem dados simulados, os números não descrevem uma cidade real, mas mostram como o painel transforma reclamações soltas em informação útil para a comunidade.

## 5. Como executar

Requisito: Python 3 (testado no Python 3.10). Não usa nenhuma biblioteca externa.

Na pasta raiz do repositório, rode:

```
python src/sistema.py
```

O comando precisa ser rodado da pasta raiz, porque o programa lê os arquivos da pasta `data/`. Em alguns sistemas, o comando é `python3`. Para sair, escolha a opção 0 no menu.

## 6. Exemplo de uso

Exemplo rodado em 17/11/2026 numa cópia dos dados, para que os arquivos do repositório continuem limpos. As linhas do menu foram omitidas.

**Ao abrir**, a validação barra a L013 e o menu mostra a data do dia e um resumo de como funciona:

```
Ocorrência L013 barrada: CEP 00150-010 não existe na base

===== PAINEL DE OCORRÊNCIAS · BORDA DO CAMPO =====
Hoje: 17/11/26
Como funciona: a ocorrência fica aberta durante o prazo da prefeitura (15 dias para iluminação,
30 para as demais). Depois fica em análise por 30 dias, quando você pode contestar se o problema
continua. Se ninguém contestar, ela é concluída.
```

**Cadastro (opção 4):** categoria 1, descrição, CEP e número.

```
Ocorrência registrada com o código I013
Local: Rua Principal 15 | Jardim do Campo

Guarde esse código: com ele você acompanha o pedido (opção 2) e contesta, se precisar (opção 5).
A prefeitura tem 15 dias para resolver, até 02/12/26.
Se o problema continuar depois disso, você pode contestar de 02/12/26 a 31/12/26.
```

**Consulta (opção 2):** código I013.

```
Código: I013
Categoria: iluminação
Descrição: Poste apagado na esquina
Local: Rua Principal 15 | Jardim do Campo
Aberta em: 17/11/26
Status: aberta

Ainda está no prazo da prefeitura, que vence em 02/12/26.
Se o problema continuar depois disso, você poderá contestar até 31/12/26 (opção 5).
```

**Alteração de situação (opção 5):** a A004 está em análise, e o morador contesta com o motivo 2.

```
Está em análise: o prazo da prefeitura venceu em 25/10/26. Você pode contestar até 23/11/26.
Qual o motivo da contestação?
1 - houve tentativa, mas não resolveu
2 - não houve tentativa
Digite o número: 2
Contestação registrada. A ocorrência voltou para aberta e está atrasada.
Novo prazo da prefeitura: 16/01/27
```

**Histórico (opção 6):** a contestação e o cadastro aparecem no topo da pilha.

```
17/11/26 | I013 registrada: Poste apagado na esquina (Rua Principal)
17/11/26 | A004 contestada: não houve tentativa
15/11/26 | A007 entrou em análise (prazo da prefeitura venceu)
```

**Saída (opção 0):**

```
Até logo!
```

## 7. Acessibilidade, inclusão e privacidade

- **Escolher em vez de digitar:** o menu, a categoria, o filtro e o motivo da contestação são escolhidos por número. Só se digita o que não cabe numa lista: descrição, CEP, número e código.
- **Erros não travam o sistema:** quando algo é digitado errado, o sistema avisa o que aconteceu e o que fazer. Aceita maiúsculas, minúsculas e espaços a mais.
- **Orientação em cada tela:** o menu mostra a data do dia e como funciona o ciclo; o cadastro informa o código, o prazo e o período para contestar; a busca explica o que a situação significa e qual opção usar em seguida.
- **Leitura confortável:** cada opção termina com uma pausa até a pessoa digitar 0; as datas aparecem no formato brasileiro; situações e categorias aparecem com acento na tela.
- **Privacidade:** nenhum dado pessoal é pedido (nome, CPF, telefone ou e-mail), e ninguém precisa se identificar. Os endereços são fictícios, com CEPs começando em 00, uma faixa que não existe nos Correios.
- **Limite reconhecido:** o painel roda num computador, e quem não tem acesso fica de fora. Ele é um apoio, não um substituto do atendimento presencial, como recomendam as diretrizes da ONU-Habitat para cidades inteligentes centradas nas pessoas.

## 8. Vídeo

Apresentação no YouTube (não listado): **https://youtu.be/qecaBMu8ymI**

## 9. Conclusões, limitações e aprendizados

**Conclusões.** O painel devolve ao morador duas coisas que hoje ele não tem: a referência de como está a sua reclamação e a visão do que os vizinhos também estão cobrando. Uma queixa isolada vira um dado compartilhado, que serve de argumento para uma cobrança coletiva.

**Limitações.**
- **Os dados só devem entrar pelo próprio sistema.** O programa espera cada linha com os campos na ordem certa e as datas no formato ano-mês-dia. Uma data inexistente escrita à mão ou o arquivo de contestações apagado impedem a leitura, e uma alteração manual quebra a ideia de extrato. Pelo cadastro e pela contestação, isso não acontece.
- **Os prazos automáticos não confirmam o conserto.** Um problema consertado antes do prazo continua aparecendo como aberto, e um problema nunca atendido passa a em análise e depois a concluído, se ninguém contestar. Uma integração com a prefeitura resolveria essa diferença, mas está fora do escopo do projeto.
- **Dados simulados:** os números não descrevem uma cidade real.

**Aprendizados.** As estruturas das três primeiras fases resolvem problemas reais quando escolhidas pelo motivo certo. A decisão que mais mudou o projeto foi não gravar a situação e calculá-la pelas datas. E o código não termina quando funciona: testando como usuário, descobri que o filtro induzia ao erro, e olhando a tela vi títulos e legendas repetidos que os testes automáticos não pegaram.

## 10. Estrutura do repositório e documentos

```
├── README.md
├── src/
│   └── sistema.py          programa principal
├── data/
│   ├── ocorrencias.csv     13 ocorrências (12 válidas e a L013, barrada de propósito)
│   ├── contestacoes.csv    contestações registradas
│   └── locais.csv          20 ruas com CEP e bairro
└── docs/
    ├── relatorio.pdf       relatório técnico
    ├── uso_ia.md           como a IA apoiou o projeto e como os resultados foram verificados
    └── link_video.txt      link do vídeo
```

- **Relatório técnico:** [`docs/relatorio.pdf`](docs/relatorio.pdf), com as fontes e referências usadas.
- **Uso de inteligência artificial e testes:** [`docs/uso_ia.md`](docs/uso_ia.md).
