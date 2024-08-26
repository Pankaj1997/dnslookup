FROM python:3.9-slim

WORKDIR /app

RUN pip install --upgrade pip \
    && pip install virtualenv

RUN virtualenv venv

COPY requirements.txt requirements.txt
RUN . venv/bin/activate && pip install -r requirements.txt

COPY . .

ENV PATH="/app/venv/bin:$PATH"

CMD ["python", "app.py"]
