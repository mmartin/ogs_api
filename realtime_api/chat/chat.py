import collections
import dataclasses
import random
import time
import typing

from ogs_api.rest_api.download import access_api
from ogs_api.realtime_api.socket import comm_socket

"""
possible chat events emitted by the server are:
 -  "chat-message": 
 -  "chat-message-removed":
 -  "chat-join":
 -  "chat-part": 
"""

_user_id: int = None

def _chat_connect():
    from ogs_api.access_tokens import get_data, get_chat_auth
    data = get_data()
    global _user_id
    _user_id = data['user']['id']
    comm_socket.emit("chat/connect", data={"auth": get_chat_auth(),
                                           "player_id": data["user"]["id"],
                                           "ranking": data["user"]["ranking"],
                                           "username": data["user"]["username"],
                                           "ui_class": data["user"]["ui_class"]})


comm_socket.on("connect", _chat_connect)


def chat_join(channel: str):
    comm_socket.emit("chat/join", data={"channel": channel})

def chat_part(channel: str):
    comm_socket.emit("chat/part", data={"channel": channel})

def chat_send(channel: str, message: str):
    comm_socket.emit("chat/send", data={
        'channel': channel,
        'uuid': _n2s(_user_id) + '.' + _n2s(int(time.time() * 1000)),
        'message': message,
    })



_name2id_cache: typing.Dict[str, int] = dict()

@dataclasses.dataclass
class PrivateChat:
    base: str
    number: int = 0

_private_chat_cache: typing.Dict[int, PrivateChat] = \
    collections.defaultdict(lambda: PrivateChat(_n2s(random.randint(0, 1000))))

def pm_send(username: str, message: str):
    try:
        player_id = _name2id_cache[username]
    except KeyError:
        results = access_api('/api/v1/players', params={'username': username})
        assert results['count'] == 1
        player_id = results['results'][0]['id']
        _name2id_cache[username] = player_id

    private_chat = _private_chat_cache[player_id]
    private_chat.number += 1

    comm_socket.emit('chat/pm', {
        'player_id': player_id,
        'username': username,
        'uid': private_chat.base + '.' + _n2s(private_chat.number),
        'message': message,
    })

_n2s_alphabet = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
_n2s_alphalen = len(_n2s_alphabet)

def _n2s(n: int) -> str:
    if n < 0:
        return '-' + str(_n2s(-n))

    if n == 0:
        return _n2s_alphabet[0]

    ret = ''
    while n:
        rem = n % _n2s_alphalen
        n = n // _n2s_alphalen
        ret = _n2s_alphabet[rem] + ret

    return ret
