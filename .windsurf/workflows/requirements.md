---
description: API REST Gestión de Batalla Naval.
auto_execution_mode: 1
---

Requerimiento funcional de la API – Juego Batalla Naval

-Nombre del proyecto: API-BatallaNaval
-Tecnología: Python + FastAPI
-Estructura general:

* Rol: Administrador

-El Administrador tiene la función de configurar las reglas iniciales del juego antes de que comiencen las partidas.

Funciones principales:

1. Crear y configurar el tablero de juego, cuyo tamaño es dinámico (por ejemplo, 8x8, 10x10, 12x12, etc.).

2. Crear la flota de barcos disponibles, definiendo:

3. Nombre de cada barco.

4. Tamaño (cantidad de casillas que ocupa).


5. Validar que los barcos creados no superen el 70% del tamaño total del tablero, es decir:

-Si el tablero es de 10x10 (100 casillas), la suma de las longitudes de todos los barcos no puede exceder 7 casillas.

6. Garantizar que los barcos creados puedan caber completamente en el tablero, sin salirse de los límites.

7. Supervisar el inicio de las partidas: sólo puede comenzar una partida cuando ambos jugadores hayan ubicado toda su flota.

8. No participa directamente en el juego (no realiza disparos), pero controla las condiciones globales y las validaciones del sistema.


* Rol: Jugador

-El Jugador participa directamente en la partida de Batalla Naval.

Funciones principales:

1. Registrarse en la API con un nombre único.

2. Recibir el tablero configurado por el Administrador.

3. Ubicar sus barcos en el tablero según las dimensiones y tamaños definidos.

4. Los barcos se almacenan en un árbol N-ario, donde el nodo raíz representa la flota del jugador y los nodos hijos son los barcos.

5. Una vez que el jugador confirma la ubicación de todos sus barcos, no podrá modificarlos, moverlos ni eliminarlos.

6. Realizar disparos por turnos a coordenadas del tablero del oponente.

7. Cada disparo se guarda en un árbol binario de búsqueda (ABB) de coordenadas, que registra si la posición fue “agua”, “impacto” o “hundido”.

8. Consultar su propio tablero y los resultados de los disparos.

9. El jugador gana cuando logra hundir todos los barcos del oponente.


Paquete model → contiene los modelos de dominio.

Paquete service → contiene la lógica de negocio.

Paquete controller → contiene los endpoints REST.


Objetivo

-Desarrollar una API REST que permita gestionar partidas de Batalla Naval entre dos jugadores: registro de jugadores, ubicación de barcos, realización de disparos, almacenamiento de resultados y determinación del ganador. La API debe usar:

-un árbol N-ario para registrar los barcos de cada jugador.

-un árbol binario para registrar las coordenadas de disparo de cada jugador.


* Reglas del juego

Basadas en las reglas estándar de Batalla Naval. 

-El juego es para dos jugadores. 

-Cada jugador dispone de un tablero dinámico.

-Cada jugador coloca su flota de barcos en su tablero, de forma horizontal o vertical, sin superponerse y sin salirse del tablero. 

-Una vez que ambos jugadores han posicionado todos sus barcos, no se permite modificar la ubicación de ningún barco. A partir de ese momento arranca la fase de juego (disparos).

-Los jugadores se turnan para realizar un disparo por turno a una coordenada del oponente (una fila + columna). 

-El oponente informa si la coordenada disparada es un “impacto” (hit) o “agua” (water). 

-Cuando todas las casillas de un barco han sido alcanzadas, se indica que ese barco está “hundido” (sunk). 

-El juego finaliza cuando un jugador ha hundido todos los barcos del otro jugador. Ese jugador es el ganador. 



* Estructuras de datos a usar

Árbol N-ario para barcos:

-Cada jugador tendrá un nodo raíz que representa su flota.

-Cada hijo del nodo raíz representa un barco de ese jugador.

-Dentro de cada nodo-barco se puede almacenar su tamaño, la orientación, las coordenadas ocupadas.


Árbol binario para coordenadas de disparo:

-Cada jugador tendrá un árbol binario de búsqueda (BST) para sus disparos realizados.

-Almacena nodos que representan coordenadas (fila, columna) y el estado del disparo (agua/impacto).

-Permite verificar rápidamente si una coordenada ya fue disparada.



