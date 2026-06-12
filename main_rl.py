import tkinter as tk
from tkinter import *
import os
import sys
import copy
import time

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(_SCRIPT_DIR)
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)

from checkers_core import BLACK, best_black_move, jump_exists
from rl_agent import get_trained_agent

board_cells = []
board_ready = False
board_frame = None

_rl_agent_cache = None


def load_rl_agent():
    global _rl_agent_cache
    if _rl_agent_cache is None:
        _rl_agent_cache = get_trained_agent()
    return _rl_agent_cache

def encrypt(text, shift):

    encrypted_text = []
    
    for char in text:
        # Сдвигаем символ по алфавиту
        shifted_char = chr(ord(char) + shift)
        encrypted_text.append(shifted_char)
       
    
    return ''.join(encrypted_text)


def decrypt(text, shift):
   
    decrypted_text = []
    
    for char in text:
    
        # Сдвигаем символ по алфавиту в противоположную сторону
        shifted_char = chr(ord(char) - shift)
        decrypted_text.append(shifted_char)
        
    
    return ''.join(decrypted_text)


def dismiss(win_t):
        win_t.grab_release()
        win_t.destroy()


def regis():
    global txt, txtl, txtp, login, password, label_game, restart_button


    saved_login = login.get()
    saved_password = password.get()

    if len(saved_login) == 0 or len(saved_password) == 0:
        win = Toplevel(root, relief=SUNKEN)
        win.geometry("400x100+510+300")
        win.title("Регистрация / Авторизация")
        win.minsize(width=400, height=100)
        win.maxsize(width=400, height=100)
        win.protocol("WM_DELETE_WINDOW", lambda: dismiss(win))  # перехватываем нажатие на крестик
        Label(win, text='Пуcтое поле "Логин" или "Пароль"', font=("Arial", 14, 'bold')).place(x=30, y=10)
        close_button = tk.Button(win, text="Повторить ввод", command=lambda: dismiss(win))
        close_button.place(x=150, y=50)
        win.grab_set()  # захватываем пользовательский ввод
    else:
        f_reg = False
        file = open("l_p.txt", "r+", encoding="utf8")  # открываем файл
        a = file.read().split()  # читаем файл
        for j in range(len(a) - 1):  # ищем совпадение логин и пароль
            if decrypt(a[j], 10) == saved_login and decrypt(a[j + 1], 10) == saved_password:
                f_reg = True
                break

        if not f_reg:  # совпадения нет
            file.seek(0, os.SEEK_END)
            file.write(encrypt(saved_login, 10) + ' ' + encrypt(saved_password, 10) + ' ')  # записываем новые логин и пароль
            file.close()

        win_r = Toplevel(root, relief=SUNKEN)
        win_r.geometry("400x130+730+420")
        win_r.title("Регистрация / Авторизация")
        win_r.minsize(width=400, height=130)
        win_r.maxsize(width=400, height=130)
        win_r.protocol("WM_DELETE_WINDOW", lambda: dismiss(win_r))  # перехватываем нажатие на крестик
        Label(win_r, text="Уважаемый(-ая) " + saved_login + ", вы успешно\n зарегистрировались / авторизовались",
              font=("Arial", 14, 'bold')).place(x=5, y=10)
        
        def update_enemy_bot():
            global enemy_bot
            enemy_bot = radio_var.get() == 1

        radio_var = IntVar(value=1)  # По умолчанию играть с компьютером
        Radiobutton(win_r, text="Играть с компьютером", variable=radio_var, value=1, command=update_enemy_bot).place(x=40, y=60)
        Radiobutton(win_r, text="Играть с человеком", variable=radio_var, value=0, command=update_enemy_bot).place(x=200, y=60)
        update_enemy_bot()  # применить значение по умолчанию

        
        close_button = tk.Button(win_r, text="Начать игру", command=lambda: dismiss(win_r))
        close_button.place(x=150, y=100)
        win_r.grab_set()  # захватываем пользовательский ввод

        txt.place_forget()  # стираем виджеты регистрации
        txtl.place_forget()
        txtp.place_forget()
        login.place_forget()
        password.place_forget()
        close_but.place_forget()
        label_game['text'] = 'выбор \n шашки'
        global restart_button
        if restart_button is None:
            restart_button = Button(
                root, text="начать с\nначала", compound="c", command=restart,
                font=("Arial", 10, 'bold'), borderwidth=3,
            )
            restart_button.grid(row=8, column=6)
        setup_board_once()  # доска создаётся один раз


