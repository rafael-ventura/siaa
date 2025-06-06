import os
import streamlit as st
from modules.limpeza.validadorPlanilha import ValidadorPlanilha
from modules.web.explicacoes.base_explicacoes import get_explicacao_coluna

def render_inicio():
    st.title("📊 Ferramenta de Análise Acadêmica - BSI/UNIRIO")

    st.markdown("""
    ### 👋 Bem-vindo!
    Esta ferramenta foi criada para coordenações de cursos e docentes do curso de **Sistemas de Informação da UNIRIO**, permitindo a geração de dashboards dinâmicos a partir de uma planilha padronizada.
    Outros cursos da universidade que compartilham a mesma base de dados também podem utilizar a ferramenta.

    ---
    ### 📝 Como usar:
    1. Faça o download da planilha de exemplo.
    2. Preencha os dados conforme a estrutura abaixo.
    3. Faça o upload da planilha preenchida.
    4. Clique em "Carregar e Gerar Dashboard".
    5. Explore os gráficos e informações geradas.

    ---
    ### 📂 Estrutura esperada da planilha:
    """)

    for col in ValidadorPlanilha.COLUNAS_ESPERADAS:
        with st.expander(f"📄 {col}"):
            explicacao = get_explicacao_coluna(col)
            if explicacao:
                st.markdown(explicacao, unsafe_allow_html=True)

    st.markdown("---")
    exemplo = os.path.join(
        os.path.dirname(__file__),
        "..", "..", "dados", "exemplo_dados.xlsx"
    )
    exemplo = os.path.abspath(exemplo)
    with open(exemplo, "rb") as f:
        st.download_button(
            label="📅 Baixar planilha de exemplo",
            data=f.read(),
            file_name="exemplo_dados.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    # uploader: guarda em session_state.uploaded_file
    st.file_uploader(
        "Envie um arquivo .xlsx conforme o modelo acima.",
        type=["xlsx"],
        key="uploaded_file"
    )
