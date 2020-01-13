import asyncore
import json
import socket

PORT = 8080
ADDR = '0.0.0.0'

matches = []
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
            "conn": conn
        }
        print(meta)
        lobby.append(meta)
        if len(lobby) > 1:
            print(f"matched {lobby[0]['ip']} with {lobby[1]['ip']}")
            matches.append(Match(lobby[0], lobby[1]))
            del lobby[0]
            del lobby[0]

    def handle_close(self):
        print("disconnect")


class Player(asyncore.dispatcher):
    opponent = None

    def __init__(self, conn, addr):
        self.addr = addr
        self.buffer = b""
        asyncore.dispatcher.__init__(self, sock=conn)

    def handle_read(self):
        chunk = self.recv(512)
        self.buffer += chunk
        if chunk.decode()[-1] == '\n':
            cmd = json.loads(self.buffer.decode())

            self.evaluate_cmd(cmd)

    def evaluate_cmd(self, cmd):
        if cmd["forward"]:
            print(f"msg from {self.addr} to {self.opponent.addr}: {cmd['forward']}")
            self.opponent.send(json.dumps(cmd["payload"]).encode())


class Match:
    def __init__(self, p1, p2):
        connection_message = json.dumps({
            "info": "match_found"
        }).encode()
        self.player1 = Player(p1["conn"], p1["ip"])
        self.player2 = Player(p2["conn"], p2["ip"])
        self.player1.opponent = self.player2
        self.player2.opponent = self.player1
        p1["conn"].send(connection_message)
        p2["conn"].send(connection_message)


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
