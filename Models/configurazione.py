# Models/configurazione.py

class ConfigurazionePreset:
    def __init__(self, nome_preset: str, lista_dati_configurazione: list = None):
        self.nome_preset = nome_preset
        # Contiene i dizionari dei singoli pedali (tipo, posizione, parametri, bypass)
        self.lista_dati_configurazione = lista_dati_configurazione if lista_dati_configurazione is not None else []

    def to_dict(self):
        return {
            "nome_preset": self.nome_preset,
            "pedali": self.lista_dati_configurazione
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            nome_preset=data.get("nome_preset"),
            lista_dati_configurazione=data.get("pedali", [])
        )