def end_of_game():
    global gaming_field, label_game
    count_of_black, count_of_white = 0, 0
    count_of_movable_white, count_of_movable_black = 0,0
    check_qween()
    for i in range(64):
        x = i // 8
        y = i % 8
          
        if gaming_field[x][y] == -1 or gaming_field[x][y] == -2:
            count_of_white += 1
            if is_jump_exist(-1) or is_valid_move(x, y, x + 1, y + 1, gaming_field[x][y]) or is_valid_move(x, y, x + 1, y - 1, gaming_field[x][y]) or\
                 is_valid_move(x, y, x - 1, y + 1, gaming_field[x][y]) or is_valid_move(x, y, x - 1, y - 1, gaming_field[x][y]):
                count_of_movable_white += 1
        elif gaming_field[x][y] == 1 or gaming_field[x][y] == 2:
            count_of_black += 1
            if is_jump_exist(1) or is_valid_move(x, y, x + 1, y + 1, gaming_field[x][y]) or is_valid_move(x, y, x + 1, y - 1, gaming_field[x][y]) or\
                 is_valid_move(x, y, x - 1, y + 1, gaming_field[x][y]) or is_valid_move(x, y, x - 1, y - 1, gaming_field[x][y]):
                count_of_movable_black += 1
    if count_of_black == 0 or count_of_movable_black == 0:
        label_game['text'] = 'Белые\n выиграли'
    
    elif count_of_white == 0 or count_of_movable_white == 0:
        label_game['text'] = 'Черные\n выиграли'
 

        
    if label_game['text'] == 'Черные\n выиграли' or label_game['text'] == 'Белые\n выиграли':
        win = Toplevel(root, relief=SUNKEN)
        win.geometry("400x100+730+420")
        win.title("ПОБЕДА!")
        if label_game['text'] == 'Черные\n выиграли':
            text = "Черные выиграли"
        else:
            text = "Белые выиграли"
        txt = Label(win, text=text, font=("Arial", 14, 'bold'))
        txt.place(x=100, y=20)
        win.minsize(width=400, height=120)
        win.maxsize(width=400, height=120)
        win.protocol("WM_DELETE_WINDOW", exit)  # перехватываем нажатие на крестик

        close_button = tk.Button(win, text="Завершить игру", command=exit)
        close_button.place(x=20, y=70)
        
        tk.Button(win, text="Начать сначала", command=lambda: [win.destroy(), restart()]).place(x=250, y=70)
        


def restart():
    global gaming_field, current_player, is_button_active, count_of_moves, x1,x2,y1,y2,max_score,multiple_move
    
    gaming_field = [
    [0, 1, 0, 1, 0, 1, 0, 1],
    [1, 0, 1, 0, 1, 0, 1, 0],
    [0, 1, 0, 1, 0, 1, 0, 1],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [-1, 0, -1, 0, -1, 0, -1, 0],
    [0, -1, 0, -1, 0, -1, 0, -1],
    [-1, 0, -1, 0, -1, 0, -1, 0]
    ]
    
    is_button_active = False
    count_of_moves = 0
    x1, y1, x2, y2= 0, 0, 0, 0
    multiple_move, max_score, current_player = False, 0, -1
    
    refresh_board()


def check_qween():
    global gaming_field
    for i in range(64):
        x = i // 8
        y = i % 8
        if gaming_field[x][y] == 1 and x == 7: 
            gaming_field[x][y] = 2
            change_button(x,y, gaming_field[x][y])
            
        if gaming_field[x][y] == -1 and x == 0: 
            gaming_field[x][y] = -2
            change_button(x,y, gaming_field[x][y])


def _cell_bg(x, y):
    return "#f0f0f0" if (x + y) % 2 == 0 else "gray"


