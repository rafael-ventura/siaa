import os
import time
import numpy as np
import pandas as pd
import googlemaps
from datetime import datetime, timedelta

class ModuloDistanciaGoogle:
    BASE_DIR = os.path.dirname(__file__)
    ARQUIVO_DISTANCIAS = os.path.join(BASE_DIR, "../dados/dfDistancias_google.csv")
    DESTINO_UNIRIO = "Av. Pasteur 459, Urca, Rio de Janeiro, RJ"  # Endereço da UNIRIO/Urca

    @staticmethod
    def inicializar_client(api_key):
        return googlemaps.Client(key=api_key)

    @staticmethod
    def carregar_cache_distancias() -> dict:
        caminho = ModuloDistanciaGoogle.ARQUIVO_DISTANCIAS
        if not os.path.exists(caminho) or os.path.getsize(caminho) == 0:
            pd.DataFrame(columns=["BAIRRO", "CIDADE", "ESTADO", "MODO", "DISTANCIA_KM", "DURACAO", "SAIDA_PARA_18H"]).to_csv(caminho, index=False)
            return {}
        df = pd.read_csv(caminho)
        return {
            (row['BAIRRO'], row['CIDADE'], row['ESTADO'], row['MODO']): {
                "DISTANCIA_KM": row['DISTANCIA_KM'],
                "DURACAO": row['DURACAO'],
                "SAIDA_PARA_18H": row['SAIDA_PARA_18H']
            }
            for _, row in df.iterrows()
        }

    @staticmethod
    def salvar_distancias(cache_distancias: dict):
        caminho = ModuloDistanciaGoogle.ARQUIVO_DISTANCIAS
        os.makedirs(os.path.dirname(caminho), exist_ok=True)
        linhas = []
        for k, v in cache_distancias.items():
            bairro, cidade, estado, modo = k
            linhas.append({
                "BAIRRO": bairro,
                "CIDADE": cidade,
                "ESTADO": estado,
                "MODO": modo,
                "DISTANCIA_KM": v["DISTANCIA_KM"],
                "DURACAO": v["DURACAO"],
                "SAIDA_PARA_18H": v["SAIDA_PARA_18H"]
            })
        pd.DataFrame(linhas).to_csv(caminho, index=False)

    @staticmethod
    def calcular_tempo_e_distancia(bairro, cidade, estado, gmaps, chegada="18:00", modo="transit"):
        origem = f"{bairro}, {cidade}, {estado}"
        destino = ModuloDistanciaGoogle.DESTINO_UNIRIO

        hoje = datetime.now()
        chegada_dt = hoje.replace(hour=int(chegada.split(":")[0]), minute=int(chegada.split(":")[1]), second=0, microsecond=0)
        if chegada_dt < hoje:
            chegada_dt += timedelta(days=1)

        try:
            res = gmaps.distance_matrix(
                origins=[origem],
                destinations=[destino],
                mode=modo,
                arrival_time=int(chegada_dt.timestamp()),
                language="pt-BR"
            )
            element = res["rows"][0]["elements"][0]
            if element["status"] == "OK":
                distancia_km = element["distance"]["value"] / 1000
                duracao_texto = element["duration"]["text"]
                duracao_seg = element["duration"]["value"]
                saida_estimada = chegada_dt - timedelta(seconds=duracao_seg)
                return round(distancia_km, 2), duracao_texto, saida_estimada.strftime("%H:%M")
            else:
                return np.NaN, None, None
        except Exception as e:
            print(f"[GoogleMaps API] Erro em {origem} modo {modo}: {e}")
            return np.NaN, None, None

    @staticmethod
    def adicionar_distancia_urca(df: pd.DataFrame, api_key: str) -> pd.DataFrame:
        if "ESTADO" not in df.columns:
            print("⚠️ Coluna ESTADO ausente. Ignorando cálculo de distância.")
            return df

        df["ESTADO"] = df["ESTADO"].astype(str).str.strip().str.upper()
        df_validos = df[df["ESTADO"].str.lower() == "rj"].copy()
        if df_validos.empty:
            print("⚠️ Nenhum registro do estado 'RJ' encontrado. Ignorando cálculo de distância.")
            return df

        modos = ["transit"]  # Só calcula ônibus
        grupos = df_validos[["BAIRRO", "CIDADE", "ESTADO"]].drop_duplicates()
        gmaps = ModuloDistanciaGoogle.inicializar_client(api_key)
        cache = ModuloDistanciaGoogle.carregar_cache_distancias()

        for modo in modos:
            for _, row in grupos.iterrows():
                chave = (row["BAIRRO"], row["CIDADE"], row["ESTADO"], modo)
                if chave in cache and cache[chave]["DISTANCIA_KM"] is not None:
                    print(f"[CACHE] {chave} já calculado, pulando.")
                    continue
                if row["BAIRRO"].lower() == "urca":
                    print(f"[INFO] Bairro 'Urca' (modo {modo}) – distância = 0km")
                    cache[chave] = {
                        "DISTANCIA_KM": 0.0,
                        "DURACAO": "0 min",
                        "SAIDA_PARA_18H": "18:00"
                    }
                    continue
                print(f"[CALCULANDO] {row['BAIRRO']}, {row['CIDADE']}, {row['ESTADO']} (modo {modo})...")
                dist, dur, saida = ModuloDistanciaGoogle.calcular_tempo_e_distancia(
                    row["BAIRRO"], row["CIDADE"], row["ESTADO"], gmaps, modo=modo
                )
                print(f"    Resultado: {dist}km, {dur}, saída: {saida}")
                cache[chave] = {
                    "DISTANCIA_KM": dist,
                    "DURACAO": dur,
                    "SAIDA_PARA_18H": saida
                }
                time.sleep(0.25)

        ModuloDistanciaGoogle.salvar_distancias(cache)

        # Colunas para ônibus (sem sufixo, se quiser, ou mantenha o "_ONIBUS" para clareza)
        suf = ""  # ou "_ONIBUS" se preferir
        col_dist = f"DISTANCIA_URCA{suf}"
        col_km = f"DISTANCIA_GOOGLE_KM{suf}"
        col_tempo = f"TEMPO_DESLOCAMENTO{suf}"
        col_saida = f"HORA_SAIDA_PARA_CHEGAR_18H{suf}"

        df[col_dist] = np.NaN
        df[col_km] = np.NaN
        df[col_tempo] = None
        df[col_saida] = None

        for idx, row in df.iterrows():
            chave = (row["BAIRRO"], row["CIDADE"], row["ESTADO"], "transit")
            info = cache.get(chave, {})
            df.at[idx, col_dist] = info.get("DISTANCIA_KM", np.NaN)
            df.at[idx, col_km] = info.get("DISTANCIA_KM", np.NaN)
            df.at[idx, col_tempo] = info.get("DURACAO", None)
            df.at[idx, col_saida] = info.get("SAIDA_PARA_18H", None)

        return df
