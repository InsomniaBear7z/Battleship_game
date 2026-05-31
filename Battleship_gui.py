import pygame
import sys
import os
from Battleship_class import Ship, Board, EasyAI, HardAI, place_random_ships

pygame.init()
pygame.mixer.init()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MUSIC_DIR = os.path.join(BASE_DIR, "music")
IMAGE_DIR = os.path.join(BASE_DIR, "image")
HISTORY_FILE = os.path.join(BASE_DIR, "history.txt")

game_settings = {
    "sound": True,
    "music": True,
    "score": 0,
    "difficulty": "Chưa chọn"
}

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return [line.strip() for line in f.readlines()]
    return []

history_data = load_history()

def save_match_history(is_human_win):
    global history_data, game_settings, board_human, board_ai
    human_alive = sum(1 for ship in board_human.ships if not ship.isSunk())
    ai_alive = sum(1 for ship in board_ai.ships if not ship.isSunk())
    diff = game_settings["difficulty"]
    
    if is_human_win:
        result = "THANG"
        ship_diff = human_alive  
        score_change = 200 if diff == "Kho" else 100
    else:
        result = "THUA"
        ship_diff = ai_alive     
        score_change = -100 if diff == "Kho" else -50
        
    game_settings["score"] += score_change
    record = f"KQ: {result} | May: {diff.upper()} | Tau con lai: {ship_diff} | Diem: {score_change:+d}"
    
    history_data.insert(0, record)
    if len(history_data) > 7:
        history_data.pop()
        
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        for rec in history_data:
            f.write(rec + "\n")

try:
    pygame.mixer.music.load(os.path.join(MUSIC_DIR, "Battleship music.mp3"))
    pygame.mixer.music.set_volume(0.4) 
    if game_settings["music"]:
        pygame.mixer.music.play(-1) 
except Exception:
    pass

try:
    cannon_sound = pygame.mixer.Sound(os.path.join(MUSIC_DIR, "Cannon sound effect for ships.wav"))
    cannon_sound.set_volume(0.8) 
except Exception:
    cannon_sound = None

monitor_info = pygame.display.Info()
SCREEN_WIDTH = monitor_info.current_w
SCREEN_HEIGHT = monitor_info.current_h
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF)
pygame.display.set_caption("Battleship Game")
clock = pygame.time.Clock()

try:
    bg_image_raw = pygame.image.load(os.path.join(IMAGE_DIR, "pirate_bg.jpg"))
    bg_image = pygame.transform.scale(bg_image_raw, (SCREEN_WIDTH, SCREEN_HEIGHT))
    dark_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    dark_overlay.fill((10, 5, 0))  
    dark_overlay.set_alpha(130)    
    bg_image.blit(dark_overlay, (0, 0))
    has_bg = True
except:
    has_bg = False

try:
    ava_human_raw = pygame.image.load(os.path.join(IMAGE_DIR, "ava_human.png")).convert_alpha()
    ava_human = pygame.transform.scale(ava_human_raw, (80, 80))
except:
    ava_human = None

try:
    ava_ai_raw = pygame.image.load(os.path.join(IMAGE_DIR, "ava_ai.png")).convert_alpha()
    ava_ai = pygame.transform.scale(ava_ai_raw, (80, 80))
except:
    ava_ai = None

try:
    ship_base_raw = pygame.image.load(os.path.join(IMAGE_DIR, "ship.png")).convert_alpha()
except:
    ship_base_raw = None

COLOR_BG = (15, 10, 10)         
COLOR_PANEL = (30, 15, 10, 200) 
COLOR_TEXT = (255, 215, 0)      
COLOR_BTN = (105, 20, 20)       
COLOR_HOVER = (165, 42, 42)     
COLOR_ACTIVE = (218, 165, 32)   
COLOR_SHIP = (139, 69, 19)      
COLOR_HIT = (255, 69, 0)        
COLOR_MISS = (173, 216, 230)    

font_title = pygame.font.SysFont("algerian", int(SCREEN_HEIGHT * 0.06), bold=True)
font_menu = pygame.font.SysFont("algerian", int(SCREEN_HEIGHT * 0.035), bold=True)
font_sub = pygame.font.SysFont("arial", int(SCREEN_HEIGHT * 0.025), bold=True) 

current_state = 'MAIN'
board_human = None
board_ai = None
ai_player = None
current_turn = "HUMAN"
game_over = False
winner_text = ""
ai_wait_time = 0