* Modelos principales (paquete model)

-Jugador:

id (string)

nombre (string)

flota (árbol N-ario de barcos)

disparos (árbol binario de coordenadas)


-Barco:

nombre (string) – p.ej., Portaaviones, Acorazado, Submarino, Destructor

tamaño (int)

orientación (enum: HORIZONTAL o VERTICAL)

lista de coordenadas ocupadas por el barco (cada coordenada = fila, columna)


-CoordenadaDisparo:

fila (int)

columna (int)

estado (enum: AGUA, IMPACTO, HUNDIDO)


-Partida:

id (string)

jugadores (lista de 2 jugadores)

turnoActual (referencia al jugador que realiza el turno)

estado (enum: EN_CURSO, FINALIZADA)

ganador (Jugador o none)

bandera ubicaciónCompletada (boolean) para saber cuándo ya los barcos no se pueden modificar y el juego de disparos arranca.



* Reglas específicas para la API

Antes de que comience la fase de disparos, cada jugador debe posicionar todos sus barcos. Sólo cuando ambos jugadores hayan completado su flota, se cambiará la bandera ubicaciónCompletada = true. A partir de ese momento:

-No se permitirán más modificaciones a los barcos (ni agregar, ni mover, ni quitar).

-Los endpoints de “modificar barco” o “mover barco” deberán rechazar la solicitud con error si ubicaciónCompletada = true.


En cada turno:

1. El jugador actual envía una solicitud de disparo a una coordenada del oponente.

2. Si la coordenada ya existe en su árbol de disparos, la API devuelve error “coordenada ya disparada”.

3. La API determina si hay un barco del oponente en esa coordenada.

Si no hay: se marca en el árbol binario como estado = AGUA.

Si sí hay: se marca estado = IMPACTO y se evalúa si ese barco está completamente hundido → si es así, marca estado = HUNDIDO para ese barco.

4. Si el disparo hunde el último barco del oponente, se actualiza estado = FINALIZADA y ganador = jugadorActual.

5. Se cambia el turno al otro jugador (si el juego no finalizó).


-Los endpoints de consulta permitirán ver: estado de la partida, turno actual, listado de disparos realizados por cada jugador (o parte de ellos), listado de barcos con su estado (hundidos/no hundidos).

-Seguridad: cada solicitud de disparo debe validar que es el turno del jugador que realiza la acción.


* Endpoints (paquete controller)

Aquí algunos endpoints a implementar:

-POST /api/jugadores → crear jugador

-POST /api/partidas → crear partida (se asignan dos jugadores)

-POST /api/partida/{id}/flota → cada jugador envía su flota de barcos (ubicación, orientación, tamaño) → hasta completar la flota.

-GET  /api/partidas/{id}/flota/{jugadorId} → consultar flota de un jugador (solo ver barcos y coordenadas)

-POST /api/partidas/{id}/disparo → realizar disparo (se envía jugadorId, fila, columna)

-GET  /api/partidas/{id}/estado → devolver estado de la partida (jugadores, turnoActual, resultado parcial)

-GET  /api/partidas/{id}/ganador → devuelve el ganador si existe


* Validaciones adicionales

-No permitir barcos que salgan del tablero.

-Coordenadas válidas: fila y columna entre 1 y 10 (o 0–9 según convención).

-Una vez que los jugadores completaron su flota, bloquear modificaciones a ésta.

-En el árbol binario de disparos, evitar duplicados de coordenadas.

-Verificar alternancia correcta del turno.

-Manejar situación de finalización de la partida.


Flujo de uso típico

1. Crear dos jugadores.


2. Crear una partida con esos jugadores.


3. Cada jugador posiciona sus barcos (a través del endpoint flota).


4. Cuando ambos jugadores han finalizado la posición de su flota  la API cambia la fase de “ubicación” a “disparos” (flag ubicaciónCompletada = true).


5. Jugador A realiza disparo , la API determina resultado → marca en su árbol binario → cambia turno.


6. Jugador B realiza disparo, la API determina resultado → marca en su árbol binario → cambia turno.


7. Se repite hasta que uno de los jugadores hunde todos los barcos del otro → la API marca ganador y la partida pasa a estado FINALIZADA.


8. Ya no se aceptan más disparos ni movimientos de barcos.