import pytest
from fastapi.testclient import TestClient
from main import app
from src.models.game import GameService, GameCreate

# Клієнт для тестування API
client = TestClient(app)

# ТЕСТИ ДЛЯ СЕРВІСУ

def test_game_service_create():
    """Тест створення гри безпосередньо через сервіс"""
    service = GameService()
    # Очищуємо список перед тестом
    service.games = [] 
    
    game_data = GameCreate(title="Test Unit", min_players=2)
    created = service.create_game(game_data)
    
    assert created.title == "Test Unit"
    assert len(service.get_games()) == 1

def test_game_service_delete():
    """Тест видалення гри через сервіс"""
    service = GameService()
    game = service.games[0]
    result = service.delete_game(game.game_id)
    assert result is True
    assert len(service.get_games()) == 0

# ТЕСТИ ДЛЯ КОНТРОЛЕРА / API

def test_api_get_games():
    """Перевірка отримання списку ігор через API"""
    response = client.get("/api/games")
    assert response.status_code == 200
    # Має повернути список
    assert isinstance(response.json(), list)

def test_api_create_game_valid():
    """Перевірка створення гри через POST запит"""
    payload = {
        "title": "API Test Game",
        "description": "Testing controller",
        "minPlayers": 1,
        "rulesConfig": {"speed": "fast"}
    }
    response = client.post("/api/games", json=payload)
    assert response.status_code == 201
    assert response.json()["title"] == "API Test Game"

def test_api_validation_error():
    """Перевірка валідації (Вимога Г1) через API"""
    # Пустий заголовок має викликати помилку 422
    payload = {"title": "  ", "minPlayers": 1}
    response = client.post("/api/games", json=payload)
    assert response.status_code == 422