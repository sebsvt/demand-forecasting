FROM python:3.11

# Install dependencies
RUN pip install pandas pika pymongo python-dotenv

# Install prophet
RUN pip install prophet

# Patch prophet package
RUN sed -i 's/np.float_/np.float64/g' /usr/local/lib/python3.11/site-packages/prophet/forecaster.py

# Copy your application code
COPY . /app

WORKDIR /app

CMD ["python", "worker.py"]
