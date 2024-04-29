# DNS System


## Информация о файлах конфигурации
Все конфигурции можно найти в директории:
```bash
src/dns_system/config
```

## Информаци о ENV-параметрах
Имеющиеся env-параметры в проекте:
```
MYSQL_SERVER: str
MYSQL_USER: str
MYSQL_PASSWORD: str
MYSQL_DB: str
MYSQL_PORT: int

DSN: str
CLOUDFLARE_API_KEY: str
CLOUDFLARE_API: str
CLOUDFLARE_ACCOUNT_ID: str
```


### Запуск воркера

1. Создайте виртуальное окружение

```bash
python3 -m venv venv
```

2. Активировать виртуальное окружение: 

```bash
source venv/bin/activate
```

3. Установить зависимости: 

```bash
pip3 install -r requirements.txt
```

4. Собрать приложение как модуль:

```bash
python3 -m pip install .
```

5. Запусить приложение:
```bash
dns-system
```

### Запуск с помощью Dockerfile


1. Dockerfile:
```dockerfile
FROM python:3.11.4-slim AS deps

RUN apt update && apt -y install \
    build-essential libffi-dev libssl-dev \
    pandoc \
    gcc g++

WORKDIR /app

COPY . ./

RUN pip --no-cache-dir install --upgrade \
    setuptools\
    wheel \
    pip \
    twine \
    pytest \
    pytest-cov \
    tox \
    flake8 \
    toml

RUN pip install pip-tools

RUN python3 -m piptools compile -o requirements.txt pyproject.toml

FROM deps AS build
RUN pip --no-cache-dir install -r requirements.txt

FROM build AS package
RUN pip wheel . --wheel-dir=dist

FROM python:3.11.4-slim AS runtime
COPY --from=package /app/dist/*.whl /app/dist/

RUN pip --no-cache-dir install /app/dist/*.whl \
    && rm -f /app/*.whl

ENTRYPOINT ["dns-system"]
```

3. Cборка образа:
```bash
docker build -t dns_system .
```

4. Запуск контейнера:
```bash
docker run dns_system
```