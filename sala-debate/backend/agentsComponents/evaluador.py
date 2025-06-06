# ia_module.py
from agentscope import init
from agentscope.agents import DictDialogAgent
from agentscope.parsers import MarkdownJsonDictParser
from agentscope.message import Msg
import os
import ast

base_dir = os.path.dirname(os.path.abspath(__file__))
model_config_path = os.path.join(base_dir, "configs", "model_configs.json")

init(
    model_configs=model_config_path,
    project="prueba cde calidad"
)

charles = DictDialogAgent(
    name="Charles",
    model_config_name="gpt-4",
    sys_prompt=(
        "Eres un analista experto en detectar baja calidad argumentativa. "
        "Evalúas mensajes en busca de falta de lógica, evidencia o claridad. "
        "Responde solo si detectas baja calidad en el mensaje reciente."
        "SIEMPRE debes entregar la evaluacion, respuesta e intervencion en formato Json"
    )
)

parser1 = MarkdownJsonDictParser(
    content_hint={
        "evaluacion": "breve juicio de calidad del argumento",
        "respuesta": "respuesta si hay baja calidad, responde None en caso que no debas intervenir",
        "intervencion": "true si decides intervenir, false en caso contrario (tipo booleano)"
    },
    keys_to_metadata="intervencion",
    required_keys=["evaluacion","respuesta", "intervencion"],
)
charles.set_parser(parser1)

# Almacena historial
historiales = {}

def analizar_argumento(room, user_input, user_name):
    if room not in historiales:
        historiales[room] = []

    msg = Msg(user_name, user_input, "user")
    historiales[room].append(msg)

    respuesta = charles(historiales[room])
    parsed = ast.literal_eval(respuesta.content)

    return {
        "evaluacion": parsed["evaluacion"],
        "respuesta": parsed["respuesta"],
        "intervencion": respuesta.metadata,
        "agente": charles.name,
        "evaluado": user_name 
    }