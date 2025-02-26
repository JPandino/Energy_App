# Web-App-MILPM-PSH (daily)
Aplicação Web com Flask para uso simplificado da ferramenta de otimização "MILPM-PSH"

O aplicativo em questão emprega um modelo de otimização da comercialização de energia no Ambiente de Contratação Livre (ACL) e no Mercado de Curto Prazo (MCP) para Usinas Hidrelétricas Reversíveis (UHR).
As UHR...
A modelagem leva em consideração a individualização das máquinas da UHR, discretização horária e um horizonte de planejamento diário. A função objetivo e as restrições são representadas através de relações matemáticas lineares, que caracterizam um problema de programação linear inteira mista, já que algumas das variáveis de decisão são inteiras, e outras contínuas. Dimensões do Problema

**Tabela** - Dimensão do Problema

Link do APP: https://optimizeruhr.pythonanywhere.com/

O aplicativo é uma ferramenta que oferece ao usuário uma análise da máxima receita gereda a partir da operação diária da UHR
de acordo com as características da usina, condições de mercado e vazão afluente nos reservatórios, que são fornecidas
ao aplicativo inicialmente. Além da receita máxima, informações de custo e sobre a operação da usina também são apresentadas.

**Imagem** - Interface da ferramneta
