# 1. Usa un'immagine base di Python
FROM python:3.10-slim

# 2. Imposta la cartella di lavoro all'interno del container
WORKDIR /app

# 3. Copia il file requirements.txt (contenente le librerie necessarie) nella cartella di lavoro
COPY requirements.txt .

# 4. Installa le dipendenze
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copia il resto del progetto nella cartella di lavoro
COPY . .

# 6. Imposta il comando per avviare il programma
CMD ["python", "main.py"]