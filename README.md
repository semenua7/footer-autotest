[![CI - Footer Autotest](https://github.com/USER/only-footer-autotest/actions/workflows/ci.yml/badge.svg)](https://github.com/USER/only-footer-autotest/actions/workflows/ci.yml)


# Only Digital — Footer Autotest (pytest + Selenium)

Проверяет наличие **футера** и ключевых элементов внутри него на нескольких страницах `https://only.digital/`.

## Что проверяем
- Футер присутствует на странице (`<footer>` / `[role="contentinfo"]` / id/class со словом `footer`).
- Во футере есть хотя бы **одна ссылка** (`<a>`).
- Текст футера не пустой (≥ 20 символов).
- Найдена **политика/конфиденциальность** (по тексту/ссылке `policy|privacy|confidential|Политик`), *или* раздел `Контакты/Contact`.
- Найдена хотя бы одна **социальная ссылка** (`vk|t.me|telegram|instagram|linkedin|youtube`) *или* контакт (`mailto:`, `tel:`).

> Тест **ничего не отправляет**, формы не трогает, капчу не обходит.

## Быстрый старт

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Запуск (по умолчанию берутся до 5 страниц с главной):
pytest -v

# Прогнать только главную страницу:
BASE_URL=https://only.digital pytest -v -k test_footer_present

# Явно задать страницы через переменную окружения (через запятую):
PAGES="https://only.digital,https://only.digital/services,https://only.digital/cases" pytest -v
```

## Структура
```
.
├── README.md
├── requirements.txt
├── pytest.ini
├── conftest.py
└── tests
    └── test_footer.py
```

## Примечания
- По умолчанию берём до **5 внутренних ссылок** с главной страницы (GET-запросом), чтобы минимально нагружать сайт.
- Браузер запускается **в headless-режиме**.
- URL-адреса можно переопределить переменной окружения `PAGES`.



## GitHub Actions (CI)
В репозитории есть workflow `.github/workflows/ci.yml`:
- ставит Python 3.11,
- устанавливает зависимости,
- запускает pytest в headless-режиме,
- сохраняет HTML-отчёт как artifact.

После `git push` на ветку `main`/`master` зайдите во вкладку **Actions** и скачайте артефакт `pytest-html-report`.

## Опции запуска
- Переопределить список страниц:
  ```bash
  PAGES="https://only.digital,https://only.digital/services" pytest -v
  ```
- Указать базовый URL:
  ```bash
  BASE_URL=https://only.digital pytest -v
  ```
Отчёт сохранится в `reports/report.html` (локально) и как artifact в CI.



## Скриншоты при падении
При любом падении теста автоматически сохраняется скриншот в `reports/screenshots/failed_<page>.png`.
В CI (GitHub Actions) папка со скриншотами поднимается как artifact `pytest-screenshots`.
