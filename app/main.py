
import sys
from pathlib import Path

# Agregar el directorio raíz al path de Python
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import APIRouter
from app.controller.Game_controller import router as game_router

# Configuración básica de la aplicación
app = FastAPI(
    title='API Batalla Naval',
    description='API para el juego de Batalla Naval',
    version='1.0.0'
)

# Configuración CORS básica
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Incluir rutas de la API

api_router = APIRouter()
app.include_router(game_router)

# Iniciar la aplicación
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
