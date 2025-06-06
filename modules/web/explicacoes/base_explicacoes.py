def explicacao_forma_ingresso():
    return """
### Valores aceitos para a coluna FORMA_INGRESSO

A coluna **FORMA_INGRESSO** deve conter exatamente **um dos valores listados abaixo**, sem necessidade de acentos ou formatações específicas.

Os valores informados serão automaticamente agrupados nas seguintes categorias:

#### ✅ **Ampla Concorrência**
- `SISU Ampla Concorrência`
- `VE - Vestibular`
- `EN - ENEM`  
> Alunos com ingresso anterior a 2014 também serão classificados nessa categoria, como **Ampla Concorrência - Pré-Cotas**.

#### ✅ **Escola pública, sem renda**
- `SISU Escola Pública - Indep. de Renda`

#### ✅ **Escola pública, com renda**
- `SISU Escola Pública até 1,5 S.M.`

#### ✅ **Escola pública, sem renda + étnico-racial**
- `SISU Indep. de Renda: Preto, Pardo, Indígena`

#### ✅ **Escola pública, com renda + étnico-racial**
- `SISU até 1,5 S.M. : Preto, Pardo, Indígena`

#### ⚠️ **Outros**
- Qualquer valor diferente dos listados acima pode vir a ser agrupado como **Outros**
"""


def explicacao_sexo():
    return """
### Valores aceitos para a coluna SEXO

Indica o sexo do aluno no momento do ingresso. Apenas dois valores são aceitos:

- `M`  
          
- `F` 

> Outros valores serão considerados inválidos.
"""


def explicacao_forma_evasao():
    return """
### Valores aceitos para a coluna FORMA_EVASAO

A coluna **FORMA_EVASAO** deve conter exatamente **um dos valores listados abaixo**. O sistema irá agrupar automaticamente esses valores nas seguintes categorias:

#### ✅ **Concluiu**
- `CON - Curso concluído`

#### ✅ **Evasão**
- `ABA - Abandono do curso`
- `CAN - Cancelamento Geral do curso`
- `Desistência SISU`
- `DES - Desligamento`
- `JUB - Jubilamento`
- `TIC - Transferência interna`

#### ✅ **Cursando**
- `Sem evasão`

#### ✅ **Outros**
- `Não identificada`
- `FAL - Falecimento`

> ⚠️ Caso o valor informado não seja um dos listados acima, ele será automaticamente classificado como **Outros**.
"""


def explicacao_cra():
    return """
### Valores aceitos para o CRA:

A escala vai de **0 a 10**, podendo ter **casas decimais**.

#### Formatos aceitos:
- Pode estar separado por **vírgula** (preferencial) ou **ponto**
  - Exemplos válidos: `6,4654`, `7.8`, `0`, `10`
- Pode ser um número inteiro ou decimal
- Se vier em branco ou vazio, será automaticamente considerado como **0.0**
"""


def explicacao_dt_nascimento():
    return """
### Valores aceitos para Data de Nascimento

A coluna **DT_NASCIMENTO** deve conter datas válidas e completas no formato **dia/mês/ano**, com ou sem zero à esquerda.

#### Formatos aceitos:
- `17/09/1990`
- `5/1/2003`
- `03/10/1996`

#### Regras de tratamento:
- O sistema converte automaticamente os valores para o padrão de data reconhecido.
- Se a data estiver incompleta ou inválida, ela será marcada como **nula** e desconsiderada nas análises que dependem da idade ou data de nascimento.

"""


def explicacao_periodo_ingresso():
    return """
### Valores aceitos para Período de Ingresso

O período de ingresso pode ser informado de **duas formas**:

#### 1. Usando a coluna `PERIODO_INGRESSO`  
- Deve seguir o formato: **`ano/semestre`**
  - Exemplos válidos: `2014/1º semestre`, `2020/2`, `2018/1`
- O sistema extrai automaticamente:
  - `ANO_INGRESSO` (ex: 2014)
  - `SEMESTRE_INGRESSO` (1 ou 2)

#### 2. Usando as colunas `ANO_INGRESSO` e `SEMESTRE_INGRESSO` separadamente  
- Exemplo:
  - `ANO_INGRESSO = 2017`  
  - `SEMESTRE_INGRESSO = 2` ou `SEMESTRE_INGRESSO = 2º semestre`

> ⚠️ Caso as duas formas sejam enviadas, o sistema prioriza o uso de `ANO_INGRESSO` e `SEMESTRE_INGRESSO`.
"""


