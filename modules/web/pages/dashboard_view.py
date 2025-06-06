import streamlit as st

from modules.web.graficos.secao_genero import graficos_secao_genero
from modules.web.graficos.secao_geografica import graficos_secao_geografica
from modules.web.graficos.secao_ingresso import graficos_secao_ingresso
from modules.web.graficos.secao_pandemia import graficos_secao_pandemia
from modules.web.graficos.secao_perfil import graficos_secao_perfil


def render_dashboard(df):
    st.title("📊 Dashboard Acadêmico")

    if st.button("⬅️ Voltar para o início"):
        st.session_state.pagina = "inicio"
        st.session_state.carregou = False
        st.rerun()

    st.markdown("---")

    tabs = st.tabs([
        " Formas de Ingresso",
        " Relações de Gênero",
        " Impactos Sociodemográficos",
        " Impactos da Pandemia",
        " Perfil do Aluno",
    ])

    with tabs[0]:
        graficos_secao_ingresso(df)

    # Seção 2: Relações de Gênero
    with tabs[1]:
        graficos_secao_genero(df)

    # Seção 3: Impactos Sociodemográficos
    with tabs[2]:
        graficos_secao_geografica(df)

    # Seção 4: Impactos da Pandemia
    with tabs[3]:
        graficos_secao_pandemia(df)

    with tabs[4]:
        graficos_secao_perfil(df)
