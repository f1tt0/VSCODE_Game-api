import logging
from typing import List
from uuid import UUID, uuid4
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException

# Імпортуємо нові моделі сесій
from src.models.game import (
    GameCreate, GameResponse, GameUpdate, GameService, get_game_service,
    SessionCreate, SessionResponse
)

logger = logging.getLogger(__name__)

router = APIRouter()

# --- ЕНДПОІНТИ ДЛЯ ІГОР ---

@router.post("/games", response_model=GameResponse, status_code=201, description="Створити нову гру", tags=["games"])
def create_game(game: GameCreate, service: GameService = Depends(get_game_service)):
    created_game = service.create_game(game)
    logger.info("Створено нову гру з id %s", created_game.game_id)
    return created_game

@router.get("/games", response_model=List[GameResponse], description="Отримати список всіх ігор", tags=["games"])
def get_games(service: GameService = Depends(get_game_service)):
    return service.get_games()

@router.get("/games/{game_id}", response_model=GameResponse, description="Отримати гру за її ID", tags=["games"])
def get_game(game_id: UUID, service: GameService = Depends(get_game_service)):
    game = service.get_game(game_id)
    if not game:
        logger.error("Гра з id %s не знайдена", game_id)
        raise HTTPException(status_code=404, detail="Game not found")
    return game

@router.put("/games/{game_id}", response_model=GameResponse, description="Оновити дані існуючої гри", tags=["games"])
def update_game(game_id: UUID, game_data: GameUpdate, service: GameService = Depends(get_game_service)):
    game = service.update_game(game_id, game_data)
    if not game:
        logger.error("Спроба оновити неіснуючу гру з id %s", game_id)
        raise HTTPException(status_code=404, detail="Game not found")
    logger.info("Гру з id %s успішно оновлено", game_id)
    return game

@router.delete("/games/{game_id}", status_code=204, description="Видалити гру за її ID", tags=["games"])
def delete_game(game_id: UUID, service: GameService = Depends(get_game_service)):
    deleted = service.delete_game(game_id)
    if not deleted:
        logger.error("Спроба видалити неіснуючу гру з id %s", game_id)
        raise HTTPException(status_code=404, detail="Game not found")
    logger.info("Гру з id %s успішно видалено", game_id)
    return None

# --- ЕНДПОІНТИ ДЛЯ СЕСІЙ ---

# In-memory сховище для сесій
sessions_db = []

@router.post("/sessions/start", response_model=SessionResponse, status_code=201, description="Запустити ігрову сесію", tags=["sessions"])
def start_session(session_in: SessionCreate):
    # Створюємо нову сесію
    new_session = SessionResponse(
        session_id=uuid4(),
        game_id=session_in.game_id,
        status="active",
        started_at=datetime.now(timezone.utc)
    )
    
    # Додаємо до списку
    sessions_db.append(new_session)
    logger.info("Запущено нову сесію %s для гри %s", new_session.session_id, session_in.game_id)
    
    return new_session