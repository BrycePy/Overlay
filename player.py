import asyncio
from asyncapis import AsyncAPI
import time
import event
from config import config
from stats import Stats

uuid_cache = {}

class Player:
    def __init__(self, ign=None, uuid=None):
        self.data = {}
        self.ign = ign
        self.uuid = uuid
        self.nicked = False
        self.updating = False
        self.pending_render = True
        self.error_message = None
        self.active = True

    async def update(self, timeout=5):
        if self.updating: return
        self.updating = True
        #print("updating", self.ign)
        try:
            hypixel_api_key = config.get("hypixel_api_key")
            if not hypixel_api_key:
                self.error_message = f"$bplease do $e/api new"
                self.render_request()
                return

            cached_uuid = uuid_cache.get(self.ign.lower())
            if cached_uuid:
                status_code, data = await AsyncAPI.get_hypixel(api_key=hypixel_api_key, uuid=cached_uuid, timeout=timeout)
            else:
                status_code, data = await AsyncAPI.get_hypixel(api_key=hypixel_api_key, ign=self.ign, timeout=timeout)

            if status_code == 408:
                #print("timeout")
                if self.active:
                    self.error_message = f"$bRetrying....."
                    self.render_request()
                    self.updating = False
                    await self.update(timeout=15)
                return

            if data.get("cause",None) == "You have already looked up this name recently":
                self.error_message = f"Username lookup failed."
                self.render_request()
                uuid = await AsyncAPI.get_uuid(self.ign)
                if uuid:
                    self.uuid = uuid
                else:
                    self.nicked = True
                    return
                self.error_message = f"Retrying..."
                self.render_request()
                status_code, data = await AsyncAPI.get_hypixel(api_key=hypixel_api_key, uuid=uuid)
            
            if data.get("throttle",None):
                if self.active:
                    for i in range(3):
                        self.error_message = f"$bRetrying in {3-i} sec"
                        self.render_request()
                        await asyncio.sleep(1)
                    self.error_message = f"$bRetrying....."
                    self.render_request()
                    self.updating = False
                    await self.update()
                return

            if data.get("cause",None) == "Invalid API key":
                self.error_message = f"$cInvalid API key."
                self.render_request()
                await asyncio.sleep(2)
                self.error_message = f"$bplease do $e/api new"
                self.render_request()
                return

            if data.get("player",0) is None:
                self.nicked = True
                return

            player = data.get("player")
            hypixel = Stats(player)
            self.data["hypixel"] = hypixel

            self.uuid = hypixel.uuid
            uuid_cache[self.ign.lower()] = self.uuid
            self.ign = hypixel.displayname
            
            self.render_request()
            self.data["skin"] = await AsyncAPI.get_session_skin(self.uuid, int(24))

        except Exception as e:
            print(e)

        finally:
            self.render_request()
            self.updating = False

    def render_notification(self):
        self.pending_render = False

    def render_request(self):
        self.pending_render = True
        event.post("render_request",None)

    @staticmethod
    def set_apikey(key):
        config.set("hypixel_api_key", key)
        config.dump()