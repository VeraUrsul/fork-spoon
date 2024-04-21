# fork-spoon

![main_fork_spoon_workflow](https://github.com/VeraUrsul/fork-spoon/workflows/Fork-Spoon%20workflow/badge.svg)


![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white) ![Ubuntu](https://img.shields.io/badge/Ubuntu-E95420?style=for-the-badge&logo=ubuntu&logoColor=white)  ![Nginx](https://img.shields.io/badge/nginx-%23009639.svg?style=for-the-badge&logo=nginx&logoColor=white) ![Linux](https://img.shields.io/badge/Linux-FCC624?style=for-the-badge&logo=linux&logoColor=black) ![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white)  ![DjangoREST](https://img.shields.io/badge/DJANGO-REST-ff1709?style=for-the-badge&logo=django&logoColor=white&color=ff1709&labelColor=gray) ![Visual Studio Code](https://img.shields.io/badge/Visual%20Studio%20Code-0078d7.svg?style=for-the-badge&logo=visual-studio-code&logoColor=white) ![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)

## Описание проекта

Сервис "Вилка-ложка" - это уютное местечко, где можно попробовать приготовить много вкусного и разнообразного. Нет идеи что приготовить? Тогда Вам сюда, а готовый список продуктов поможет купить всё необходимое ;) /br
Здесь ты можешь:
- поделиться своими любимыми рецептами
- добавить в избранное понравившиеся рецепты;
- подписаться на интересных авторов;
- выгрузить из приложения список необходимых продуктов в нужном количестве!


## Разворачиваем проект на удаленном сервере

### 1. Клонирование кода приложения с GitHub на сервер
```

# Вместо <Ваш_аккаунт> подставьте свой логин, который используете на GitHub.
git clone git@github.com:VeraUrsul/fork-spoon.git

```
### 2. Создание и активация виртуального окружения
```

# Переходим в директорию backend-приложения проекта.
cd fork-spoon/backend/
# Создаём виртуальное окружение.
python3 -m venv venv
# Активируем виртуальное окружение.
source venv/bin/activate

```
### 3. Устанавливаем зависимости и применяем миграции
```

# Устанавливаем зависимости
pip install -r requirements.txt
# Применяем миграции.
python manage.py migrate

```

## Создание и заполнение файла .env

```

touch .env
nano .env

SECRET_KEY=<your_secret_key>

```

### Автор [Урсул Вера](https://github.com/VeraUrsul)
