from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
import tempfile
import os
import subprocess
from faster_whisper import WhisperModel

# Define caminho do ffmpeg
# os.environ["PATH"] += os.pathsep + r"/\ffmpeg-7.1.1\bin"

# Inicia FastAPI
app = FastAPI()

# Carrega modelo Whisper otimizado
model = WhisperModel("large-v3", compute_type="int8", device="cpu")  # use "cuda" se tiver GPU

@app.post("/transcrever/")
async def transcrever_audio(file: UploadFile = File(...)):
    if not file.filename.endswith(".ogg"):
        raise HTTPException(status_code=400, detail="O arquivo deve ser .ogg")
    try:
        # Salva .ogg temporariamente
        with tempfile.NamedTemporaryFile(delete=False, suffix=".ogg") as temp_ogg:
            temp_ogg.write(await file.read())
            ogg_path = temp_ogg.name

        # Converte para .wav com 16kHz mono
        wav_path = ogg_path.replace(".ogg", ".wav")
        subprocess.run([
            "ffmpeg", "-y", "-i", ogg_path,
            "-ar", "16000", "-ac", "1", wav_path
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # Transcrição com faster-whisper
        segments, _ = model.transcribe(wav_path, language="pt")
        transcription = " ".join([segment.text for segment in segments]).strip().lower()

        # Limpa arquivos
        os.remove(ogg_path)
        os.remove(wav_path)

        return JSONResponse(content={"transcricao": transcription})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/teste/")
async def testarApi(file: UploadFile = File(...)):
    try:
        return JSONResponse(content={"transcricao": "Funcionando!"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8100, reload=True)
