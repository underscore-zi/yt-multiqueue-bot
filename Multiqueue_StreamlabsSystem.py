import os
import sys
import json
import urllib

import os
import ctypes
import codecs

ScriptName = "YT Multiqueue Bot"
Website = "http://little-canada.org"
Description = "Bot to allow for interactions with Warp.World's Multiqueue from Youtube"
Creator = "zi"
Version = "0.0.1"

base_domain = "https://api.warp.world"
configFile = "settings.json"
settings = {}
commands = {}
headers = {
    "user-agent": "{}/{} - zi@0x0539.net".format(ScriptName, Version)
}

def ScriptToggled(state):
    return

def Init():
    global settings

    path = os.path.dirname(__file__)
    try:
        with codecs.open(os.path.join(path, configFile), encoding='utf-8-sig', mode='r') as file:
            settings = json.load(file, encoding='utf-8-sig')
    except:
        settings = {
            "warpworld_username": "",
            "warpworld_key": "",
            "command_character": "!",
            "permission_join": "Everyone",
            "permission_next": "Owner",
        }

    if settings['warpworld_username'] == "" or settings['warpworld_key'] == "":
        Parent.Log(ScriptName, "[ERROR] You must provide your Warp World username and key.")
        raise Exception("You must provide your Warp World username and key.")

    init_settings()
    init_commands()

def init_settings():
    global settings
    settings['permission_leave'] = settings['permission_join']
    settings['permission_current'] = settings['permission_join']
    settings['permission_position'] = settings['permission_join']
    settings['permission_list'] = settings['permission_join']
    settings['permission_queue'] = settings['permission_join']

    settings['permission_random'] = settings['permission_next']
    settings['permission_subnext'] = settings['permission_next']
    settings['permission_subrandom'] = settings['permission_next']
    settings['permission_ban'] = settings['permission_next']
    settings['permission_open'] = settings['permission_next']
    settings['permission_close'] = settings['permission_next']
    settings['permission_nextactive'] = settings['permission_next']
    settings['permission_won'] = settings['permission_next']
    settings['permission_loss'] = settings['permission_next']
    settings['permission_newsession'] = settings['permission_next']
    settings['permission_endsession'] = settings['permission_next']



def init_commands():
    global settings
    global commands
    url = "https://api.warp.world/{}/warpbot_queue_commands?token={}".format(settings['warpworld_username'],
                                                                       settings['warpworld_key'])
    res = Parent.GetRequest(url, headers)
    js = json.loads(res)
    if js['status'] != 200:
        raise Exception('[WarpWorld] Unexpected status code: {}'.format(js['status']))

    if 'commands' not in js['response']:
        raise Exception('[WarpWorld] Response does not contain commands: {}'.format(js['response']))

    response = json.loads(js['response'])

    # Essentially invert the commands list so we can lookup user command and get WarpWorld command
    for k in response['commands']:
        commands[response['commands'][k]] = k.lower()

    commands['nextactive'] = 'nextactive'




def ScriptToggled(state):
    return

def Execute(data):
    if data.IsFromYoutube() and data.IsChatMessage():
        cmd = data.GetParam(0).lower()
        if cmd[0] != settings['command_character']:
            return
        cmd = cmd[1:]

        if cmd not in commands:
            return

        normalized_cmd = commands[cmd]

        permission_key = "permission_" + normalized_cmd
        if permission_key not in settings:
            Parent.Log(ScriptName, "[{}|{}] has not been implemented yet".format(cmd, normalized_cmd))
            return

        if not settings[permission_key] == "Everyone" and not Parent.HasPermission(data.User, settings[permission_key], ""):
            Parent.SendStreamMessage("@{} You do not have permission to use that command.".format(data.UserName))
            return

        if normalized_cmd in CMD_MAP:
            CMD_MAP[normalized_cmd](data)
        else:
            Parent.Log(ScriptName, "{} is not in the command map.".format(cmd))



def ReloadSettings(jsonData):
    global settings
    settings = json.loads(jsonData)
    init_settings()
    init_commands()

def Tick():
    pass

def YoutubeIdtoNumber(uid):
    # Just take the ord of characters in reverse to create a number for them
    return "".join([str(ord(c)) for c in uid[::-1]])[:15]

def WW_handle_response(res):
    res = json.loads(res)
    if res['status'] != 200:
        Parent.Log(ScriptName, "Unable to communicate with Warp World")
        Parent.Log(ScriptName, res['response'])
        Parent.SendStreamMessage("Something went wrong.")
        return res
    js = json.loads(res['response'])
    if 'message' in js and js['message'] != "":
        Parent.SendStreamMessage(js['message'])
    return js


def WW_join(data):
    if data.GetParamCount() < 2:
        return
    uid = YoutubeIdtoNumber(data.User)

    params = {
        "notes": data.GetParam(1),
        "token": settings['warpworld_key'],
        "viewerID": uid,
        "viewerName": data.UserName,
        "viewerFollow": 0,
        "viewerSub": 0,
        "service":"youtube",
    }
    query = urllib.urlencode(params)
    url = base_domain + "/{username}/join_queue?{query}".format(username=settings['warpworld_username'], query=query)
    WW_handle_response(Parent.GetRequest(url, headers))


