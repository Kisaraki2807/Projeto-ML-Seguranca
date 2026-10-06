import streamlit as st
import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from scipy.sparse import hstack
import plotly.graph_objects as go

# ============================================================
# CONFIGURAÇÃO
# ============================================================

st.set_page_config(
    page_title="Mapa de Risco de Bullying",
    page_icon="🛡️",
    layout="wide",
)

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"

RISK_FILE = DATA_DIR / "risco_capitais.csv"
TOX_MODEL_FILE = MODELS_DIR / "modelo_toxicidade_told.joblib"
TOX_VECTORIZER_FILE = MODELS_DIR / "vetorizador_told.joblib"
RISK_MODEL_FILE = MODELS_DIR / "modelo_risco_escolar.joblib"

# ============================================================
# CAPITAIS
# ============================================================

CAPITAIS = {
    "AC": ("Rio Branco", -9.9754, -67.8249),
    "AL": ("Maceió", -9.6658, -35.7353),
    "AP": ("Macapá", 0.0349, -51.0694),
    "AM": ("Manaus", -3.1190, -60.0217),
    "BA": ("Salvador", -12.9777, -38.5016),
    "CE": ("Fortaleza", -3.7319, -38.5267),
    "DF": ("Brasília", -15.7939, -47.8828),
    "ES": ("Vitória", -20.3155, -40.3128),
    "GO": ("Goiânia", -16.6869, -49.2648),
    "MA": ("São Luís", -2.5307, -44.3068),
    "MT": ("Cuiabá", -15.6014, -56.0979),
    "MS": ("Campo Grande", -20.4697, -54.6201),
    "MG": ("Belo Horizonte", -19.9167, -43.9345),
    "PA": ("Belém", -1.4558, -48.4902),
    "PB": ("João Pessoa", -7.1195, -34.8450),
    "PR": ("Curitiba", -25.4284, -49.2733),
    "PE": ("Recife", -8.0476, -34.8770),
    "PI": ("Teresina", -5.0892, -42.8016),
    "RJ": ("Rio de Janeiro", -22.9068, -43.1729),
    "RN": ("Natal", -5.7945, -35.2110),
    "RS": ("Porto Alegre", -30.0346, -51.2177),
    "RO": ("Porto Velho", -8.7612, -63.9004),
    "RR": ("Boa Vista", 2.8235, -60.6758),
    "SC": ("Florianópolis", -27.5954, -48.5480),
    "SP": ("São Paulo", -23.5505, -46.6333),
    "SE": ("Aracaju", -10.9472, -37.0731),
    "TO": ("Palmas", -10.1840, -48.3336),
}

UF_POR_CAPITAL = {v[0]: uf for uf, v in CAPITAIS.items()}


# ============================================================
# DADOS
# ============================================================

@st.cache_data
def carregar_riscos():
    df = pd.read_csv(RISK_FILE)
    df["risco_base"] = pd.to_numeric(df["risco_base"], errors="coerce").fillna(0)
    df["risco_atual"] = df["risco_base"]
    df["denuncias_sessao"] = 0
    return df


if "riscos" not in st.session_state:
    st.session_state.riscos = carregar_riscos().copy()


# ============================================================
# MODELOS
# ============================================================

@st.cache_resource
def carregar_modelos():
    arquivos = [
        TOX_MODEL_FILE,
        TOX_VECTORIZER_FILE,
        RISK_MODEL_FILE,
    ]

    faltantes = [str(p.relative_to(BASE_DIR)) for p in arquivos if not p.exists()]

    if faltantes:
        return None, faltantes

    modelo_toxicidade = joblib.load(TOX_MODEL_FILE)
    vetorizador = joblib.load(TOX_VECTORIZER_FILE)
    modelo_risco = joblib.load(RISK_MODEL_FILE)

    return {
        "toxicidade": modelo_toxicidade,
        "vetorizador": vetorizador,
        "risco": modelo_risco,
    }, []


modelos, arquivos_faltantes = carregar_modelos()


def classificar_denuncia(texto):
    """
    Executa o pipeline:
        texto
          -> TF-IDF aprendido no ToLD-BR
          -> probabilidade de toxicidade
          -> TF-IDF + probabilidade
          -> classificação de gravidade
    """
    if modelos is None:
        raise FileNotFoundError(
            "Modelos não encontrados. Coloque os três arquivos .joblib "
            "na pasta models/."
        )

    vetor = modelos["vetorizador"].transform([texto])

    prob_toxicidade = modelos["toxicidade"].predict_proba(vetor)[0, 1]

    features = hstack([
        vetor,
        np.array([[prob_toxicidade]])
    ])

    gravidade = modelos["risco"].predict(features)[0]
    probabilidades = modelos["risco"].predict_proba(features)[0]

    probs = dict(
        zip(modelos["risco"].classes_, probabilidades)
    )

    return prob_toxicidade, gravidade, probs


