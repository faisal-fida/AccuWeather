import asyncio
import websockets
import json

async def fetch_xhr_requests(ws_url):
    async with websockets.connect(ws_url) as websocket:
        await websocket.send(json.dumps({
            "id": 1,
            "method": "Network.enable"
        }))
        
        while True:
            response = await websocket.recv()
            message = json.loads(response)
            
            # Listen for network events
            if message.get("method") == "Network.requestWillBeSent":
                request = message["params"]["request"]
                if request["method"] == "POST" and "xhr" in request["headers"].get("Accept", ""):
                    print(f"XHR Request: {request['url']}")
            
            if message.get("method") == "Network.responseReceived":
                response = message["params"]["response"]
                if response["requestHeaders"].get("X-Requested-With") == "XMLHttpRequest":
                    print(f"XHR Response: {response['url']}")

ws_url = "ws://127.0.0.1:58486/devtools/browser/f2348f86-5020-4b17-a6a4-ea83bf25c07a"

asyncio.get_event_loop().run_until_complete(fetch_xhr_requests(ws_url))