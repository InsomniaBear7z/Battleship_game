from Battleship_class import Board, EasyAI, place_random_ships

def main():
    board_human = Board()
    board_ai = Board()
    place_random_ships(board_human)
    place_random_ships(board_ai)
    ai_player = EasyAI("AI", board_ai)

    print("--- BATTLESHIP CONSOLE ---")
    while True:
        try:
            x = int(input("Nhap toa do X (0-9): "))
            y = int(input("Nhap toa do Y (0-9): "))
            if 0 <= x < 10 and 0 <= y < 10:
                if (x, y) not in board_ai.shots:
                    is_hit = board_ai.receive_shot(x, y)
                    print("TRUNG!" if is_hit else "TRUOT!")
                    if board_ai.all_ships_sunk():
                        print("BAN DA THANG!")
                        break
                    
                    ai_player.takeShot(board_human)
                    if board_human.all_ships_sunk():
                        print("AI DA THANG!")
                        break
                else:
                    print("Da ban o nay!")
            else:
                print("Toa do khong hop le!")
        except ValueError:
            print("Nhap so nguyen!")

if __name__ == "__main__":
    main()
