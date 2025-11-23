
from enum import Enum
from typing import List, Optional, Dict, Any, Set
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID, uuid4


class ShipOrientation(str, Enum):
    HORIZONTAL = "HORIZONTAL"
    VERTICAL = "VERTICAL"


class Coordinate(BaseModel):
    row: int
    col: int
    
    def __hash__(self):
        return hash((self.row, self.col))

    def __eq__(self, other):
        if not isinstance(other, Coordinate):
            return False
        return self.row == other.row and self.col == other.col


class ShipCreate(BaseModel):
    name: str
    size: int
    orientation: ShipOrientation
    coordinates: List[Coordinate]



class GameState(str, Enum):
    IN_PROGRESS = "IN_PROGRESS"
    FINISHED = "FINISHED"



class ShotResult(str, Enum):
    WATER = "WATER"
    HIT = "HIT"
    SUNK = "SUNK"


class ShipNode(BaseModel):
    """Representa un barco en el juego."""
    id: UUID = Field(default_factory=uuid4)
    name: str
    size: int
    orientation: ShipOrientation
    coordinates: List[Coordinate] = Field(default_factory=list)
    hits: int = 0

    @property
    def is_sunk(self) -> bool:
        """Retorna True si el barco ha sido hundido."""
        return self.hits >= self.size

    def add_coordinate(self, row: int, col: int):
        """Añade una coordenada a la posición del barco."""
        self.coordinates.append(Coordinate(row=row, col=col))

    def receive_shot(self, row: int, col: int) -> bool:
        """
        Registra un disparo en este barco.
        Retorna True si fue un impacto, False en caso contrario.
        """
        for coord in self.coordinates:
            if coord.row == row and coord.col == col:
                self.hits += 1
                return True
        return False


class ShotNode:
    """Nodo para el árbol binario de búsqueda de disparos."""
    def __init__(self, coordinate: Coordinate, result: ShotResult, affected_ship: Optional[str] = None):
        self.coordinate = coordinate
        self.result = result
        self.affected_ship = affected_ship
        self.left = None
        self.right = None

    def __lt__(self, other):
        if not isinstance(other, ShotNode):
            return NotImplemented
        return (self.coordinate.row, self.coordinate.col) < (other.coordinate.row, other.coordinate.col)


class ShotTree:
    """Árbol binario de búsqueda para almacenar los disparos de un jugador."""
    def __init__(self):
        self.root = None
        self._nodes = {}

    def insert(self, shot: ShotNode):
        """Inserta un nuevo disparo en el árbol."""
        coord_key = (shot.coordinate.row, shot.coordinate.col)
        if coord_key in self._nodes:
            # Ya existe un disparo en estas coordenadas
            return

        if not self.root:
            self.root = shot
            self._nodes[coord_key] = shot
            return

        current = self.root
        while True:
            if (shot.coordinate.row, shot.coordinate.col) < (current.coordinate.row, current.coordinate.col):
                if not current.left:
                    current.left = shot
                    break
                current = current.left
            else:
                if not current.right:
                    current.right = shot
                    break
                current = current.right
        
        self._nodes[coord_key] = shot

    def find(self, row: int, col: int) -> Optional[ShotNode]:
        """Busca un disparo por sus coordenadas."""
        return self._nodes.get((row, col))

    def get_all(self) -> List[ShotNode]:
        """Retorna todos los disparos en el árbol."""
        return list(self._nodes.values())


