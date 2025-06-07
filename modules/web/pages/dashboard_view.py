import streamlit as st

from modules.web.graficos.secao_geografica import graficos_secao_geografica
from modules.web.graficos.secao_genero import graficos_secao_genero
from modules.web.graficos.secao_ingresso import graficos_secao_ingresso
from modules.web.graficos.secao_pandemia import graficos_secao_pandemia
from modules.web.graficos.secao_perfil import graficos_secao_perfil
from modules.web.service.export_pdf import exportar_pdf


def render_dashboard(df):
    st.title("📊 Dashboard Acadêmico")
    col1, col2 = st.columns([2, 1])

    with col1:
        if st.button("⬅️ Voltar para o início"):
            st.session_state.pagina = "inicio"
            st.session_state.carregou = False
            st.rerun()

    with col2:
        exportar = st.button("⬇️ Exportar relatório em PDF")

    st.markdown("---")

    tabs = st.tabs([
        " Formas de Ingresso",
        " Relações de Gênero",
        " Impactos Sociodemográficos",
        " Impactos da Pandemia",
        " Perfil do Aluno",
    ])

    # Aqui, adaptar as funções de seção para retornar as imagens dos gráficos
    graficos_imgs = []
    with tabs[0]:
        graficos_imgs.extend(graficos_secao_ingresso(df))
    with tabs[1]:
        graficos_imgs.extend(graficos_secao_genero(df))
    with tabs[2]:
        graficos_imgs.extend(graficos_secao_geografica(df))
    with tabs[3]:
        graficos_imgs.extend(graficos_secao_pandemia(df))
    with tabs[4]:
        graficos_imgs.extend(graficos_secao_perfil(df))

    if exportar:
        if not graficos_imgs:
            st.warning("Nenhum gráfico encontrado para exportação.")
        else:
            buffer = exportar_pdf(graficos_imgs)
            st.download_button(
                label="Clique para baixar o PDF",
                data=buffer.getvalue(),
                file_name="relatorio_academico.pdf",
                mime="application/pdf"
            )
