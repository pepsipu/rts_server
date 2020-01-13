import socket
import threading
import time
import json

PORT = 8000

matches = []
lobby = []


def handle_connection(conn, addr):
    pass


def begin_match(p1, p2):
    connection_message = json.dumps({
        "info": "match_found"
    }).encode()
    p1["conn"].send(connection_message)
    p2["conn"].send(connection_message)


def match_players():
    while True:
        if len(lobby) > 1:
            print(f"matched {lobby[0]['ip']} with {lobby[1]['ip']}")
            new_match = threading.Thread(target=begin_match, args=(lobby[0], lobby[1]))
            matches.append(new_match)
            new_match.start()
            del lobby[0]
            del lobby[0]
        time.sleep(1)


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('0.0.0.0', PORT))
    sock.listen(20)
    threading.Thread(target=match_players).start()
    while True:
        new_conn, new_addr = sock.accept()
        new_player = {
            "conn": new_conn,
            "ip": new_addr[0],
            "port": new_addr[1]
        }
        print(new_player)
        lobby.append(new_player)  # add the IP to the lobby as well as a reference to the socket


if __name__ == "__main__":
    main()
