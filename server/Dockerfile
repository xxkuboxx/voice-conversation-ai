FROM python:3.10-bullseye

WORKDIR /app
COPY requirements.txt /app/
RUN pip3 install -r requirements.txt

COPY *.py /app/
COPY assets/* /app/assets/
COPY frame_processors/* /app/frame_processors/
COPY utils/* /app/utils/
RUN mkdir /app/output/

EXPOSE 7860

CMD ["python3", "server.py"]
