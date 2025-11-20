
#!/bin/bash

# API REST - Batalla Naval
# Comandos CURL para probar la API
# NOTA: Como administrador, personaliza los nombres de barcos y jugadores según necesites

# Base URL
BASE_URL="http://localhost:8000"

echo "=========================================="
echo "API REST - BATALLA NAVAL"
echo "=========================================="

# ==========================================
# 1. ADMINISTRADOR - CONFIGURACIÓN
# ==========================================
echo ""
echo "1. ADMINISTRADOR - Crear Barcos (Admin)"
echo "=========================================="
echo "PERSONALIZA: tamaño del tablero, nombres y tamaños de los 5 barcos"
echo ""
curl -X POST "$BASE_URL/api/admin/configurar-barcos" \
  -H "Content-Type: application/json" \
  -d '{
    "board_size": TAMAÑO_TABLERO,
    "ships": [
      {
        "name": "NOMBRE_BARCO_1",
        "size": TAMAÑO_BARCO_1
      },
      {
        "name": "NOMBRE_BARCO_2",
        "size": TAMAÑO_BARCO_2
      },
      {
        "name": "NOMBRE_BARCO_3",
        "size": TAMAÑO_BARCO_3
      },
      {
        "name": "NOMBRE_BARCO_4",
        "size": TAMAÑO_BARCO_4
      },
      {
        "name": "NOMBRE_BARCO_5",
        "size": TAMAÑO_BARCO_5
      }
    ]
  }'

# ==========================================
# 2. JUGADORES
# ==========================================
echo ""
echo ""
echo "2. JUGADORES - Crear Jugador 1"
echo "=========================================="
echo "PERSONALIZA EL NOMBRE DEL PRIMER JUGADOR"
echo ""
curl -X POST "$BASE_URL/api/jugadores" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "NOMBRE_JUGADOR_1"
  }'

echo ""
echo ""
echo "3. JUGADORES - Crear Jugador 2"
echo "=========================================="
echo "PERSONALIZA EL NOMBRE DEL SEGUNDO JUGADOR"
echo ""
curl -X POST "$BASE_URL/api/jugadores" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "NOMBRE_JUGADOR_2"
  }'

echo ""
echo ""
echo "4. JUGADORES - Listar Jugadores"
echo "=========================================="
curl -X GET "$BASE_URL/api/jugadores" \
  -H "Content-Type: application/json"

# ==========================================
# 3. PARTIDAS
# ==========================================
echo ""
echo ""
echo "5. PARTIDAS - Crear Partida (2 Jugadores)"
echo "=========================================="
echo "Nota: Reemplaza PLAYER_1_ID y PLAYER_2_ID con los IDs obtenidos al crear jugadores"
curl -X POST "$BASE_URL/api/partidas" \
  -H "Content-Type: application/json" \
  -d '{
    "player_1_id": "PLAYER_1_ID",
    "player_2_id": "PLAYER_2_ID"
  }'

echo ""
echo ""
echo "6. PARTIDAS - Colocar Flota - Jugador 1"
echo "=========================================="
echo "EL JUGADOR 1 ACOMODA SUS BARCOS"
echo "Nota: Reemplaza GAME_ID, PLAYER_1_ID, NOMBRE_BARCO_X con los valores correspondientes"
echo "Los nombres deben coincidir con los definidos en el paso 1 (Crear Barcos)"
echo "EL JUGADOR DEFINE: orientación (HORIZONTAL/VERTICAL) y coordenadas de cada barco"
echo ""
curl -X POST "$BASE_URL/api/partidas/GAME_ID/flota/PLAYER_1_ID" \
  -H "Content-Type: application/json" \
  -d '[
    {
      "name": "NOMBRE_BARCO_1",
      "orientation": "HORIZONTAL",
      "coordinates": [
        {"row": 0, "col": 0},
        {"row": 0, "col": 1},
        {"row": 0, "col": 2}
      ]
    },
    {
      "name": "NOMBRE_BARCO_2",
      "orientation": "VERTICAL",
      "coordinates": [
        {"row": 2, "col": 0},
        {"row": 3, "col": 0},
        {"row": 4, "col": 0}
      ]
    },
    {
      "name": "NOMBRE_BARCO_3",
      "orientation": "HORIZONTAL",
      "coordinates": [
        {"row": 7, "col": 0},
        {"row": 7, "col": 1}
      ]
    },
    {
      "name": "NOMBRE_BARCO_4",
      "orientation": "VERTICAL",
      "coordinates": [
        {"row": 2, "col": 5},
        {"row": 3, "col": 5}
      ]
    },
    {
      "name": "NOMBRE_BARCO_5",
      "orientation": "HORIZONTAL",
      "coordinates": [
        {"row": 6, "col": 5},
        {"row": 6, "col": 6}
      ]
    }
  ]'

