from agentscope import init
from agentscope.agents import DictDialogAgent
from agentscope.parsers import MarkdownJsonDictParser
from agentscope.message import Msg
from agentscope.msghub import msghub
import os
import ast
import re

# === utils ===
def filter_agents(string, agents):
    if len(agents) == 0:
        return []
    pattern = r"@(" + "|".join(re.escape(agent.name) for agent in agents) + r")\b"
    matches = re.findall(pattern, string)
    agent_dict = {agent.name: agent for agent in agents}
    ordered_agents = [agent_dict[name] for name in matches if name in agent_dict]
    return ordered_agents

# === INIT ===
base_dir = os.path.dirname(os.path.abspath(__file__))
model_config_path = os.path.join(base_dir, "configs", "model_configs.json")

init(model_configs=model_config_path, project="prueba cde calidad")

# === AGENTES ===

analista = DictDialogAgent(
    name="analista",
    model_config_name="gpt-4",
    sys_prompt=(
        "Eres un analista experto en detectar baja calidad argumentativa. "
        "Evalúas mensajes en busca de falta de lógica, evidencia o claridad. "
        "Si identificas estos problemas, debes 'tagear' al experto usando @Experto y explicarle brevemente por qué debe intervenir."
    )
)

parser_analista = MarkdownJsonDictParser(
    content_hint={
        "evaluacion": "breve juicio de calidad del argumento",
        "intervencion": True
    },
    keys_to_metadata="intervencion",
    required_keys=["evaluacion", "intervencion"]
)
analista.set_parser(parser_analista)

experto = DictDialogAgent(
    name="Experto",
    model_config_name="gpt-4",
    sys_prompt=(
        "Eres un experto en mejorar la calidad de los argumentos en una conversación. "
        "Solo intervienes si otro agente te taggea usando @Experto. "
        "Cuando te taggean, responde con sugerencias para mejorar la conversación."
    )
)

parser_experto = MarkdownJsonDictParser(
    content_hint={
        "respuesta": "sugerencia para mejorar la conversación"
    },
    keys_to_metadata="respuesta",
    required_keys=["respuesta"]
)
experto.set_parser(parser_experto)

agentes = [analista, experto]  # <- corregido, no uses list(...) mal usado

SYS_PROMPT = """
Puedes designar a un agente miembro para que responda. Si eres el analista, puedes tagear al experto con @ para que responda.
Los participantes son: {agent_names}
"""
hint = Msg("host", content=SYS_PROMPT.format(agent_names=[agent.name for agent in agentes]),role="system")

# === LOOP DE CONVERSACIÓN ===
historial = []

try:
    with msghub(agentes, announcement=hint):
        while True:
            user_input = input("👤 Humano: ")
            msg = Msg("Estudiante", user_input, role="user")
            historial.append(msg)

            # Paso 1: analista responde
            respuesta_analista = analista(historial)
            historial.append(respuesta_analista)
            print(f"\n🧠 Analista: {respuesta_analista.content}")

            # Paso 2: detectar si se taggeó a alguien
            agentes_taggeados = filter_agents(respuesta_analista.content, agentes)

            # Paso 3: si @Experto fue taggeado, responde
            if experto in agentes_taggeados:
                respuesta_experto = experto(historial)
                historial.append(respuesta_experto)
                print(f"\n🎓 Experto: {respuesta_experto.content}")
            else:
                print("✅ No se taggeó a ningún agente.")

except KeyboardInterrupt:
    print("\n🛑 Sesión finalizada.")
