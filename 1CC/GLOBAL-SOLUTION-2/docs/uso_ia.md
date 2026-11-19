# Uso de Inteligência Artificial

Este arquivo registra como usei inteligência artificial no **Neighborhood Action Dashboard** e como conferi os resultados, como pede o enunciado da Global Solution 2026.2.

## 1. Ferramenta e forma de uso

Usei o **Claude**, da Anthropic, em um projeto separado para a faculdade, configurado para funcionar como orientador: explicar os conceitos, me ajudar a organizar o trabalho e apontar erros, sem fazer o projeto no meu lugar. As ideias principais, as regras do sistema e as decisões foram minhas. Todo o código do `src/sistema.py` foi digitado por mim, e cada parte foi testada antes de seguir para a próxima.

Durante o projeto, mantive um registro das decisões e de onde a IA mapeou e organizou a ideias e assim facilitando as tomadas de decisões futuras e também a relembrar decisões tomadas anteriores oque ajudou no relatório final. Este arquivo foi escrito a partir desse registro, com o apoio do Claude na redação, e revisado por mim.

## 2. O que foi meu e onde o Claude apoiou

| Etapa                   | O que foi meu                                                                                                                                                                                                                                                                                                                            | Como o Claude apoiou                                                                                                                                                                          |
| ----------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Entendimento do desafio | Li o enunciado e as diretrizes da ONU-Habitat e defini o problema: o morador perde a referência do próprio pedido e não sabe se os vizinhos têm o mesmo problema                                                                                                                                                                         | Conferiu se as ideias atendiam cada requisito do enunciado e ajudou a resumir os pontos das diretrizes                                                                                        |
| Cidade e dados          | Criei Borda do Campo, inspirada em Santo André, porque moro no Grande ABC                                                                                                                                                                                                                                                                | Gerou os nomes fictícios das ruas, os CEPs com prefixo 00 e as 13 ocorrências de exemplo (o enunciado permite usar IA para gerar dados fictícios)                                             |
| Pesquisa                | Decidi usar prazos reais e um dado real para mostrar que o problema existe                                                                                                                                                                                                                                                               | Pesquisou as fontes (cartas de serviço de Porto Alegre e Caraguatatuba, Diário do Grande ABC, origem do nome Borda do Campo) e formatou as referências em ABNT                                |
| Regras do sistema       | Presumir o conserto quando o prazo da prefeitura vence; o morador contesta se o problema continuar; novo prazo de 60 dias; motivo da contestação; situação calculada pelas datas; sistema usando a data do dia; nunca reescrever os arquivos; validação na entrada; escolha por número; pausa entre as telas; data no formato brasileiro | Ajudou a organizar essas regras em estruturas e funções: o modelo de "extrato" para os arquivos, a pilha, a fila, a matriz e a hierarquia, e a divisão do programa em funções e subalgoritmos |
| Código                  | Organizei o programa em funções a partir do mapa que montamos; digitei cada parte no meu arquivo, rodei, conferi na tela, corrigi os erros e decidi o que entrava                                                                                                                                                                        | Me ajudou a organizar e mapear o que precisava entrar em cada função e em que ordem, para eu não me perder no projeto, e explicou cada conceito novo com exemplos.                            |
| Auditoria               | Decidi corrigir os pontos fracos encontrados                                                                                                                                                                                                                                                                                             | Comparou o sistema com o enunciado e apontou dois requisitos fracos: o histórico com pelo menos 8 atualizações de situação e o tempo simulado de acompanhamento                               |
| Mensagens de orientação | Percebi que, para quem criou, o uso parecia óbvio, mas um morador não entenderia os prazos. Decidi como seria: explicação no menu, situações com acento na tela e aviso claro quando o CEP não existe                                                                                                                                    | Mapeou, tela por tela, onde faltava orientação e sugeriu os textos das mensagens                                                                                                              |
| Relatório e README      | Defini o conteúdo, a ordem e o que entrava; revisei e adaptei cada parte com a minha voz                                                                                                                                                                                                                                                 | Montou o esqueleto, revisou a formatação do PDF e fez o README                                                                                                                                |

## 3. Os testes automáticos

**Como foram feitos.** São 153 testes, escritos pelo Claude a meu pedido, porque testar à mão todas as combinações seria inviável no prazo da entrega. Eles rodam numa cópia do código e dos dados, nunca nos arquivos originais. O arquivo dos testes não faz parte do repositório, porque usa recursos de Python que não são do conteúdo das Fases 1 a 3; ele serviu só para conferir o sistema.

**Por que os testes fixam 19/11/2026.** O sistema usa a data do dia em que é aberto, então os resultados mudam a cada dia. Para que cada teste tenha uma resposta esperada fixa, a data dos testes é fixada em 19/11/2026 (a linha comentada logo abaixo do `HOJE`, no topo do `sistema.py`). A cópia de teste também tem uma ocorrência a mais (I013), usada para testar o cadastro e a fila. Por isso alguns números dos testes, como 13 ocorrências válidas e 6 abertas, são diferentes dos números do relatório.

**Resultado: 151 de 153 testes aprovados.**

