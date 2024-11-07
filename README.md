
# Order Management System with FastAPI and Kafka

This project is a simple Order Management System built using FastAPI and SQLAlchemy. It integrates with Kafka for event-driven communication, allowing actions like creating, updating, and deleting orders to be published as messages to a Kafka topic.

## Features
- **CRUD Operations**: Create, read, update, and delete orders using FastAPI.
- **Event-Driven Architecture**: Publish order events to Kafka topics.
- **Kafka Consumer**: Consume and process order events from Kafka.
- **SQLAlchemy Integration**: Use SQLAlchemy ORM for database interactions.
- **Logging**: Log important events and errors for debugging and monitoring.

---

## Project Setup

### Prerequisites
- **Python**: Ensure Python 3.8 or higher is installed.
- **Kafka**: Apache Kafka must be set up and running on a separate server or locally.
- **SQLite**: Used as the default database (or you can configure a different one).

---

## Step-by-Step Setup Guide

### 1. Clone the Repository
```bash
git clone <repository-url>
cd <repository-name>
```

### 2. Set Up Python Virtual Environment
```bash
python -m venv env
source env/bin/activate  # On Linux/macOS
envScriptsactivate     # On Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up Kafka on Ubuntu (or any Linux System)
1. **Download Kafka**:
    ```bash
    wget https://dlcdn.apache.org/kafka/3.5.0/kafka_2.13-3.5.0.tgz
    tar -xzf kafka_2.13-3.5.0.tgz
    mv kafka_2.13-3.5.0 ~/kafka
    ```
2. **Start ZooKeeper**:
    ```bash
    ~/kafka/bin/zookeeper-server-start.sh ~/kafka/config/zookeeper.properties
    ```
3. **Start Kafka Server**:
    ```bash
    add below two lines on below file 
    vi kafka/config/server.properties
    advertised.listeners=PLAINTEXT://172.23.146.220:9092
    advertised.listeners=PLAINTEXT://172.23.146.220:9092 -- update your ip address
    ~/kafka/bin/kafka-server-start.sh ~/kafka/config/server.properties
    ```
4. **Create Kafka Topic**:
    ```bash
    ~/kafka/bin/kafka-topics.sh --create --topic order_updates --bootstrap-server localhost:9092 --replication-factor 1 --partitions 1
    ```

### 5. Configure the Environment Variables
- Create a `.env` file in the project root (if required) and add the necessary configuration:
  ```
  KAFKA_BOOTSTRAP_SERVERS=localhost:9092
  KAFKA_TOPIC=order_updates
  KAFKA_GROUP_ID=order_group
  DATABASE_URL=sqlite:///./orders.db
  ```

---

## Running the Application

### 1. Start FastAPI Server
```bash
uvicorn main:app --reload
```
- **Access the API Documentation**: Navigate to `http://127.0.0.1:8000/docs` in your browser.

### 2. Running the Kafka Producer
```bash
python kafka_producer.py
```
- This script publishes a test message to the Kafka topic.

### 3. Running the Kafka Consumer
```bash
python kafka_consumer.py
```
- This script consumes messages from the Kafka topic and processes them.

---

## Project Structure
```
.
├── config.py           # Configuration for Kafka and database
├── db.py               # Database setup with SQLAlchemy
├── kafka_consumer.py   # Kafka consumer implementation
├── kafka_producer.py   # Kafka producer implementation
├── logger.py           # Logger configuration
├── main.py             # FastAPI app with CRUD endpoints
├── models.py           # SQLAlchemy models
├── schemas.py          # Pydantic schemas
├── requirements.txt    # List of dependencies
└── README.md           # Project documentation
```

---

## Execution Flow
1. **Start Kafka**: Make sure Kafka and ZooKeeper are running.
2. **Start FastAPI**: Launch the FastAPI server using `uvicorn`.
3. **Publish Messages**: Use the Kafka producer to publish order events.
4. **Consume Messages**: Use the Kafka consumer to process and handle events.

---

## Notes
- **Database**: The default database is SQLite. You can configure a different database by updating `DATABASE_URL` in `config.py`.
- **Kafka Setup**: Ensure Kafka is properly configured and running on your server. If using a different server for Kafka, update the `KAFKA_BOOTSTRAP_SERVERS` setting.

---

## Future Enhancements
- **Add Authentication**: Secure the API endpoints.
- **Implement Alembic**: Use Alembic for database migrations.
- **Switch to PostgreSQL**: For production, consider switching to a more robust database like PostgreSQL.
