FROM python:3
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt
COPY . /code
ENV PYTHONUNBUFFERED=1
CMD ["/bin/bash"]