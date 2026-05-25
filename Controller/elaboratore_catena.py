import os
import wave
import struct

class ElaboratoreCatena:
    def __init__(self, repo):
        self.repo = repo

    def set_parametro_pedale(self, idx, parametri):
        pedale = self.repo.get_pedale(idx)
        if pedale:
            pedale.imposta_parametri(parametri)
            self.repo.save_to_json()

    def applica_dsp_catena(self, percorso_file: str, percorso_uscita: str) -> str:
        #Elabora il file WAV selezionato e lo salva nel percorso d'uscita 
        #stabilito e già verificato dalla Boundary.

        percorso_pulito = os.path.normpath(percorso_file)
        print(f"[DEBUG CONTROLLER]: Tento di aprire il file: {percorso_pulito}")
        print(f"[DEBUG CONTROLLER]: Il file di uscita sarà: {percorso_uscita}")

        # 1. Lettura del file originale
        try:
            with wave.open(percorso_pulito, 'rb') as wav_in:
                params = wav_in.getparams()
                n_channels = params.nchannels
                sampwidth = params.sampwidth
                framerate = params.framerate
                n_frames = params.nframes
                
                print(f"[DEBUG WAV]: Canali={n_channels}, Risoluzione={sampwidth*8}-bit, Frequenza={framerate}Hz, Frame totali={n_frames}")
                
                if sampwidth != 2:
                    return f"ERRORE: Il file WAV è a {sampwidth*8}-bit. Questo algoritmo supporta SOLO file a 16-bit PCM."

                data_bytes = wav_in.readframes(n_frames)
                print(f"[DEBUG WAV]: Letti {len(data_bytes)} byte dal file originale.")
        except Exception as e:
            return f"ERRORE durante la lettura del file WAV: {e}"

        # 2. Conversione Byte -> Interi -> Float (-1.0 a 1.0)
        num_samples = len(data_bytes) // 2
        formato = f"<{num_samples}h"
        
        try:
            campioni_interi = struct.unpack(formato, data_bytes)
        except Exception as e:
            return f"ERRORE nel parsing dei byte audio (struct unpack): {e}"
            
        segnale_float = [float(s) / 32768.0 for s in campioni_interi]
        print(f"[DEBUG DSP]: Convertiti {len(segnale_float)} campioni in formato Float.")

        # 3. Applicazione degli effetti in cascata sequenziale
        pedali = self.repo.get_tutti_i_pedali()
        segnale_elaborato = segnale_float
        
        effetti_applicati = 0
        for pedale in pedali:
            if pedale and not pedale.bypass:
                print(f"[DEBUG DSP]: Applicazione effetto {pedale.tipo}...")
                segnale_elaborato = pedale.applica_effetto(segnale_elaborato)
                effetti_applicati += 1
        
        if effetti_applicati == 0:
            print("[DEBUG DSP]: Nessun pedale attivo o presente nella catena. Il suono passerà pulito.")

        # 4. Riconversione Float -> Interi 16-bit con protezione hard-clipping
        campioni_out_interi = []
        for s in segnale_elaborato:
            s_clipped = max(min(s, 1.0), -1.0)
            campioni_out_interi.append(int(s_clipped * 32767.0))

        # 5. Preparazione dei byte finali e scrittura
        try:
            data_out_bytes = struct.pack(f"<{len(campioni_out_interi)}h", *campioni_out_interi)
            nuovo_n_frames = len(campioni_out_interi) // n_channels

            print(f"[DEBUG CONTROLLER]: Scrittura sul disco in corso...")
            with wave.open(percorso_uscita, 'wb') as wav_out:
                wav_out.setnchannels(n_channels)
                wav_out.setsampwidth(sampwidth)
                wav_out.setframerate(framerate)
                wav_out.setnframes(nuovo_n_frames)
                wav_out.writeframes(data_out_bytes)
            
            # Controllo finale di avvenuta scrittura
            if os.path.exists(percorso_uscita):
                print(f"[DEBUG CONTROLLER]: Verifica completata. Il file esiste fisicamente sul disco.")
                return f"File elaborato salvato correttamente!\nPercorso: {percorso_uscita}"
            else:
                return "ERRORE: Il processo è terminato senza errori ma il file non è presente sulla cartella."
                
        except Exception as e:
            return f"ERRORE durante la scrittura del file WAV finale: {e}"