| Grupo | Aprovados | O que confere |
|---|---|---|
| 1. Carga dos arquivos | 7 de 7 | 20 ruas na base; a L013 barrada com o motivo na tela; datas convertidas; contestações carregadas; o dicionário aponta para as mesmas fichas da lista |
| 2. Validação na entrada | 6 de 6 | Ficha válida passa; descrição vazia, CEP vazio, categoria inexistente e CEP fora da base são barrados; com dois erros, aparece só o primeiro motivo |
| 3. Situação calculada | 15 de 15 | Situação, vencimento e fim da contestação de todas as ocorrências iguais a uma tabela conferida à mão; a I008 contestada aparece aberta e atrasada |
| 4. Datas de fronteira | 15 de 15 | Um dia antes de vencer (aberta); o dia do vencimento (em análise); o último dia para contestar (em análise); o dia seguinte (concluída); prazo de 15 dias da iluminação; virada do ano; ano bissexto; duas contestações (vale a mais recente) |
| 5. Busca (opção 2) | 7 de 7 | Código certo, em minúsculo e com espaços; código inexistente; a L013 barrada não é encontrada; Enter vazio não quebra |
| 6. Filtro (opção 3) | 12 de 12 | Contagem por categoria e por situação; número fora da lista, letra e Enter vazio dão "Opção inválida" |
| 7. Cadastro (opção 4) | 15 de 15 | Código gerado em sequência; a ocorrência entra na lista, no dicionário e no arquivo com 6 campos; `;` vira `,`; seis entradas inválidas são recusadas sem gravar nada (inclusive CEP real de Santo André e CEP sem hífen); ao reabrir, tudo é carregado do arquivo |
| 8. Menu | 4 de 4 | Listagem completa; número fora do menu, letra e Enter vazio dão "Opção inválida"; a pausa só sai com 0 |
| 9. Arquivos com problema | 3 de 5 | Linha em branco no fim dos arquivos e linha com campo faltando são ignoradas, e o sistema segue. **Não passam:** data inexistente escrita no arquivo e arquivo de contestações apagado (ver abaixo) |
| 10. Contestação (opção 5) | 17 de 17 | Cada situação recebe a mensagem certa; motivo inválido não grava nada; a contestação reabre a ocorrência com 60 dias e é gravada; ao reabrir o sistema, continua atrasada; quando o novo prazo vence, volta a ficar em análise |
| 11. Últimas atualizações (opção 6) | 13 de 13 | Registros, contestações e mudanças de situação feitas pelo calendário, em ordem de data; pelo menos 8 atualizações de situação (eram 12); o mais recente aparece primeiro |
| 12. Fila (opção 7) | 10 de 10 | Só as abertas, na ordem de registro; a atrasada marcada; a fila não altera a lista principal; fila vazia não quebra |
| 13. Indicadores (opção 8) | 19 de 19 | Matriz 4 × 3 e sua soma; porcentagens; atrasadas; tempo médio conferido com a conta feita à mão; divisão por zero não quebra; com tudo concluído, mostra 0 de 0 e 100% |
| 14. Bairro e rua (opção 9) | 7 de 7 | Cada rua dentro do seu bairro; ocorrência nova aparece na hora; tudo concluído não quebra |
| 15. Percurso completo | 1 de 1 | As nove opções em sequência, sem nenhum erro |

**Os dois testes que não passam** são limitações reconhecidas na seção 8 do relatório: se alguém escrever à mão no arquivo uma data que não existe, ou apagar o arquivo de contestações, o programa não consegue fazer a leitura e para. Pelo próprio sistema, isso não acontece, porque o cadastro e a contestação sempre gravam no formato certo. Tratar esses casos exigiria recursos que não fazem parte do conteúdo das Fases 1 a 3.

**Ajustes feitos nos testes, e não no código**, registrados por transparência:
- Um teste do filtro esperava 3 ocorrências de iluminação; com a I013 da cópia de teste, o certo era 4.
- Um teste usava a opção 9 como exemplo de opção inexistente; quando a opção 9 foi criada, passou a usar 99.
- Quando o sistema passou a usar a data do dia, os testes passaram a fixar 19/11/2026.
- Quando o histórico passou a mostrar as mudanças de situação, o total esperado de eventos mudou.
- Quando as situações passaram a aparecer com acento na tela e a mensagem de CEP inexistente mudou, 11 textos esperados foram atualizados. Nenhum teste foi removido.

## 4. Onde a IA errou e como percebi

Nada foi aceito sem conferência, e isso fez diferença:
- Ao indicar onde inserir um trecho, o Claude chegou a usar números de linha errados. Percebi porque o código não ficava no lugar certo, e a partir daí ele passou a ler o meu arquivo antes de indicar qualquer linha.
- Na revisão do relatório, ele avaliou a formatação a partir de uma conversão própria do arquivo, que mostrava problemas que não existiam no meu documento. Percebi a diferença e passei a mandar o PDF exportado por mim.
- Alguns testes esperavam valores errados, como o do filtro citado acima. A diferença apareceu quando conferi o resultado com os dados.

#### Registro

Atualizado em 17/11/2026, sobre a versão final do código.
