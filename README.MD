# Books Scraper

## Цель

Собрать данные о книгах с сайта [books.toscrape.com](https://books.toscrape.com):
название, цену, рейтинг, наличие, описание и характеристики из таблицы
Product Information. Парсер обходит все страницы каталога, умеет сохранять
результат в файл и запускаться ежедневно по расписанию.

## Запуск

```bash
# 1. Виртуальное окружение и зависимости
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux/macOS
pip install -r requirements.txt

# 2. Разовый парсинг всего каталога (результат -> artifacts/books_data.txt)
python -c "from scraper import scrape_books; r = scrape_books(is_save=True); print(len(r))"

# 3. Ежедневный запуск в 19:00 (бесконечный цикл)
python scraper.py

# 4. Тесты
python -m pytest tests/test_scraper.py -v