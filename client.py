import socket, sys, os

def send_file(ip, port):
    """
    Transfers the file from the sender's directory to the receiver's.

    Parameters
    ----------
    ip : str
        IP address.
    port : int
        port number.
    """
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((ip, port))
    server.listen(5)
    while True:
        client_socket, client_address = server.accept()
        data = client_socket.recv(1024)
        while data == '':
            data = client_socket.recv(1024)
        data = data[:-1]
        f = open(data, 'rb')
        l = f.read(1024)
        while (l):
            client_socket.send(l)
            l = f.read(1024)
        f.close()
        client_socket.close()


def request_file(sender_ip, sender_port, file_name):
    """
    Connects the receiver to the sender and asks him for the needed file.

    Parameters
    ----------
    sender_ip : str
        sender's ip address.
    sender_port : int
        sender's port number.
    file_name : str
        needed file's name.
    """
    # create a new TCP socket.
    h = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    h.connect((sender_ip, sender_port))
    request = file_name + "\n"
    h.send(request.encode())
    f = open(file_name, 'wb')
    l = h.recv(1024)
    while (l):
        f.write(l)
        l = h.recv(1024)
    f.close()
    h.close()


def handle_data(data):
    """
    Processing the results received from server.

    Parameters
    ----------
    data : str
        results string.

    Returns
    ----------
    results : dict
        results dictionary - indices mapped to tuples of (name, ip, port).
    """
    items = data.split(',')
    items.sort()
    results = {}
    i = 1
    for item in items:
        it = item.split(' ')
        results[i] = (it[0], it[1], int(it[2]))
        print str(i) + " " + it[0]
        i += 1
    return results


# extract ip and port from args.
connection_type = int(sys.argv[1])
server_ip = str(sys.argv[2])
server_port =  int(sys.argv[3])
# for connection type = 0, add the client to the server's listeners list.
if connection_type == 0:
    port = int(sys.argv[4])
    files_list = next(os.walk("."))[2]
    files_str = "1 " + str(port) + " " + ','.join(files_list) + "\n"
    # create a new TCP socket.
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((server_ip, server_port))
    s.send(files_str.encode())
    s.close()
    send_file(server_ip, port)
# for connection type = 1, start a search-choose loop to allow client pick files.
if connection_type == 1:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    msg = raw_input("Search: ")
    while not msg == 'quit':
        query = "2 " + msg + "\n"
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((server_ip, server_port))
        s.send(query.encode())
        options = s.recv(4096)
        while options[len(options) - 1] != '\n':
            options = s.recv(4096)
        s.close()
        # if server returned no results, ignore the user's choice and let him search again.
        # if server returned "\n" because the client pressed only "enter" key, ignore his choice too.
        if options.decode() == "not_found\n" or options.decode() == '\n':
            raw_input("Choose: ")
            msg = raw_input("Search: ")
            continue
        # if the server returned valid resuls, handle them and print a menu to the user.
        results = handle_data(options)
        # let the client choose one option.
        choice = raw_input("Choose: ")
        # if choice is invalid, ignore it.
        if (int(choice.encode()) < 1) or (int(choice.encode()) > len(results)):
            msg = raw_input("Search: ")
            continue
        # if choice is valid, get the file owner's details and connect to him to request the file.
        details = results.get(int(choice.encode()))
        sender_port = details[2]
        file_name = details[0]
        request_file(server_ip, sender_port, file_name)
        msg = raw_input("Search: ")
    s.close()
