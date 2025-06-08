import pandas as pd
from .texto import ModuloTexto
from ..dados.correcoes_localizacao import correcoes_bairros, correcoes_cidades
from ..dados.zonas_geograficas import ZONAS_GEOGRAFICAS
import unidecode


class ModuloLocalizacao:
    @staticmethod
    def padronizar_bairros_cidades(df: pd.DataFrame) -> pd.DataFrame:
        df = ModuloTexto.normalizar_e_corrigir(df, "BAIRRO", correcoes_bairros)
        df = ModuloTexto.normalizar_e_corrigir(df, "CIDADE", correcoes_cidades)
        return df

    @staticmethod
    def normalizar_texto(texto: str) -> str:
        return unidecode.unidecode(str(texto)).strip().lower()

    @staticmethod
    def adicionar_zona_geografica(df: pd.DataFrame) -> pd.DataFrame:
        import unidecode

        def normalizar(texto):
            return unidecode.unidecode(str(texto)).strip().lower()

        zonas_bairros = ["zona norte", "zona oeste", "zona sul", "centro"]
        zonas_bairros_dict = {
            zona: set(normalizar(b) for b in bairros)
            for zona, bairros in ZONAS_GEOGRAFICAS.items()
            if zona in zonas_bairros
        }
        zonas_cidades_dict = {
            zona: set(normalizar(c) for c in bairros)
            for zona, bairros in ZONAS_GEOGRAFICAS.items()
            if zona not in zonas_bairros
        }

        def obter_zona(row) -> str:
            estado = str(row.get("ESTADO", "")).strip().upper()
            if estado != "RJ":
                return "Outro Estado"
            bairro_norm = normalizar(row.get('BAIRRO', ''))
            cidade_norm = normalizar(row.get('CIDADE', ''))
            for zona, bairros_normalizados in zonas_bairros_dict.items():
                if bairro_norm in bairros_normalizados:
                    return zona
            for zona, cidades_normalizadas in zonas_cidades_dict.items():
                if cidade_norm in cidades_normalizadas:
                    return zona
            # Se for RJ mas não achou bairro/cidade, pode usar um valor explícito
            return "NAO_IDENTIFICADO_RJ"

        if {"BAIRRO", "CIDADE", "ESTADO"}.issubset(df.columns):
            df["ZONA_GEOGRAFICA"] = df.apply(obter_zona, axis=1)
        return df

    @staticmethod
    def adicionar_cidade_estado(df: pd.DataFrame) -> pd.DataFrame:
        if "CIDADE" in df.columns and "ESTADO" not in df.columns:
            df["ESTADO"] = "RJ"
        return df

    @staticmethod
    def corrigir_enderecos_especificos(df: pd.DataFrame) -> pd.DataFrame:
        # Mapeamento (bairro original normalizado) -> (bairro corrigido, cidade corrigida, estado corrigido)
        correcoes = {
            "aldeia da prata (manilha)": ("aldeia da prata", "itaborai", "rj"),
            "centro/nova iguacu": ("centro", "nova iguacu", "rj"),
            "colubande": ("colubande", "sao goncalo", "rj"),
            "cosmorama": ("cosmorama", "mesquita", "rj"),
            "da luz": ("da luz", "nova iguacu", "rj"),
            "edson passos": ("edson passos", "mesquita", "rj"),
            "farrula": ("farrula", "sao joao de meriti", "rj"),
            "ibes": ("ibes", "vila velha", "es"),
            "itaipu": ("itaipu", "niteroi", "rj"),
            "itapeba": ("itapeba", "marica", "rj"),
            "parada 40": ("parada 40", "niteroi", "rj"),
            "jardim gramacho": ("jardim gramacho", "duque de caxias", "rj"),
            "ouro verde": ("ouro verde", "nova iguacu", "rj"),
            "mutua": ("mutua", "sao goncalo", "rj"),
            "coelho da rocha": ("coelho da rocha", "são joão de meriti", "rj"),
            "jardim meriti": ("jardim meriti", "são joão de meriti", "rj"),
            "quitandinha": ("quitandinha", "petrópolis", "rj"),
            "vila nova": ("vila nova", "nova iguacu", "rj"),
            "olavo bilac": ("jardim olavo bilac", "são joão de meriti", "rj"),
            "glaucia": ("jardim glaucia", "belford roxo", "rj"),
            "aldeia de prata": ("aldeia da prata", "itaborai", "rj"),
            "morin" : ("morin", "petrópolis", "rj"),
            "centenario" : ("vila centenário", "duque de caxias", "rj"),
            "lins" : ("lins de vasconcelos", "rio de janeiro", "rj"),
            "laranjal" : ("laranjal","são gonçalo", "rj"),
            "jardim tropical" : ("jardim tropical", "nova iguaçu", "rj"),
            "jardim jurema" : ("jardim jurema", "são joão de meriti", "rj"),
            "monte castelo" : ("monte castelo", "nova iguaçu", "rj"),
            "icarai" : ("icarai", "niterói", "rj"),
            "santa rosa" : ("santa rosa", "niterói", "rj"),
            "inga" : ("inga", "niterói", "rj"),
            "fonseca" : ("fonseca", "niterói", "rj"),
            "barreto" : ("barreto", "niterói", "rj"),
            "piratininga" : ("piratininga", "niterói", "rj"),
            "vila inhomirim" : ("vila inhomirim", "magé", "rj"),
            "vila centenario" : ("vila centenario", "duque de caxias", "rj"),
            "jardim primavera" : ("jardim primavera", "duque de caxias", "rj"),
            "varzea" : ("várzea", "teresópolis", "rj"),
            "vila brasil" : ("vila brasil", "itaboraí", "rj"),
            "vilar dos teles" : ("vilar dos teles", "são joão de meriti", "rj"),
            "jardim anhanga" : ("jardim anhanga", "duque de caxias", "rj"),
            "santa teresinha" : ("santa teresinha", "mesquita", "rj"),
            "prata" : ("prata", "teresópolis", "rj"),
            "queimados" : ("queimados", "queimados", "rj"),
            "raul veiga" : ("raul veiga", "são gonçalo", "rj"),
            "riachao" : ("riachão", "nova iguaçu", "rj"),
            "rio do ouro" : ("rio do ouro", "niterói", "rj"),
            "santa catarina" : ("santa catarina", "sao gonçalo", "rj"),
            "sao francisco" : ("são francisco", "niterói", "rj"),
            "bairro das gracas" : ("bairro das graças", "belford roxo", "rj"),
            "petropolis" : ("petrópolis", "petrópolis", "rj"),
            "piabeta" : ("piabetá", "magé", "rj"),
            "santa cruz da serra" : ("santa cruz da serra", "duque de caxias", "rj"),
            "ponto chic" : ("ponto chic", "nova iguaçu", "rj"),
            "sao goncalo" : ("são gonçalo", "são gonçalo", "rj"),
            "engenho do mato" : ("engenho do mato", "niterói", "rj"),
            "engenho do porto" : ("engenho do porto", "duque de caxias", "rj"),
            "fatima" : ("bairro de fátima", "rio de janeiro", "rj"),
            "niteroi" : ("niterói", "niterói", "rj"),
            "vila sao sebastiao" : ("vila são sebastião", "duque de caxias", "rj"),
            "nossa senhora das gracas" : ("copacabana", "rio de janeiro", "rj"),
            "nova america" : ("nova américa", "nova iguaçu", "rj"),
            "maria paula" : ("maria paula", "são gonçalo", "rj"),
            "parque sao vicente" : ("parque são vicente", "belford roxo", "rj"),
            "jardim campomar" : ("jardim campomar", "rio das ostras", "rj"),
            "lindo parque" : ("lindo parque", "sao gonçalo", "rj"),
            "prado" :  ("prado", "nova friburgo", "rj"),
            "vila rosario" : ("vila rosário", "duque de caxias", "rj"),
            "vila leopoldina" : ("vila leopoldina", "duque de caxias", "rj"),
            "vila de cava" : ("vila de cava", "nova iguaçu", "rj"),
            "sete pontes" : ("sete pontes", "sao gonçalo", "rj"),
            "santa luzia" : ("santa luzia", "sao gonçalo", "rj"),
            "santa eugenia" : ("santa eugenia", "nova iguaçu", "rj"),
            "banco de areia" : ("banco de areia", "mesquita", "rj"),
            "brasilandia" : ("brasilândia", "sao gonçalo", "rj"),
            "carlos sampaio" : ("carlos sampaio", "nova iguaçu", "rj"),
            "cruzeiro do sul" : ("cruzeiro do sul", "mesquita", "rj"),
            "ferradura" : ("ferradura", "Armacao dos Buzios", "rj"),
            "nova cidade" : ("nova cidade", "nilópolis", "rj"),
            "parque lafaiete" : ("parque lafaiete", "duque de caxias", "rj"),
            "parque vila nova" : ("parque vila nova", "duque de caxias", "rj"),
            "pauline" : ("vila pauline", "belford roxo", "rj"),
            "praia brava" : ("praia brava", "angra dos reis", "rj"),
            "vila sao luis" : ("vila são luís", "duque de caxias", "rj"),
            "vila itamarati" : ("vila itamarati", "duque de caxias", "rj"),
            "vila guanabara" : ("vila guanabara", "duque de caxias", "rj"),
            "praca da ponte" : ("praça da ponte", "miguel pereira", "rj"),
            "mutando" : ("mutondo", "são gonçalo", "rj"),
            "freguesia (ilha do governador)": ("freguesia", "rio de janeiro", "rj"),
            "jardim excelsior" : ("jardim excelsior", "cabo frio", "rj"),
            "caxias" : ("centro", "duque de caxias", "rj"),
            "jardim caicara" : ("jardim caiçara", "cabo frio", "rj"),
            "jardim rosario" : ("jardim rosário", "duque de caxias", "rj"),
            "jardim boa esperanca" : ("jardim boa esperança", "bom jardim", "rj"),
            "parque ipiranga" : ("parque ipiranga", "resende", "rj"),
            "vila oito de maio" : ("vila 8 de maio", "duque de caxias", "rj"),
            "mirandopolis" : ("mirandópolis", "quatis", "rj"),
            "plante cafe" : ("plante café", "miguel pereira", "rj"),
            "parque vitoria" : ("parque vitória", "duque de caxias", "rj"),
            "santo amaro" : ("santo amaro", "sao paulo", "sp"),
            "santo anta'nio" : ("santo antônio", "são paulo", "sp"),
            "ufrrj" : ("ufrj", "seropedica", "rj"),
            "village sao roque" : ("village são roque", "miguel pereira", "rj"),
            "rio de janeiro" : ("praca seca", "rio de janeiro", "rj"),
            "piquet" : ("centro", "maricá", "rj")
        }

        def normalizar(texto):
            import unidecode
            return unidecode.unidecode(str(texto)).strip().lower()

        for idx, row in df.iterrows():
            bairro_norm = normalizar(row.get("BAIRRO", ""))
            if bairro_norm in correcoes:
                novo_bairro, nova_cidade, novo_estado = correcoes[bairro_norm]
                df.at[idx, "BAIRRO"] = novo_bairro
                df.at[idx, "CIDADE"] = nova_cidade
                df.at[idx, "ESTADO"] = novo_estado

        return df
