import os, traceback, re

class NoClientFoundError(Exception):
    """raise when there is no client found on user's system"""

class LogListerner:
    def __init__(self):
        self.client_name = None
        self.client_path = None
        self.client_paths = {"Vanila/Forge":r"$appdata\.minecraft\logs\latest.log",
                             "Lunar Client (1.8)":r"$USERPROFILE\.lunarclient\offline\1.8\logs\latest.log"}
        self.update_client()
        self.error_count = 0
        
        if False:
            self.client_name = "Vanila/Forge Test"
            self.client_path = os.path.expandvars(r"$appdata\.minecraft\logs\latesttest.log")
            self.open(self.client_path)
        
    def close(self) -> None:
        try: self.log_file.close()
        except: pass

    def open(self,path) -> None:
        print(f" *  log_listener: opening {path}")
        self.path = path
        self.close()
        self.log_file = open(self.path, "r", errors="ignore")
        self.log_file.seek(0, 2) # seek end of the file

    def get_update(self) -> list:
        try:
            lines = self.log_file.readlines()
            lines = [x for x in lines if len(x)>0] # remove empty lines
            self.error_count += len([0 for x in lines if "Exception" in x])
            return lines
        except Exception as e:
            self.close()
            print("")
            traceback.print_exc()
            print("Error:",e)
            return [e]

    def get_messages(self) -> list:
        lines = self.get_update()
        #print(lines)
        pattern_chat = re.compile("(?:\:\ \[CHAT\]\ )(.+)")
        pattern_party = re.compile("^.+ has invited you to join .+ party!")
        
        messages = list()
        for line in lines:
            a = pattern_chat.search(line)
            b = pattern_party.match(line)
            
            if a:
                messages.append(a.group(1))
            elif b:
                messages.append(b.group())
                
        return messages

    def get_client(self):
        print(f" *  log_listener: loaded {len(self.client_paths)} clients profile")
        client_buffer = {}
        for client in self.client_paths:
            raw_path = self.client_paths[client]
            client_path = os.path.expandvars(raw_path)

            if os.path.isfile(client_path):
                print(f" *  log_listener: {client} found at {client_path}")
                client_buffer[client] = {"last_modified":os.path.getmtime(client_path),
                                         "path": client_path}
        
        if not client_buffer: raise NoClientFoundError
        
        sort_by_time = sorted(client_buffer.items(), key=lambda x: x[1]["last_modified"])
        current_client = sort_by_time[-1]
        
        client_name = current_client[0]
        client_path = current_client[1]["path"]
        
        print(f" *  log_listener: hooked to {client_name}")
        
        return client_name, client_path

    def update_client(self,callback=None):
        name, path = self.get_client()
        if name!=self.client_name or path!=self.client_path:
            self.client_name = name
            self.client_path = path
            self.open(self.client_path)
            if callback: callback()
            return name, path