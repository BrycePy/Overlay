
event_list = {}

def subscribe(event_name, fn):
    event_list[event_name] = event_list.get(event_name,[])
    event_list[event_name].append(fn)
    
def post(event_name, data=None):
    events = event_list.get(event_name,[])
    for event in events: event(data)