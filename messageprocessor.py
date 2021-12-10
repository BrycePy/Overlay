import re
import asyncio
import aiohttp
import tkinter as tk
import json
import event
import util
from colored import fg, attr

# -----------------------------
# You have joined [VIP+] oSpittinz's party!
# You'll be partying with: [MVP+] Kurenaiiii, [MVP+] B1u3Y
# -----------------------------

# -----------------------------
# You left the party.
# -----------------------------

class ConsoleColour():
    BLACK = str(fg('black'))
    WHITE = str(fg('white'))
    RED = str(fg('red'))
    GREEN = str(fg('green'))
    YELLOW = str(fg('yellow'))
    BLUE = str(fg('blue'))
    CYAN = str(fg('cyan'))
    MAGENTA = str(fg('magenta'))
    VIOLET = str(fg('violet'))
    ORCHID = str(fg('orchid'))
    TAN = str(fg('tan'))
    RESET = str(attr('reset'))
    ORANGE_4A = str(fg('orange_4a'))
    ORANGE_4B = str(fg('orange_4b'))
    ORANGE_3 = str(fg('orange_3'))
    DARK_ORANGE = str(fg('dark_orange'))
    ORANGE_1 = str(fg('orange_1'))

class Mode:
    general = 0
    bedwars = 1
    skywars = 2
    duels = 3

class General:
    def __init__(self,host):
        self.host = host

        self.party_members = list()

    async def process(self,message):
        party_invite = re.compile("^(\w+)(?:\ \[[\w\+]+\])? has invited you to join their party!").match(message)
        party_join = ""
        party_leave = ""
        party_left = ""
        party_play_with = "You'll be partying with: "
        party_join_leader = "Party Leader: "
        party_join_leader = "Party Moderators: "
        party_join_members = "Party Members: "
        
        if party_invite:
            username = party_invite.group(1)
            print(username)

class Bedwars:
    lobby = 0
    queue = 1