# ============================================================
# ATUALIZAÇÃO DO ÍNDICE
# ============================================================

def converter_gravidade_para_valor(gravidade, probabilidades):
    """
    Converte a saída categórica em uma intensidade entre 0 e 1.

    Se as classes forem Baixa/Média/Alta, utiliza:
        Baixa = 0.25
        Média = 0.60
        Alta  = 0.90

    Caso contrário, utiliza a classe prevista como fallback.
    """
    pesos = {
        "baixa": 0.25,
        "baixo": 0.25,
        "média": 0.60,
        "media": 0.60,
        "médio": 0.60,
        "medio": 0.60,
        "alta": 0.90,
        "alto": 0.90,
    }

    chave = str(gravidade).strip().lower()

    if chave in pesos:
        return pesos[chave]

    # Fallback para classes não padronizadas.
    if probabilidades:
        classes = list(probabilidades.keys())
        valores = np.linspace(0.25, 0.90, len(classes))
        return float(
            valores[np.argmax(list(probabilidades.values()))]
        )

    return 0.60


def atualizar_risco(uf, gravidade, probabilidades):
    """
    Atualiza o indicador apenas na sessão atual.

    A atualização é uma demonstração do mecanismo proposto:
        R_novo = (1-alpha)*R_atual + alpha*D

    Não representa uma estimativa epidemiológica real.
    """
    alpha = 0.05
    valor_gravidade = converter_gravidade_para_valor(
        gravidade,
        probabilidades
    )

    idx = st.session_state.riscos.index[
        st.session_state.riscos["uf"] == uf
    ]

    if len(idx) == 0:
        return None

    i = idx[0]

    risco_atual = float(
        st.session_state.riscos.loc[i, "risco_atual"]
    )

    novo_risco = (
        (1 - alpha) * risco_atual
        + alpha * valor_gravidade
    )

    novo_risco = float(np.clip(novo_risco, 0, 1))

    st.session_state.riscos.loc[i, "risco_atual"] = novo_risco
    st.session_state.riscos.loc[i, "denuncias_sessao"] += 1

    return novo_risco


# ============================================================
# MAPA
# ============================================================

def criar_mapa():
    df = st.session_state.riscos.copy()

    df["capital"] = df["uf"].map(
        lambda uf: CAPITAIS[uf][0]
    )
    df["lat"] = df["uf"].map(
        lambda uf: CAPITAIS[uf][1]
    )
    df["lon"] = df["uf"].map(
        lambda uf: CAPITAIS[uf][2]
    )

    fig = go.Figure()

    fig.add_trace(
        go.Scattergeo(
            lat=df["lat"],
            lon=df["lon"],
            text=df["capital"],
            customdata=np.stack(
                [
                    df["uf"],
                    df["risco_atual"],
                    df["denuncias_sessao"],
                ],
                axis=-1,
            ),
            mode="markers",
            marker=dict(
                size=12,
                color=df["risco_atual"],
                colorscale="RdYlGn_r",
                cmin=0,
                cmax=1,
                line=dict(width=1, color="white"),
                colorbar=dict(
                    title="Índice de risco",
                    tickformat=".0%",
                ),
            ),
            hovertemplate=(
                "<b>%{text}</b><br>"
                "UF: %{customdata[0]}<br>"
                "Índice: %{customdata[1]:.1%}<br>"
                "Denúncias nesta sessão: %{customdata[2]}"
                "<extra></extra>"
            ),
        )
    )

    fig.update_geos(
        scope="south america",
        showland=True,
        showcountries=True,
        countrycolor="white",
        showcoastlines=True,
        coastlinecolor="gray",
        fitbounds="locations",
    )

    fig.update_layout(
        height=600,
        margin=dict(l=0, r=0, t=20, b=0),
        showlegend=False,
    )

    return fig


# ============================================================
# INTERFACE
# ============================================================

st.title("🛡️ Mapa de Risco de Bullying")
st.caption(
    "Protótipo experimental para visualização de indicadores "
    "e classificação de denúncias escolares."
)

st.info(
    "As denúncias deste MVP são processadas anonimamente. "
    "Não informe nome, CPF, telefone ou outros dados pessoais."
)

tab_mapa, tab_denuncia, tab_sobre = st.tabs(
    ["🗺️ Mapa de risco", "📢 Realizar denúncia", "ℹ️ Sobre o projeto"]
)


# ============================================================
# ABA MAPA
# ============================================================

