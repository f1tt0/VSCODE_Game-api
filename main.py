from contextlib import asynccontextmanager
from functools import lru_cache
from typing import Annotated
import fastapi as FastAPI
from fastapi import Depends
import logging

from src.api import games
from src.middlewares import error_handler
import config
from src.models.game import GameCreate, get_game_service
import os

# налаштування системи логування
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(name)s: %(message)s"
)

logger = logging.getLogger(__name__)

tags_metadata = [
    {
        "name": "games",
        "description": "Operations with games.",
    },
    {
        "name": "sessions",
        "description": "Operations with game sessions.",
    }
]

@lru_cache
def get_settings():
    return config.Settings()

#Функція Lifespan із заповненням бази
@asynccontextmanager
async def lifespan(app: FastAPI.FastAPI):
    logger.info("Запуск Game API... Ініціалізація ресурсів.")
    
    settings = get_settings()
    
    if settings.TEST_MODE:
        logger.info("TEST_MODE увімкнено. Заповнюємо базу тестовими даними...")
        service = get_game_service()
        
        # Створюємо хардкодні дані (БЕЗ rules_config)
        test_games = [
            GameCreate(title="Chess", description="Класична настільна гра", min_players=2),
            GameCreate(title="Cubs", description="Підкидання кубика", min_players=1),
            GameCreate(title="Casino", description="Кучу фрі-спінов, грай та вигравай", min_players=1)
        ]
        
        for game_data in test_games:
            created_game = service.create_game(game_data)
            logger.info(f"Додано тестовий запис: Гра '{created_game.title}' (ID: {created_game.game_id})")
    
    yield 
    
    logger.info("Зупинка Game API... Очищення ресурсів.")

app = FastAPI.FastAPI(
    title="Game API",
    description="API for game and session management",
    version="1.0.0",
    contact={
        "name": "Oleksandr Miroshnichenko", 
        "email": "sasha.miroshnichenko@outlook.com",
    },
    openapi_tags=tags_metadata,
    lifespan=lifespan
)

app.add_middleware(error_handler.ErrorHandlerMiddleware)
error_handler.setup_exception_handlers(app)

app.include_router(games.router, prefix="/api")

@app.get("/info", tags=["system"])
async def info(settings: Annotated[config.Settings, Depends(get_settings)]):
    return {
        "application_version": settings.APPLICATION_VERSION,
        "test_mode": settings.TEST_MODE
    }

@app.get("/app/info", tags=["system"])
def get_app_info():
    version = os.getenv("APP_VERSION", "Not set")
    return {"status": "ok", "version": version}