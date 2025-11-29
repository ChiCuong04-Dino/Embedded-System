from fastapi import FastAPI, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import asyncio
import httpx
from typing import List
from config import ADAFRUIT_IO_KEY, MONGO_URL, DATABASE_NAME, COLLECTION_NAME, POLLING_URL, CONTROL_URL
from model import ControlRequest, SensorDataResponse

app = FastAPI()

# Global variables
db = None
polling_task = None

@app.on_event("startup")
async def startup_event():
    global db, polling_task
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DATABASE_NAME]
    polling_task = asyncio.create_task(poll_adafruit_data())


@app.on_event("shutdown")
async def shutdown_event():
    if polling_task:
        polling_task.cancel()


# Background polling task
async def poll_adafruit_data():
    while True:
        try:
            async with httpx.AsyncClient() as client:
                headers = {"X-AIO-Key": ADAFRUIT_IO_KEY}
                response = await client.get(POLLING_URL, headers=headers)

                if response.status_code == 200:
                    data = response.json()
                    if "last_value" in data:
                        import json
                        sensor_data = json.loads(data["last_value"])
                        sensor_data["timestamp"] = datetime.now()

                        await db[COLLECTION_NAME].insert_one(sensor_data)
                        print(f"Data stored: {sensor_data}")
                else:
                    print(f"Polling failed: {response.status_code}")
        except Exception as e:
            print(f"Polling error: {e}")

        await asyncio.sleep(10)


# API Endpoints
@app.get("/")
async def root():
    return {"message": "Embedded System API Server"}


@app.get("/data/latest", response_model=SensorDataResponse)
async def get_latest_data():
    """Get the most recent sensor data"""
    data = await db[COLLECTION_NAME].find_one({}, {"_id": 0}, sort=[("timestamp", -1)])
    if not data:
        raise HTTPException(status_code=404, detail="No data found")

    data["timestamp"] = data["timestamp"].isoformat()
    return data


@app.get("/data/history", response_model=List[SensorDataResponse])
async def get_data_history(limit: int = 100):
    """Get historical sensor data"""
    cursor = db[COLLECTION_NAME].find({}, {"_id": 0}).sort("timestamp", -1).limit(limit)
    data_list = []
    async for doc in cursor:
        doc["timestamp"] = doc["timestamp"].isoformat()
        data_list.append(doc)
    return data_list


@app.get("/data/range")
async def get_data_by_range(start_time: str, end_time: str):
    """Get sensor data within time range (ISO format: 2023-12-01T00:00:00)"""
    try:
        start_dt = datetime.fromisoformat(start_time)
        end_dt = datetime.fromisoformat(end_time)

        cursor = db[COLLECTION_NAME].find({
            "timestamp": {"$gte": start_dt, "$lte": end_dt}
        }, {"_id": 0}).sort("timestamp", -1)

        data_list = []
        async for doc in cursor:
            doc["timestamp"] = doc["timestamp"].isoformat()
            data_list.append(doc)
        return data_list
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid datetime format")


@app.post("/control")
async def control_devices(control: ControlRequest):
    """Control LED and Fan states"""
    try:
        async with httpx.AsyncClient() as client:
            headers = {
                "X-AIO-Key": ADAFRUIT_IO_KEY,
                "Content-Type": "application/json"
            }
            payload = {
                "value": f'{{"led_state":{str(control.led_state).lower()},"fan_state":{str(control.fan_state).lower()}}}'
            }

            response = await client.post(CONTROL_URL, headers=headers, json=payload)

            if response.status_code in [200, 201]:
                return {"message": "Control command sent successfully", "data": control.dict()}
            else:
                raise HTTPException(status_code=500, detail="Failed to send control command")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)