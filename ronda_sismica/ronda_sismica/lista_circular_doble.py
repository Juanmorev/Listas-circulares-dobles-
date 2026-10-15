"""
Estructura de datos: LISTA CIRCULAR DOBLE
-----------------------------------------
Cada nodo tiene dos punteros:
    - next : estación siguiente de la ronda
    - prev : estación anterior de la ronda
y la lista es circular: la última estación apunta a la primera (next) y
la primera apunta a la última (prev).

Caso de estudio: ronda de monitoreo de estaciones sísmicas de un volcán.
"""

from dataclasses import dataclass


@dataclass
class Estacion:
    """Dato que guarda cada nodo de la lista."""
    nombre: str
    altitud: int = 0
    estado: str = "Normal"      # Normal | Alerta | Crítico


class Nodo:
    def __init__(self, data):
        self.data = data
        self.prev = None
        self.next = None


class ListaCircularDoble:
    def __init__(self):
        self.head = None        # primera estación de la lista
        self.actual = None      # estación donde está el guarda ahora mismo
        self.size = 0

    # ------------------------------------------------------------------ #
    #  Inserción
    # ------------------------------------------------------------------ #
    def insertar_inicio(self, data):
        nuevo = Nodo(data)
        if self.head is None:
            nuevo.next = nuevo
            nuevo.prev = nuevo
            self.head = nuevo
            self.actual = nuevo
        else:
            last = self.head.prev
            nuevo.next = self.head
            nuevo.prev = last
            self.head.prev = nuevo
            last.next = nuevo
            self.head = nuevo
        self.size += 1
        return nuevo

    def insertar_final(self, data):
        nuevo = Nodo(data)
        if self.head is None:
            nuevo.next = nuevo
            nuevo.prev = nuevo
            self.head = nuevo
            self.actual = nuevo
        else:
            last = self.head.prev
            last.next = nuevo
            nuevo.prev = last
            nuevo.next = self.head
            self.head.prev = nuevo
        self.size += 1
        return nuevo

    # ------------------------------------------------------------------ #
    #  Búsqueda y eliminación
    # ------------------------------------------------------------------ #
    def buscar(self, nombre):
        """Devuelve el nodo cuyo nombre coincide (sin distinguir mayúsculas)."""
        if self.head is None:
            return None
        nombre = nombre.strip().lower()
        nodo = self.head
        while True:
            if nodo.data.nombre.lower() == nombre:
                return nodo
            nodo = nodo.next
            if nodo is self.head:
                return None

    def eliminar(self, nombre):
        nodo = self.buscar(nombre)
        if nodo is None:
            return False

        if self.size == 1:
            self.head = None
            self.actual = None
        else:
            # re-asignar los punteros de siguiente y anterior
            nodo.prev.next = nodo.next
            nodo.next.prev = nodo.prev
            if nodo is self.head:
                self.head = nodo.next
            if nodo is self.actual:
                self.actual = nodo.next
        self.size -= 1
        return True

    # ------------------------------------------------------------------ #
    #  Movimiento del guarda (recorrido bidireccional)
    # ------------------------------------------------------------------ #
    def avanzar(self):
        if self.actual:
            self.actual = self.actual.next
        return self.actual

    def retroceder(self):
        if self.actual:
            self.actual = self.actual.prev
        return self.actual

    # ------------------------------------------------------------------ #
    #  Recorridos
    # ------------------------------------------------------------------ #
    def nodos(self):
        """Lista de nodos desde head siguiendo next."""
        resultado = []
        if self.head is None:
            return resultado
        nodo = self.head
        while True:
            resultado.append(nodo)
            nodo = nodo.next
            if nodo is self.head:
                break
        return resultado

    def recorrer_adelante(self):
        return [n.data for n in self.nodos()]

    def recorrer_atras(self):
        resultado = []
        if self.head is None:
            return resultado
        nodo = self.head
        while True:
            resultado.append(nodo.data)
            nodo = nodo.prev
            if nodo is self.head:
                break
        return resultado

    # ------------------------------------------------------------------ #
    #  Reversión (más sencilla gracias a los dos punteros)
    # ------------------------------------------------------------------ #
    def invertir(self):
        if self.head is None or self.size == 1:
            return
        nodo = self.head
        while True:
            nodo.next, nodo.prev = nodo.prev, nodo.next
            nodo = nodo.prev            # prev ya es el antiguo next
            if nodo is self.head:
                break
        self.head = self.head.next      # antiguo último nodo

    def __len__(self):
        return self.size
