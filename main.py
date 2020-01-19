import asyncore
import json
import socket
import time

PORT = 8000
ADDR = '0.0.0.0'

lobby = []


class MainServer(asyncore.dispatcher):
    def __init__(self):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.bind((ADDR, PORT))
        self.listen(20)
        return

    def handle_accept(self):
        conn, addr = self.accept()
        meta = {
            "port": addr[1],
            "ip": addr[0],
            "conn": conn,
            "player": Player(conn)
        }
        print(f"{meta['ip'] + ' ' + str(meta['port'])} connected")
        lobby.append(meta)
        if len(lobby) > 1:
            print(f"matched {lobby[0]['ip']} {lobby[0]['port']} with {lobby[1]['ip']} {lobby[0]['port']}")
            Match(lobby[0], lobby[1])
            del lobby[0]
            del lobby[0]

    def handle_close(self):
        return


class Player(asyncore.dispatcher):
    opponent = None

    def __init__(self, conn):
        self.buffer = b""
        asyncore.dispatcher.__init__(self, sock=conn)

    def handle_read(self):
        if self.opponent is not None:
            chunk = self.recv(512)
            if not chunk:
                return
            self.buffer += chunk
            if chunk.decode()[-1] == '\n':
                cmd = json.loads(self.buffer.decode())
                self.buffer = b""
                self.evaluate_cmd(cmd)

    def evaluate_cmd(self, cmd):
        if cmd["forward"]:
            print(f"msg from {self.addr} to {self.opponent.addr}: {cmd['payload']}")
            self.opponent.send(json.dumps(cmd["payload"]).encode())

    def handle_close(self):
        print(f"{self.addr} bye byed")
        self.close()
        if self.opponent is not None:
            self.opponent.send(json.dumps({
                "msg": "opponent_disconnect"
            }).encode())
            self.opponent.opponent = None
        else:
            for i in range(len(lobby)):
                if lobby[i]["player"] == self:
                    print(f"deleted {lobby[i]} from lobby")
                    del lobby[i]
        print(f"lobby: {[i['ip'] for i in lobby]}")


class Match:
    def __init__(self, p1, p2):
        connection_message = {
            "info": "match_found",
            "id": 1
        }
        ping = {
            "info": "ping"
        }
        self.player1 = p1["player"]
        self.player2 = p2["player"]
        self.player1.opponent = self.player2
        self.player2.opponent = self.player1
        try:
            # ping both connections before saying that a match was found
            p1["conn"].send(json.dumps(ping).encode())
            p2["conn"].send(json.dumps(ping).encode())

            p1["conn"].send(json.dumps(connection_message).encode())
            connection_message["id"] = 2
            p2["conn"].send(json.dumps(connection_message).encode())
        except:
            print("match failed to start due to connection errors")
            print(f"\t{p1['ip']} & {p2['ip']}")


def main():
    server = MainServer()
    try:
        asyncore.loop()
    except:
        pass
    print("server closing")
    server.close()


if __name__ == "__main__":
    main()
