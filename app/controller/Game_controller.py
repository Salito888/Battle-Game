
from fastapi import APIRouter, HTTPException, status
from typing import List, Dict, Optional
from uuid import UUID
from pydantic import BaseModel, Field
from app.model.Game_model import (
    Game, Player, ShipNode, Coordinate, ShipOrientation, 
    ShotResult, GameState, ShotNode, ShotTree)
from app.model.Game_model import ShipCreate


router = APIRouter()


# Almacenamiento en memoria (en producción, usar una base de datos)
games = {}
players = {}
admin_config = {
    "board_size": None,
    "ships": []
}

# Modelos de solicitud (Request Models)
class PlayerCreate(BaseModel):
    name: str

class ShipConfig(BaseModel):
    name: str
    size: int

class AdminConfigureShips(BaseModel):
    board_size: int
    ships: List[ShipConfig]

class ShipCreate(BaseModel):
    name: str
    size: int
    orientation: ShipOrientation
    coordinates: list[dict]
    

coordinates = [
    Coordinate(row=c.row, col=c.col)
    for c in ship_data.coordinates
]
ship.coordinates = coordinates


class ShotCreate(BaseModel):
    player_id: UUID
    row: int = Field(..., ge=0, description="Row coordinate (0-based)")
    col: int = Field(..., ge=0, description="Column coordinate (0-based)")

class GameCreate(BaseModel):
    board_size: int = Field(..., gt=0, description="Size of the game board (NxN)")
    max_ships: int = Field(..., gt=0, description="Number of ships per player")
    max_ships_length_ratio: float = Field(default=0.7, ge=0.1, le=1.0)

class GameCreateWithPlayers(BaseModel):
    player_1_id: str = Field(..., description="ID del primer jugador")
    player_2_id: str = Field(..., description="ID del segundo jugador")

# Almacenamiento de configuración del administrador
admin_config = {
    "board_size": None,
    "ships": []
}

# Endpoints
@router.post("/admin/configurar-barcos", status_code=status.HTTP_201_CREATED)
async def configure_ships(config: AdminConfigureShips):
    """El administrador configura el tamaño del tablero y los barcos disponibles."""
    # Validar tamaño del tablero
    if config.board_size < 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Board size must be at least 5"
        )
    
    # Validar que no haya barcos duplicados
    ship_names = [ship.name for ship in config.ships]
    if len(ship_names) != len(set(ship_names)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ship names must be unique"
        )
    
    # Validar límite del 70%
    total_ship_length = sum(ship.size for ship in config.ships)
    max_allowed = config.board_size * config.board_size * 0.7
    
    if total_ship_length > max_allowed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Total ship length ({total_ship_length}) exceeds 70% of board ({max_allowed})"
        )
    
    # Guardar configuración
    admin_config["board_size"] = config.board_size
    admin_config["ships"] = [{"name": ship.name, "size": ship.size} for ship in config.ships]
    
    return {
        "message": "Ships configured successfully",
        "board_size": config.board_size,
        "ships": admin_config["ships"]
    }



@router.post("/jugadores", status_code=status.HTTP_201_CREATED)
async def create_player(player_data: PlayerCreate):
    """Crea un nuevo jugador con un nombre único."""
    # Verificar si el nombre ya existe
    if any(p.name == player_data.name for p in players.values()):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Player name already exists"
        )
    
    player = Player(name=player_data.name)
    players[str(player.id)] = player
    return {"player_id": player.id, "name": player.name}

@router.get("/jugadores", status_code=status.HTTP_200_OK)
async def list_players():
    """Obtiene el listado de todos los jugadores."""
    return {
        "total": len(players),
        "players": [
            {
                "player_id": str(player.id),
                "name": player.name,
                "is_ready": player.is_ready
            }
            for player in players.values()
        ]
    }

@router.post("/partidas", status_code=status.HTTP_201_CREATED)
async def create_game(game_data: GameCreateWithPlayers):

    """Crea una nueva partida con exactamente 2 jugadores usando la configuración del administrador."""
    # Verificar que la configuración del administrador esté establecida
    if not admin_config["board_size"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El administrador debe configurar los barcos primero"
        )
    
    # Verificar que ambos jugadores existan
    if game_data.player_1_id not in players:
        raise HTTPException(status_code=404, detail="Jugador 1 no encontrado")
    
    if game_data.player_2_id not in players:
        raise HTTPException(status_code=404, detail="Jugador 2 no encontrado")
    
    if game_data.player_1_id == game_data.player_2_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El Jugador 1 y el Jugador 2 deben ser diferentes"
        )
    
    # Crear partida con la configuración del administrador
    num_ships = len(admin_config["ships"])
    game = Game(
        board_size=admin_config["board_size"],
        max_ships=num_ships,
        max_ships_length_ratio=0.7
    )
    
    # Agregar los 2 jugadores
    player_1 = players[game_data.player_1_id]
    player_2 = players[game_data.player_2_id]
    
    game.add_player(player_1)
    game.add_player(player_2)
    
    # Usar string como clave para game_id
    game_id_str = str(game.id)
    games[game_id_str] = game
    
    return {
        "game_id": game_id_str,
        "board_size": game.board_size,
        "player_1": {"id": player_1.id, "name": player_1.name},
        "player_2": {"id": player_2.id, "name": player_2.name},
        "ships_config": admin_config["ships"]
    }

@router.post("/partidas/{game_id}/unirse/{player_id}", status_code=status.HTTP_200_OK)
async def join_game(game_id: str, player_id: str):
    """Une a un jugador a una partida existente."""
    if game_id not in games:
        raise HTTPException(status_code=404, detail="Partida no encontrada")
    
    if player_id not in players:
        raise HTTPException(status_code=404, detail="Jugador no encontrado")
    
    game = games[game_id]
    player = players[player_id]
    
    if len(game.players) >= 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La partida ya tiene el número máximo de jugadores"
        )
    
    game.add_player(player)
    return {"message": f"Jugador {player.name} se unió a la partida {game_id}"}


