from io import BytesIO
from fpdf import FPDF
import os

def exportar_pdf(graficos_imgs, titulo="Relatório Acadêmico"):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=16)
    pdf.cell(0, 10, titulo, ln=1, align='C')

    for nome, img in graficos_imgs:
        pdf.ln(5)
        pdf.set_font("Arial", size=12)
        pdf.cell(0, 10, nome, ln=1)
        # Salva imagem temporária (evita conflitos)
        temp_path = f"temp_{abs(hash(nome))}.png"
        img.save(temp_path)
        pdf.image(temp_path, w=180)
        os.remove(temp_path)
    buffer = BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    return buffer
