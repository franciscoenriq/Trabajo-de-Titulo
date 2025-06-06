from agentscope.agents import BaseAgent
from agentscope.message import Msg
from agentscope.msghub import msghub

class Observador(BaseAgent):
    def __init__(self, name):
        super().__init__(name)
        self.historial = []

    def _react(self, msg: Msg) -> list[Msg]:
        self.historial.append(msg.content)
        print(f"[{self.name}] Recibido: {msg.content}")
        return []  # No responde, solo observa


# Crear el MsgHub
hub = msghub()

# Crear el agente
observador = Observador(name="observador")

# Registrar agente en el hub
hub.add_agent(observador)

# Simular partes de una conversación
mensajes_conversacion = [
    "Creo que el robo puede ser justificado a veces.",
    "Por ejemplo, si tienes que alimentar a tu familia.",
    "Pero también entiendo que hay leyes que lo prohíben.",
    "No sé cuál es el límite ético."
]

# Inyectar mensajes uno a uno
for contenido in mensajes_conversacion:
    hub.inject(Msg(
        sender="usuario",
        receiver="observador",
        content=contenido,
        metadata={"channel": "conversacion"}
    ))

# Ejecutar una ronda por mensaje (para simular flujo gradual)
hub.run(n_round=len(mensajes_conversacion))
