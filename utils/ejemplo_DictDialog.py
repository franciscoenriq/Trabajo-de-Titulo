from agentscope import init 
from agentscope.agents import DictDialogAgent
from agentscope.parsers import MarkdownJsonDictParser
from agentscope.message import Msg
import os 
#ruta absoluta en donde esta el script.
base_dir = os.path.dirname(os.path.abspath(__file__))

model_config_path = os.path.join(base_dir,"configs","model_configs.json")

init(
    model_configs=model_config_path,
    project="prueba con dialogdicagent"
    )

charles = DictDialogAgent(
    name="Charles",
    model_config_name="gpt-4",
    sys_prompt="eres un agente gentil y muy capaz llamado charles",
    max_retries=3, # The maximum number of retries when failing to get a required structured output

)
parser1 = MarkdownJsonDictParser(
    content_hint={
        "pensamiento":"que es lo que piensas",
        "conversacion":"que es lo que vas a decir",
        "decision":"tu decision final, verdadero/falso"
    },
    keys_to_metadata="decision",
    required_keys=["pensamiento","conversacion","decision"],
    
)

charles.set_parser(parser1)
msg1 = charles(Msg("Bob"," ¿ es buena idea ir afuera cuando está lloviendo?","user"))

print(f"metadata:{msg1.metadata}")
print(f"el tipo de la metadata:{type(msg1.metadata)}")