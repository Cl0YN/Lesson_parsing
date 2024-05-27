import aiohttp
import asyncio
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import collections
import nest_asyncio

nest_asyncio.apply()  # Применяем патч для совместимости

# Начальная и целевая статьи
start_url = "https://en.wikipedia.org/wiki/2007%E2%80%9308_Scottish_League_Cup"
target_url = "https://en.wikipedia.org/wiki/Philosophy"

# Асинхронная функция для получения HTML страницы
async def fetch(session, url):
    try:
        async with session.get(url, ssl=False) as response:
            if response.status == 200:
                return await response.text()
            else:
                return None
    except Exception as e:
        return None

# Асинхронная функция для извлечения ссылок
async def extract_links(html, base_url):
    if not html:
        return []

    soup = BeautifulSoup(html, 'html.parser')
    links = [urljoin(base_url, a.get('href')) for a in soup.find_all('a', href=True)]
    links = [link for link in links if urlparse(link).netloc == 'en.wikipedia.org']
    return links

# Функция для поиска кратчайшего пути между статьями
async def find_shortest_path(start_url, target_url):
    async with aiohttp.ClientSession() as session:  # Создаем сессию и гарантируем ее закрытие
        queue = collections.deque([(start_url, 0, [start_url])])
        visited = set()  # множество посещенных URL

        while queue:
            current_url, depth, path = queue.popleft()
            if current_url in visited:
                continue

            visited.add(current_url)  # Добавляем элемент в множество

            # Получаем HTML текущей страницы
            html = await fetch(session, current_url)
            if html is None:
                continue

            # Извлекаем ссылки
            links = await extract_links(html, current_url)

            # Проверяем, достигнута ли целевая статья
            if target_url in links:
                return depth + 1, path + [target_url]  # возвращаем глубину и путь

            # Добавляем новые ссылки в очередь
            for link in links:
                if link not in visited:
                    queue.append((link, depth + 1, path + [link]))
                else:
                    print("Путь не найден")

async def main():
    shortest_path = await find_shortest_path(start_url, target_url)
    if shortest_path:
        print(f"Найден путь длиной {shortest_path[0]} между статьями:")
        for url in shortest_path[1]:
            print(f"- {url}")
    else:
        print("Путь между статьями не найден.")

if __name__ == '__main__':
    asyncio.run(main())