with tab_mapa:

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Capitais monitoradas",
            len(st.session_state.riscos)
        )

    with col2:
        st.metric(
            "Denúncias nesta sessão",
            int(
                st.session_state.riscos["denuncias_sessao"].sum()
            )
        )

    with col3:
        st.metric(
            "Maior índice atual",
            f"{st.session_state.riscos['risco_atual'].max():.1%}"
        )

    st.plotly_chart(
        criar_mapa(),
        use_container_width=True
    )

    st.subheader("Indicadores por capital")

    tabela = st.session_state.riscos.copy()
    tabela["capital"] = tabela["uf"].map(
        lambda uf: CAPITAIS[uf][0]
    )
    tabela["Índice de risco"] = (
        tabela["risco_atual"] * 100
    ).round(2).astype(str) + "%"

    tabela["Risco inicial"] = (
        tabela["risco_base"] * 100
    ).round(2).astype(str) + "%"

    tabela = tabela[
        [
            "capital",
            "uf",
            "Risco inicial",
            "Índice de risco",
            "denuncias_sessao",
        ]
    ].rename(
        columns={
            "capital": "Capital",
            "uf": "UF",
            "denuncias_sessao": "Denúncias na sessão",
        }
    )

    st.dataframe(
        tabela,
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# ABA DENÚNCIA
# ============================================================

with tab_denuncia:

    st.header("Realizar uma denúncia")

    st.write(
        "Descreva uma situação de possível bullying ocorrida "
        "em ambiente escolar. O sistema utiliza o texto para "
        "demonstrar o funcionamento do pipeline de classificação."
    )

    with st.form("form_denuncia", clear_on_submit=False):

        col1, col2 = st.columns(2)

        with col1:
            escola = st.text_input(
                "Nome da escola",
                placeholder="Ex.: Escola Estadual João da Silva",
            )

            cidade = st.text_input(
                "Cidade",
                placeholder="Ex.: Florianópolis",
            )

        with col2:
            estados = {
                uf: nome
                for uf, (nome, _, _) in CAPITAIS.items()
            }

            estado = st.selectbox(
                "Estado",
                options=list(estados.keys()),
                format_func=lambda uf: (
                    f"{uf} — {estados[uf]}"
                ),
            )

            st.caption(
                "O sistema associa a denúncia à capital do estado "
                "para fins de demonstração do indicador."
            )

        texto = st.text_area(
            "Descreva a situação",
            placeholder=(
                "Descreva o que aconteceu, sem informar "
                "nome ou outros dados pessoais..."
            ),
            height=180,
        )

        confirmar = st.checkbox(
            "Não estou informando nomes, contatos ou outros "
            "dados pessoais na descrição."
        )

        enviar = st.form_submit_button(
            "Enviar denúncia",
            type="primary",
        )

    if enviar:

        erros = []

        if not escola.strip():
            erros.append("Informe o nome da escola.")

        if not cidade.strip():
            erros.append("Informe a cidade.")

        if not texto.strip():
            erros.append("Descreva a situação.")

        if not confirmar:
            erros.append(
                "Confirme que a descrição não contém dados pessoais."
            )

        if erros:
            for erro in erros:
                st.error(erro)

        elif modelos is None:
            st.error(
                "Os modelos treinados não foram encontrados."
            )

            st.warning(
                "Para executar a classificação, coloque em "
                "`models/` os arquivos: "
                "`modelo_toxicidade_told.joblib`, "
                "`vetorizador_told.joblib` e "
                "`modelo_risco_escolar.joblib`."
            )

        else:
            with st.spinner("Analisando denúncia..."):

                prob_tox, gravidade, probs = classificar_denuncia(
                    texto.strip()
                )

                novo_risco = atualizar_risco(
                    estado,
                    gravidade,
                    probs,
                )

            st.success(
                "Denúncia processada com sucesso."
            )

            st.subheader("Resultado da análise")

            c1, c2 = st.columns(2)

            with c1:
                st.metric(
                    "Probabilidade de toxicidade",
                    f"{prob_tox:.1%}"
                )

            with c2:
                st.metric(
                    "Gravidade estimada",
                    str(gravidade).upper()
                )

            st.write("Probabilidades por classe:")

            for classe, prob in probs.items():
                st.progress(
                    float(prob),
                    text=f"{classe}: {prob:.1%}"
                )

            if novo_risco is not None:

                capital = CAPITAIS[estado][0]

                st.info(
                    f"Indicador experimental de **{capital}** "
                    f"atualizado para **{novo_risco:.1%}** "
                    f"nesta sessão."
                )

            st.caption(
                "Importante: este resultado é experimental e não "
                "constitui confirmação de ocorrência de bullying. "
                "O MVP utiliza uma base sintética de denúncias para "
                "demonstrar o funcionamento do pipeline."
            )



    if modelos is not None:
        st.success("Modelos treinados carregados com sucesso.")
    else:
        st.warning(
            "Modo de demonstração: os arquivos dos modelos ainda "
            "não estão disponíveis na pasta `models/`."
        )
