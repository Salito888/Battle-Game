
from typing import Dict, List, Optional
from uuid import UUID
from ..model.Game_model import (
    Game, Player, ShipNode, ShipOrientation, Coordinate, 
    GameState, ShotResult, ShotNode, ShotTree
)

class GameService:
    """
    Servicio que maneja la lógica de negocio del juego Batalla Naval.
    Gestiona la creación de partidas, colocación de barcos y ejecución de disparos.
    """
    
    def __init__(self):
        self.games: Dict[UUID, Game] = {}
        self.players: Dict[str, UUID] = {}  # Mapeo de nombre de jugador a ID de partida
        self._initialize_sample_games()  # Inicializar partidas de ejemplo
    
    
    def _initialize_sample_games(self):
        """Inicializa 5 partidas de ejemplo con diferentes configuraciones.
        
        NOTA: El administrador define los nombres y tamaños de los barcos.
        Los jugadores definen la orientación y coordenadas al colocar su flota.
        Cada partida es para exactamente 2 jugadores.
        """
        # Configuraciones de ejemplo para las 5 partidas
        configs = [

            # Partida 1: Pequeña (8x8, 5 barcos)
            {
                "name": "Partida Pequeña",
                "board_size": 8,
                "max_ships": 5,
                "players": [
                    "Jugador 1",
                    "Jugador 2"
                ],
                "ships": [
                    {"name": "Barco 1", "size": 4, "orientation": "HORIZONTAL", "start_row": 0, "start_col": 0},
                    {"name": "Barco 2", "size": 3, "orientation": "VERTICAL", "start_row": 2, "start_col": 2},
                    {"name": "Barco 3", "size": 3, "orientation": "HORIZONTAL", "start_row": 5, "start_col": 0},
                    {"name": "Barco 4", "size": 2, "orientation": "VERTICAL", "start_row": 1, "start_col": 5},
                    {"name": "Barco 5", "size": 2, "orientation": "HORIZONTAL", "start_row": 6, "start_col": 5}
                ]
            },
            # Partida 2: Mediana (10x10, 5 barcos)
            {
                "name": "Partida Mediana",
                "board_size": 10,
                "max_ships": 5,
                "players": [
                    "Jugador 3",
                    "Jugador 4"
                ],
                "ships": [
                    {"name": "Barco 1", "size": 5, "orientation": "HORIZONTAL", "start_row": 0, "start_col": 0},
                    {"name": "Barco 2", "size": 4, "orientation": "VERTICAL", "start_row": 2, "start_col": 3},
                    {"name": "Barco 3", "size": 3, "orientation": "HORIZONTAL", "start_row": 6, "start_col": 0},
                    {"name": "Barco 4", "size": 3, "orientation": "VERTICAL", "start_row": 1, "start_col": 7},
                    {"name": "Barco 5", "size": 2, "orientation": "HORIZONTAL", "start_row": 8, "start_col": 6}
                ]
            },
            # Partida 3: Grande (12x12, 5 barcos)
            {
                "name": "Partida Grande",
                "board_size": 12,
                "max_ships": 5,
                "players": [
                    "Jugador 5",
                    "Jugador 6"
                ],
                "ships": [
                    {"name": "Barco 1", "size": 5, "orientation": "HORIZONTAL", "start_row": 0, "start_col": 0},
                    {"name": "Barco 2", "size": 4, "orientation": "VERTICAL", "start_row": 2, "start_col": 4},
                    {"name": "Barco 3", "size": 3, "orientation": "HORIZONTAL", "start_row": 7, "start_col": 0},
                    {"name": "Barco 4", "size": 3, "orientation": "VERTICAL", "start_row": 1, "start_col": 9},
                    {"name": "Barco 5", "size": 2, "orientation": "HORIZONTAL", "start_row": 9, "start_col": 8}
                ]
            },
            # Partida 4: Muy Grande (14x14, 5 barcos)
            {
                "name": "Partida Muy Grande",
                "board_size": 14,
                "max_ships": 5,
                "players": [
                    "Jugador 7",
                    "Jugador 8"
                ],
                "ships": [
                    {"name": "Barco 1", "size": 5, "orientation": "HORIZONTAL", "start_row": 0, "start_col": 0},
                    {"name": "Barco 2", "size": 4, "orientation": "VERTICAL", "start_row": 2, "start_col": 5},
                    {"name": "Barco 3", "size": 3, "orientation": "HORIZONTAL", "start_row": 8, "start_col": 0},
                    {"name": "Barco 4", "size": 3, "orientation": "VERTICAL", "start_row": 1, "start_col": 11},
                    {"name": "Barco 5", "size": 2, "orientation": "HORIZONTAL", "start_row": 11, "start_col": 10}
                ]
            },
            # Partida 5: Épica (16x16, 5 barcos)
            {
                "name": "Partida Épica",
                "board_size": 16,
                "max_ships": 5,
                "players": [
                    "Jugador 9",
                    "Jugador 10"
                ],
                "ships": [
                    {"name": "Barco 1", "size": 5, "orientation": "HORIZONTAL", "start_row": 0, "start_col": 0},
                    {"name": "Barco 2", "size": 4, "orientation": "VERTICAL", "start_row": 2, "start_col": 6},
                    {"name": "Barco 3", "size": 3, "orientation": "HORIZONTAL", "start_row": 9, "start_col": 0},
                    {"name": "Barco 4", "size": 3, "orientation": "VERTICAL", "start_row": 1, "start_col": 13},
                    {"name": "Barco 5", "size": 2, "orientation": "HORIZONTAL", "start_row": 13, "start_col": 12}
                ]
            }
        ]
        
        for config in configs:
            try:
                # Crear partida
                game = self.create_game(
                    board_size=config["board_size"],
                    max_ships=config["max_ships"]
                )
                game.name = config["name"]
                
                # Añadir jugadores
                for player_name in config["players"]:
                    self.add_player(game.id, player_name)
                
                # Colocar barcos para cada jugador
                for player in game.players.values():
                    for ship_config in config["ships"]:
                        try:
                            self.place_ship(
                                game_id=game.id,
                                player_id=player.id,
                                **ship_config
                            )
                        except Exception as e:
                            print(f"Error colocando barco: {e}")
                    
                    # Marcar jugador como listo
                    self.ready_player(game.id, player.id)
                
                print(f"Partida creada: {config['name']} (ID: {game.id})")
                
            except Exception as e:
                print(f"Error creando partida {config.get('name', '')}: {str(e)}")
    
    def create_game(self, board_size: int, max_ships: int, max_ships_length_ratio: float = 0.7) -> Game:
        """Crea una nueva partida con la configuración especificada."""
        game = Game(
            board_size=board_size,
            max_ships=max_ships,
            max_ships_length_ratio=max_ships_length_ratio
        )
        self.games[game.id] = game
        return game
    
    def add_player(self, game_id: UUID, player_name: str) -> Player:
        """Añade un jugador a una partida existente."""
        if game_id not in self.games:
            raise ValueError("Partida no encontrada")
            
        game = self.games[game_id]
        
        if len(game.players) >= 2:
            raise ValueError("La partida ya tiene el máximo de jugadores")
        
        if any(p.name.lower() == player_name.lower() for p in game.players.values()):
            raise ValueError("El nombre de jugador ya está en uso")
        
        player = Player(name=player_name)
        game.add_player(player)
        self.players[player_name.lower()] = game_id
        
        if len(game.players) == 1:
            game.current_turn = player.id
        
        return player
    
    def place_ship(self, game_id: UUID, player_id: UUID, ship_name: str, size: int, 
                  orientation: str, start_row: int, start_col: int) -> ShipNode:
        """Coloca un barco en el tablero de un jugador."""
        game = self._get_game(game_id)
        player = self._get_player(game, player_id)
        
        if not game.placement_phase:
            raise ValueError("La fase de colocación de barcos ha terminado")
        
        if len(player.fleet) >= game.max_ships:
            raise ValueError(f"No se pueden colocar más de {game.max_ships} barcos")
        
        ship = ShipNode(
            name=ship_name,
            size=size,
            orientation=ShipOrientation(orientation.upper())
        )
        
        # Validar y colocar el barco
        for i in range(size):
            if orientation.upper() == 'HORIZONTAL':
                row, col = start_row, start_col + i
            else:  # VERTICAL
                row, col = start_row + i, start_col
            
            if not (0 <= row < game.board_size and 0 <= col < game.board_size):
                raise ValueError("El barco se sale de los límites del tablero")
            
            for existing_ship in player.fleet:
                if any(c.row == row and c.col == col for c in existing_ship.coordinates):
                    raise ValueError(f"El barco se superpone con otro barco en ({row}, {col})")
            
            ship.add_coordinate(row, col)
        
        # Verificar límite de longitud total de barcos
        total_length = sum(s.size for s in player.fleet) + size
        max_total_length = game.board_size * game.board_size * game.max_ships_length_ratio
        
        if total_length > max_total_length:
            raise ValueError("La longitud total de los barcos excede el límite permitido")
        
        player.add_ship(ship)
        return ship
    
    def ready_player(self, game_id: UUID, player_id: UUID) -> None:
        """Marca a un jugador como listo para comenzar el juego."""
        game = self._get_game(game_id)
        player = self._get_player(game, player_id)
        
        if not game.placement_phase:
            raise ValueError("El juego ya ha comenzado")
        
        if not player.fleet:
            raise ValueError("Debes colocar al menos un barco antes de estar listo")
        
        player.is_ready = True
        
        if all(p.is_ready for p in game.players.values()):
            game.start_game()
    
    def fire_shot(self, game_id: UUID, attacker_id: UUID, target_row: int, target_col: int) -> dict:
        """Realiza un disparo en la posición especificada."""
        game = self._get_game(game_id)
        
        if game.current_turn != attacker_id:
            raise ValueError("No es tu turno")
        
        attacker, defender = self._get_players(game, attacker_id)
        
        if attacker.shots.find(target_row, target_col) is not None:
            raise ValueError(f"Ya has disparado a la posición ({target_row}, {target_col})")
        
        if not (0 <= target_row < game.board_size and 0 <= target_col < game.board_size):
            raise ValueError("Coordenadas fuera de los límites del tablero")
        
        result = {
            'hit': False,
            'sunk': False,
            'ship_name': None,
            'game_over': False,
            'winner': None
        }
        
        target_ship = next(
            (ship for ship in defender.fleet 
             if any(c.row == target_row and c.col == target_col for c in ship.coordinates)),
            None
        )
        
        if target_ship:
            shot_result = target_ship.receive_shot(target_row, target_col)
            result['hit'] = True
            result['ship_name'] = target_ship.name
            
            if target_ship.is_sunk():
                result['sunk'] = True
                
                if defender.all_ships_sunk():
                    result['game_over'] = True
                    result['winner'] = attacker.name
                    game.state = GameState.FINISHED
                    game.winner_id = attacker.id
        else:
            shot_result = ShotResult.WATER
        
        shot_node = ShotNode(
            coordinate=Coordinate(row=target_row, col=target_col),
            result=shot_result,
            affected_ship=target_ship.name if target_ship else None
        )
        attacker.shots.insert(shot_node)
        
        if not result['game_over']:
            game.next_turn()
        
        return result
    
    def get_game_state(self, game_id: UUID, player_id: UUID) -> dict:
        """Obtiene el estado actual del juego para un jugador."""
        game = self._get_game(game_id)
        player = self._get_player(game, player_id)
        opponent = next(p for p in game.players.values() if p.id != player_id)
        
        return {
            'game_id': str(game_id),
            'player_id': str(player_id),
            'player_name': player.name,
            'board_size': game.board_size,
            'current_turn': str(game.current_turn) if game.current_turn else None,
            'is_my_turn': game.current_turn == player_id,
            'game_state': game.state.value,
            'placement_phase': game.placement_phase,
            'my_ships': self._get_ships_info(player.fleet),
            'my_shots': self._get_shots_info(player.shots),
            'received_shots': self._get_shots_info(opponent.shots),
            'ships_remaining': len([s for s in player.fleet if not s.is_sunk()]),
            'opponent_ships_remaining': len([s for s in opponent.fleet if not s.is_sunk()]),
            'winner': str(game.winner_id) if game.winner_id else None
        }
    
    def _get_game(self, game_id: UUID) -> Game:
        """Obtiene una partida por su ID o lanza una excepción si no existe."""
        if game_id not in self.games:
            raise ValueError("Partida no encontrada")
        return self.games[game_id]
    
    def _get_player(self, game: Game, player_id: UUID) -> Player:
        """Obtiene un jugador por su ID o lanza una excepción si no existe."""
        if player_id not in game.players:
            raise ValueError("Jugador no encontrado en esta partida")
        return game.players[player_id]
    
    def _get_players(self, game: Game, attacker_id: UUID) -> tuple[Player, Player]:
        """Obtiene el atacante y defensor de una partida."""
        attacker = None
        defender = None
        for player in game.players.values():
            if player.id == attacker_id:
                attacker = player
            else:
                defender = player
        return attacker, defender
    
    def _get_ships_info(self, ships: List[ShipNode]) -> List[dict]:
        """Obtiene información de los barcos en formato de diccionario."""
        return [
            {
                'name': ship.name,
                'size': ship.size,
                'hits': ship.hits,
                'sunk': ship.is_sunk(),
                'coordinates': [(c.row, c.col) for c in ship.coordinates]
            }
            for ship in ships
        ]
    
    def _get_shots_info(self, shots: ShotTree) -> List[dict]:
        """Obtiene información de los disparos en formato de diccionario."""
        return [
            {
                'row': shot.coordinate.row,
                'col': shot.coordinate.col,
                'result': shot.result.value,
                'ship': shot.affected_ship
            }
            for shot in shots.get_all()
        ]
    
# Instancia global del servicio
game_service = GameService()