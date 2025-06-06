from agentscope import init
from agentscope.agents import DictDialogAgent
from agentscope.parsers import MarkdownJsonDictParser
from agentscope.message import Msg
from agentscope.msghub import msghub
import os 
import json  
import ast

SYS_PROMPT = """
puedes designar a un agente miembro para que responda, si eres el analista podras tagear al experto para que responda, y si eres el experto sabras que te tagean con @.
ESto significa que puedes incluir el simbolo @ en tu mensake seguido del nombre de la persona, dejando un espacio despues del nombre
Tods los participantes son: {agent_names}
"""
#ruta absoluta en donde esta el script.
base_dir = os.path.dirname(os.path.abspath(__file__))

model_config_path = os.path.join(base_dir,"configs","model_configs.json")

init(
    model_configs=model_config_path,
    project="prueba cde calidad"
    )

analista = DictDialogAgent(
    name = "analista",
    model_config_name = "gpt-4",
    sys_prompt=(
        "Eres un analista experto en detectar baja calidad argumentativa. "
        "Evalúas mensajes en busca de falta de lógica, evidencia o claridad. "
        "si identificas este patron deberas decirle al experto que intervenga 'tageandolo' con @."
    ) 
)

parser_analista = MarkdownJsonDictParser(
    content_hint={
        "evaluacion":"breve juicio de calidad del argumento",
        "intervencion":"true si decides intervenir, false en caso contrario (tipo booleano)"
    },
    keys_to_metadata="intervencion",
    required_keys=["evaluacion","intervencion"],
)
analista.set_parser(parser_analista)

experto = DictDialogAgent(
    name="Experto",
    model_config_name = "gpt-4",
    sys_prompt=(
        "eres un experto dedicado a decirle a los participantes como deben dirigir sus argumentos para que la conversacion sea lo mas fructifera posible."
        "usaras el criterio del analista para que el te diga cuando intervenir. "
        "Deberas responder solo cuando el analista te 'tagee' con @ deberas intervenir "
    ) 
)
parser_experto = MarkdownJsonDictParser(
    content_hint={
        "respuesta": "debes dar la respuesta de como hacer que la conversacion sea mas fructifera"
    },
    keys_to_metadata="respuesta",
    required_keys=["respuesta"]
)
experto.set_parser(parser_experto)
agentes = list(analista,experto)
hint  = Msg(
    "host",
    content=SYS_PROMPT.format(
        agent_names=[agent.name for agent in agentes]
    )
)

# Historial de mensajes
historial = []

try:
    with msghub(agentes,announcement=hint):
        while True:
            user_input = input(" Humano: ")
            msg = Msg("Estudiante", user_input, "user")
            historial.append(msg)

            #veamos que dice el analista
            respuesta = analista(historial)
            parsed = ast.literal_eval(respuesta.content)
            if respuesta.metadata is False: 
                print("no se evalua aun")

except KeyboardInterrupt:
    print("\nSesión finalizada.")