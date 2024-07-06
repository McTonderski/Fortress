# This example grabs current weather details from Open Meteo and displays them on Badger 2040 W.
# Find out more about the Open Meteo API at https://open-meteo.com

import badger2040
from badger2040 import WIDTH
import gc
import ujson
import requests
import time

try:
    import asyncio
except ImportError:
    import uasyncio as asyncio
import modules.uaiohttpclient as aiohttp

ITEM_TEXT_SIZE = 0.8

GITHUB_TOKEN = "__INSERT_PAT_HERE__"
URL_BASE = "http://100.112.250.111:8123/"
URL_CONTAINERS = "containers"
URL_CONTAINERS_STOP = "containers/stop/"
URL_CONTAINERS_START = "containers/start/"
URL_CONTAINERS_RESTART = "containers/restart/"

SYSTEM_FAST = 3
UPDATE_TURBO = 3
# Display Setup
badger2040.system_speed(SYSTEM_FAST)
display = badger2040.Badger2040()
display.led(64)
display.set_update_speed(UPDATE_TURBO)


# Connects to the wireless network. Ensure you have entered your details in WIFI_CONFIG.py :).
display.connect()

container_names = []
_err = ""
selected = 0


class Container:
    def __init__(self, id, name, state, repo_source=None) -> None:
        self.id = id
        self.name = name
        self.state = state
        self.repo_source = repo_source

    def __eq__(self, other):
        """
        Override the __eq__ method to compare id and state attributes.
        """
        if isinstance(other, Container):
            return self.id == other.id and self.state == other.state
        return False

    def __str__(self):
        if self.repo_source:
            return self.id + self.name + self.state + self.repo_source
        else:
            return self.id + self.name + self.state


async def http_get(url) -> str:
    try:
        resp = await aiohttp.request("GET", url)
    except OSError:
        gc.collect()
        resp = await aiohttp.request("GET", url)
    _err = resp.status
    return await resp.read()


async def http_post(url) -> str | None:
    try:
        resp = await aiohttp.request("POST", url)
    except OSError:
        gc.collect()
        resp = await aiohttp.request("POST", url)
    return await resp.read()


async def get_data():
    global container_names
    print(f"Requesting URL: {URL_BASE+URL_CONTAINERS}")
    r = await http_get(URL_BASE + URL_CONTAINERS)

    # Parse the JSON response
    data = ujson.loads(r)

    # Extract container names into a list
    new_container_names = [
        Container(
            container["id"],
            container["name"],
            container["state"],
            container.get("reposource", None),
        )
        for container in data["containers"]
    ]
    # r.close()
    if new_container_names != container_names or container_names == []:
        container_names = new_container_names
        draw_page()
    await asyncio.sleep(5)