class Player(BaseModel):
    """Representa un jugador en el juego."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    id: UUID = Field(default_factory=uuid4)
    name: str
    fleet: List[ShipNode] = Field(default_factory=list)
    shots: ShotTree = Field(default_factory=ShotTree)
    is_ready: bool = False

    def add_ship(self, ship: ShipNode):
        """Añade un barco a la flota del jugador."""
        self.fleet.append(ship)

    def take_shot(self, row: int, col: int, result: ShotResult, affected_ship: str = None) -> ShotNode:
        """Registra un disparo realizado por este jugador."""
        shot = ShotNode(
            coordinate=Coordinate(row=row, col=col),
            result=result,
            affected_ship=affected_ship
        )
        self.shots.insert(shot)
        return shot

    def get_ship_at(self, row: int, col: int) -> Optional[ShipNode]:
        """Encuentra un barco en la coordenada especificada."""
        for ship in self.fleet:
            for coord in ship.coordinates:
                if coord.row == row and coord.col == col:
                    return ship
        return None

    @property
    def sunk_ships_count(self) -> int:
        """Retorna el número de barcos hundidos."""
        return sum(1 for ship in self.fleet if ship.is_sunk)

    @property
    def all_ships_sunk(self) -> bool:
        """Retorna True si todos los barcos están hundidos."""
        return all(ship.is_sunk for ship in self.fleet)


class Game(BaseModel):
    """
    Representa una partida de Batalla Naval gestionada por un administrador.
    
    El administrador es responsable de:
    1. Configuración del juego:
       - Establecer el tamaño del tablero (NxN)
       - Definir configuraciones de barcos (nombres y tamaños)
       - Establecer el número máximo de barcos por jugador
       - Establecer la longitud total máxima de barcos como proporción del tamaño del tablero
    
    2. Supervisión del juego:
       - Validar la colocación de barcos
       - Hacer cumplir las reglas del juego
       - Monitorear el estado del juego
       - Verificar condiciones de victoria
    
    3. Gestión de barcos:
       - Definir nombres y propiedades de los barcos
       - Validar posiciones de los barcos
       - Asegurar que los barcos no se superpongan
       - Rastrear el estado de los barcos (intacto, impactado, hundido)
    
    Los jugadores interactúan con el juego dentro de las restricciones y reglas definidas por el administrador.
    """
    id: UUID = Field(default_factory=uuid4)
    players: Dict[str, Player] = Field(default_factory=dict)  # id_jugador: Jugador
    current_turn: Optional[UUID] = None
    state: GameState = GameState.IN_PROGRESS
    winner_id: Optional[UUID] = None
    board_size: int = Field(..., gt=0, description="Tamaño del tablero de juego (NxN). Debe ser especificado por el administrador del juego.")
    placement_phase: bool = True
    max_ships: int = Field(..., gt=0, description="Número de barcos por jugador. Debe ser especificado por el administrador para cada partida.")
    max_ships_length_ratio: float = Field(default=0.7, description="Longitud total máxima de barcos como proporción del tamaño del tablero (0-1), establecido por el administrador") 

    def __init__(self, **data):
        super().__init__(**data)
        

        if self.board_size <= 0:
            raise ValueError("El tamaño del tablero debe ser mayor que 0")

    def add_player(self, player: Player):
        """Añade un jugador al juego."""
        if len(self.players) >= 2:
            raise ValueError("El juego ya tiene el número máximo de jugadores (2)")
        
        self.players[str(player.id)] = player
        
        # Si es el segundo jugador, comienza el turno del primer jugador
        if len(self.players) == 2 and not self.current_turn:
            self.current_turn = next(iter(self.players.keys()))

    def is_players_turn(self, player_id: UUID) -> bool:
        """Verifica si es el turno del jugador especificado."""
        return str(player_id) == str(self.current_turn)

    def next_turn(self):
        """Avanza al turno del siguiente jugador."""
        if len(self.players) != 2:
            return
            
        player_ids = list(self.players.keys())
        if self.current_turn == player_ids[0]:
            self.current_turn = player_ids[1]
        else:
            self.current_turn = player_ids[0]

    def check_winner(self) -> Optional[Player]:
        """Verifica si hay un ganador y actualiza el estado del juego."""
        for player_id, player in self.players.items():
            if player.all_ships_sunk:
                # El otro jugador es el ganador
                other_player_id = next(id for id in self.players if id != player_id)
                self.winner_id = other_player_id
                self.state = GameState.FINISHED
                return self.players[other_player_id]
        return None

    def get_game_state(self, player_id: UUID) -> Dict[str, Any]:
        """Retorna el estado actual del juego para un jugador específico."""
        player = self.players.get(str(player_id))
        if not player:
            raise ValueError("Player not found in the game")

        # Obtener el otro jugador
        other_player = next((p for p_id, p in self.players.items() if p_id != str(player_id)), None)

        return {
            "game_id": str(self.id),
            "state": self.state,
            "is_your_turn": self.is_players_turn(player_id),
            "your_ships": [{
                "name": ship.name,
                "size": ship.size,
                "is_sunk": ship.is_sunk,
                "hits": ship.hits
            } for ship in player.fleet],
            "your_shots": [{
                "row": shot.coordinate.row,
                "col": shot.coordinate.col,
                "result": shot.result,
                "affected_ship": shot.affected_ship
            } for shot in player.shots.get_all()],
            "opponent_ships_remaining": (
                sum(1 for ship in other_player.fleet if not ship.is_sunk)
                if other_player else 0
            ) if other_player else 0,
            "winner": str(self.winner_id) if self.winner_id else None,
            "placement_phase": self.placement_phase
        }

    def validate_ship_placement(self, player_id: UUID) -> bool:
        """
        Valida que los barcos del jugador cumplan con las reglas del juego:
        1. No exceder el número máximo de barcos
        2. No exceder el porcentaje máximo de área del tablero
        3. No superponerse
        4. Estar dentro de los límites del tablero
        """
        player = self.players.get(str(player_id))
        if not player:
            return False
            
        # Verificar número máximo de barcos
        if len(player.fleet) > self.max_ships:
            return False
            
        # Verificar que la longitud total de los barcos no exceda el máximo permitido
        total_ship_length = sum(ship.size for ship in player.fleet)
        
        # Calcular la longitud máxima permitida de barcos con el 70% del tamaño del tablero
        max_allowed = int(self.board_size * self.max_ships_length_ratio)
        
        if total_ship_length > max_allowed:
            return False
            
        # Verificar superposición de barcos y límites del tablero
        occupied = set()
        for ship in player.fleet:
            for coord in ship.coordinates:
                # Verificar límites del tablero
                if (coord.row < 0 or coord.row >= self.board_size or 
                    coord.col < 0 or coord.col >= self.board_size):
                    return False
                # Verificar superposiciones
                coord_tuple = (coord.row, coord.col)
                if coord_tuple in occupied:
                    return False
                occupied.add(coord_tuple)
                
        return True

    def can_start_game(self) -> bool:
        """
        Verifica si el juego puede comenzar:
        - Debe tener exactamente 2 jugadores
        - Todos los jugadores deben estar listos
        - Todos los barcos deben estar colocados válidamente
        """
        if len(self.players) != 2:
            return False
            
        # Verificar que todos los jugadores estén listos y tengan barcos colocados correctamente
        for player_id in self.players:
            if not self.players[player_id].is_ready:
                return False
            if not self.validate_ship_placement(player_id):
                return False
                
        return True

    def start_game(self):
        """Inicia el juego (finaliza la fase de colocación de barcos)."""
        if not self.can_start_game():
            raise ValueError("No se puede iniciar el juego: no todos los jugadores están listos")
        self.placement_phase = False
