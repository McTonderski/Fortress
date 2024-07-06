[![Docker Build and Deploy](https://github.com/McTonderski/DockerFortress/actions/workflows/deploy.yml/badge.svg)](https://github.com/McTonderski/DockerFortress/actions/workflows/deploy.yml)

# Docker Container Controller

This repository provides an interface for managing Docker containers through a FastAPI backend and interacting with them using a Badger 2040 W device. The project allows you to start, stop, restart, and list Docker containers via a REST API, and provides a device interface for controlling these containers.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Device Interface](#device-interface)
- [License](#license)

## Installation

### Prerequisites

- Docker
- Badger 2040 W SDK
- WiFi configuration in `WIFI_CONFIG.py`

### Backend Setup

1. Clone the repository:

```bash
git clone https://github.com/McTonderski/DockerFortress.git
cd docker-container-controller
```

2. Build the Docker image:

```bash
docker build -t docker-container-controller .
```

3. Run the Docker container:

```bash
docker run -d -p 8000:8000 docker-container-controller
```

### Device Setup

0. How to upload code to the device: [INSTRUCTION](https://learn.pimoroni.com/article/getting-started-with-badger-2040)

1. Install the necessary packages for Badger 2040 W.

2. Ensure WiFi details are filled in `WIFI_CONFIG.py`. example below.

```
SSID = "WIFI_NAME"
PSK = "WIFI_PASSWORD"
COUNTRY = "COUNTRY_CODE"
```

3. Upload the `main.py` script to your Badger 2040 W.

## Usage

### API Endpoints

#### List Containers

- **Endpoint:** `GET /containers`
- **Description:** Retrieves a list of all Docker containers with their states.
- **Response:**
  ```json
  {
    "containers": [
      {
        "id": "container_id",
        "name": "container_name",
        "state": "container_state",
        "reposource": "repo_source"
      },
      ...
    ]
  }
  ```

#### Start a Container

- **Endpoint:** `POST /containers/start/{container_id}`
- **Description:** Starts a specified Docker container.
- **Response:**
  ```json
  {
    "message": "Container {container_id} started successfully."
  }
  ```

#### Stop a Container

- **Endpoint:** `POST /containers/stop/{container_id}`
- **Description:** Stops a specified Docker container.
- **Response:**
  ```json
  {
    "message": "Container {container_id} stopped successfully."
  }
  ```

#### Restart a Container

- **Endpoint:** `POST /containers/restart/{container_id}`
- **Description:** Restarts a specified Docker container.
- **Response:**
  ```json
  {
    "message": "Container {container_id} restarted successfully."
  }
  ```

### Device Interface

The device interacts with the backend to manage Docker containers. It displays container information and allows users to start, stop, and restart containers using the physical buttons.

#### Buttons

- **Button A:** Toggle container state (start/stop).
- **Button B:** Restart the selected container.
- **Button C:** Rebuild the selected container (if applicable).
- **Button UP/DOWN:** Scroll through the list of containers.

#### Display

The Badger 2040 W displays a list of Docker containers. Each container is shown with its ID, name, and state. If a container is rebuildable, it is indicated in the state.

#### WiFi Configuration

Ensure you have entered your WiFi details in the `WIFI_CONFIG.py` file for the device to connect to your network.

### Repo Source

`repo_source` is the name of the repository from which the container is built. This information is added by including labels in the container image, such as:

```bash
--label org.opencontainers.image.title=${{ github.repository }} \
--label org.opencontainers.image.created=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
```

If an image has this label, it is considered rebuildable, and the device can trigger a rebuild by clicking the appropriate button.

## License

This project is licensed under the Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International License. See the [LICENSE](LICENSE) file for details.
