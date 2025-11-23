
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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


app.include_router(game_router, prefix="/api")


@app.get("/")
def read_root():
    return {"message": "Batalla Naval API is running!"}

# Iniciar la aplicación
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)  

