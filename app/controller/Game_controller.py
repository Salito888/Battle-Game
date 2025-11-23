
from fastapi import APIRouter, HTTPException, status
from typing import List, Dict, Optional
from uuid import UUID
from pydantic import BaseModel, Field
from app.model.Game_model import Game
from app.model.Game_model import Player
from app.model.Game_model import ShipCreate
from app.model.Game_model import ShipNode, ShotNode, Coordinate, ShotResult, GameState

router = APIRouter()

# Almacenamiento en memoria (en producción, usar una base de datos)
# Claves: strings de UUID (tal como tenías)
games: Dict[str, Game] = {}
players: Dict[str, Player] = {}
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


class ShotCreate(BaseModel):
    # recibimos player_id como string (Postman envía strings)
    player_id: str
    row: int = Field(..., ge=0, description="Row coordinate (0-based)")
    col: int = Field(..., ge=0, description="Column coordinate (0-based)")

class GameCreateWithPlayers(BaseModel):
    player_1_id: str = Field(..., description="ID del primer jugador")
    player_2_id: str = Field(..., description="ID del segundo jugador")

# Endpoints
@router.post("/admin/configurar-barcos", status_code=status.HTTP_201_CREATED)
async def configure_ships(config: AdminConfigureShips):
    """El administrador configura el tamaño del tablero y los barcos disponibles."""
    if config.board_size < 5:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Board size must be at least 5")

    # Validar nombres únicos
    ship_names = [ship.name for ship in config.ships]
    if len(ship_names) != len(set(ship_names)):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ship names must be unique")

    # Validar límite del 70% (suma de tamaños no mayor que 70% del tablero total)
    total_ship_length = sum(ship.size for ship in config.ships)
    max_allowed = config.board_size * config.board_size * 0.7
    if total_ship_length > max_allowed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Total ship length ({total_ship_length}) exceeds 70% of board ({max_allowed})"
        )

    admin_config["board_size"] = config.board_size
    admin_config["ships"] = [{"name": ship.name, "size": ship.size} for ship in config.ships]

    return {"message": "Ships configured successfully", "board_size": config.board_size, "ships": admin_config["ships"]}