@router.post("/partidas/{game_id}/flota/{player_id}", status_code=status.HTTP_200_OK)
async def place_ships(game_id: str, player_id: str, ships: List[ShipCreate]):
    """Ubica los barcos de un jugador en el tablero."""
    if game_id not in games:
        raise HTTPException(status_code=404, detail="Partida no encontrada")
    
    if player_id not in players:
        raise HTTPException(status_code=404, detail="Jugador no encontrado")
    
    game = games[game_id]
    player = players[player_id]
    
    # Verificar que el jugador pertenece a la partida
    if player.id not in [p.id for p in game.players.values()]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El jugador no pertenece a esta partida"
        )
    
    # Verificar que la partida está en fase de colocación
    if not game.placement_phase:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La fase de colocación de barcos ha terminado"
        )
    
    # Verificar que no se hayan colocado ya los barcos
    if player.fleet:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya has colocado tus barcos"
        )
    
    # Validar la configuración de barcos
    if len(ships) != len(admin_config["ships"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Debes colocar exactamente {len(admin_config['ships'])} barcos"
        )
    
    # Verificar que los nombres de los barcos coincidan con la configuración
    config_ship_names = {ship["name"] for ship in admin_config["ships"]}
    provided_ship_names = {ship.name for ship in ships}
    
    if config_ship_names != provided_ship_names:
        missing = config_ship_names - provided_ship_names
        extra = provided_ship_names - config_ship_names
        error_msg = []
        if missing:
            error_msg.append(f"Faltan barcos: {', '.join(missing)}")
        if extra:
            error_msg.append(f"Barcos no reconocidos: {', '.join(extra)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=". ".join(error_msg)
        )
    
    try:
        # Crear y colocar cada barco
        for ship_data in ships:
            # Buscar la configuración del barco
            ship_config = next(
                s for s in admin_config["ships"] 
                if s["name"] == ship_data.name
            )
            
            # Crear el barco
            ship = ShipNode(
                name=ship_data.name,
                size=ship_config["size"],
                orientation=ship_data.orientation
            )
            
            # Calcular las coordenadas del barco
            coordinates = []
            if ship_data.orientation == ShipOrientation.HORIZONTAL:
                for i in range(ship.size):
                    coordinates.append(Coordinate(
                        row=ship_data.start_row,
                        col=ship_data.start_col + i
                    ))
            else:  # VERTICAL
                for i in range(ship.size):
                    coordinates.append(Coordinate(
                        row=ship_data.start_row + i,
                        col=ship_data.start_col
                    ))
            
            # Asignar coordenadas al barco
            ship.coordinates = coordinates
            
            # Añadir el barco a la flota del jugador
            player.add_ship(ship)
        
        # Verificar que todos los barcos son válidos
        game.validate_ship_placement(player.id)
        
        # Marcar al jugador como listo si ambos jugadores han colocado sus barcos
        player.is_ready = True
        all_players_ready = all(p.is_ready for p in game.players.values())
        
        # Si todos los jugadores están listos, comenzar el juego
        if all_players_ready:
            game.start_game()
        
        return {
            "message": "Barcos colocados exitosamente",
            "player_ready": True,
            "game_started": all_players_ready
        }
        
    except ValueError as e:
        # Si hay algún error, limpiar la flota del jugador
        player.fleet = []
        player.is_ready = False
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/partidas/{game_id}/disparo", status_code=status.HTTP_200_OK)
async def take_shot(game_id: str, shot: ShotCreate):
    """Realiza un disparo en el tablero del oponente."""
    if game_id not in games:
        raise HTTPException(status_code=404, detail="Partida no encontrada")
    
    game = games[game_id]
    
    # Verificar que el jugador exista
    if shot.player_id not in players:
        raise HTTPException(status_code=404, detail="Jugador no encontrado")
    
    player = players[shot.player_id]
    
    # Verificar que el jugador sea parte de la partida
    if player.id not in [p.id for p in game.players.values()]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El jugador no pertenece a esta partida"
        )
    
    # Verificar que sea el turno del jugador
    if not game.is_players_turn(player.id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No es tu turno"
        )
    
    # Realizar el disparo
    try:
        result = game.take_shot(player.id, shot.row, shot.col)
        return {
            "result": result["result"].value,
            "ship_sunk": result.get("ship_sunk"),
            "game_over": result.get("game_over", False),
            "winner": result.get("winner")
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/partidas/{game_id}/estado/{player_id}", status_code=status.HTTP_200_OK)
async def get_game_state(game_id: str, player_id: str):
    """Obtiene el estado actual del juego para un jugador."""
    if game_id not in games:
        raise HTTPException(status_code=404, detail="Partida no encontrada")
    
    if player_id not in players:
        raise HTTPException(status_code=404, detail="Jugador no encontrado")
    
    game = games[game_id]
    player = players[player_id]
    
    # Verificar que el jugador sea parte de la partida
    if player.id not in [p.id for p in game.players.values()]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El jugador no pertenece a esta partida"
        )
    
    # Obtener estado del juego
    state = game.get_game_state(player.id)
    return {
        "game_id": game_id,
        "player_id": player.id,
        "player_name": player.name,
        "current_turn": str(game.current_turn) if game.current_turn else None,
        "game_state": game.state.value,
        "winner": str(game.winner_id) if game.winner_id else None,
        "board_size": game.board_size,
        "ships_remaining": len([s for s in player.fleet if not s.is_sunk]),
        "total_ships": len(player.fleet)
    }
