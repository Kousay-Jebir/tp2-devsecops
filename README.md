# tp2-devsecops-cicd

Minimal Flask note-taking app used to demonstrate security gates in a CI/CD pipeline
(unit tests, SAST, SCA, DAST). TP1 scan reports are kept in `docs/tp1/`.

## Routes
| Route | Description |
|---|---|
| `GET /` | List notes, optional search by title (`?q=`) |
| `POST /notes` | Create a note (`title`, `content`) |
| `GET /healthz` | Health check used by the pipeline before the DAST scan |

## Run locally
```bash
pip install -r requirements-dev.txt
python -m pytest -v          # unit tests
python app.py                # http://127.0.0.1:5000
```

## Run with Docker
```bash
docker build --target test .                 # builds and runs the unit tests
docker build --target runtime -t notes-app .
docker run --rm -p 5000:5000 notes-app
```
