import os
import pathlib
import streamlit as st
from functools import lru_cache


class BaseConfig:
    BACKEND_BASE_URL: str = os.getenv("BACKEND_BASE_URL")

    # configuration for streamlit's chat application to interact with LLM
    USER: str = "user"
    ASSISTANT: str = "assistant"
    SYSTEM: str = "system"
    MESSAGES: str = "messages"


class DevelopmentConfig(BaseConfig):
    pass


class ProductionConfig(BaseConfig):
    pass


class TestingConfig(BaseConfig):
    pass


@lru_cache()
def get_settings():
    config_cls_dict = {
        "development": DevelopmentConfig,
        "production": ProductionConfig,
        "testing": TestingConfig
    }

    config_name = os.getenv("FRONTEND_CONFIG", "development")
    config_cls = config_cls_dict[config_name]
    return config_cls()


settings = get_settings()