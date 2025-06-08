import streamlit as st

from modules.web.pages.inicio_view import render_inicio
from modules.web.pages.dashboard_view import render_dashboard
from modules.web.service.upload import load_and_process


class AppController:
    def __init__(self):
        # inicializa session_state
        if "pagina" not in st.session_state:
            st.session_state.pagina = "inicio"
        if "df" not in st.session_state:
            st.session_state.df = None
        if "carregou" not in st.session_state:
            st.session_state.carregou = False

    def run(self):
        if st.session_state.pagina == "inicio":
            self._handle_inicio()
        else:
            self._handle_dashboard()

    @staticmethod
    def _handle_inicio():
        render_inicio()
        if st.button("🚀 Carregar e Gerar Dashboard") and st.session_state.get("uploaded_file"):
            try:
                with st.spinner("⏳ Processando dados e gerando dashboard..."):
                    df = load_and_process(st.session_state.uploaded_file)
                st.session_state.df = df
                st.session_state.carregou = True
                st.success("✅ Dados carregados com sucesso! Redirecionando...")
                st.session_state.pagina = "dashboard"
                st.rerun()
            except Exception as e:
                st.error("❌ Erro ao processar os dados:")
                st.exception(e)

    @staticmethod
    def _handle_dashboard():
        df = st.session_state.df
        if df is not None:
            render_dashboard(df)
        else:
            st.error("❌ Dados não encontrados. Volte e carregue uma planilha.")
