from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID, uuid4
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List

# --- МОДЕЛІ ДЛЯ ГРИ ---

class GameBase(BaseModel):
    model_config = ConfigDict(populate_by_name=True, str_strip_whitespace=True)
    title: str = Field(min_length=1)
    description: Optional[str] = None
    min_players: int = Field(alias="minPlayers", ge=1)
    # rules_config ВИДАЛЕНО

class GameCreate(GameBase):
    pass

class GameResponse(GameBase):
    game_id: UUID = Field(default_factory=uuid4, alias="gameId")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), alias="createdAt")

class GameUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True, str_strip_whitespace=True)
    title: Optional[str] = Field(default=None, min_length=1)
    description: Optional[str] = None
    min_players: Optional[int] = Field(default=None, alias="minPlayers", ge=1)
    # rules_config ВИДАЛЕНО

# --- МОДЕЛІ ДЛЯ СЕСІЇ ---

class SessionCreate(BaseModel):
    game_id: UUID = Field(alias="gameId")

class SessionResponse(BaseModel):
    session_id: UUID = Field(alias="sessionId")
    game_id: UUID = Field(alias="gameId")
    status: str = "active"
    started_at: datetime = Field(alias="startedAt")


# --- СЕРВІС (Бізнес-логіка) ---

class GameService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GameService, cls).__new__(cls)
            cls._instance.games = [] # In-memory storage
        return cls._instance

    def create_game(self, game_data: GameCreate) -> GameResponse:
        new_game = GameResponse(**game_data.model_dump())
        self.games.append(new_game)
        return new_game

    def get_games(self) -> List[GameResponse]:
        return self.games

    def get_game(self, game_id: UUID) -> Optional[GameResponse]:
        return next((game for game in self.games if game.game_id == game_id), None)

    def update_game(self, game_id: UUID, updated_data: GameUpdate) -> Optional[GameResponse]:
        for idx, game in enumerate(self.games):
            if game.game_id == game_id:
                update_dict = updated_data.model_dump(exclude_unset=True)
                updated_game = game.model_copy(update=update_dict)
                self.games[idx] = updated_game
                return updated_game
        return None

    def delete_game(self, game_id: UUID) -> bool:
        for idx, game in enumerate(self.games):
            if game.game_id == game_id:
                del self.games[idx]
                return True
        return False

# Dependency injection
def get_game_service() -> GameService:
    return GameService()