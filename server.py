import socket, sys

class Connection:
    """
    Attributes
    ----------
    ip : str
        Client's IP address.
    port : int
        Client's port number.
    files : list
        List of file names.
    """
    def __init__(self, ip_str, port_str, files_str):
        """
        Parameters
        ----------
        ip_str : str
            IP address.
        port_str : str
            Port number.
        files_str : str
            String of relevant file names.
        """
        self.ip = ip_str
        self.port = int(port_str)
        self.files = []
        self.files = files_str.split(',')


def add_new_connection(ip, port, files, connections):
    """
    Creates a new connection and adds it to the senders list.

    Parameters
    ----------
    ip : str
        IP address of the sender.
    port: str
        port number of the sender.
    files : str
        list of files the sender owns.
    connections : list
        list of connections.
    """
    c = Connection(ip, port, files)
    connections.append(c)


def find_files(query, connections):
    """
    Creates a new connection and adds it to the senders list.

    Parameters
    ----------
    query : str
        the string that the client requests to search for.
    connections : list
        list of connections.

    Returns
    ----------
    results_str : str
        results in a string formatted as [Name] [IP] [Port],.....,[Name] [IP] [Port]\n
    """
    # if client pressed "enter" key without typing anything, return blank answer to ignore his choice.
    if query == "":
        return "\n"
    results = []
    # scan all files lists to add relevant results.
    for c in connections:
        for f in c.files:
            if query in f:
                tmp = f + " " + c.ip + " " + str(c.port) + " "
                results.append(tmp)
    results_str = ','.join(results)
    # if no files have been found, return indicative string.
    if results_str == '':
        results_str = "not_found"
    results_str += "\n"
    return results_str


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# accept all IP addresses.
server_ip = '0.0.0.0'
server_port = int(sys.argv[1])
server.bind((server_ip, server_port))
server.listen(100)
# create a list of connections.
connections = []
while True:
    # block until a new client connects.
    client_socket, client_address = server.accept()
    # receive client's message.
    # "1" prefix = add client as a listener.
    # "2" prefix = search for relevant files.
    msg = client_socket.recv(1024)
    msg = msg[:-1]
    msg_split = msg.split(" ")
    while not msg == '':
        # if message begins with "1", add the client to the connection list.
        if msg_split[0] == "1":
            add_new_connection(server_ip, msg_split[1], msg_split[2], connections)
            msg = client_socket.recv(1024)
            continue
        # if message begins with "2", search for the relevant files and return the results to the client.
        if msg_split[0] == "2":
            results = find_files(msg_split[1], connections)
            client_socket.send(results.encode())
            # reset the message and continue.
            msg = ''
            continue
            