import pytest

from scraper import get_book_data, scrape_books


URL = "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"


@pytest.fixture(scope="module")
def book():
    """Возвращает данные книги по ссылке URL."""
    return get_book_data(URL)


def test_get_book_data_returns_dict(book):
    """Возвращается словарь с нужным набором полей."""
    assert isinstance(book, dict)
    for key in ["title", "price", "rating", "availability",
                "description", "product_info"]:
        assert key in book


def test_title(book):
    """Проверяет совпадение названия книги."""
    assert book["title"] == "A Light in the Attic"


def test_price(book):
    """Цена начинается с £."""
    assert book["price"].startswith("£")


def test_rating(book):
    """Рейтинг — одно из Five..One."""
    assert book["rating"] in ["One", "Two", "Three", "Four", "Five"]


def test_product_info(book):
    """Проверяет наличие UPC в таблице характеристик."""
    info = book["product_info"]
    assert isinstance(info, dict)
    assert "UPC" in info


def test_scrape_books_count(monkeypatch):
    """scrape_books проходит все 50 страниц и отдаёт 1000 книг."""
    fake = {
        "title": "stub",
        "price": "£0.00",
        "rating": "One",
        "availability": "In stock",
        "description": "",
        "product_info": {},
    }
    monkeypatch.setattr("scraper.get_book_data", lambda url: dict(fake))

    books = scrape_books(is_save=False)

    assert isinstance(books, list)
    assert len(books) == 1000
    assert all("url" in b for b in books)
