# 📊 SIAA - Sistema Interativo de Análise Acadêmica

O **SIAA** é uma ferramenta interativa desenvolvida em Python com Streamlit que permite analisar e visualizar dados acadêmicos de forma dinâmica. A partir do upload de uma planilha `.xlsx`, a aplicação processa os dados e apresenta dashboards com gráficos e indicadores importantes sobre os estudantes do curso.

> 💡 O projeto também está disponível online em: [siaa-tcc.streamlit.app](https://siaa-tcc.streamlit.app/). Como se trata de um ambiente gratuito, ele permanece inativo até alguém acessá-lo. Caso queira utilizar a versão online, basta acessar o link, clicar para ativar a aplicação, aguardar alguns instantes e começar a explorar.

## 🚀 Como usar localmente

1. **Clone o repositório**

   ```bash
   git clone https://github.com/rafael-ventura/siaa.git
   cd siaa
   ```

2. **Instale as dependências**
   Recomendado: usar um ambiente virtual

   ```bash
   pip install -r requirements.txt
   ```

3. **Execute a aplicação**

   ```bash
   streamlit run app.py
   ```

4. **Navegue pela interface**

   * Acesse a aplicação no navegador (geralmente: [http://localhost:8501](http://localhost:8501)).
   * Faça o **download da planilha modelo** – ela já vem preenchida com dados de exemplo para testes.
   * Você pode apenas subir essa planilha para testar a ferramenta.
   * Depois, se quiser, substitua pelos seus próprios dados seguindo o mesmo formato.
   * Explore os gráficos interativos divididos em cinco seções:

     * Formas de Ingresso
     * Relações de Gênero
     * Impactos Sociodemográficos
     * Impactos da Pandemia
     * Perfil do Aluno

## 📁 Estrutura da Aplicação

* `app.py` – Arquivo principal que executa a interface.
* `modules/` – Código modular dividido por responsabilidade:

  * `web/` – Interface com páginas e controle de navegação.
  * `service/` – Processamento e validação da planilha.
  * `graficos/` – Funções para gerar os gráficos.
  * `explicacoes/` – Textos descritivos usados na interface.
* `assets/` – Pasta para imagens, ícones e arquivos estáticos.

## 💡 Observações

* A aplicação **não armazena os dados** enviados. Todo o processamento é feito localmente.
* Pequenas variações nos nomes das colunas da planilha são toleradas.
* O código é aberto e pode ser adaptado para outros cursos ou contextos educacionais.

## 📚 Licença

Este projeto está licenciado sob a [MIT License](LICENSE).
