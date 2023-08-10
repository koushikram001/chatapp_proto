import tkinter as tk
import socket
import threading 
import openai


 
# pre_prompt = "You are a helpful assistant. You do not respond as 'User' or pretend to be 'User'. You only respond once as 'Assistant'."
openai.api_key = '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'
messages = [ {"role": "system", "content": 
              "You are a intelligent assistant."} ]

window = tk.Tk()
window.title("Sever")

# Top frame consisting of two buttons widgets (i.e. btnStart, btnStop)
topFrame = tk.Frame(window)
btnStart = tk.Button(topFrame, text="Connect", command=lambda : start_server())
btnStart.pack(side=tk.LEFT)
btnStop = tk.Button(topFrame, text="Stop", command=lambda : stop_server(), state=tk.DISABLED)
btnStop.pack(side=tk.LEFT)
topFrame.pack(side=tk.TOP, pady=(5, 0))

# Middle frame consisting of two labels for displaying the host and port info
middleFrame = tk.Frame(window)
lblHost = tk.Label(middleFrame, text = "Host: X.X.X.X")
lblHost.pack(side=tk.LEFT)
lblPort = tk.Label(middleFrame, text = "Port:XXXX")
lblPort.pack(side=tk.LEFT)
middleFrame.pack(side=tk.TOP, pady=(5, 0))





# The client frame shows the client area
clientFrame = tk.Frame(window)
lblLine = tk.Label(clientFrame, text="**********Client List**********").pack()
scrollBar = tk.Scrollbar(clientFrame)
scrollBar.pack(side=tk.RIGHT, fill=tk.Y)
tkDisplay = tk.Text(clientFrame, height=15, width=30)
tkDisplay.pack(side=tk.LEFT, fill=tk.Y, padx=(5, 0))
scrollBar.config(command=tkDisplay.yview)
tkDisplay.config(yscrollcommand=scrollBar.set, background="#F4F6F7", highlightbackground="grey", state="disabled")
clientFrame.pack(side=tk.BOTTOM, pady=(5, 10))


server = None
HOST_ADDR = "127.0.0.2"
HOST_PORT = 1235
client_name = " "
clients = []
clients_names = []
#file_his = open("chat_hist.txt","a")






# Start server function
def start_server():
    global server, HOST_ADDR, HOST_PORT # code is fine without this
    btnStart.config(state=tk.DISABLED)
    btnStop.config(state=tk.NORMAL)

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(socket.AF_INET)
    print(socket.SOCK_STREAM)

    server.bind((HOST_ADDR, HOST_PORT))
    server.listen(5)  # server is listening for client connection

    threading._start_new_thread(accept_clients, (server, " "))

    lblHost["text"] = "Host: " + HOST_ADDR
    lblPort["text"] = "Port: " + str(HOST_PORT)
    


# Stop server function
def stop_server():
    global server
    btnStart.config(state=tk.NORMAL)
    btnStop.config(state=tk.DISABLED)
    #test
    print(clients_names)
    print(clients)
    #end test
    




def accept_clients(the_server, y):
    while True:
        client, addr = the_server.accept()
        clients.append(client)

        # use a thread so as not to clog the gui thread
        threading._start_new_thread(send_receive_client_message, (client, addr))



# Function to receive message from current client AND
# Send that message to other clients
def send_receive_client_message(client_connection, client_ip_addr):
    global server, client_name, clients, clients_addr
    client_msg = " "

    #test
    #file_his = open("chat_hist.txt","a")
    #test

    

    # send welcome message to client
    client_name  = client_connection.recv(4096).decode()
    welcome_msg = "Welcome " + client_name + ". Use 'exit' to quit"
    client_connection.send(welcome_msg.encode())

    clients_names.append(client_name)

    update_client_names_display(clients_names)  # update client names display
    


    while True:
        data = client_connection.recv(4096).decode()
        if not data: break
        if data == "exit": break

        client_msg = data

        

        idx = get_client_index(clients, client_connection)
        sending_client_name = clients_names[idx]

        for c in clients:
            if c != client_connection:
                prompt = client_msg[len("@ai "):]
                first_three_client_chr = client_msg[:3]

                if first_three_client_chr == "@ai" :
                    #to replay in context with users
                    filename = "c1.txt"

                    with open(filename, "r") as file:
                        lines = file.readlines()

                    last_five_lines = lines[-10:]

                    for line in last_five_lines:
                        print(line.strip())
                        final = line.strip()
                       
                    if prompt:
                        messages.append(
                        {"role": "user", "content": final + prompt},
                        )
                        chat = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo", messages=messages
                        )
                    reply = chat.choices[0].message.content
                    print(f"ChatGPT: {reply}")
                    messages.append({"role": "assistant", "content": reply})
                    server_msg = str("\nAI_bot --> " + reply )
                    client_connection.send(server_msg.encode())
                else:
                    server_msg = str(sending_client_name + "->" + client_msg)
                c.send(server_msg.encode())
                #file_his.write(server_msg + "\n")##collecting in a seperate file
                
                
                print(server_msg)
                #file_his.close()

                
                
                
    # find the client index then remove from both lists(client name list and connection list)
    idx = get_client_index(clients, client_connection)
    del clients_names[idx]
    del clients[idx]
    server_msg = "BYE!"
    client_connection.send(server_msg.encode())
    client_connection.close()
    
    

    update_client_names_display(clients_names)  # update client names display
    


# Return the index of the current client in the list of clients
def get_client_index(client_list, curr_client):
    idx = 0
    for conn in client_list:
        if conn == curr_client:
            break
        idx = idx + 1

    return idx


# Update client name display when a new client connects OR
# When a connected client disconnects
def update_client_names_display(name_list):
    tkDisplay.config(state=tk.NORMAL)
    tkDisplay.delete('1.0', tk.END)

    for c in name_list:
        tkDisplay.insert(tk.END, c+"\n")
    tkDisplay.config(state=tk.DISABLED)


window.mainloop()