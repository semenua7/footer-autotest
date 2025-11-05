# Only Digital — Footer Autotest

Проверка наличия футера и ключевых элементов на странице https://only.digital/

## Что проверяем
1. Существование элемента футера.
2. Наличие логотипа (img/svg) в футере.
3. Наличие хотя бы одной внутренней навигационной ссылки.
4. Наличие контактов (mailto:/tel: или контактный текст).
5. (Мягкая проверка) Ссылки на соцсети — если не найдены, тест не падает, но пишет примечание.

## Технологии
- Python 3.11
- Selenium 4 (Selenium Manager — без ручного драйвера)
- Pytest + pytest-html
- GitHub Actions (headless Chrome)

## Локальный запуск
```bash
python -m venv .venv
# Windows:
. .venv/Scripts/activate
# macOS/Linux:
# source .venv/bin/activate

pip install -r requirements.txt
pytest -v --html=reports/report.html --self-contained-html
