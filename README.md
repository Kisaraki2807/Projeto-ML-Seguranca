# Segurança Escolar — Detecção Inteligente de Situações de Risco

Este repositório contém atualmente as entregas da Sprint 0 referentes ao projeto de detecção de risco em relatos escolares, utilizando Machine Learning integrado à inteligência geográfica, com foco no cidadão e na Segurança Pública.

---

## Artigo Científico
O documento contendo a Introdução, Problema, Objetivos e Justificativa, demais seções estão sendo elaboradas. 

Versão 1.0 = main/article/Segurança_Escolar_Planejamento_e_Gestao_de_Projetos

Desenvolvimento no Overleaf - https://www.overleaf.com/project/6a83cb778a4ac76df76ab246

---

## Bases de Dados e Justificativa

O projeto utiliza três bases de dados principais para viabilizar a análise espacial e o treinamento do modelo de Inteligência Artificial:

* **ToLD-Br (Textos Tóxicos):** Este dataset público será usado para o treinamento inicial da Inteligência Artificial. Como ele conta com milhares de textos já rotulados, é a ferramenta ideal para que o algoritmo aprenda a identificar linguagem agressiva, ofensas e toxicidade no português brasileiro.
* **Base Sintética (Denúncias Escolares):** Devido às regras de sigilo do ECA e da LGPD, não é possível utilizar denúncias reais envolvendo menores de idade. Por isso, utilizaremos uma base de dados simulada para adaptar o modelo, ensinando a IA a interpretar o vocabulário do ambiente escolar e a classificar a gravidade dos relatos em níveis de risco (Baixo, Médio ou Alto).
* **PeNSE 2024 (IBGE):** Os microdados da Pesquisa Nacional de Saúde do Escolar (PeNSE) serão utilizados para estruturar o cenário real de saúde e segurança das escolas nas capitais brasileiras. Por ser uma pesquisa oficial, ela fornece indicadores muito mais organizados e específicos do que os boletins de ocorrência policiais, garantindo informações seguras e sólidas para a construção do painel de risco.

---

## Kanban e Backlog
Ambos como views diferentes no projeto associado.

---

## Business Model Canvas

| Componente | Descrição |
| :--- | :--- |
| Problema | A triagem manual de denúncias escolares é lenta, e a ausência de espacialização dos dados dificulta a visão macro e a alocação de recursos preventivos pela Segurança Pública. |
| Solução | Dashboard visual desenvolvido em Streamlit com motor de Machine Learning (NLP) para classificação de gravidade em relatos e plotagem de mapas de risco cruzados com dados do Censo Escolar de SC. |
| Proposta de Valor | Plataforma inteligente que une análise de linguagem natural e geoprocessamento para transformar denúncias em um índice visual de atenção, garantindo proteção ágil e preventiva. |
| Vantagem Injusta | Arquitetura metodológica que cruza dados oficiais de geolocalização (INEP) com um modelo NLP adaptado para a identificação de gravidade no contexto estudantil brasileiro. |
| Segmentos de Clientes | Órgãos de Segurança Pública, gestores escolares e cidadãos (alunos, pais e comunidade local). |
| Canais | Portais de transparência do governo, secretarias de educação e campanhas de integração nas escolas. |
| Métricas-Chave | Acurácia do algoritmo na classificação de gravidade dos relatos e tempo de resposta do sistema para processamento do texto e atualização do mapa de risco. |