class AllGame:
    lobby = 0
    queue = 1
    def __init__(self,host):
        self.host = host

        self.players = list()
        self.game_state = Bedwars.lobby
        self.lobby_players = list()

        self.start_timer = 0
        self.player_count = 0
        self.player_count_max = 0

    async def process(self,message):
        previous_message = self.host.message_buffer[-2].get("message","")
        
        join_message = re.compile("^(\w+) has joined \((\d+)\/(\d+)\)\!").match(message)
        leave_message = re.compile("^(\w+) has quit!").match(message)
        start_timer = re.compile("^The game starts in (\d+) seconds!").match(message)
        start2_timer = re.compile("^The game is starting in (\d+) seconds!").match(message)
        who_command = re.compile("^ONLINE: ([\w,\ ]+)$").match(message)
        who2_command = re.compile("^Team #(\d+)\: (.+)").match(message)
        bw_lobby_chat = re.compile("^(?:\[(\w+).\]) (?:\[(.+)\] )?(\w+): (.+)").match(message)
        apikey_new = re.compile("^Your new API key is ((?:[a-f0-9]{8})-(?:[a-f0-9]{4})-(?:[a-f0-9]{4})-(?:[a-f0-9]{4})-(?:[a-f0-9]{12}))").match(message)
        msg_command = re.compile("^Can't find a player by the name of '([\w]{2,17})@'$").match(message)
        party_invite = re.compile("^(?:\[.+\] )(\w+) has invited you to join (?:\[.+\] )?(?:their|(\w+)\'s) party!").match(message)

        join_queue = (join_message or start_timer or start2_timer) and previous_message == " "*7
        join_lobby = message == " "*25 and previous_message == " "*37

        if who_command or join_message or leave_message:
            self.game_state = Bedwars.queue
        
        if join_queue:
            self.players = list()
            print(ConsoleColour.ORANGE_3 + f"bedwars_handler: Spawn in a queue" + ConsoleColour.RESET)
            async def send_who():
                await asyncio.sleep(0.25)
                await util.send_command("who")
            asyncio.get_event_loop().create_task(send_who())
            event.post("queue_join", None)
            event.post("player_list_update",self.players)
            
        if join_message:
            username, player_count, player_count_max = join_message.groups()
            self.player_count = int(player_count)
            self.player_count_max = int(player_count_max)
            self.players.append(username)
            print(ConsoleColour.ORANGE_3 + f"bedwars_handler: ({len(self.players)}/{self.player_count}/{self.player_count_max}) {username} Added!" + ConsoleColour.RESET)
            event.post("player_join",username)
            event.post("player_list_update",self.players)

        elif leave_message:
            username = leave_message.group(1)
            if username in self.players:
                self.player_count -= 1
                self.players.remove(username)
            print(ConsoleColour.ORANGE_3 + f"bedwars_handler: ({len(self.players)}/{self.player_count}/{self.player_count_max}) {username} Removed!" + ConsoleColour.RESET)
            event.post("player_leave",username)
            event.post("player_list_update",self.players)
            
        elif start_timer:
            self.start_timer = start_timer.group(1)
            print(ConsoleColour.ORANGE_3 + f"bedwars_handler: Game starting in {self.start_timer} sec" + ConsoleColour.RESET)
            event.post("start_timer", self.start_timer)
        
        elif start2_timer:
            self.start_timer = start2_timer.group(1)
            print(ConsoleColour.ORANGE_3 + f"bedwars_handler: Game starting in {self.start_timer} sec" + ConsoleColour.RESET)
            event.post("start_timer", self.start_timer)
        
        elif who_command:
            self.players = who_command.group(1).split(", ")
            print(ConsoleColour.ORANGE_3 + f"bedwars_handler: /who detected. {len(self.players)} players added!" + ConsoleColour.RESET)
            event.post("who_command", self.players)
            event.post("player_list_update",self.players)
        
        elif who2_command:
            usernames = who2_command.group(2).split(",")
            for username in usernames:
                username = username.strip()
                self.players.append(username)
            event.post("player_join",username)
            event.post("player_list_update",self.players)

        elif apikey_new:
            apikey = apikey_new.group(1)
            print(ConsoleColour.ORANGE_3 + f"bedwars_handler: /api new detected. {apikey}" + ConsoleColour.RESET)
            event.post("apikey_new", apikey)

        elif msg_command:
            username = msg_command.group(1)
            print(ConsoleColour.ORANGE_3 + f"bedwars_handler: /t <ign>@ detected. {username}" + ConsoleColour.RESET)
            event.post("msg_command", username)

        elif join_lobby:
            self.game_state = Bedwars.lobby
            self.lobby_players = list()
            event.post("lobby_join")
            #event.post("player_list_update",self.players)
            print(ConsoleColour.ORANGE_3 + "bedwars_handler: Spawn in a lobby" + ConsoleColour.RESET)

        elif bw_lobby_chat and self.game_state == Bedwars.lobby:
            username = bw_lobby_chat.group(3)
            raw_message = self.host.message_buffer[-1].get("raw_message","").replace("?",chr(0x2605),1)
            event.post("chat",(username,raw_message))

        elif party_invite:
            username = party_invite.group(1)
            username2 = party_invite.group(2)
            event.post("chat",(username,": $c### $bPARTY INVITE $c###"))
            if username2:
                event.post("chat",(username2,": $c### $bPARTY INVITE $c###"))

class MessageProcessor:
    def __init__(self):
        self.message_buffer = [{}]*100
        self.current_mode = "all"
        
        self.handlers = {
                        "all":AllGame(self)
                        }
        
        self.players = {}
        
    async def process(self,raw_message):
        message = re.sub(chr(167)+"[0-9a-fA-F]","",raw_message)

        self.message_buffer.append(dict(message=message,raw_message=raw_message))
        if len(self.message_buffer)>100: self.message_buffer.pop(0)
        
        #await self.handlers[Mode.general].process(message)
        await self.handlers[self.current_mode].process(message)



