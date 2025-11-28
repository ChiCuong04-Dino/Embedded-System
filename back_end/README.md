# Embedded System API Server

FastAPI server that polls data from Adafruit IO and stores it in MongoDB.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Start MongoDB (make sure it's running on localhost:27017)

3. Run the server:
```bash
python main.py
```

## API Endpoints

- `GET /` - Health check
- `GET /data/latest` - Get most recent sensor data
- `GET /data/history?limit=100` - Get historical data (default 100 records)
- `GET /data/range?start_time=2023-12-01T00:00:00&end_time=2023-12-01T23:59:59` - Get data by time range
- `POST /control` - Control LED and Fan states

## Control API Example

```bash
curl -X POST "http://localhost:8000/control" \
     -H "Content-Type: application/json" \
     -d '{"led_state": true, "fan_state": false}'
```

## Features

- Automatic polling from Adafruit IO every 10 seconds
- MongoDB storage with timestamps
- RESTful APIs for frontend integration
- Device control via Adafruit IO