def change_button(x, y, value, refresh=True):
    global board_cells, image_white_checker, image_black_checker, image_black_qween, image_white_qween
    if current_player > 0:
        label_current_turn['text'] = 'ход\nчерных'
    elif current_player < 0:
        label_current_turn['text'] = 'ход\nбелых'

    index = x * 8 + y
    if not board_cells or index >= len(board_cells):
        return

    bg = _cell_bg(x, y)
    btn = board_cells[index]
    if value == 1:
        btn.config(image=image_black_checker, background=bg, activebackground=bg, state=NORMAL)
    elif value == -1:
        btn.config(image=image_white_checker, background=bg, activebackground="red", state=NORMAL)
    elif value == -2:
        btn.config(image=image_white_qween, background=bg, activebackground="red", state=NORMAL)
    elif value == 2:
        btn.config(image=image_black_qween, background=bg, activebackground=bg, state=NORMAL)
    else:
        btn.config(image=pixel, background=bg, activebackground=bg, state=NORMAL)

    if refresh:
        root.update_idletasks()


def refresh_board():
    """Обновить доску без создания новых кнопок."""
    check_qween()
    for i in range(64):
        x, y = i // 8, i % 8
        change_button(x, y, gaming_field[x][y], refresh=False)
    root.update_idletasks()


def setup_board_once():
    """Создать 64 клетки один раз внутри board_frame (без наложения)."""
    global board_cells, board_ready, board_frame, label_current_turn
    if board_ready:
        refresh_board()
        return

    for w in board_frame.winfo_children():
        w.destroy()
    board_cells = []
    label_current_turn['text'] = 'ход\nбелых'

    for i1 in range(8):
        for j1 in range(8):
            index = i1 * 8 + j1
            bg_color = _cell_bg(i1, j1)
            board_cells.append(
                Button(
                    board_frame, image=pixel, text="", height=k, width=k, compound="c",
                    command=lambda i=index: click_button(i),
                    background=bg_color, activebackground=bg_color,
                )
            )
            board_cells[-1].grid(column=j1, row=i1, sticky=NW)

    board_ready = True
    refresh_board()


def is_valid_move(start_x, start_y, end_x, end_y, player):
    global gaming_field
    if 7 < start_x or start_x < 0 or 7 < start_y or start_y < 0 or 7 < end_x or end_x < 0 or 7 < end_y or end_y < 0:
        return False
    # Проверка, что конечная клетка пустая
    if gaming_field[end_x][end_y] != 0:
        return False

    # Разница по координатам
    dx, dy = end_x - start_x, end_y - start_y

    # Для обычной шашки (не дамки)
    if player in [-1, 1]:
        if player == -1:  # Ход белых
            if dx != -1 or abs(dy) != 1:  # Движение строго вверх на одну клетку
                return False
        elif player == 1:  # Ход чёрных
            if dx != 1 or abs(dy) != 1:  # Движение строго вниз на одну клетку
                return False

    # Для дамки
    elif player in [-2, 2]:  # Белая дамка (-2) или черная дамка (2)
        if abs(dx) != abs(dy):  # Ход только по диагонали
            return False

        # Проверка, что путь до конечной клетки свободен
        step_x = 1 if dx > 0 else -1
        step_y = 1 if dy > 0 else -1
        for i in range(1, abs(dx)):  # Проверка клеток на пути
            if gaming_field[start_x + i * step_x][start_y + i * step_y] != 0:
                return False

    return True


