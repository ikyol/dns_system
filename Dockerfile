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