CELL_SIZE = int(SCREEN_HEIGHT * 0.052) 
GRID_SIZE_PX = 10 * CELL_SIZE

GRID_OFFSET_X_HUMAN = (SCREEN_WIDTH // 2) - GRID_SIZE_PX - int(SCREEN_WIDTH * 0.06)
GRID_OFFSET_X_AI = (SCREEN_WIDTH // 2) + int(SCREEN_WIDTH * 0.06)
GRID_OFFSET_Y = (SCREEN_HEIGHT // 2) - (GRID_SIZE_PX // 2) - 20

placement_sizes = [5, 4, 3, 3, 2, "2x2"]
placement_index = 0          
placement_horizontal = True  

def draw_button(text, x, y, w, h, inactive_color, active_color, action=None):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    if x < mouse[0] < x + w and y < mouse[1] < y + h:
        pygame.draw.rect(screen, active_color, (x, y, w, h), border_radius=12)
        if click[0] == 1 and action is not None:
            pygame.time.delay(250) 
            return action()
    else:
        pygame.draw.rect(screen, inactive_color, (x, y, w, h), border_radius=12)
    text_surf = font_menu.render(text, True, COLOR_TEXT)
    text_rect = text_surf.get_rect(center=((x + w/2), (y + h/2)))
    screen.blit(text_surf, text_rect)

def set_state(state_name):
    global current_state
    current_state = state_name

def toggle_sound(): 
    game_settings["sound"] = not game_settings["sound"]

def toggle_music(): 
    game_settings["music"] = not game_settings["music"]
    if game_settings["music"]:
        pygame.mixer.music.unpause()
    else:
        pygame.mixer.music.pause()

def reset_score(): game_settings["score"] = 0

def start_game(diff):
    global board_human, board_ai, ai_player, current_turn, game_over, winner_text, placement_index, ai_wait_time
    game_settings["difficulty"] = diff
    board_human = Board() 
    board_ai = Board()
    place_random_ships(board_ai) 
    if diff == "Kho":
        ai_player = HardAI("AI Khó", board_ai)
    else:
        ai_player = EasyAI("AI Dễ", board_ai)
    current_turn = "HUMAN"
    game_over = False
    winner_text = ""
    placement_index = 0 
    ai_wait_time = 0
    set_state('PLACEMENT')

def draw_main_menu():
    panel_w, panel_h = int(SCREEN_WIDTH * 0.4), int(SCREEN_HEIGHT * 0.65)
    panel_x, panel_y = (SCREEN_WIDTH // 2) - (panel_w // 2), (SCREEN_HEIGHT // 2) - (panel_h // 2) + 30
    s = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
    s.fill(COLOR_PANEL)
    screen.blit(s, (panel_x, panel_y))
    pygame.draw.rect(screen, COLOR_ACTIVE, (panel_x, panel_y, panel_w, panel_h), 2, border_radius=4)
    title_surf = font_title.render("BAN TAU CHIEN", True, COLOR_TEXT)
    screen.blit(title_surf, (SCREEN_WIDTH//2 - title_surf.get_width()//2, panel_y - int(SCREEN_HEIGHT * 0.12)))
    
    btn_w, btn_h = int(panel_w * 0.7), int(SCREEN_HEIGHT * 0.08)
    btn_x = (SCREEN_WIDTH // 2) - (btn_w // 2)
    start_y = panel_y + int(panel_h * 0.1)
    gap = btn_h + int(SCREEN_HEIGHT * 0.03)

    draw_button("CHOI GAME", btn_x, start_y, btn_w, btn_h, COLOR_BTN, COLOR_HOVER, lambda: set_state('DIFFICULTY'))
    draw_button("LICH SU", btn_x, start_y + gap, btn_w, btn_h, COLOR_BTN, COLOR_HOVER, lambda: set_state('HISTORY'))
    draw_button("CAU HINH", btn_x, start_y + gap*2, btn_w, btn_h, COLOR_BTN, COLOR_HOVER, lambda: set_state('SETTINGS'))
    draw_button("THOAT GAME", btn_x, start_y + gap*3, btn_w, btn_h, (185, 28, 28), (220, 38, 38), sys.exit)

def draw_difficulty_menu():
    panel_w, panel_h = int(SCREEN_WIDTH * 0.4), int(SCREEN_HEIGHT * 0.5)
    panel_x, panel_y = (SCREEN_WIDTH // 2) - (panel_w // 2), (SCREEN_HEIGHT // 2) - (panel_h // 2) + 40
    s = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
    s.fill(COLOR_PANEL)
    screen.blit(s, (panel_x, panel_y))
    pygame.draw.rect(screen, COLOR_ACTIVE, (panel_x, panel_y, panel_w, panel_h), 2, border_radius=4)
    title_surf = font_title.render("CHON DO KHO", True, COLOR_TEXT)
    screen.blit(title_surf, (SCREEN_WIDTH//2 - title_surf.get_width()//2, panel_y - int(SCREEN_HEIGHT * 0.12)))
    
    btn_w, btn_h = int(panel_w * 0.7), int(SCREEN_HEIGHT * 0.08)
    btn_x = (SCREEN_WIDTH // 2) - (btn_w // 2)
    draw_button("DE (Easy AI)", btn_x, panel_y + int(panel_h * 0.15), btn_w, btn_h, COLOR_BTN, COLOR_HOVER, lambda: start_game("De"))
    draw_button("KHO (Hard AI)", btn_x, panel_y + int(panel_h * 0.4), btn_w, btn_h, COLOR_BTN, COLOR_HOVER, lambda: start_game("Kho"))
    draw_button("QUAY LAI", btn_x, panel_y + int(panel_h * 0.7), btn_w, btn_h, COLOR_SHIP, COLOR_HOVER, lambda: set_state('MAIN'))

def draw_settings_menu():
    panel_w, panel_h = int(SCREEN_WIDTH * 0.5), int(SCREEN_HEIGHT * 0.6)
    panel_x, panel_y = (SCREEN_WIDTH // 2) - (panel_w // 2), (SCREEN_HEIGHT // 2) - (panel_h // 2) + 40
    s = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
    s.fill(COLOR_PANEL)
    screen.blit(s, (panel_x, panel_y))
    pygame.draw.rect(screen, COLOR_ACTIVE, (panel_x, panel_y, panel_w, panel_h), 2, border_radius=4)
    title_surf = font_title.render("CAU HINH TRO CHOI", True, COLOR_TEXT)
    screen.blit(title_surf, (SCREEN_WIDTH//2 - title_surf.get_width()//2, panel_y - int(SCREEN_HEIGHT * 0.12)))
    
    sound_txt = f"AM THANH: {'BAT' if game_settings['sound'] else 'TAT'}"
    music_txt = f"NHAC NEN: {'BAT' if game_settings['music'] else 'TAT'}"
    score_txt = f"DIEM SO: {game_settings['score']}"
    btn_w, btn_h = int(panel_w * 0.7), int(SCREEN_HEIGHT * 0.07)
    btn_x = (SCREEN_WIDTH // 2) - (btn_w // 2)
    
    draw_button(sound_txt, btn_x, panel_y + int(panel_h * 0.12), btn_w, btn_h, COLOR_BTN, COLOR_HOVER, toggle_sound)
    draw_button(music_txt, btn_x, panel_y + int(panel_h * 0.3), btn_w, btn_h, COLOR_BTN, COLOR_HOVER, toggle_music)
    draw_button("RESET DIEM SO", btn_x, panel_y + int(panel_h * 0.48), btn_w, btn_h, COLOR_ACTIVE, COLOR_HOVER, reset_score)
    score_surf = font_sub.render(score_txt, True, COLOR_TEXT)
    screen.blit(score_surf, (SCREEN_WIDTH//2 - score_surf.get_width()//2, panel_y + int(panel_h * 0.68)))
    draw_button("QUAY LAI", btn_x, panel_y + int(panel_h * 0.8), btn_w, btn_h, COLOR_SHIP, COLOR_HOVER, lambda: set_state('MAIN'))

def draw_history_menu():
    panel_w, panel_h = int(SCREEN_WIDTH * 0.6), int(SCREEN_HEIGHT * 0.5)
    panel_x, panel_y = (SCREEN_WIDTH // 2) - (panel_w // 2), (SCREEN_HEIGHT // 2) - (panel_h // 2) + 40
    s = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
    s.fill(COLOR_PANEL)
    screen.blit(s, (panel_x, panel_y))
    pygame.draw.rect(screen, COLOR_ACTIVE, (panel_x, panel_y, panel_w, panel_h), 2, border_radius=4)
    title_surf = font_title.render("LICH SU TRAN CHIEN", True, COLOR_TEXT)
    screen.blit(title_surf, (SCREEN_WIDTH//2 - title_surf.get_width()//2, panel_y - int(SCREEN_HEIGHT * 0.12)))
    
    for i, records in enumerate(history_data):
        rec_surf = font_sub.render(records, True, COLOR_TEXT)
        screen.blit(rec_surf, (panel_x + 30, panel_y + 80 + i * 45))
        
    btn_w, btn_h = int(panel_w * 0.4), int(SCREEN_HEIGHT * 0.07)
    draw_button("QUAY LAI", SCREEN_WIDTH//2 - btn_w//2, panel_y + panel_h - btn_h - 30, btn_w, btn_h, COLOR_SHIP, COLOR_HOVER, lambda: set_state('MAIN'))

def draw_grid(board, offset_x, offset_y, hide_ships):
    pygame.draw.rect(screen, COLOR_ACTIVE, (offset_x - 4, offset_y - 4, GRID_SIZE_PX + 8, GRID_SIZE_PX + 8), 3, border_radius=4)
    grid_bg = pygame.Surface((GRID_SIZE_PX, GRID_SIZE_PX), pygame.SRCALPHA)
    grid_bg.fill((15, 23, 42, 180)) 
    screen.blit(grid_bg, (offset_x, offset_y))

    for x in range(10):
        for y in range(10):
            rect = (offset_x + x * CELL_SIZE, offset_y + y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, (255, 255, 255), rect, 1)

    if not hide_ships and board is not None:
        drawn_ships = [] 
        for ship in board.ships:
            if ship not in drawn_ships:
                min_x = min(p[0] for p in ship.positions)
                max_x = max(p[0] for p in ship.positions)
                min_y = min(p[1] for p in ship.positions)
                max_y = max(p[1] for p in ship.positions)
                
                px_x = offset_x + min_x * CELL_SIZE
                px_y = offset_y + min_y * CELL_SIZE
                px_w = (max_x - min_x + 1) * CELL_SIZE
                px_h = (max_y - min_y + 1) * CELL_SIZE
                
                if ship_base_raw:
                    is_horizontal = (max_x > min_x) and (max_y == min_y)
                    if is_horizontal:
                        rotated_ship = pygame.transform.rotate(ship_base_raw, -90)
                        scaled_ship = pygame.transform.scale(rotated_ship, (px_w - 4, px_h - 4))
                    else:
                        scaled_ship = pygame.transform.scale(ship_base_raw, (px_w - 4, px_h - 4))
                    screen.blit(scaled_ship, (px_x + 2, px_y + 2))
                else:
                    for (sx, sy) in ship.positions:
                        rect_fallback = (offset_x + sx * CELL_SIZE, offset_y + sy * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                        pygame.draw.rect(screen, COLOR_SHIP, (rect_fallback[0]+4, rect_fallback[1]+4, CELL_SIZE-8, CELL_SIZE-8), border_radius=4)
                drawn_ships.append(ship)

    if board is not None:
        for (x, y) in board.hits_coords:
            center = (offset_x + x * CELL_SIZE + CELL_SIZE//2, offset_y + y * CELL_SIZE + CELL_SIZE//2)
            pygame.draw.circle(screen, COLOR_HIT, center, CELL_SIZE//2 - 4)
        for (x, y) in board.miss_coords:
            center = (offset_x + x * CELL_SIZE + CELL_SIZE//2, offset_y + y * CELL_SIZE + CELL_SIZE//2)
            pygame.draw.circle(screen, COLOR_MISS, center, CELL_SIZE//2 - int(CELL_SIZE*0.3))

def draw_placement_state():
    title_surf = font_title.render("DAT TAU", True, COLOR_ACTIVE)
    screen.blit(title_surf, (SCREEN_WIDTH//2 - title_surf.get_width()//2, int(SCREEN_HEIGHT * 0.04)))
    
    info_x = GRID_OFFSET_X_HUMAN + GRID_SIZE_PX + int(SCREEN_WIDTH * 0.08)
    current_size = placement_sizes[placement_index]
    size_str = "Khối vuông 2x2" if current_size == "2x2" else f"{current_size} ô liền"
    
    guide_txt1 = font_menu.render(f"Loai tau: {size_str}", True, COLOR_TEXT)
    guide_txt2 = font_sub.render("Nhan [SPACE] de XOAY huong", True, COLOR_ACTIVE)
    guide_txt3 = font_menu.render(f"Huong: {'NGANG' if placement_horizontal else 'DOC'}", True, COLOR_TEXT)
    
    screen.blit(guide_txt1, (info_x, GRID_OFFSET_Y + 50))
    if current_size != "2x2":
        screen.blit(guide_txt2, (info_x, GRID_OFFSET_Y + 110))
        screen.blit(guide_txt3, (info_x, GRID_OFFSET_Y + 160))
    
    draw_grid(board_human, GRID_OFFSET_X_HUMAN, GRID_OFFSET_Y, hide_ships=False)
    
    mouse_x, mouse_y = pygame.mouse.get_pos()
    if GRID_OFFSET_X_HUMAN <= mouse_x < GRID_OFFSET_X_HUMAN + GRID_SIZE_PX and \
       GRID_OFFSET_Y <= mouse_y < GRID_OFFSET_Y + GRID_SIZE_PX:
        gx = (mouse_x - GRID_OFFSET_X_HUMAN) // CELL_SIZE
        gy = (mouse_y - GRID_OFFSET_Y) // CELL_SIZE
        size = placement_sizes[placement_index]
        
        temp_positions = []
        is_valid = True
        
        if size == "2x2":
            if gx + 1 < 10 and gy + 1 < 10:
                temp_positions = [(gx, gy), (gx + 1, gy), (gx, gy + 1), (gx + 1, gy + 1)]
            else: is_valid = False
        else:
            if placement_horizontal:
                if gx + size <= 10:
                    temp_positions = [(gx + i, gy) for i in range(size)]
                else: is_valid = False
            else:
                if gy + size <= 10:
                    temp_positions = [(gx, gy + i) for i in range(size)]
                else: is_valid = False
            
        if is_valid:
            for ship in board_human.ships:
                if any(p in ship.positions for p in temp_positions):
                    is_valid = False
                    break
                    
        preview_color = COLOR_ACTIVE if is_valid else COLOR_HIT
        for (tx, ty) in temp_positions:
            px = GRID_OFFSET_X_HUMAN + tx * CELL_SIZE + 4
            py = GRID_OFFSET_Y + ty * CELL_SIZE + 4
            s = pygame.Surface((CELL_SIZE-8, CELL_SIZE-8))
            s.set_alpha(180)
            s.fill(preview_color)
            screen.blit(s, (px, py))

    btn_w, btn_h = int(SCREEN_WIDTH * 0.2), int(SCREEN_HEIGHT * 0.07)
    draw_button("MENU", SCREEN_WIDTH//2 - btn_w//2, SCREEN_HEIGHT - btn_h - 40, btn_w, btn_h, COLOR_SHIP, COLOR_HOVER, lambda: set_state('MAIN'))

def draw_playing_state():
    title_surf = font_title.render(f"BATTLESHIP: {game_settings['difficulty'].upper()}", True, COLOR_ACTIVE)
    screen.blit(title_surf, (SCREEN_WIDTH//2 - title_surf.get_width()//2, int(SCREEN_HEIGHT * 0.04)))

    txt_human = font_menu.render("BAN DO CUA BAN", True, COLOR_TEXT)
    txt_human_x = GRID_OFFSET_X_HUMAN + (GRID_SIZE_PX//2) - txt_human.get_width()//2
    screen.blit(txt_human, (txt_human_x, GRID_OFFSET_Y - 40))
    if ava_human:
        screen.blit(ava_human, (txt_human_x - 90, GRID_OFFSET_Y - 70))

    txt_ai = font_menu.render("BAN DO CUA AI", True, COLOR_HIT)
    txt_ai_x = GRID_OFFSET_X_AI + (GRID_SIZE_PX//2) - txt_ai.get_width()//2
    screen.blit(txt_ai, (txt_ai_x, GRID_OFFSET_Y - 40))
    if ava_ai:
        screen.blit(ava_ai, (txt_ai_x + txt_ai.get_width() + 10, GRID_OFFSET_Y - 70))

    draw_grid(board_human, GRID_OFFSET_X_HUMAN, GRID_OFFSET_Y, hide_ships=False)
    draw_grid(board_ai, GRID_OFFSET_X_AI, GRID_OFFSET_Y, hide_ships=True)

    if game_over:
        msg_surf = font_title.render(winner_text, True, COLOR_TEXT)
        screen.blit(msg_surf, (SCREEN_WIDTH//2 - msg_surf.get_width()//2, SCREEN_HEIGHT - int(SCREEN_HEIGHT * 0.22)))
    else:
        turn_txt = "LUOT CUA BAN" if current_turn == "HUMAN" else "LUOT CUA AI..."
        turn_color = COLOR_ACTIVE if current_turn == "HUMAN" else COLOR_MISS
        turn_surf = font_menu.render(turn_txt, True, turn_color)
        screen.blit(turn_surf, (SCREEN_WIDTH//2 - turn_surf.get_width()//2, SCREEN_HEIGHT - int(SCREEN_HEIGHT * 0.22)))

    btn_w, btn_h = int(SCREEN_WIDTH * 0.15), int(SCREEN_HEIGHT * 0.07)
    draw_button("THOAT", SCREEN_WIDTH//2 - btn_w//2, SCREEN_HEIGHT - btn_h - 40, btn_w, btn_h, COLOR_BTN, COLOR_HOVER, lambda: set_state('MAIN'))


running = True
while running:
    if has_bg:
        screen.blit(bg_image, (0, 0))
    else:
        screen.fill(COLOR_BG)
        
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            
        if current_state == 'PLACEMENT':
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    placement_horizontal = not placement_horizontal
                    
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                if GRID_OFFSET_X_HUMAN <= mx < GRID_OFFSET_X_HUMAN + GRID_SIZE_PX and \
                   GRID_OFFSET_Y <= my < GRID_OFFSET_Y + GRID_SIZE_PX:
                    gx = (mx - GRID_OFFSET_X_HUMAN) // CELL_SIZE
                    gy = (my - GRID_OFFSET_Y) // CELL_SIZE
                    size = placement_sizes[placement_index]
                    
                    positions = []
                    is_valid = True
                    
                    if size == "2x2":
                        if gx + 1 < 10 and gy + 1 < 10:
                            positions = [(gx, gy), (gx + 1, gy), (gx, gy + 1), (gx + 1, gy + 1)]
                        else: is_valid = False
                    else:
                        if placement_horizontal:
                            if gx + size <= 10:
                                positions = [(gx + i, gy) for i in range(size)]
                            else: is_valid = False
                        else:
                            if gy + size <= 10:
                                positions = [(gx, gy + i) for i in range(size)]
                            else: is_valid = False
                        
                    if is_valid:
                        for ship in board_human.ships:
                            if any(p in ship.positions for p in positions):
                                is_valid = False
                                break
                                
                    if is_valid:
                        actual_size = 4 if size == "2x2" else size
                        board_human.add_ship(Ship(actual_size, positions))
                        placement_index += 1
                        if placement_index >= len(placement_sizes):
                            set_state('PLAYING')
        
        if current_state == 'PLAYING' and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if not game_over and current_turn == "HUMAN":
                mx, my = event.pos
                if GRID_OFFSET_X_AI <= mx < GRID_OFFSET_X_AI + GRID_SIZE_PX and \
                   GRID_OFFSET_Y <= my < GRID_OFFSET_Y + GRID_SIZE_PX:
                    grid_x = (mx - GRID_OFFSET_X_AI) // CELL_SIZE
                    grid_y = (my - GRID_OFFSET_Y) // CELL_SIZE
                    
                    if (grid_x, grid_y) not in board_ai.shots:
                        if game_settings["sound"] and cannon_sound:
                            cannon_sound.play()
                        board_ai.receive_shot(grid_x, grid_y)
                        if board_ai.all_ships_sunk():
                            game_over = True
                            winner_text = "BAN DA THANG!"
                            save_match_history(is_human_win=True)
                        else:
                            current_turn = "AI_WAITING" 
                            ai_wait_time = pygame.time.get_ticks() + 1500

    if current_state == 'PLAYING' and current_turn == "AI_WAITING" and not game_over:
        if pygame.time.get_ticks() >= ai_wait_time:
            if game_settings["sound"] and cannon_sound:
                cannon_sound.play()
            ai_player.takeShot(board_human)
            if board_human.all_ships_sunk():
                game_over = True
                winner_text = "AI DA THANG!"
                save_match_history(is_human_win=False)
            else:
                current_turn = "HUMAN"
            
    if current_state == 'MAIN':
        draw_main_menu()
    elif current_state == 'DIFFICULTY':
        draw_difficulty_menu()
    elif current_state == 'SETTINGS':
        draw_settings_menu()
    elif current_state == 'HISTORY':
        draw_history_menu()
    elif current_state == 'PLACEMENT':
        draw_placement_state()
    elif current_state == 'PLAYING':
        draw_playing_state()
        
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
