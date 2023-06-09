FROM python:3.8-alpine as builder

WORKDIR /app

COPY pyproject.toml /app/pyproject.toml
COPY fuo /app/fuo

RUN pip wheel -w whls .

FROM python:3.8-alpine

WORKDIR /app

COPY --from=builder /app/whls /app/whls
RUN pip install --no-cache-dir whls/*.whl && rm -rf whls
ENTRYPOINT [ "fuo-bot" ]
CMD [ "run" ]