@router.post("/jugadores", status_code=status.HTTP_201_CREATED)
async def create_player(player_data: PlayerCreate):
    """Crea un nuevo jugador con un nombre único."""
    # Verificar si el nombre ya existe
    if any(p.name == player_data.name for p in players.values()):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Player name already exists")

    player = Player(name=player_data.name)
    players[str(player.id)] = player
    return {"player_id": str(player.id), "name": player.name}


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
    if not admin_config["board_size"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El administrador debe configurar los barcos primero")

    # Verificar que ambos jugadores existan (players keys son strings)
    if game_data.player_1_id not in players:
        raise HTTPException(status_code=404, detail="Jugador 1 no encontrado")
    if game_data.player_2_id not in players:
        raise HTTPException(status_code=404, detail="Jugador 2 no encontrado")
    if game_data.player_1_id == game_data.player_2_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El Jugador 1 y el Jugador 2 deben ser diferentes")

    num_ships = len(admin_config["ships"])
    game = Game(board_size=admin_config["board_size"], max_ships=num_ships, max_ships_length_ratio=0.7)

    # Agregar los 2 jugadores (Player objetos, ya guardados en players por create_player)
    player_1 = players[game_data.player_1_id]
    player_2 = players[game_data.player_2_id]

    game.add_player(player_1)
    game.add_player(player_2)

    game_id_str = str(game.id)
    games[game_id_str] = game

    return {
        "game_id": game_id_str,
        "board_size": game.board_size,
        "player_1": {"id": str(player_1.id), "name": player_1.name},
        "player_2": {"id": str(player_2.id), "name": player_2.name},
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
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La partida ya tiene el número máximo de jugadores")

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
    if str(player.id) not in list(game.players.keys()):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El jugador no pertenece a esta partida")

    # Verificar que la partida está en fase de colocación
    if not game.placement_phase:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La fase de colocación de barcos ha terminado")

    # Verificar que no se hayan colocado ya los barcos
    if player.fleet:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ya has colocado tus barcos")

    # Validar la configuración de barcos
    if len(ships) != len(admin_config["ships"]):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Debes colocar exactamente {len(admin_config['ships'])} barcos")

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
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=". ".join(error_msg))

    try:
        # Crear y colocar cada barco usando las coordenadas que envía el cliente
        for ship_data in ships:
            # Buscar la configuración del barco para obtener el tamaño esperado
            ship_config = next(s for s in admin_config["ships"] if s["name"] == ship_data.name)

            # Crear el ShipNode con la orientación correcta
            ship = ShipNode(
                name=ship_data.name,
                size=ship_config["size"],
                orientation=ship_data.orientation
            )

            # Asignar coordenadas desde ship_data.coordinates (esperadas como lista de Coordinate)
            coords: List[Coordinate] = []
            for c in ship_data.coordinates:
                # si vienen como dict, pydantic los convertirá; aquí nos aseguramos de crear Coordinate
                if isinstance(c, Coordinate):
                    coords.append(Coordinate(row=c.row, col=c.col))
                else:
                    coords.append(Coordinate(row=c["row"], col=c["col"]))

            ship.coordinates = coords

            # Añadir el barco a la flota del jugador
            player.add_ship(ship)

        # Verificar que todos los barcos son válidos
        valid = game.validate_ship_placement(str(player.id))
        if not valid:
            # limpiar y reportar
            player.fleet = []
            raise ValueError("Colocación de barcos inválida (superposición, límites o límites de cantidad)")

        # Marcar al jugador como listo
        player.is_ready = True
        all_players_ready = all(p.is_ready for p in game.players.values())

        # Si todos los jugadores están listos, comenzar el juego
        if all_players_ready:
            game.start_game()

        return {"message": "Barcos colocados exitosamente", "player_ready": True, "game_started": all_players_ready}

    except ValueError as e:
        # Si hay algún error, limpiar la flota del jugador
        player.fleet = []
        player.is_ready = False
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/partidas/{game_id}/disparo", status_code=status.HTTP_200_OK)
async def take_shot(game_id: str, shot: ShotCreate):
    """Realiza un disparo en el tablero del oponente."""
    if game_id not in games:
        raise HTTPException(status_code=404, detail="Partida no encontrada")

    game = games[game_id]

    # Verificar que el jugador exista en global players
    if shot.player_id not in players:
        raise HTTPException(status_code=404, detail="Jugador no encontrado")

    attacker = players[shot.player_id]

    # Verificar que el jugador sea parte de la partida
    if str(attacker.id) not in list(game.players.keys()):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El jugador no pertenece a esta partida")

    # Verificar que sea el turno del jugador
    if not game.is_players_turn(attacker.id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No es tu turno")

    # Encontrar defensor
    defender = None
    for pid, p in game.players.items():
        if pid != str(attacker.id):
            defender = p
            break

    if defender is None:
        raise HTTPException(status_code=404, detail="No hay defensor en la partida")

    # Verificar duplicado de disparo
    if attacker.shots.find(shot.row, shot.col) is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Ya has disparado a la posición ({shot.row}, {shot.col})")

    # Validar límites del tablero
    if not (0 <= shot.row < game.board_size and 0 <= shot.col < game.board_size):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Coordenadas fuera de los límites del tablero")

    # Buscar barco en la coordenada objetivo
    target_ship = defender.get_ship_at(shot.row, shot.col)

    result = {
        "result": ShotResult.WATER,
        "ship_sunk": None,
        "game_over": False,
        "winner": None
    }

    if target_ship:
        # receive_shot ya retorna True/False, no necesitas verificar 'hit' después
        hit = target_ship.receive_shot(shot.row, shot.col)
        result["result"] = ShotResult.HIT if hit else ShotResult.WATER
        
        if target_ship.is_sunk:  # Sin paréntesis - es una propiedad
            result["result"] = ShotResult.SUNK
            result["ship_sunk"] = target_ship.name
            
            # Verificar si todos los barcos del defensor están hundidos
            if defender.all_ships_sunk:  # Sin paréntesis - es una propiedad
                result["game_over"] = True
                result["winner"] = str(attacker.id)
                game.state = GameState.FINISHED
                game.winner_id = attacker.id

    else:
        result["result"] = ShotResult.WATER


    # Registrar el disparo
    shot_node = ShotNode(
        coordinate=Coordinate(row=shot.row, col=shot.col),
        result=result["result"],
        affected_ship=target_ship.name if target_ship else None
    )
    attacker.shots.insert(shot_node)

    # Cambiar turno si no terminó el juego
    if not result.get("game_over", False):
        game.next_turn()

    return {
        "result": result["result"].value,
        "ship_sunk": result.get("ship_sunk"),
        "game_over": result.get("game_over", False),
        "winner": result.get("winner")
    }


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
    if str(player.id) not in list(game.players.keys()):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El jugador no pertenece a esta partida")

    state = game.get_game_state(player.id)
    return {
        "game_id": game_id,
        "player_id": str(player.id),
        "player_name": player.name,
        "current_turn": str(game.current_turn) if game.current_turn else None,
        "game_state": game.state.value,
        "winner": str(game.winner_id) if game.winner_id else None,
        "board_size": game.board_size,
        "ships_remaining": len([s for s in player.fleet if not s.is_sunk]),
        "total_ships": len(player.fleet)
    }


