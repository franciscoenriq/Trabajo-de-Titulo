from agentscope import init
from agentscope.agents import DictDialogAgent
from agentscope.parsers import MarkdownJsonDictParser
from agentscope.message import Msg
import os 
import json  
import ast    
#ruta absoluta en donde esta el script.
base_dir = os.path.dirname(os.path.abspath(__file__))

model_config_path = os.path.join(base_dir,"configs","model_configs.json")

init(
    model_configs=model_config_path,
    project="prueba cde calidad"
    )

charles = DictDialogAgent(
    name = "Charles",
    model_config_name = "gpt-4",
    sys_prompt=(
        "Eres un analista experto en detectar baja calidad argumentativa. "
        "Evalúas mensajes en busca de falta de lógica, evidencia o claridad. "
        "Responde solo si detectas baja calidad en el mensaje reciente."
    ) 
)

parser1 = MarkdownJsonDictParser(
    content_hint={
        "evaluacion":"breve juicio de calidad del argumento",
        "respuesta":"espuesta opcional si hay baja calidad",
        "intervencion":"true si decides intervenir, false en caso contrario (tipo booleano)"
    },
    keys_to_metadata="intervencion",
    required_keys=["evaluacion","intervencion"],
)
charles.set_parser(parser1)

# Historial de mensajes
historial = []

# Bucle de entrada del humano
print("Inicio del análisis. Escribe tus argumentos uno a uno (Ctrl+C para salir).")
try:
    while True:
        user_input = input(" Humano: ")
        msg = Msg("Estudiante", user_input, "user")
        historial.append(msg)

        # El agente analiza todo el historial
        respuesta = charles(historial)
        parsed = ast.literal_eval(respuesta.content)
        print("Evaluación:", parsed["evaluacion"])
        print(respuesta)
        if respuesta.metadata is False: 
            print("no se evalua aun")

except KeyboardInterrupt:
    print("\nSesión finalizada.")