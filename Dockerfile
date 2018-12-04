FROM python:3
ADD . /todo
WORKDIR /todo
RUN pip install -r requirements.txt
ENV INSERT_KEY baduba
CMD ["python", "server/main.py"]