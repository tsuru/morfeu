FROM tsuru/python

ENV PORT 8000
ENV SOURCE_DIR /home/application/current
RUN mkdir -p $SOURCE_DIR
WORKDIR $SOURCE_DIR
EXPOSE $PORT

COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

CMD "python main.py --daemon"
