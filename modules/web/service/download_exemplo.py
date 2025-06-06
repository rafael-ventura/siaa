import os, streamlit as st

def render_download_exemplo():
    caminho = os.path.abspath(
        os.path.join(os.path.dirname(__file__),
                     "..", "..", "dados", "exemplo_dados.xlsx")
    )
    with open(caminho, "rb") as f:
        st.download_button(
            label="📅 Baixar planilha de exemplo",
            data=f.read(),
            file_name="exemplo_dados.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
