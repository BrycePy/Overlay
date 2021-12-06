from PIL.Image import LINEAR
import aiohttp
import asyncio
import json
import base64
from io import BytesIO
from PIL import Image
import time

class AsyncAPI:
    async def _get_json(url):
        data = None
        async with aiohttp.ClientSession() as session:
            try:
                respond = await session.get(url, timeout = 30)
                data = await respond.json()
                status_code = respond.status
            except asyncio.TimeoutError:
                data = None
                status_code = 408
        if status_code!=200: print(status_code,url,data)
        return status_code, data

    async def _get_content(url):
        data = None
        async with aiohttp.ClientSession() as session:
            try:
                respond = await session.get(url, timeout = 30)
                data = await respond.read()
                status_code = respond.status
            except asyncio.TimeoutError:
                data = None
                status_code = 408
        if status_code!=200: print(status_code,url)
        return status_code, data

    async def get_hypixel(api_key,ign=None,uuid=None):
        if uuid:
            url = f"https://api.hypixel.net/player?key={api_key}&uuid={uuid}"
        else:
            url = f"https://api.hypixel.net/player?key={api_key}&name={ign}"
        status_code, data = await AsyncAPI._get_json(url)
        return status_code, data
        
        # 403 invalid key
        # 429 rate limited/ already look up

    async def get_uuid(ign):
        url = f"https://playerdb.co/api/player/minecraft/{ign}"
        status_code, data = await AsyncAPI._get_json(url)
        if status_code == 200:
            uuid = data.get("data").get("player").get("raw_id")
            return uuid
        else:
            return None

    async def get_skin(uuid, size=30):
        url = f"https://crafatar.com/avatars/{uuid}?overlay=true&size={size}"
        status_code, data = await AsyncAPI._get_content(url)
        if status_code == 200:
            return data
        else:
            return None

    async def get_session_skin(uuid, size=30):
        url = f"https://sessionserver.mojang.com/session/minecraft/profile/{uuid}"
        status_code, data = await AsyncAPI._get_json(url)
        if status_code == 200:
            for property in data.get("properties",[]):
                if property.get("name") == "textures":
                    session_data_raw = property.get("value")
                    session_data = json.loads(base64.b64decode(session_data_raw))
                    skin_url = session_data.get("textures").get("SKIN").get("url")
                    status_code, data = await AsyncAPI._get_content(skin_url)

                    im = Image.open(BytesIO(data))
                    base = Image.new("RGBA",(size,size))
                    face = im.crop((8,8,16,16)).resize((int(size/8*7),int(size/8*7)), resample=Image.NEAREST)
                    overlay = im.crop((40,8,48,16)).resize((size,size), resample=Image.NEAREST)

                    base.paste(face, (size//16,size//16))
                    base.paste(overlay, (0,0), overlay)

                    return base
            return None
        else:
            return None


async def test():
    ref = time.perf_counter()
    skin_img = await AsyncAPI.get_session_skin("2c5e94e4e42f422f90fad13ba5271480",1000)
    print(time.perf_counter() - ref)
    skin_img.show()
    

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(test())