def is_valid_jump(start_x, start_y, end_x, end_y, player):
    global gaming_field
    global delete_enemy
    delete_enemy = []

    # Проверка, что конечная клетка пустая
    if gaming_field[end_x][end_y] != 0:
        return False

    # Разница по координатам
    dx, dy = end_x - start_x, end_y - start_y

    # Для обычной шашки
    if player in [-1, 1]:
        delete_enemy = [x1 + (x2 - x1) // 2, y1 + (y2 - y1) // 2]
        # Проверка, что прыжок ровно на 2 клетки
        if abs(dx) != 2 or abs(dy) != 2:
            return False

        # Проверка, что между начальной и конечной клеткой есть шашка противника
        middle_x, middle_y = start_x + dx // 2, start_y + dy // 2
        if gaming_field[middle_x][middle_y] != -player and gaming_field[middle_x][middle_y] != -player * 2:  # Противник
            return False

    # Для дамки
    elif player in [-2, 2]:
        if abs(dx) != abs(dy):  # Прыжок только по диагонали
            return False

        step_x = 1 if dx > 0 else -1
        step_y = 1 if dy > 0 else -1
        count_of_enemy = 0
        for i in range(1, abs(dx)):  # Проверка клеток на пути
            if gaming_field[start_x + i * step_x][start_y + i * step_y] == -player / 2 or \
                    gaming_field[start_x + i * step_x][start_y + i * step_y] == -player:
                delete_enemy = [start_x + i * step_x, start_y + i * step_y]
                count_of_enemy += 1
            elif gaming_field[start_x + i * step_x][start_y + i * step_y] == player / 2 or \
                    gaming_field[start_x + i * step_x][start_y + i * step_y] == player:
                return False
        if count_of_enemy != 1:
            return False

    return True


def click_button(i):
    x = i // 8
    y = i % 8
    global x1, x2, y1, y2, delete_enemy, count_of_moves, max_score, old_field, enemy_bot
    global gaming_field, board_cells, label_game, is_button_active, multiple_move, current_player
    

    if is_button_active:
        x2 = i // 8
        y2 = i % 8
        if is_jump_exist(current_player) and is_valid_move(x1, y1, x2, y2, gaming_field[x1][y1]):
            '''
            проверка на наличие вражеских шашек под боем, если такие есть 
            и ход игрока это игнорирует, то выводим ошибку
            '''
            label_game['text'] = "нужно\nсъесть"
            if not multiple_move:
                is_button_active = False
            refresh_board()
            return
        elif is_jump_exist(current_player) and is_valid_jump(x1, y1, x2, y2, gaming_field[x1][y1]):
            change_button(x2,y2, gaming_field[x1][y1])
            change_button(x1, y1, 0)
            change_button(delete_enemy[0],delete_enemy[1],0)
            
            gaming_field[delete_enemy[0]][delete_enemy[1]] = 0
            gaming_field[x2][y2] = gaming_field[x1][y1]
            gaming_field[x1][y1] = 0
            count_of_moves += 1
            check_qween()
            #board_cells[i].config(state=tk.NORMAL, bg="#f0f0f0")
            end_of_game()
            if is_jump_exist_for_one(x2 * 8 + y2, current_player):
                multiple_move = True
                x1 = x2
                y1 = y2
                board_cells[x1 * 8 + y1].config(state=tk.NORMAL, bg="red")


            else:
                is_button_active = False
                multiple_move = False
                if count_of_moves == max_score:
                    count_of_moves = 0
                    if enemy_bot : bot_move()
                    else: current_player = current_player * -1
                    check_qween()
                    return
                else:
                    label_game['text'] = "нужно\nсъесть\nбольше"
                    gaming_field = copy.deepcopy(old_field)
                    count_of_moves = 0
                    refresh_board()
                    return
        elif not is_jump_exist(current_player) and is_valid_move(x1, y1, x2, y2, gaming_field[x1][y1]):
            '''
            нету вражеских шашек под боем и ход возможен,
            делаем ход
            '''
            gaming_field[x2][y2] = gaming_field[x1][y1]
            change_button(x2,y2, gaming_field[x1][y1])
            gaming_field[x1][y1] = 0
            change_button(x1,y1, 0)
            is_button_active = False
            if enemy_bot : bot_move()
            else: current_player = current_player * -1
            check_qween()
            return
        else: # не выполнено ни одно из условий
            label_game['text'] = "неверный\nход"
            if not multiple_move:
                is_button_active = False
                refresh_board()

            return

    elif not is_button_active and (x + y) % 2 != 0 and (
            gaming_field[i // 8][i % 8] == current_player or gaming_field[i // 8][i % 8] == current_player * 2) :
        '''
        корректно выбрана шашка для хода
        '''
        max_score = 0
        for t in range(64):
            xc = t // 8
            yc = t % 8
            if gaming_field[xc][yc] == current_player  or gaming_field[xc][yc] == current_player * 2:
                score_field[xc][yc] = count_captures(gaming_field, xc,yc)[0]
                max_score = max(max_score, score_field[xc][yc])

        if  score_field[x][y] == max_score:
            x1 = i // 8
            y1 = i % 8
            is_button_active = True
            board_cells[i].config(state=tk.NORMAL, bg="red")
            label_game['text'] = "выбери\nклетку\nдля хода"
            return
        else:
            is_button_active = False
        label_game['text'] = "есть\nварианты\nлучше"
        refresh_board()
    else:
        is_button_active = False
        label_game['text'] = "неверная\nклетка"
        refresh_board()


def is_jump_exist_for_one(i, side):
    all_moves = lambda x, y: [(x + dx, y + dy) for dx, dy in
                              [(-i, -i) for i in range(1, 8)] + [(-i, i) for i in range(1, 8)] + [(i, -i) for i in
                                                                                                  range(1, 8)] + [(i, i)
                                                                                                                  for i
                                                                                                                  in
                                                                                                                  range(
                                                                                                                      1,
                                                                                                                      8)]
                              if 0 <= x + dx < 8 and 0 <= y + dy < 8]

    directions = [
        (-2, -2), (-2, 2),  # для обычных шашек - вверх (диагональ влево и вправо)
        (2, -2), (2, 2)  # для обычных шашек - вниз (диагональ влево и вправо)
    ]
    x = i // 8
    y = i % 8
    if gaming_field[x][y] == side:
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < 8 and 0 <= ny < 8:
                # Проверяем, если через нее можно перепрыгнуть и клетка свободна
                if is_valid_jump(x, y, nx, ny, side):
                    return True


    elif gaming_field[x][y] == side * 2:
        for j in all_moves(x, y):
            if is_valid_jump(x, y, j[0], j[1], side * 2):
                return True
    return False


def is_jump_exist(side):  # side сторона 1 для черных -1 для белых
    for i in range(64):
        if is_jump_exist_for_one(i, side):
            return True
    return False


def can_capture(board, x, y, dx, dy, enemy_values):
    """
    Проверяет, можно ли выполнить съедение в указанном направлении.
    """
    nx, ny = x + dx, y + dy
    next_x, next_y = nx + dx, ny + dy
    
    # Проверяем границы и наличие шашек
    if 0 <= nx < len(board) and 0 <= ny < len(board[0]) and board[nx][ny] in enemy_values:
        if 0 <= next_x < len(board) and 0 <= next_y < len(board[0]) and board[next_x][next_y] == 0:
            return True
    return False


def get_moves(board, x, y, enemy_values, directions, is_king):
    """
    Возвращает список всех возможных ходов с текущего положения.
    """
    moves = []
    
    for dx, dy in directions:
        if is_king:  # Для дамки проверяем все клетки на диагонали
            step = 1
            while True:
                nx, ny = x + step * dx, y + step * dy
                next_x, next_y = nx + dx, ny + dy
                
                # Проверяем границы
                if not (0 <= nx < len(board) and 0 <= ny < len(board[0])):
                    break
                
                # Если нашли вражескую шашку, проверяем возможность прыжка
                if board[nx][ny] in enemy_values and 0 <= next_x < len(board) and 0 <= next_y < len(board[0]) and board[next_x][next_y] == 0:
                    moves.append(((nx, ny), (next_x, next_y)))
                    break
                
                
                # Прерываем, если на пути свои шашки или пустые клетки
                if board[nx][ny] != 0:
                    break
                step += 1
        else:  # Для обычной шашки проверяем ближайшие клетки
            if can_capture(board, x, y, dx, dy, enemy_values):
                nx, ny = x + dx, y + dy
                next_x, next_y = nx + dx, ny + dy
                moves.append(((nx, ny), (next_x, next_y)))
    return moves


def capture_recursive(board, x, y, enemy_values, directions, is_qween, path):
    """
    Рекурсивная функция для подсчета максимального количества шашек и списка ходов.
    """
    moves = get_moves(board, x, y, enemy_values, directions, is_qween)
    if not moves:  # Базовый случай: нет возможных ходов
        return 0, path  # Возвращаем текущий путь как результат

    max_captures = 0
    best_path = []

    for (enemy_pos, new_pos) in moves:
        nx, ny = new_pos
        ex, ey = enemy_pos

        # Копируем доску для нового состояния
        new_board = [row[:] for row in board]
        new_board[x][y] = 0  # Текущая шашка покидает клетку
        new_board[ex][ey] = 0  # Вражеская шашка съедена
        new_board[nx][ny] = board[x][y]  # Ставим шашку на новое место

        # Рекурсивный вызов
        captures, current_path = capture_recursive(
            new_board, nx, ny, enemy_values, directions, is_qween, path + [(nx, ny)]
        )

        # Учитываем текущее съедение
        captures += 1

        # Сохраняем лучший результат
        if captures > max_captures:
            max_captures = captures
            best_path = current_path

    return max_captures, best_path


def count_captures(board, x, y):
    """
    Главная функция, определяющая количество съеденных шашек и список ходов.
    """
    piece = board[x][y]
    if piece == 0:
        return 0, []  # Пустая клетка

    # Определяем направление и вражеские шашки
    if piece > 0:  # Черные шашки
        enemy_values = {-1, -2}
    else:  # Белые шашки
        enemy_values = {1, 2}

    directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]  # Диагональные направления
    is_king = abs(piece) == 2  # Проверяем, является ли шашка дамкой

    # Запускаем рекурсивный поиск
    captures, path = capture_recursive(board, x, y, enemy_values, directions, is_king, [(x, y)])
    return captures, path


def apply_core_move(new_board):
    global gaming_field
    for r in range(8):
        for c in range(8):
            gaming_field[r][c] = int(new_board[r][c])
    refresh_board()


def bot_move():
    """Ход чёрных: сильный мини-макс (макс. взятие + выигрышная позиция)."""
    global gaming_field, old_field, label_game, enemy_bot

    if not enemy_bot:
        return

    time.sleep(0.15)
    label_game["text"] = "ход\nкомпьютера"
    root.update_idletasks()

    old_field = copy.deepcopy(gaming_field)
    move = best_black_move(gaming_field, depth=4)
    if move is None:
        end_of_game()
        return

    _, new_board, _ = move
    apply_core_move(new_board)
    end_of_game()

            
root = Tk()
k = 70  # размер клетки
root.geometry("610x660+500+50")
root.resizable(False, False)
root.title('Бразильские шашки — ИИ: Q-learning (лаб. 6)')

pixel = tk.PhotoImage(width=100, height=100)
image_white_checker, image_black_checker = PhotoImage(file="res\\white.png"), PhotoImage(file="res\\black.png")
image_white_qween, image_black_qween = PhotoImage(file="res\\white_qween_image.png"), PhotoImage(
    file="res\\black_qween_image.png")

board_frame = Frame(root, bd=0)
board_frame.grid(row=0, column=0, rowspan=8, columnspan=8, sticky=NW)

gaming_field = [
    [0, 1, 0, 1, 0, 1, 0, 1],
    [1, 0, 1, 0, 1, 0, 1, 0],
    [0, 1, 0, 1, 0, 1, 0, 1],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [-1, 0, -1, 0, -1, 0, -1, 0],
    [0, -1, 0, -1, 0, -1, 0, -1],
    [-1, 0, -1, 0, -1, 0, -1, 0]
]


old_field = copy.deepcopy(gaming_field)

score_field = [
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0]
]

move_field = [
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
]


x1, y1, x2, y2= 0, 0, 0, 0
multiple_move, max_score, current_player = False, 0, -1
enemy_bot = True
restart_button = None
best_moves = []
best_move = []
delete_enemy = []
s_l = tk.StringVar(value="")
s_p = tk.StringVar(value="")
is_button_active = False
count_of_moves = 0
txt = Label(root, text="Для игры введите Ваш логин и пароль\nДля регистрации введите новый логин и пароль",
            font=("Arial", 14, 'bold'))
txt.place(x=80, y=200)

txtl = Label(root, text='Логин', font=("Arial", 14, 'bold'))
txtl.place(x=220, y=260)

login = tk.Entry(root, width=10, bd=3, textvariable=s_l)
login.place(x=300, y=260)

txtp = Label(root, text='Пароль', font=("Arial", 14, 'bold'))
txtp.place(x=220, y=300)

password = tk.Entry(root, width=10, bd=3, textvariable=s_p)
password.place(x=300, y=300)

close_but = tk.Button(root, text="Зарегистрироваться / начать игру", command=regis)
close_but.place(x=200, y=340)

label_game = Label(root, text="", font=("Arial", 10, 'bold'))
label_game.grid(row=8, column=3)
label_current_turn = Label(root, text="", font=("Arial", 10, 'bold'))
label_current_turn.grid(row=8, column=1)


mainloop()
