# Фреймворк UI-автотестирования `udacha-market.ru`

Проект автоматизированного тестирования UI на базе **Python + Playwright (sync API) + pytest + allure-pytest + Faker** для интернет-магазина **Караван Удачи** (`https://www.udacha-market.ru`, раздел каталога [`/catalog/napolnye_pokrytiya/linoleum/`](https://www.udacha-market.ru/catalog/napolnye_pokrytiya/linoleum/)).

## Замена сайта согласно ТЗ (§01)

Первоначально рассматривавшийся сайт `https://www.electra.ru/catalog/Lyustry_Reluce/1434820/` был заменён на `udacha-market.ru` в полном соответствии с разделом `01 / Выбор сайта` ТЗ:
- на `electra.ru` регистрация закрыта только для ИП/юрлиц с ручной модерацией менеджера и защищена Yandex SmartCaptcha;
- без одобренного B2B-аккаунта на `electra.ru` отсутствует возможность входа и добавления товара в корзину.

На `udacha-market.ru` открыта самостоятельная регистрация, на страницах `/auth/` и `/order/` отсутствует CAPTCHA, а каталог «Линолеум» позволяет пройти полный сквозной путь до оформления заказа.

## Архитектура проекта

```text
autotests/
├── core/
│   ├── config.py           # Чтение конфигурации и секретов из .env / переменных окружения
│   ├── masking.py          # Единая фильтрация и маскирование паролей, email, телефонов, токенов
│   ├── logger.py           # Логгер (DEBUG, INFO, WARNING, ERROR) в консоль и logs/test.log
│   ├── browser.py          # Запуск Playwright Browser и изолированного BrowserContext на тест
│   └── data/
│       ├── auth_cases.py   # Параметризованные негативные наборы авторизации (Faker)
│       └── order_data.py   # Эталонные данные товара и генератор контактов покупателя
├── ui/
│   ├── base_element.py     # Обёртка над Playwright Locator (auto-wait, скролл, безопасное логирование)
│   ├── base_page.py        # Базовая страница (навигация, поиск в шапке, статус сессии, logout)
│   └── pages/
│       ├── login_page.py   # Страница авторизации /auth/
│       ├── catalog_page.py # Каталог и результаты поиска
│       ├── product_page.py # Карточка товара
│       ├── cart_page.py    # Корзина /basket/
│       └── checkout_page.py# Оформление заказа /order/
├── autotest/
│   ├── conftest.py         # Фикстуры сессии/изоляции + Allure-хук скриншота и лога при падении
│   ├── test_auth_positive.py # Позитивные проверки авторизации (до 2 способов: логин/email, телефон)
│   ├── test_auth_negative.py # 7 параметризованных негативных проверок по классам ошибок
│   └── test_e2e_purchase.py  # Сквозной сценарий: вход -> поиск -> карточка -> корзина -> оформление
├── requirements.txt        # Зафиксированные версии зависимостей
├── pytest.ini              # Конфигурация pytest и --alluredir=allure-results
└── .env.example            # Шаблон переменных окружения без секретов
```

## Установка и настройка с нуля

1. Перейти в папку проекта:
   ```bash
   cd autotests
   ```
2. Создать виртуальное окружение и установить зависимости:
   ```bash
   python3 -m venv .venv
   .venv/bin/pip install -r requirements.txt
   ```
3. Браузер Playwright:
   - Если используется системный Chromium (`/usr/bin/chromium`), укажите `BROWSER_EXECUTABLE_PATH=/usr/bin/chromium` в `.env`.
   - Либо установите встроенный Chromium Playwright и оставьте `BROWSER_EXECUTABLE_PATH=` пустым:
     ```bash
     .venv/bin/playwright install chromium
     ```
4. Создайте `.env` на основе `.env.example` и заполните учётные данные:
   ```bash
   cp .env.example .env
   ```
   Обязательно укажите `AUTH_LOGIN` и `AUTH_PASSWORD` вашего аккаунта на `udacha-market.ru` (а также `AUTH_PHONE`, если используется второй способ входа по номеру телефона).  
   Для полного создания заказа в конце e2e установите `E2E_SUBMIT_ORDER=true` (по умолчанию `false` — форма полностью заполняется и проверяется готовность кнопки «Оформить заказ» без создания реального заказа).

## Запуск тестов и генерация отчёта Allure

Запуск всех тестов (включая позитивные, негативные и сквозной сценарий):
```bash
.venv/bin/pytest -v --alluredir=allure-results
```

Запуск только проверок авторизации или только сквозного сценария:
```bash
.venv/bin/pytest -m auth -v --alluredir=allure-results
.venv/bin/pytest -m e2e -v --alluredir=allure-results
```

Генерация и просмотр отчёта Allure (требуется установленный [Allure Commandline](https://allurereport.org/docs/install/)):
```bash
allure serve allure-results
# или сборка статического отчёта:
allure generate allure-results -o allure-report --clean
```

## Состав проверок авторизации (9 суммарно, строго ≤ 10)

| ID кейса | Тип | Класс / описание | Ожидаемый результат |
|---|---|---|---|
| `AUTH-POS-01` | Позитивный | Основной вход (`AUTH_LOGIN` + `AUTH_PASSWORD`) | Переход с `/auth/`, подтверждение сессии в `/personal/` и шапке, затем `logout` |
| `AUTH-POS-02` | Позитивный | Вход по телефону (`AUTH_PHONE` + `AUTH_PASSWORD`) | Выполняется, если задан `AUTH_PHONE`; иначе `skip` |
| `AUTH-NEG-01` | Негативный | Пустой идентификатор (`""`) | Клиентская ошибка `Заполните это поле`, пользователь гость |
| `AUTH-NEG-02` | Негативный | Пустой пароль (`""`) | Клиентская ошибка `Заполните это поле`, пользователь гость |
| `AUTH-NEG-03` | Негативный | Некорректный формат логина (`invalid@@format login!`) | Серверная ошибка `Неверный логин или пароль`, пользователь гость |
| `AUTH-NEG-04` | Негативный | Несуществующий email (генерируется Faker) | Серверная ошибка `Неверный логин или пароль`, пользователь гость |
| `AUTH-NEG-05` | Негативный | Несуществующий телефон (генерируется Faker) | Серверная ошибка `Неверный логин или пароль`, пользователь гость |
| `AUTH-NEG-06` | Негативный | Неверный пароль | Серверная ошибка `Неверный логин или пароль`, пользователь гость |
| `AUTH-NEG-07` | Негативный | Неверный регистр пароля | Серверная ошибка `Неверный логин или пароль`, пользователь гость |

## Обоснование ключевых локаторов

Все локаторы подобраны вручную по семантическим идентификаторам и атрибутам `data-entity` шаблона Bitrix/Aspro без использования автогенерируемых путей DevTools:

| Экран | Элемент | Локатор | Почему выбран |
|---|---|---|---|
| Авторизация `/auth/` | Форма входа | `#auth-page-form` | Уникальный ID формы авторизации |
| Авторизация `/auth/` | Поля логина и пароля | `#USER_LOGIN_POPUP`, `#USER_PASSWORD_POPUP` | Уникальные стабильные ID полей ввода |
| Авторизация `/auth/` | Кнопка «Войти» | `#auth-page-form button[type='submit'][name='Login1']` | Ограничена формой входа и функциональным именем кнопки |
| Авторизация `/auth/` | Ошибки валидации | `#auth-page-form label.error:visible`, `.alert-danger:visible, font.errortext:visible` | Разделение клиентских подсказок jQuery Validate и серверных алертов Bitrix |
| Шапка / Поиск | Строка поиска | `#title-search-input` | Уникальный ID десктопного поиска |
| Каталог / Поиск | Карточка результата | `.catalog_item_wrapp .item-title a:has-text('...')` | Связка контейнера карточки и ссылки наименования |
| Карточка товара | Артикул, цена, корзина | `.catalog_detail .article:visible`, `.catalog_detail .price[data-value]:visible`, `.catalog_detail .to-cart:visible`, `.catalog_detail a.in-cart` | Семантические классы карточки и атрибут `data-value` цены |
| Корзина `/basket/` | Позиции и итог | `#basket-item-table tr[data-entity='basket-item']`, `input[data-entity='basket-item-quantity-field']`, `[data-entity='basket-total-price']:visible`, `[data-entity='basket-checkout-button']:visible` | Стандартные семантические `data-entity`-атрибуты компонента `sale.basket.basket` |
| Оформление `/order/` | Поля, оплата, согласия | `#bx-soa-delivery`, `#bx-soa-paysystem`, `#soa-property-1..3`, `#licenses_order`, `#offer_order`, `#bx-soa-order a[data-save-button='true']:visible` | Стабильные ID секций, свойств заказа и атрибут сохранения Bitrix SOA |

## Допущения и ограничения стенда

- Авторизованные проверки (`AUTH-POS-01`, `AUTH-POS-02`, `test_e2e_purchase`) требуют заполненных `AUTH_LOGIN` и `AUTH_PASSWORD` в `.env`.
- На живом стенде при оформлении заказа выбраны безопасные параметры «Самовывоз» и «Наложенный платеж», чтобы не вызывать сторонний платёжный шлюз.
- Выход `allure serve` / `allure generate` в HTML требует наличия установленной утилиты `allure` CLI (при отсутствии CLI все результаты и вложения сохраняются в `allure-results/`).
