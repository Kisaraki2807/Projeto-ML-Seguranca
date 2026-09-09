# Segurança Escolar — Detecção Inteligente de Situações de Risco

Este repositório contém as entregas das **Sprints 0, 1 e 2** referentes ao projeto de detecção de risco em relatos escolares, utilizando Machine Learning integrado à inteligência geográfica, com foco no cidadão e na Segurança Pública.

### Links Importantes
* **Artigo Científico:** [Desenvolvimento no Overleaf](https://www.overleaf.com/project/6a83cb778a4ac76df76ab246)
* **Google Colab (Notebooks de ML):** [Acessar Colab](https://colab.research.google.com/drive/1tIYo9nI6l-Jfjgs7rbxkP9rv4QJZja5S#scrollTo=2r_6ApldbLwa)

---

### Bases de Dados e Justificativa

O projeto utiliza três bases de dados principais (disponíveis na pasta `/data/`) para viabilizar a análise espacial e o treinamento do modelo de Inteligência Artificial:

* **ToLD-Br (Textos Tóxicos):** Dataset público usado para o treinamento inicial da Inteligência Artificial. Como conta com milhares de textos já rotulados, é ideal para o algoritmo aprender a identificar linguagem agressiva, ofensas e toxicidade no português brasileiro.
* **Base Sintética (Denúncias Escolares):** Devido às regras de sigilo do ECA e da LGPD, não é possível utilizar denúncias reais envolvendo menores de idade. Utiliza-se uma base de dados simulada para adaptar o modelo, ensinando a IA a interpretar o vocabulário escolar e a classificar a gravidade dos relatos (Baixo, Médio ou Alto).
* **PeNSE 2024 (IBGE):** Microdados da Pesquisa Nacional de Saúde do Escolar. Serão utilizados para estruturar o cenário real de saúde e segurança das escolas nas capitais brasileiras. Fornece indicadores organizados e seguros para a construção do painel de risco.

---

### Gestão e Planejamento

**Kanban e Backlog:** Ambos controlados como views diferentes no projeto associado a este repositório. As estimativas ágeis das tarefas foram registradas nos cartões de cada Sprint.

**Business Model Canvas:**
* **Problema:** A triagem manual de denúncias escolares é lenta, e a ausência de espacialização dos dados dificulta a visão macro e a alocação de recursos preventivos pela Segurança Pública.
* **Solução:** Dashboard visual desenvolvido em Streamlit com motor de Machine Learning (NLP) para classificação de gravidade em relatos e plotagem de mapas de risco cruzados com dados do Censo Escolar de SC.
* **Proposta de Valor:** Plataforma inteligente que une análise de linguagem natural e geoprocessamento para transformar denúncias em um índice visual de atenção, garantindo proteção ágil e preventiva.
* **Vantagem Injusta:** Arquitetura metodológica que cruza dados oficiais de geolocalização (INEP) com um modelo NLP adaptado para a identificação de gravidade no contexto estudantil brasileiro.
* **Segmentos de Clientes:** Órgãos de Segurança Pública, gestores escolares e cidadãos (alunos, pais e comunidade local).
* **Canais:** Portais de transparência do governo, secretarias de educação e campanhas de integração nas escolas.
* **Métricas-Chave:** Acurácia do algoritmo na classificação de gravidade e tempo de resposta do sistema para processamento do texto e atualização do mapa de risco.

---

### Requisitos do Sistema

**Histórias de Usuário:**
* **HU01 - Relato Cidadão:** 
  * *Quem?* Cidadão (aluno, pai ou membro da comunidade local). 
  * *O quê?* Precisa inserir um relato textual sobre um incidente escolar e ver a confirmação visual intuitiva. 
  * *Para quê?* Garantir o amparo das autoridades caso o nível de ameaça seja alto.
* **HU02 - Visão de Segurança Pública:** 
  * *Quem?* Gestor de Segurança Pública ou educacional. 
  * *O quê?* Precisa visualizar a variação dos níveis de risco num painel com filtros por área, integrando dados estruturais. 
  * *Para quê?* Tomar decisão imediata de alocar recursos preventivos, resolvendo o atraso na análise manual.

**Casos de Uso Principais (Sprint 1):**
* **CS01 - Envio de Denúncia:** O cidadão preenche e envia o relato. O sistema salva a informação.
* **CS02 - Classificação de Risco (NLP):** O sistema envia o texto para o modelo de ML, faz a extração de atributos (TF-IDF) e classifica o relato automaticamente.
* **CS03 - Visualização Geográfica:** O sistema cruza os alertas gerados pela IA com as coordenadas das escolas (IBGE) e atualiza o mapa no dashboard do Gestor.

---

### Entregas de Machine Learning (Sprint 2 - MVP Analítico)

Nesta etapa, foi realizada a engenharia de atributos (TF-IDF) e o treinamento dos modelos de classificação (Regressão Logística e Random Forest) utilizando o Google Colab. 

Modelos constam em /models | Notebook consta em /notebook | Bancos de Dados estão em /data

Os modelos de melhor desempenho (*Baseline*) foram exportados e versionados na raiz deste repositório para futura integração com o Streamlit:
* `modelo_risco_escolar.joblib` e `vetorizador_risco.joblib`: Motor treinado na Base Sintética para classificar a gravidade da denúncia.
* `modelo_toxicidade_told.joblib` e `vetorizador_told.joblib`: Motor treinado na ToLD-Br para detecção de toxicidade geral.

**Os modelos da ToLD-BR são muito pesados para o github, estão no drive compartilhado: https://drive.google.com/drive/u/0/folders/1t1uM9PtaDhI-_g6Imu_geYyLnIKI1Aeb**




