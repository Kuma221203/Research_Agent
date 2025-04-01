import os
from functools import lru_cache
from dotenv import load_dotenv


class Config:
    PREFIX = "staging"
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def __init__(self):
        pass

class StagingConfig(Config):
    PREFIX = "staging"


class ProductionConfig(Config):
    PREFIX = "prod"
    

def setup_enviroment():
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY not found in enviroment variables.")

    LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")
    if not LANGCHAIN_API_KEY:
        raise ValueError("LANGCHAIN_API_KEY not found in enviroment variables.")
    
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
    if not TAVILY_API_KEY:
        raise ValueError("TAVILY_API_KEY not found in enviroment variables.")

    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
    os.environ["LANGCHAIN_PROJECT"] = "langgraph_tutorial"


@lru_cache()
def get_settings():
    config_cls_dict = {"staging": StagingConfig, "prod": ProductionConfig}
    env_dict = {"staging": ".env.staging", "prod": ".env.prod"}

    config_name = os.getenv("ENV", "staging")
    config_cls = config_cls_dict.get(config_name)
    env_path = os.path.join(Config.BASE_DIR, env_dict.get(config_name))
    print("Load env from ", env_path)
    load_dotenv(env_path)
    
    setup_enviroment()
    return config_cls()

settings = get_settings()
