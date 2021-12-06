import asyncio
from asyncapis import AsyncAPI
import time

apikey = "44e1c058-bda3-4438-a695-6a2ca455872f"

test_uuid_cache = {}

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

    async def update(self):
        if self.updating: return
        self.updating = True
        print("updating", self.ign)
        try:
            if test_uuid_cache.get(self.ign):
                status_code, data = await AsyncAPI.get_hypixel(api_key=apikey, uuid=test_uuid_cache.get(self.ign))
            else:
                status_code, data = await AsyncAPI.get_hypixel(api_key=apikey, ign=self.ign)

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
                status_code, data = await AsyncAPI.get_hypixel(api_key=apikey, uuid=uuid)
            
            if data.get("throttle",None):
                expected_reset = time.time()%60
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

            if data.get("player",0) is None:
                self.nicked = True
                return
            
            player = data.get("player")
            self.uuid = player.get("uuid")
            test_uuid_cache[self.ign.lower()] = self.uuid
            self.ign = player.get("displayname")
            self.data["hypixel"] = player
            self.render_request()

            self.data["skin"] = await AsyncAPI.get_session_skin(self.uuid, int(24))
            self.render_request()

        except Exception as e:
            print(e)

        finally:
            self.render_request()
            self.updating = False

    def render_notification(self):
        self.pending_render = False

    def render_request(self):
        self.pending_render = True