echo ""
echo ""
echo "7. PARTIDAS - Colocar Flota - Jugador 2"
echo "=========================================="
echo "EL JUGADOR 2 ACOMODA SUS BARCOS"
echo "Nota: Reemplaza GAME_ID, PLAYER_2_ID, NOMBRE_BARCO_X con los valores correspondientes"
echo "Los nombres deben coincidir con los definidos en el paso 1 (Crear Barcos)"
echo "EL JUGADOR DEFINE: orientación (HORIZONTAL/VERTICAL) y coordenadas de cada barco"
echo ""
curl -X POST "$BASE_URL/api/partidas/GAME_ID/flota/PLAYER_2_ID" \
  -H "Content-Type: application/json" \
  -d '[
    {
      "name": "NOMBRE_BARCO_1",
      "orientation": "VERTICAL",
      "coordinates": [
        {"row": 0, "col": 5},
        {"row": 1, "col": 5},
        {"row": 2, "col": 5}
      ]
    },
    {
      "name": "NOMBRE_BARCO_2",
      "orientation": "HORIZONTAL",
      "coordinates": [
        {"row": 6, "col": 2},
        {"row": 6, "col": 3},
        {"row": 6, "col": 4}
      ]
    },
    {
      "name": "NOMBRE_BARCO_3",
      "orientation": "VERTICAL",
      "coordinates": [
        {"row": 1, "col": 8},
        {"row": 2, "col": 8}
      ]
    },
    {
      "name": "NOMBRE_BARCO_4",
      "orientation": "HORIZONTAL",
      "coordinates": [
        {"row": 8, "col": 2},
        {"row": 8, "col": 3}
      ]
    },
    {
      "name": "NOMBRE_BARCO_5",
      "orientation": "VERTICAL",
      "coordinates": [
        {"row": 5, "col": 8},
        {"row": 6, "col": 8}
      ]
    }
  ]'

echo ""
echo ""
echo "8. PARTIDAS - Obtener Estado de Partida"
echo "=========================================="
echo "Nota: Reemplaza GAME_ID con el ID de la partida"
curl -X GET "$BASE_URL/api/partidas/GAME_ID/estado" \
  -H "Content-Type: application/json"

echo ""
echo ""
echo "9. PARTIDAS - Obtener Flota de Jugador"
echo "=========================================="
echo "Nota: Reemplaza GAME_ID y PLAYER_1_ID con los valores correspondientes"
curl -X GET "$BASE_URL/api/partidas/GAME_ID/flota/PLAYER_1_ID" \
  -H "Content-Type: application/json"

# ==========================================
# 4. DISPAROS
# ==========================================
echo ""
echo ""
echo "10. DISPAROS - Realizar Disparo - Jugador 1"
echo "=========================================="
echo "Nota: Reemplaza GAME_ID y PLAYER_1_ID con los valores correspondientes"
curl -X POST "$BASE_URL/api/partidas/GAME_ID/disparo" \
  -H "Content-Type: application/json" \
  -d '{
    "player_id": "PLAYER_1_ID",
    "row": 5,
    "col": 5
  }'

echo ""
echo ""
echo "11. DISPAROS - Realizar Disparo - Jugador 2"
echo "=========================================="
echo "Nota: Reemplaza GAME_ID y PLAYER_2_ID con los valores correspondientes"
curl -X POST "$BASE_URL/api/partidas/GAME_ID/disparo" \
  -H "Content-Type: application/json" \
  -d '{
    "player_id": "PLAYER_2_ID",
    "row": 3,
    "col": 3
  }'

echo ""
echo ""
echo "=========================================="
echo "FIN DE LOS COMANDOS"
echo "=========================================="