def draw_page():
    display.set_pen(15)
    display.clear()
    if len(container_names) > 0:
        display.set_font("bitmap6")
        for id, container in enumerate(
            container_names[12 * (selected // 12) : 12 * (selected // 12) + 12]
        ):
            display.set_pen(0)
            if id == selected % 12:
                display.rectangle(0, 4 + ((id % 12) * 10), WIDTH, 10)
                display.set_pen(15)
            header = f"{id + (12 * (selected // 12)) + 1}: {container.name}"
            state = container.state if container.state != "running" else ""
            if container.repo_source:
                state += "rebuildable"

            display.text(header, 3, 4 + (id * 10), WIDTH, ITEM_TEXT_SIZE)
            if state != "":
                text_length = display.measure_text(header, ITEM_TEXT_SIZE)
                state_length = display.measure_text(state, ITEM_TEXT_SIZE)
                if id != selected % 12:
                    display.rectangle(
                        text_length + 8, 4 + ((id % 12) * 10), state_length + 2, 10
                    )
                display.set_pen(15)
                display.text(
                    state, text_length + 10, 4 + (id * 10), WIDTH, ITEM_TEXT_SIZE
                )

    else:
        display.set_pen(0)
        display.rectangle(0, 60, WIDTH, 25)
        display.set_pen(15)
        if _err == "":
            display.text(
                "Unable to display container names! Check your network settings in WIFI_CONFIG.py",
                5,
                65,
                WIDTH,
                1,
            )
        else:
            display.text(_err, 5, 65, WIDTH, 1)

    display.update()


async def start_container():
    container_name = container_names[selected].name
    print(f"Requesting stop URL: {URL_BASE+URL_CONTAINERS_START+container_name}")
    r = await http_post(URL_BASE + URL_CONTAINERS_START + container_name)

    # get_data()
    print(f"Container: {container_name} started")


async def restart_container():
    container_name = container_names[selected].name
    print(f"Requesting stop URL: {URL_BASE+URL_CONTAINERS_RESTART+container_name}")
    r = await http_post(URL_BASE + URL_CONTAINERS_RESTART + container_name)

    # await get_data()
    print(f"Container: {container_name} restarted")


async def stop_container():
    container_name = container_names[selected].name
    print(f"Requesting stop URL: {URL_BASE+URL_CONTAINERS_STOP+container_name}")
    await http_post(URL_BASE + URL_CONTAINERS_STOP + container_name)

    # get_data()
    print(f"Container: {container_name} stopped")


async def toggle_container():
    container_state = container_names[selected].state
    if container_state == "restarting":
        return
    if container_state == "exited":
        await start_container()
    else:
        await stop_container()


async def rebuild_container():
    global GITHUB_TOKEN
    if not container_names[selected].repo_source:
        print("can't rebuild")
        print(container_names[selected])
        return

    container_source = container_names[selected].repo_source

    # Replace with your GitHub username or organization and repository name

    # Generate timestamp

    # URL and Headers
    url = f"https://api.github.com/repos/{container_source}/dispatches"
    print(url)
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "YourCustomUserAgent/1.0",
    }

    # Payload
    payload = {"event_type": "testing Badger"}

    # Send the request
    response = requests.post(url, json=payload, headers=headers)

    # Print the response
    print("Status Code:", response.status_code)
    print("Response Body:", response.text)


def update_portion():
    # TODO: update that method but it's far from perfect
    # display.partial_update(
    #     0,  # int: x coordinate of the update region
    #     4+((selected%12)*10)-15,  # int: y coordinate of the update region (must be a multiple of 8)
    #     WIDTH,  # int: width of the update region
    #     45,   # int: height of the update region (must be a multiple of 8)
    # )
    draw_page()


def scroll(side=True):
    global selected
    if not side and selected < len(container_names) - 1:
        selected += 1
    elif not side and selected == len(container_names) - 1:
        selected = 0
    elif selected > 0:
        selected -= 1
    elif selected == 0:
        selected = len(container_names) - 1
    else:
        return
    update_portion()


async def button(pin):
    while display.pressed_any():
        time.sleep(0.01)
    global changed
    changed = True

    if pin == badger2040.BUTTON_A:
        if container_names[selected].state != "started":
            await toggle_container()
    if pin == badger2040.BUTTON_B:
        if container_names[selected].state != "stopped":
            await restart_container()
    if pin == badger2040.BUTTON_C:
        await rebuild_container()
    if pin == badger2040.BUTTON_UP:
        # if state["page"] > 0:
        #     state["page"] -= 1
        scroll()
    if pin == badger2040.BUTTON_DOWN:
        # if state["page"] < MAX_PAGE - 1:
        #     state["page"] += 1
        scroll(False)


async def main():
    # Create tasks for both get_data and the main loop
    data_task = asyncio.create_task(get_data())
    while True:
        display.keepalive()

        if display.pressed(badger2040.BUTTON_A):
            await button(badger2040.BUTTON_A)
        if display.pressed(badger2040.BUTTON_B):
            await button(badger2040.BUTTON_B)
        if display.pressed(badger2040.BUTTON_C):
            await button(badger2040.BUTTON_C)
        if display.pressed(badger2040.BUTTON_UP):
            await button(badger2040.BUTTON_UP)
        if display.pressed(badger2040.BUTTON_DOWN):
            await button(badger2040.BUTTON_DOWN)

        # Check if data_task has finished, and if so, restart it
        if data_task.done():
            data_task = asyncio.create_task(get_data())

        await asyncio.sleep(0.01)  # Add a small delay to prevent busy-waiting


asyncio.run(main())
