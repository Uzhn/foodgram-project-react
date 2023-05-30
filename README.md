![Workflow](https://github.com/uzhn/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)
# Foodgram - Ваш продуктовый помощник!
---
Проект foodgram «Продуктовый помощник»: сайт, на котором пользователи будут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Сервис «Список покупок» позволит пользователям создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

## Шаблон наполнения env-файла
```
DB_ENGINE=django.db.backends.postgresql указываем, что работаем с postgresql
DB_NAME=postgres имя базы данных (установите свой)
POSTGRES_USER=postgres логин для подключения к базе данных (установите свой)
POSTGRES_PASSWORD=postgres пароль для подключения к БД (установите свой)
DB_HOST=db название сервиса (контейнера)
DB_PORT=5432 порт для подключения к БД
```

## Описание команды для запуска приложения в контейнерах

__Пересобрать контейнеры и запустить их__

```
docker-compose up -d --build
```

## Описание команды для заполнения базы данными

__Выполнить миграции в контейнере__

```
docker-compose exec web python manage.py migrate
```

__Создать суперпользователя__

```
docker-compose exec web python manage.py createsuperuser
```

__Собрать статику__

```
docker-compose exec web python manage.py collectstatic --no-input 
```

__По этой ссылке вы можете ознакомиться с проектом__


http://158.160.63.1/


__Административная панель__


http://51.250.29.11/admin/


__Документация__

http://51.250.29.11/api/docs/