def explicacao_periodo_evasao():
    return """
### Valores aceitos para Período de Evasão

O período de evasão também pode ser informado de **duas formas**:

#### 1. Usando a coluna `PERIODO_EVASAO`  
- Mesmo padrão do ingresso:
  - Exemplos válidos: `2019/2º. semestre`, `2022/1`, `2017/2`
- O sistema extrai automaticamente:
  - `ANO_EVASAO` (ex: 2022)
  - `SEMESTRE_EVASAO` (1 ou 2)

#### 2. Usando as colunas `ANO_EVASAO` e `SEMESTRE_EVASAO` separadamente  
- Exemplo:
  - `ANO_EVASAO = 2021`  
  - `SEMESTRE_EVASAO = 1` ou `SEMESTRE_EVASAO = 2°. semestre`

> ⚠️ Caso as duas formas estejam presentes, o sistema dará preferência para `ANO_EVASAO` e `SEMESTRE_EVASAO`.
"""


def explicacao_bairro():
    return """
### Valores aceitos para a coluna BAIRRO

A coluna **BAIRRO** representa o bairro de residência do aluno ao ingressar no curso.

#### Regras de preenchimento:
- Pode ser preenchido com ou sem **acentos**, em **maiúsculas ou minúsculas**.
- O sistema faz a **normalização automática**:
  - Exemplos válidos: `copacabana`, `Copacabana`, `copa cabana` → todos serão tratados como **Copacabana**.
- Quando a coluna **BAIRRO** estiver ausente, o sistema tentará extrair o bairro a partir da coluna **ENDERECO**, se estiver presente.

> Se o valor de **BAIRRO** estiver vazio, o registro será **ignorado nas análises geográficas** (ex: zona geográfica, distância, agrupamentos).
> A extração de bairro a partir de **ENDERECO** depende de uma estrutura clara e pode apresentar falhas.
"""


def explicacao_cidade():
    return """
### Valores aceitos para a coluna CIDADE

A coluna **CIDADE** indica o município de residência do aluno ao ingressar no curso.

#### Regras de preenchimento:
- Pode ser escrita com ou sem **acentos**, e com qualquer combinação de maiúsculas/minúsculas.
  - Exemplo: `rio de janeiro`, `RIO DE JANEIRO`, `Rio De Janeiro` → tudo será tratado como **Rio de Janeiro**.
- O sistema aplica **normalização automática** para uniformizar os dados.
- Caso a coluna esteja ausente, o sistema tentará extrair a cidade do campo **ENDERECO**, se existir.

> Se o valor de **CIDADE** estiver vazio, o registro será **ignorado em análises que dependem da localização**.
"""


def explicacao_estado():
    return """
### Valores aceitos para a coluna ESTADO

A coluna **ESTADO** indica a unidade federativa do aluno ao ingressar no curso.

#### Regras de preenchimento:
- É aceito o nome completo (`Rio de Janeiro`) ou a sigla (`RJ`), com ou sem acentos.
  - Exemplo: `rj`, `RJ`, `rio de janeiro` → todos tratados como **Rio de Janeiro (RJ)**.
- O sistema normaliza automaticamente os valores para garantir consistência.
- Se a coluna estiver ausente, o sistema tentará inferir o estado a partir do campo **ENDERECO**, se disponível.

> Se o valor de **ESTADO** estiver vazio, o registro será **desconsiderado de todas as análises geográficas**.
"""


def explicacao_endereco():
    return """
### Valores aceitos para a coluna ENDERECO

A coluna **ENDERECO** pode ser usada quando as colunas **BAIRRO**, **CIDADE** e **ESTADO** não estiverem presentes separadamente.

#### Como deve vir o valor:
- O endereço completo deve conter os seguintes elementos separados por **vírgula** ou **hífen**:
  - **Bairro**, **Cidade** - **UF**
  - Exemplo válido:  
    `Rua Pasteur, 458, Urca - Rio de Janeiro, RJ`

#### Regras aplicadas automaticamente:
- O sistema tenta extrair os dados do **bairro**, **cidade** e **estado** a partir do final do endereço.
- São aceitas diferentes pontuações e variações como:
  - `Avenida Presidente Vargas, 3131, Centro - Rio de Janeiro - RJ`
  - `Praça da Sé, 111, Sé, São Paulo, SP`  
  - `Tijuca, Rio de Janeiro - RJ`

> ⚠️ Caso o padrão esperado não seja encontrado, os campos serão deixados em branco e o registro poderá ser ignorado em análises geográficas.
> É importante garantir que **bairro, cidade e estado** estejam corretamente posicionados no campo de endereço.
"""


def get_explicacao_coluna(coluna: str) -> str | None:
    match coluna:
        case "FORMA_INGRESSO":
            return explicacao_forma_ingresso()
        case "SEXO":
            return explicacao_sexo()
        case "FORMA_EVASAO":
            return explicacao_forma_evasao()
        case "CRA":
            return explicacao_cra()
        case "DT_NASCIMENTO":
            return explicacao_dt_nascimento()
        case "PERIODO_INGRESSO":
            return explicacao_periodo_ingresso()
        case "PERIODO_EVASAO":
            return explicacao_periodo_evasao()
        case "BAIRRO":
            return explicacao_bairro()
        case "CIDADE":
            return explicacao_cidade()
        case "ESTADO":
            return explicacao_estado()
        case "ENDERECO":
            return explicacao_endereco()
        case _:
            return None
