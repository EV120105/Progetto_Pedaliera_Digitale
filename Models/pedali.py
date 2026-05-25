from abc import ABC, abstractmethod

import math
class Pedale(ABC):

    def __init__(self, tipo: str, posizione: int, bypass: bool = False):

        self.tipo = tipo

        self.posizione = posizione

        self.bypass = bypass

        self.parametri = {}



    @abstractmethod

    def applica_effetto(self, segnale: list) -> list:

        pass



    def imposta_parametri(self, nuovi_parametri: dict):

        self.parametri.update(nuovi_parametri)

        print(f"[{self.tipo}] Parametri aggiornati: {self.parametri}")



    def toggle_bypass(self):

        self.bypass = not self.bypass

        stato = "Attivo" if not self.bypass else "In Bypass"

        print(f"[{self.tipo}] Stato: {stato}")



    def to_dict(self):

        return {

            "tipo": self.tipo,

            "posizione": self.posizione,

            "parametri": self.parametri,

            "bypass": self.bypass

        }



class PedaleDistorsione(Pedale):

    def __init__(self, posizione: int, gain: float = 0.5):

        super().__init__("Distorsione", posizione)

        self.parametri = {"gain": gain}



    def applica_effetto(self, segnale: list) -> list:

        if self.bypass: return segnale

        # DSP: Hard Clipping deciso. Moltiplichiamo per un fattore alto per forzare la distorsione udibile

        g = self.parametri.get("gain", 0.5) * 50  # Spingiamo il guadagno

        return [max(min(s * g, 1.0), -1.0) for s in segnale]



class PedaleDelay(Pedale):

    def __init__(self, posizione: int, tempo: float = 500.0, feedback: float = 0.4):

        super().__init__("Delay", posizione)

        self.parametri = {"tempo": tempo, "feedback": feedback}



    def applica_effetto(self, segnale: list) -> list:

        if self.bypass: return segnale

       

        feedback = self.parametri.get("feedback", 0.4)

        tempo_ms = self.parametri.get("tempo", 500.0)

       

        # Assumiamo una frequenza standard di 44100Hz per calcolare il ritardo in campioni

        frequenza_campionamento = 44100

        ritardo_campioni = int((tempo_ms / 1000.0) * frequenza_campionamento)

       

        # Creiamo un array di uscita grande abbastanza da contenere le code del delay

        lunghezza_estesa = len(segnale) + (ritardo_campioni * 4)

        uscita = [0.0] * lunghezza_estesa

       

        # Copiamo il segnale originale

        for i in range(len(segnale)):

            uscita[i] = segnale[i]

           

        # Applichiamo l'eco campione per campione nel buffer

        for i in range(lunghezza_estesa):

            if i >= ritardo_campioni:

                uscita[i] += uscita[i - ritardo_campioni] * feedback

               

        return uscita



class PedaleChorus(Pedale):

    def __init__(self, posizione: int, rate: float = 1.5, depth: float = 0.4):

        super().__init__("Chorus", posizione)

        self.parametri = {"rate": rate, "depth": depth}



    def applica_effetto(self, segnale: list) -> list:

        if self.bypass: return segnale

       

        rate = self.parametri.get("rate", 1.5)

        depth = self.parametri.get("depth", 0.4)

        fs = 44100  # Frequenza di campionamento stimata

       

        uscita = []

        # Modulazione del ritardo tramite una funzione Sinusoidale (LFO)

        for i, s in enumerate(segnale):

            # Calcola il ritardo variabile nel tempo usando il seno

            lfo = math.sin(2 * math.pi * rate * (i / fs))

            # Ritardo medio di 25ms modificato dall'LFO in base alla profondità (depth)

            ritardo = int((0.025 + (0.005 * lfo * depth)) * fs)

           

            if i >= ritardo:

                # Misceliamo il segnale originale (Dry) con quello ritardato nel tempo (Wet)

                uscita.append(s * 0.7 + segnale[i - ritardo] * 0.3)

            else:

                uscita.append(s)

        return uscita



