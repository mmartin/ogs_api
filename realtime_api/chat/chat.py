import time

from ogs_api.realtime_api.socket import comm_socket

"""
possible chat events emitted by the server are:
 -  "chat-message": 
 -  "chat-message-removed":
 -  "chat-join":
 -  "chat-part": 
"""


def _chat_connect():
    from ogs_api.access_tokens import get_data, get_chat_auth
    data = get_data()
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

def chat_send(channel: str, user_id: int, message: str):
    comm_socket.emit("chat/send", data={
        'channel': channel,
        'uuid': _n2s(int(time.time() * 1000)),
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
