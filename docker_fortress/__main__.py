from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from docker import DockerClient
import asyncio

async def periodic_task():
    while True:
        # Your periodic task logic goes here
        print("Running periodic task...")
        await asyncio.sleep(5)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the ML model
    background_task = periodic_task()
    yield
    # Clean up the ML models and release the resources
    background_task.cancel()


app = FastAPI(lifespan=lifespan)
docker_client = DockerClient(base_url='unix://var/run/docker.sock')


@app.get("/")
def read_root():
    return {"message": "Welcome to the Docker container controller!"}

@app.post("/containers/start/{container_id}")
def start_container(container_id: str):
    try:
        container = docker_client.containers.get(container_id)
        container.start()
        return {"message": f"Container {container_id} started successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start container {container_id}: {str(e)}")

@app.post("/containers/stop/{container_id}")
def stop_container(container_id: str):
    try:
        container = docker_client.containers.get(container_id)
        container.stop()
        return {"message": f"Container {container_id} stopped successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop container {container_id}: {str(e)}")

@app.post("/containers/restart/{container_id}")
def reastart_container(container_id: str):
    try:
        container = docker_client.containers.get(container_id)
        container.restart()
        return {"message": f"Container {container_id} restarted successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to restart container {container_id}: {str(e)}")


@app.get("/containers")
def list_containers():
    try:
        containers = docker_client.containers.list(all=True)
        container_info = []

        for container in containers:
            container_id = container.id
            container_name = container.name
            container_attrs = container.attrs  # Access all attributes of the container
            container_labels = container.labels

            # Get the state of the container from its attributes
            container_state = container_attrs['State']['Status']

            # Create a dictionary with container information including state
            container_data = {
                "id": container_id,
                "name": container_name,
                "state": container_state
            }
            if 'org.opencontainers.image.title' in container_labels:
                container_data["reposource"] = container_labels['org.opencontainers.image.title']

            # Add the container data to the list
            container_info.append(container_data)

        return {"containers": container_info}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list containers: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
