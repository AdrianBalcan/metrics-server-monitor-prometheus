FROM python:2.7-alpine3.8
LABEL maintainer="contact@adrianbalcan.com"

RUN pip install flask prometheus_client

COPY ./src/metrics-server-monitor-prometheus.py /metrics-server-monitor-prometheus.py

EXPOSE 9100

CMD ["python2", "/metrics-server-monitor-prometheus.py"]
