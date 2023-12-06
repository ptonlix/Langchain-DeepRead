"""FastAPI app creation, logger configuration and main API routes."""
from langchain_deepread.di import global_injector
from langchain_deepread.launcher import create_app

app = create_app(global_injector)