def WW_leave(data):
    uid = YoutubeIdtoNumber(data.User)
    url = base_domain + "/{}/update_entry?token={}".format(settings['warpworld_username'],settings['warpworld_key'])
    params = {
        "status": "leave",
        "viewerID": uid,
        "username": data.UserName,
        "service": "youtube",
    }
    WW_handle_response(Parent.PostRequest(url, headers, params, True))


def WW_current(data):
    url = base_domain + "/{}/warp_queue".format(settings['warpworld_username'])
    js = WW_handle_response(Parent.GetRequest(url, headers))
    if js['active_entry']:
        d = js['active_entry_details']
        Parent.SendStreamMessage("Currently playing {} submited by {}.".format(d['notes'], d['viewerName']))
    else:
        Parent.SendStreamMessage("@{} No level is active.".format(data.UserName))



def WW_position(data):
    uid = YoutubeIdtoNumber(data.User)
    params = {
        "position": 1,
        "token": settings['warpworld_key'],
        "viewerID": uid,
        "viewerName": data.UserName,
        "service": "youtube",
    }
    query = urllib.urlencode(params)
    url = base_domain + "/{username}/join_queue?{query}".format(username=settings['warpworld_username'], query=query)
    #Parent.SendStreamMessage(query)
    WW_handle_response(Parent.GetRequest(url, headers))


def WW_status(newstatus):
    url = base_domain + "/{}/update_entry?token={}".format(settings['warpworld_username'], settings['warpworld_key'])
    params = {
        "status": newstatus,
        "service": "youtube",
    }
    WW_handle_response(Parent.PostRequest(url, headers, params, True))
6 

def WW_next(_):
    WW_status("next")


def WW_subnext(_):
    WW_status("subnext")


def WW_random(_):
    WW_status("random")


def WW_subrandom(_):
    WW_status("subrandom")


def WW_ban(_):
    WW_status("banned")

def WW_won(_):
    WW_status("won")

def WW_loss(_):
    WW_status("loss")


def WW_update_setting(setting_name, value):
    url = base_domain + "/{}/update_queue_settings?token={}".format(settings['warpworld_username'], settings['warpworld_key'])
    params = {
        "setting_name": setting_name,
        "value": value,
    }
    WW_handle_response(Parent.PostRequest(url, headers, params, True))


def WW_open(_):
    WW_update_setting('status', "1")


def WW_close(_):
    WW_update_setting('status', "0")

def WW_list(data):
    status = data.GetParam(1)
    params = {
        "onlinestatus": status,
        "token": settings['warpworld_key'],
    }
    query = urllib.urlencode(params)
    url = base_domain + "/{username}/warpqueue_list?{query}".format(username=settings['warpworld_username'], query=query)
    WW_handle_response(Parent.GetRequest(url, headers))

def WW_queue(_):
    url = base_domain + "/{}/".format(settings['warpworld_username'])
    res = Parent.GetRequest(url, headers)
    res = json.loads(res)
    if res['status'] != 200:
        Parent.Log(ScriptName, "Got an unexpected status code from Warp World")

    res = json.loads(res['response'])
    if 'multi_queue_information' not in res or 'queue_description' not in res['multi_queue_information']:
        Parent.Log(ScriptName, "No queue is active")
    else:
        Parent.SendStreamMessage(res['multi_queue_information']['queue_description'])

def WW_newsession(data):
    url = base_domain + "/{}/new_session?token={}".format(settings['warpworld_username'],settings['warpworld_key'])
    name = data.GetParam(1)
    params = {
        "sessionName": name,
    }
    WW_handle_response(Parent.PostRequest(url, headers, params, True))

def WW_endsession(data):
    url = base_domain + "/{}/end_session?token={}".format(settings['warpworld_username'],settings['warpworld_key'])
    name = data.GetParam(1)
    params = {
        "sessionName": name,
    }
    WW_handle_response(Parent.PostRequest(url, headers, params, True))



def next_active(_):
    url = base_domain + "/{}/warp_queue".format(settings['warpworld_username'])
    js = WW_handle_response(Parent.GetRequest(url, headers))
    entries = js['entries']
    active = [str(YoutubeIdtoNumber(u)) for u in Parent.GetActiveUsers()]
    for e in entries:
        if e['status'] == 'active':
            continue

        if(str(e['viewerID']) in active):
            url = base_domain + "/{}/update_entry?token={}".format(settings['warpworld_username'], settings['warpworld_key'])
            params = {
                "entryID": e['id'],
                "queueID": js['queueID'],
                "status": "active",
            }
            Parent.PostRequest(url, headers, params, True)
            Parent.SendStreamMessage("Now playing {} submited by {}".format(e['notes'], e['viewerName']))
            return
    Parent.SendStreamMessage("There are no levels in the queue from active users.")

CMD_MAP = {
    "join": WW_join,
    "leave": WW_leave,
    "position": WW_position,
    "next": WW_next,
    "subnext": WW_subnext,
    "random": WW_random,
    "subrandom": WW_subrandom,
    "current": WW_current,
    "ban": WW_ban,
    "open": WW_open,
    "close": WW_close,
    "won": WW_won,
    "loss": WW_loss,
    "list": WW_list, #no offline/online support
    "queue": WW_queue,
    "newsession": WW_newsession,
    "endsession": WW_endsession,
    "nextactive": next_active,
}
