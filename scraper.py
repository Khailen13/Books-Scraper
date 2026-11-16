import json
import os
import time
from urllib.parse import urljoin

import requests
import schedule
from bs4 import BeautifulSoup


CATALOGUE_URL = "https://books.toscrape.com/catalogue/page-{page}.html"
HEADERS = {"User-Agent": "Mozilla/5.0 (educational-scraper)"}
OUTPUT_FILE = os.path.join("artifacts", "books_data.txt")


def get_book_data(book_url):
    """Загружает данные одной книги и возвращает в виде словаря.

    book_url — полный адрес страницы книги (например,
    http://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html)

    Возвращает dict с полями:
    title, price, rating, availability, description, product_info.
    """
    r = requests.get(book_url, headers=HEADERS, timeout=10)
    r.raise_for_status()
    soup = BeautifulSoup(r.content, "html.parser")

    main = soup.find("div", class_="product_main")

    rating_p = main.find("p", class_="star-rating")
    rating = rating_p["class"][1] if rating_p else ""

    desc_div = soup.find("div", id="product_description")
    if desc_div:
        description = desc_div.find_next_sibling("p").get_text(strip=True)
    else:
        description = ""

    product_info = {}
    table = soup.find("table", class_="table table-striped")
    if table:
        for row in table.find_all("tr"):
            key = row.find("th").get_text(strip=True)
            val = row.find("td").get_text(strip=True)
            product_info[key] = val

    return {
        "title": main.find("h1").get_text(strip=True),
        "price": main.find("p", class_="price_color").get_text(strip=True),
        "rating": rating,
        "availability": main.find("p", class_="availability").get_text(strip=True),
        "description": description,
        "product_info": product_info,
    }


def scrape_books(is_save=False, output_path=OUTPUT_FILE):
    """Проходит по всем страницам каталога и собирает данные о книгах.

    is_save=True — сохраняет результат в json-файл output_path.
    Возвращает список словарей.
    """
    books = []
    page = 1

    while True:
        url = CATALOGUE_URL.format(page=page)
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code != 200:
            break

        soup = BeautifulSoup(r.content, "html.parser")
        links = soup.select("article.product_pod h3 a")
        if not links:
            break

        for a in links:
            book_url = urljoin(url, a["href"])
            try:
                info = get_book_data(book_url)
                info["url"] = book_url
                books.append(info)
            except Exception as e:
                # не роняем весь парсинг из-за одной книги
                print(f"skip {book_url}: {e}")

        if not soup.find("li", class_="next"):
            break
        page += 1

    if is_save:
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(books, f, ensure_ascii=False, indent=2)
        print(f"Сохранено в файл: {output_path}")

    return books


def run_scheduler():
    """Запускает scrape_books каждый день в 19:00."""
    schedule.every().day.at("19:00").do(scrape_books, is_save=True)

    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    res = scrape_books(is_save=True)
    print(type(res), len(res))
    run_scheduler()
