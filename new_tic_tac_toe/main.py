import pygame
import tkinter
import socket
import tkinter as tk
import numpy as np
from threading import Thread

pygame.init()

client_win = None
server_win = None
screen = None
win_size = None
gameover = False
BG_COLOR = (28, 170, 156)
LINE_WIDTH = 15
LINE_COLOR = (23, 145, 135)
player_1 = [' ', 0]
player_2 = [' ', 0]
basefont = pygame.font.Font(None, 102)
smallfont = pygame.font.Font(None, 22)
BG_COLOR = (28, 170, 156)
LINE_COLOR = (23, 145, 135)
CIRCLE_COLOR = (239, 231, 200)
CROSS_COLOR = (66, 66, 66)
LINE_WIDTH = 15
BOARD_ROWS = 3
BOARD_COLS = 3
CIRCLE_RADIUS = 60
CIRCLE_WIDTH = 25
CROSS_WIDTH = 30
SPACE = 55
board = np.zeros((BOARD_ROWS, BOARD_COLS))
player = 1
client_thread = None

def start():
    main_win = tk.Tk()
    main_win.title("tic_tac_toe")
    main_win.attributes("-fullscreen", True)
    main_win['background'] = "#1CAA9C"
    myfont = ("Comic Sans MS", 32, "bold")

    def marksquare(row, col, player):
        board[row][col] = player

    def available_square(row, col):
        return board[row][col] == 0

    def is_board_full():
        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                if board[row][col] == 0:
                    return False
                else:
                    return True

    def draw_figure():
        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                if board[row][col] == 1:
                    pygame.draw.circle(screen, CIRCLE_COLOR, (int(
                        (col * 200 + 200/2) + 80), int((row * 200 + 200/2)+80)), CIRCLE_RADIUS, CIRCLE_WIDTH)
                elif board[row][col] == 2:
                    pygame.draw.line(screen, CROSS_COLOR, ((col * 200 + SPACE)+80, (row * 200 + 200 - SPACE)+80),
                                     ((col * 200 + 200 - SPACE)+80, (row * 200 + SPACE)+80), CROSS_WIDTH)
                    pygame.draw.line(screen, CROSS_COLOR, ((col * 200 + SPACE)+80, (row * 200 + SPACE)+80),
                                     ((col * 200 + 200 - SPACE)+80, (row * 200 + 200 - SPACE)+80), CROSS_WIDTH)

    def check_winner(player):
        # vertical win check
        for col in range(BOARD_COLS):
            if board[0][col] == player and board[1][col] == player and board[2][col] == player:
                draw_vertical_win_line(col, player)
                # time.sleep(1)
                return True

        # horzontal win check
        for row in range(BOARD_ROWS):
            if board[row][0] == player and board[row][1] == player and board[row][2] == player:
                draw_horizontal_win_line(row, player)
                return True

        # ace diagonal
        if board[2][0] == player and board[1][1] == player and board[0][2] == player:
            draw_asc_diagonal_win_line(player)
            return True

        # dec diagonal
        if board[0][0] == player and board[1][1] == player and board[2][2] == player:
            draw_dec_diagonal_win_line(player)
            return True

        return False

    def draw_vertical_win_line(col, player):
        posX = col * 200 + 100 + 80

        if player == 1:
            Color = CIRCLE_COLOR
        elif player == 2:
            Color = CROSS_COLOR

        pygame.draw.line(screen, Color, (posX, 95),
                         (posX, win_size[1] - 95), 15)

    def draw_horizontal_win_line(row, player):
        posY = row * 200 + 100 + 80

        if player == 1:
            Color = CIRCLE_COLOR
        elif player == 2:
            Color = CROSS_COLOR

        pygame.draw.line(screen, Color, (95, posY), (680 - 15, posY), 15)

    def draw_asc_diagonal_win_line(payer):
        if player == 1:
            Color = CIRCLE_COLOR
        elif player == 2:
            Color = CROSS_COLOR

        pygame.draw.line(screen, Color, (80, 680), (680, 80), 15)

    def draw_dec_diagonal_win_line(player):
        if player == 1:
            Color = CIRCLE_COLOR
        elif player == 2:
            Color = CROSS_COLOR

        pygame.draw.line(screen, Color, (115, 115), (650, 650), 15)

    def restart():
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        screen.fill(BG_COLOR)
        # drawLines()
        player = 1
        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                board[row][col] = 0

    def server():
        global gameover, board, player
        server_socket = socket.socket()
        host = socket.gethostname()
        port = 1234
        server_socket.bind((host, port))
        server_socket.listen(1)
        connection, address = server_socket.accept()
        game("server")
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    if event.key == pygame.K_RETURN:
                        # winningSound.stop()
                        restart()
                        gameover = False
                if event.type == pygame.MOUSEBUTTONDOWN and not gameover:
                    mouseX = event.pos[0]
                    mouseY = event.pos[1]

                    click_row = int((mouseY-80) // 200)
                    click_col = int((mouseX-80) // 200)

                    if (click_col < 3 and click_row < 3):
                        clicked_col = click_col
                        clicked_row = click_row
                        # print(clicked_col," ",clicked_row)
                    else:
                        continue

                    if available_square(clicked_row, clicked_col):
                        if player == 1:
                            marksquare(clicked_row, clicked_col, 1)
                            # clickSound.play()
                            if check_winner(player):
                                # winningSound.play()
                                # player_1[1] += 1
                                gameover = True
                            player = 2
                            response = board
                            print(type(response))
                            connection.sendall(response)
                        # elif player == 2:
                        #     marksquare(clicked_row, clicked_col, 2)
                        #     # clickSound.play()
                        #     if check_winner(player):
                        #         winningSound.play()
                        #         # player_2[1] += 1
                        #         gameover = True
                        #     player = 1
                        draw_figure()
            pygame.display.update()
        connection.close()

    def client(host):
        global client_win, board
        s = socket.socket()
        port = 1234
        # Connect to the server
        s.connect((host, port))
        # client_win.destroy()
        game("client")
        running = True
        while running:
            response = s.recv(1024)
            martix_response = np.frombuffer(response, dtype=np.float64)
            board = martix_response.reshape((3, 3))
            draw_figure()
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        print(event.key)
                        running = False
            pygame.display.update()

        s.close()

    def send():
        global server_win
        main_win.destroy()
        server_win = tk.Tk()
        server_win.attributes("-fullscreen", True)
        server_win['background'] = "#1CAA9C"
        server_win.title("server")
        # getting ip address
        ipaddress = socket.gethostbyname(socket.gethostname())

        iplabel = tk.Label(server_win, text=ipaddress, bg="#1CAA9C")
        iplabel.configure(font=myfont)
        iplabel.pack(anchor="center")

        Thread(target=server).start()

    def recv():
        global client_win,client_thread
        host_address = tk.StringVar()
        main_win.destroy()
        client_win = tk.Tk()
        client_win.attributes("-fullscreen", True)
        client_win['background'] = "#1CAA9C"
        client_win.title("client")

        ip_label = tk.Label(
            client_win, text="Enter host's 12 digit number displaying on the screen ", bg="#1CAA9C")
        ip_label.configure(font=myfont)
        ip_label.place(x=50, y=250)

        ip_input = tk.Entry(client_win,
                            width=16,
                            textvariable=host_address,
                            bg="#4ff0e0", bd=0)
        ip_input.configure(font=myfont)
        ip_input.place(x=150, y=350)

        def connect():
            global host,client_thread
            host = ip_input.get()
            client(host)

        connect = tk.Button(client_win, text="Connect",
                            command=connect, height=4, width=40, bg="#61ffef")
        connect.place(x=350, y=500)
        # print("Debug 1")
        # client_thread = Thread(target=client, args=(host,))
        # client_thread.start()
        # print("Debug 3")


    def game(name):
        global screen
        screen = pygame.display.set_mode((0,0),pygame.FULLSCREEN)
        screen.fill(BG_COLOR)
        if name == "client":
            pygame.display.set_caption("client")
        if name == "server":
            pygame.display.set_caption("server")

        win_size = pygame.display.get_window_size()
        # HORIZONTAL_ABOVE
        pygame.draw.line(screen, LINE_COLOR, (80, 280), (680, 280), LINE_WIDTH)
        # HORIZONTAL_BELOW
        pygame.draw.line(screen, LINE_COLOR, (80, 480), (680, 480), LINE_WIDTH)
        # # #VERTICAL_LEFT
        pygame.draw.line(screen, LINE_COLOR, (280, 80), (280, 680), LINE_WIDTH)
        # VERTICAL_RIGHT
        pygame.draw.line(screen, LINE_COLOR, (480, 80), (480, 680), LINE_WIDTH)

    # button to send req
    btn = tk.Button(main_win, text="Send a request", command=send,
                    height=4, width=40, bg="#61ffef")
    btn.place(x=350, y=300)
    # button to connect
    connect = tk.Button(main_win, text="Connect",
                        command=recv, height=4, width=40, bg="#61ffef")
    connect.place(x=350, y=500)
    main_win.mainloop()


start()