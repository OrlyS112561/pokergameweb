from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
import random as rd
import datetime

counter = 0
wins = 0
switch = True
player_stack = 0
straight_list = [[1,2,3,4,5],[2,3,4,5,6],[3,4,5,6,7],[4,5,6,7,8],[5,6,7,8,9],[6,7,8,9,10],
                 [7,8,9,10,11],[8,9,10,11,12],[9,10,11,12,13],[10,11,12,13,1]]


#check if board is quads
def check_board_quads(player1, player2, board):
    is_board_quads = False
    kicker = 0
    for i in range(0,14):
        if board.count(i) == 4:
            for k in range(0,14):
                if board.count(k) == 1:
                    kicker = k
                    if kicker == 1:
                        is_board_quads = True
                    elif player1[0] == 1 or player1[1] == 1 or player2[0] == 1 or player2[1] == 1:
                        is_board_quads = False
                    elif player1[0] <= kicker and player1[1] <= kicker:
                        if player2[0] <= kicker and player2[1] <= kicker:
                            is_board_quads = True
                            return is_board_quads
    return is_board_quads

# check if board is fullhouse
def check_board_fullhouse(player1, player2, board):
    is_board_fullhouse = False
    card3ofakind = 0
    for i in range(0,14):
        if board.count(i) == 3:
            card3ofakind = i
            for i in range(0,14):
                if board.count(i) == 2:
                    card2ofakind = i
                    if player1[0] == card3ofakind or player1[1] == card3ofakind or player2[0] == card3ofakind or player2[1] == card3ofakind:
                            is_board_fullhouse = False
                    elif player1[0] == card2ofakind and player1[0] > card3ofakind or player1[1] == card2ofakind and player1[1] > card3ofakind or player2[0] == card2ofakind and player2[0] > card3ofakind or player2[1] == card2ofakind and player2[1] > card3ofakind:
                            is_board_fullhouse = False
                    else:
                        is_board_fullhouse = True
                        break
            break
    return is_board_fullhouse

# check if board is 3 of a kind
def check_board_3ofakind(player1, player2, board):
    is_board_3ofakind = False
    card_3ofakind = 0
    if board.count(player1[0]) >= 1 or board.count(player1[1]) >= 1 or board.count(player2[0]) >= 1 or board.count(player2[1]) >= 1:
        return is_board_3ofakind
    for i in range(1,14):
        if board.count(i) == 3:
            card_3ofakind = i
            card_not3ofakind = []
            for i in range(1,14):
                if i == card_3ofakind:
                    pass
                else:
                    if board.count(i) == 2:
                        return is_board_3ofakind
                    else:
                        if board.count(i) == 1:
                            card_not3ofakind.append(i)
            for i in card_not3ofakind:
                if player1[0] > i or player1[1] > i or player2[0] > i or player2[1] > 0:
                    return is_board_3ofakind
            is_board_3ofakind = True
    return is_board_3ofakind

# check if board is 2 pairs
def check_board_2pairs(player1, player2, board):
    is_board_2pairs = False
    card1_2ofakind = 0
    for i in range(0,14):
        if board.count(i) == 2:
            card1_2ofakind = i
            card2_2ofakind = 0
            for i in range(0,14):
                if i == card1_2ofakind:
                    pass
                else:
                    if board.count(i) == 2:
                        card2_2ofakind = i
                        for i in range(0,14):
                            if board.count(i) == 1:
                                kicker = i
                                if player1.count(card1_2ofakind) >= 1 or player2.count(card1_2ofakind):
                                    is_board_2pairs = False
                                    break
                                elif player1.count(card2_2ofakind) >= 1 or player2.count(card2_2ofakind):
                                        is_board_2pairs = False
                                        break
                                else:
                                    if player1[0] == player1[1] and player1[0] > card1_2ofakind:
                                        is_board_2pairs = False
                                        break
                                    elif player1[0] == player1[1] and player1[0] == 1:
                                        is_board_2pairs = False
                                        break
                                    elif player1[0] == player1[1] and player1[0] > card2_2ofakind:
                                        is_board_2pairs = False
                                        break
                                    elif player2[0] == player2[1] and player2[0] > card1_2ofakind:
                                        is_board_2pairs = False
                                        break
                                    elif player2[0] == player2[1] and player2[0] == 1:
                                        is_board_2pairs = False
                                        break
                                    elif player2[0] == player2[1] and player2[0] > card2_2ofakind:
                                        is_board_2pairs = False
                                        break
                                    else:
                                        if player1[0] == kicker or player1[1] == kicker:
                                            if kicker > card1_2ofakind or kicker > card2_2ofakind or kicker == 1:
                                                is_board_2pairs = False
                                                break
                                        elif player2[0] == kicker or player2[1] == kicker:
                                            if kicker > card1_2ofakind or kicker > card2_2ofakind or kicker == 1:
                                                is_board_2pairs = False
                                                break
                                        elif kicker == 1:
                                            is_board_2pairs = True
                                            break
                                        elif player1.count(1) == 1 or player2.count(1) == 1:
                                            is_board_2pairs = False
                                            break
                                        elif player1[0] < kicker and player1[1] < kicker and player2[0] < kicker and player2[1] < kicker:
                                            is_board_2pairs = True
                                            break
    return is_board_2pairs


#check if board is flush
def check_board_flush(player1, player2, board):
    is_board_flush = False
    shades_in_board = []
    board_value =[]
    for shade in board:
        shades_in_board.append(shade[1])
        board_value.append(shade[0])
    if shades_in_board.count("S") == 5:
        if player1[0][1] == "S" and player1[0][0] > min(board_value):
            is_board_flush = False
        elif player1[1][1] == "S" and player1[1][0] > min(board_value):
            is_board_flush = False
        elif player2[0][1] == "S" and player2[0][0] > min(board_value):
            is_board_flush = False
        elif player2[1][1] == "S" and player2[1][0] > min(board_value):
            is_board_flush = False
        else:
            is_board_flush = True
    elif shades_in_board.count("H") == 5:
        if player1[0][1] == "H" and player1[0][0] > min(board_value):
            is_board_flush = False
        elif player1[1][1] == "H" and player1[1][0] > min(board_value):
            is_board_flush = False
        elif player2[0][1] == "H" and player2[0][0] > min(board_value):
            is_board_flush = False
        elif player2[1][1] == "H" and player2[1][0] > min(board_value):
            is_board_flush = False
        else:
            is_board_flush = True
    elif shades_in_board.count("C") == 5:
        if player1[0][1] == "C" and player1[0][0] > min(board_value):
            is_board_flush = False
        elif player1[1][1] == "C" and player1[1][0] > min(board_value):
            is_board_flush = False
        elif player2[0][1] == "C" and player2[0][0] > min(board_value):
            is_board_flush = False
        elif player2[1][1] == "C" and player2[1][0] > min(board_value):
            is_board_flush = False
        else:
            is_board_flush = True
    elif shades_in_board.count("D") == 5:
        if player1[0][1] == "D" and player1[0][0] > min(board_value):
            is_board_flush = False
        elif player1[1][1] == "D" and player1[1][0] > min(board_value):
            is_board_flush = False
        elif player2[0][1] == "D" and player2[0][0] > min(board_value):
            is_board_flush = False
        elif player2[1][1] == "D" and player2[1][0] > min(board_value):
            is_board_flush = False
        else:
            is_board_flush = True
    return is_board_flush

#check if board is straight
def check_board_straight(player1, player2, board):
    is_board_straight = False
    for i in range(1,14):
        if board.count(i) == 2:
            return is_board_straight
    for comb in reversed(straight_list):
        count = 0
        for card in board:
            if comb.count(card) == 1:
                count += 1
        if count == 5:
            if max(comb) == 13 and min(comb) == 9:
                if min(player1) != 1 and min(player2) != 1:
                    is_board_straight = True
            else:
                if max(player1) != max(comb) + 1 and max(player2) != max(comb) + 1:
                    is_board_staight = True
    return is_board_straight

def straight_flush_dict():
    letters = ['S', 'C', 'H', 'D']
    sfl = []
    sfl_dict = {}
    ctr = 0
    for letter in letters:
        for i in range(0, 10):
            sfl = []
            for _ in range(1, 6):
                num = _ + i
                if num == 1 or num == 14:
                    num = 'A'
                    y = num + letter
                elif num == 11:
                    num = 'J'
                    y = num + letter
                elif num == 12:
                    num = 'Q'
                    y = num + letter
                elif num == 13:
                    num = 'K'
                    y = num + letter
                else:
                    y = str(_ + i) + letter
                sfl.append(y)
            sfl_dict[i + ctr] = sfl
        ctr += 10
    return sfl_dict

#check if hand is straight_flush
def check_if_straight_flush(hand, board):
    is_straight_flush = False
    sfl_dict = straight_flush_dict()
    a_set = set(hand)
    b_set = set(board)
    for i in reversed(range(40)):
        c_set = sfl_dict[i]
        hand_set = (a_set.intersection(c_set))
        board_set = (b_set.intersection(c_set))
        strflush = hand_set.union(board_set)
        if len(board_set) == 5 and len(strflush) == 5:
            straight_flush = [is_straight_flush]
            return straight_flush
            break
        if len(hand_set) > 0:
            if len(board_set) < 5 and len(strflush.intersection(c_set)) == 5:
                is_straight_flush = True
                straight_flush_cards = []
                straight_flush_cards = c_set
                for card in straight_flush_cards:
                    if card[-1] == 'S':
                        flush_shade = '♠'
                    if card[-1] == 'C':
                        flush_shade = '♣'
                    if card[-1] == 'H':
                        flush_shade = '❤'
                    if card[-1] == 'D':
                        flush_shade = '♦'
                straight_flush = [is_straight_flush, straight_flush_cards, flush_shade]
                return straight_flush
    straight_flush = [is_straight_flush]
    return straight_flush

#check if a hand is flush
def check_if_flush(hand, board):
    is_flush = False
    hand_shade = []
    board_shade = []
    for card in hand:
        shade = card[-1]
        hand_shade.append(shade)
    for card in board:
        shade = card[-1]
        board_shade.append(shade)
    if hand_shade.count('D') >=1 and board_shade.count('D') + hand_shade.count('D') >= 5:
        is_flush = True
    if hand_shade.count('H') >=1 and board_shade.count('H') + hand_shade.count('H') >= 5:
        is_flush = True
    if hand_shade.count('S') >=1 and board_shade.count('S') + hand_shade.count('S') >= 5:
        is_flush = True
    if hand_shade.count('C') >=1 and board_shade.count('C') + hand_shade.count('C') >= 5:
        is_flush = True
    return is_flush

def get_player_flush(hand, board):
    hand_shade = []
    board_shade = []
    for card in hand:
        shade = card[-1]
        hand_shade.append(shade)
    for card in board:
        shade = card[-1]
        board_shade.append(shade)
    if hand_shade.count('S') >=1 and board_shade.count('S') + hand_shade.count('S') >= 5:
        player_flush = '♠'
    if hand_shade.count('H') >=1 and board_shade.count('H') + hand_shade.count('H') >= 5:
        player_flush = '❤'
    if hand_shade.count('C') >=1 and board_shade.count('C') + hand_shade.count('C') >= 5:
        player_flush = '♣'
    if hand_shade.count('D') >=1 and board_shade.count('D') + hand_shade.count('D') >= 5:
        player_flush = '♦'
    return player_flush

def compare_flush_cards(player1, player2, flush):
    if flush == '♠':
        flush = 'S'
    if flush == '❤':
        flush = 'H'
    if flush == '♣':
        flush = 'C'
    if flush == '♦':
        flush = 'D'
    player1_flush = []
    for card in player1:
        if card[-1] == flush:
            if len(card) == 3:
                player1_flush.append(int(card[0:2]))
            else:
                player1_flush.append(int(card[0]))
    player2_flush = []
    for card in player2:
        if card[-1] == flush:
            if card[-1] == flush:
                if len(card) == 3:
                    player2_flush.append(int(card[0:2]))
                else:
                    player1_flush.append(int(card[0]))
    print(player1_flush, player2_flush)
    if max(player1_flush) > max(player2_flush):
        winner = 'Player'
    elif max(player1_flush) < max(player2_flush):
        winner = 'Dealer'
    else:
        winner = "It's a draw!"
    return winner

def check_if_straight(hand_value, board_value):
    is_straight = False
    for list in reversed(straight_list):
        global straight_hand
        straight_hand = []
        for h in hand_value:
            if h in straight_hand:
                pass
            elif h in list:
                straight_hand.append(h)
        for b in board_value:
            if b in straight_hand:
                pass
            elif b in list:
                straight_hand.append(b)
        if len(straight_hand) >= 5:
            is_straight = True
            return is_straight
    return is_straight

def get_player_straight(hand_value, board_value):
    for list in reversed(straight_list):
        global straight_hand
        straight_hand = []
        for h in hand_value:
            if h in straight_hand:
                pass
            elif h in list:
                straight_hand.append(h)
        for b in board_value:
            if b in straight_hand:
                pass
            elif b in list:
                straight_hand.append(b)
        if len(straight_hand) >= 5:
            break
    return straight_hand

def get_high_card_straight(player_straight):
    high_card_straight = 0
    if min(player_straight) == 1 and max(player_straight) == 13:
        high_card_straight = 'A'
    elif max(player_straight) == 12:
        high_card_straight = 'Q'
    elif max(player_straight) == 11:
        high_card_straight = 'J'
    elif max(player_straight) == 13:
        high_card_straight = 'K'
    else:
        high_card_straight = max(player_straight)
    return high_card_straight

def get_low_card_straight(player_straight):
    low_card_straight = min(player_straight)
    high_card_straight = max(player_straight)
    if low_card_straight == 1 and high_card_straight == 13:
        low_card_straight = 10
    elif low_card_straight == 1 and high_card_straight == 5:
        low_card_straight = 'A'
    else:
        low_card_straight = min(player_straight)
    return low_card_straight

def get_card_value(p_hand):
    p_card_value = 0
    if len(p_hand) == 3:
        p_card_value = 10
    elif p_hand[0] == 'J':
        p_card_value = 11
    elif p_hand[0] == 'Q':
        p_card_value = 12
    elif p_hand[0] == 'K':
        p_card_value = 13
    elif p_hand[0] == 'A':
        p_card_value = 1
    else:
        p_card_value = int(p_hand[0])
    return p_card_value

# check for quads
def check_if_quads(hand_value, board_value):
    is_quads = False
    if hand_value[0] == hand_value[1]: # pair
        hit_count = board_value.count(hand_value[0])
        if hit_count == 2:
            is_quads = True
            return is_quads
    else:
        for card in hand_value:
            hit_count = board_value.count(card)
            if hit_count == 3:
                is_quads = True
                return is_quads
    return is_quads

#check for fullhouse
def check_if_fullhouse(hand_value, board_value):
    is_fullhouse = False
    if hand_value[0] == hand_value[1]: # pair
        if board_value.count(hand_value[0]) == 1:
            for i in range(1,14):
                if board_value.count(i) >= 2:
                    is_fullhouse = True
                    return is_fullhouse
        else:
            for i in range(1,14):

                if board_value.count(i) == 3:
                    is_fullhouse = True
                    return is_fullhouse
    else:
        for card in hand_value:
            if board_value.count(card) == 2:
                fullhouse_card = card
                for i in reversed(range(1, 14)):
                    if i == fullhouse_card:
                        pass
                    elif board_value.count(i) == 2:
                        is_fullhouse = True
                        return is_fullhouse
                    else:
                        for card in hand_value:
                            if board_value.count(card) == 1:
                                is_fullhouse = True
                                return is_fullhouse
            else:
                if board_value.count(card) == 1:
                    for i in range(1,14):
                        if i == card:
                            pass
                        else:
                            if board_value.count(i) == 3:
                                is_fullhouse = True
                                return is_fullhouse
    return is_fullhouse

def get_fullhouse_card(player_hand, board):
    if player_hand[0] == player_hand[1] and board.count(player_hand[0]) == 1:
        fullhouse_card = player_hand[0]
        for i in reversed(range(1,14)):
            if i == fullhouse_card:
                pass
            elif board.count(i) == 3:
                if player_hand[0] == 1 and i != 1:
                    kicker = i
                elif player_hand[0] !=1 and i == 1:
                    kicker = fullhouse_card
                    fullhouse_card = i
                elif fullhouse_card > i:
                    kicker = i
                else:
                    kicker = fullhouse_card
                    fullhouse_card = i
            elif board.count(i) == 2:
                kicker = i
    else:
        if board.count(max(player_hand)) == 2:
            fullhouse_card = max(player_hand)
            if board.count(min(player_hand)) == 2:
                kicker = min(player_hand)
            else:
                for i in reversed(range(1, 14)):
                    if i == fullhouse_card:
                        pass
                    elif board.count(i) == 3:
                        if i > fullhouse_card:
                            kicker = fullhouse_card
                            fullhouse_card = i
                            break
                    elif board.count(i) == 2 and board.count(min(player_hand)) == 1:
                        if i > min(player_hand):
                            kicker = i
                        else:
                            kicker = min(player_hand)
                        break
                    elif board.count(min(player_hand)) == 1:
                        kicker = min(player_hand)
                        break
                    elif board.count(i) == 2:
                        kicker = i
                        break
        elif board.count(min(player_hand)) == 2:
            fullhouse_card = min(player_hand)
            for i in reversed(range(1, 14)):
                if i == fullhouse_card:
                    pass
                elif board.count(i) == 3:
                    if i > fullhouse_card:
                        kicker = fullhouse_card
                        fullhouse_card = i
                        break
                    else:
                        kicker = i
                        break
                elif board.count(i) == 2 and board.count(max(player_hand)) == 1:
                    if i > max(player_hand):
                        kicker = i
                        break
                    else:
                        kicker = max(player_hand)
                        break
                elif board.count(i) == 2:
                    kicker = i
                    break
                else:
                    if board.count(max(player_hand)) == 1:
                        kicker = max(player_hand)
                        break
        else:
            for i in range(1, 14):
                if board.count(i) == 3:
                    fullhouse_card = i
                    break
            if board.count(max(player_hand)) == 1:
                kicker = max(player_hand)
            else:
                kicker = min(player_hand)
    fullhouse = (fullhouse_card, kicker)
    return fullhouse

#check if 3 of a kind
def check_if_3ofakind(hand_value, board_value):
    is_3ofakind = False
    if hand_value[0] == hand_value[1]: # pair
        hit_count = board_value.count(hand_value[0])
        if hit_count == 1:
            is_3ofakind = True
            return is_3ofakind
    else:
        for card in hand_value:
            hit_count = board_value.count(card)
            if hit_count == 2:
                is_3ofakind = True
                return is_3ofakind
    return is_3ofakind

def get_player_3ofakind(player_hand_value, board_value):
    player_3ofakind = 0
    if player_hand_value[0] == player_hand_value[1]:
        player_3ofakind = player_hand_value[0]
    else:
        for card in player_hand_value:
            if board_value.count(card) == 2:
                player_3ofakind = card
    return player_3ofakind

# check if 2 pairs
def check_if_2pairs(hand_value, board_value):
    is_2pairs = False
    board2pairs = []
    for card in board_value:
        if board_value.count(card) == 2:
            if board2pairs.count(card) == 1:
                pass
            else:
                board2pairs.append(card)
    if hand_value[0] == hand_value[1]:
        if len(board2pairs) >= 1:
            is_2pairs = True
    elif board_value.count(hand_value[0]) == 1 and board_value.count(hand_value[1]) == 1:
        is_2pairs = True
    elif board_value.count(hand_value[0]) == 1 and len(board2pairs) >= 1:
        is_2pairs = True
    elif board_value.count(hand_value[1]) == 1 and len(board2pairs) >= 1:
        is_2pairs = True
    elif len(board2pairs) == 2:
        is_2pairs = True
    return is_2pairs

def get_player_2pairs(hand_value, board_value):
    player_2pairs = []
    board_pairs = []
    for card in board_value:
        if board_value.count(card) == 2:
            if board_pairs.count(card) == 1:
                pass
            else:
                board_pairs.append(card)
    if hand_value[0] == hand_value[1]:
        if min(board_pairs) == 1:
            player_2pairs = [min(board_pairs),hand_value[0]]
        elif hand_value[0] == 1 or hand_value[0] > max(board_pairs):
            player_2pairs = [hand_value[0],max(board_pairs)]
        elif min(board_pairs) == 2:
            if hand_value[0] > min(board_pairs):
                player_2pairs = [max(board_pairs), hand_value[0]]
            else:
                player_2pairs = board_pairs
        else:
            player_2pairs = [board_pairs[0], hand_value[0]]
    elif board_value.count(hand_value[0]) == 1 and board_value.count(hand_value[1]) == 1:
        if len(board_pairs) == 1:
            if min(hand_value) == 1:
                if max(hand_value) > max(board_pairs):
                    player_2pairs = hand_value
                else:
                    player_2pairs = [min(hand_value), max(board_pairs)]
            elif min(board_pairs) == 1:
                print('yo')
                print(min(board_pairs), max(hand_value))
                player_2pairs = [min(board_pairs),max(hand_value)]
            elif max(hand_value) > min(board_pairs):
                if min(hand_value) > min(board_pairs):
                    player_2pairs = hand_value
                else:
                    player_2pairs = [max(hand_value),min(board_pairs)]
            else:
                player_2pairs = [board_pairs[0], max(hand_value)]
        else:
            player_2pairs = hand_value
    elif board_value.count(min(hand_value)) == 1:
        if min(hand_value) == 1:
            player_2pairs = [min(hand_value), max(board_pairs)]
        elif len(board_pairs) == 2:
            if min(board_pairs) == 1:
                if min(hand_value) > max(board_pairs):
                    player_2pairs = [min(board_pairs),min(hand_value)]
                else:
                    player_2pairs = board_pairs
            elif min(hand_value) > max(board_pairs):
                player_2pairs = [min(hand_value), max(board_pairs)]
            elif min(hand_value) > min(board_pairs):
                player_2pairs = [max(board_pairs), min(hand_value)]
            else:
                player_2pairs = board_pairs
        elif min(hand_value) > max(board_pairs):
            player_2pairs = [min(hand_value), max(board_pairs)]
        else:
            player_2pairs = [max(board_pairs), min(hand_value)]
    elif board_value.count(max(hand_value)) == 1:
        if min(board_pairs) == 1 and max(hand_value) > max(board_pairs):
            player_2pairs = [min(board_pairs), max(hand_value)]
        elif len(board_pairs) == 2:
            if max(hand_value) > max(board_pairs):
                player_2pairs = [max(hand_value), max(board_pairs)]
            elif max(hand_value) > min(board_pairs):
                player_2pairs = [max(board_pairs), max(hand_value)]
            else:
                player_2pairs = board_pairs
        else:
            if max(hand_value) > max(board_pairs):
                player_2pairs = [max(hand_value), max(board_pairs)]
            else:
                player_2pairs = [max(board_pairs),max(hand_value)]
    else:
        player_2pairs = board_pairs
    return player_2pairs

# check if pair
def check_if_pair(hand_value, board_value):
    is_pair = False
    board_pair = []
    for card in board_value:
        if board_value.count(card) == 2:
            board_pair.append(card)
    if hand_value[0] == hand_value[1]:  # pair
        if hand_value[0] == 1 or len(board_pair) == 0:
            is_pair = True
        elif len(board_pair) == 2:
            if hand_value[0] > board_pair[0] or hand_value[0] > board_pair[1]:
                is_pair = True
    else:
        for card in hand_value:
            hit_count = board_value.count(card)
            if hit_count == 1:
                if card == 1 or len(board_pair) == 0:
                    is_pair = True
                    break
                elif len(board_pair) == 2:
                    if hand_value[0] > board_pair[0] or hand_value[0] > board_pair[1]:
                        is_pair = True
                        break
    return is_pair

def get_player_pair(hand_value, board_value):
    player_pair = 0
    if hand_value[0] == hand_value[1]:
        player_pair = hand_value[0]
    else:
        for card in hand_value:
            if board_value.count(card) == 1:
                player_pair = card
    return player_pair

def check_high_card(high_card):
    if high_card == 1:
        high_card = 'A'
    elif high_card == 11:
        high_card = 'J'
    elif high_card == 12:
        high_card = 'Q'
    elif high_card == 13:
        high_card = 'K'
    else:
        high_card = high_card
    return high_card

def compare_high_cards(player1_hand_value, player2_hand_value, board):
    winner = ''
    if min(player1_hand_value) == 1 and min(player2_hand_value) != 1:
        winner = 'Player'
    elif min(player1_hand_value) != 1 and min(player2_hand_value) == 1:
        winner = 'Dealer'
    elif max(player1_hand_value) > max(player2_hand_value):  # compare high cards
        winner = check_board_highcard(max(player1_hand_value), board)
        if winner:
            winner = 'Player'
        else:
            winner = "It's a draw!"
    elif max(player1_hand_value) < max(player2_hand_value):
        winner = check_board_highcard(max(player2_hand_value), board)
        if winner:
            winner = 'Dealer'
        else:
            winner = "It's a draw!"
    elif min(player1_hand_value) > min(player2_hand_value):
        winner = check_board_highcard(min(player1_hand_value), board)
        if winner:
            winner = 'Player'
        else:
            winner = "It's a draw!"
    elif min(player1_hand_value) < min(player2_hand_value):
        winner = check_board_highcard(min(player2_hand_value), board)
        if winner:
            winner = 'Dealer'
        else:
            winner = "It's a draw!"
    else:
        winner = "It's a draw!"
    return winner

def check_board_highcard(player, board):
    ctr = 0
    is_winner = False
    for card in board:
        if card == 1 or board.count(card) >= 2:
            pass
        elif player > card:
            ctr += 1
    if ctr >= 1:
        is_winner = True
    else:
        is_winner = False
    return is_winner

def deal_hands():
    deck_no = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
    deck_shade = ['S', 'H', 'C', 'D']
    card = ''
    card = rd.choice(deck_no) + rd.choice(deck_shade)
    return card

#######################################################################################
# Start Poker Game Program

def poker_game():
    text = ""
    straight_hand = []
    is_quads1 = False
    is_quads2 = False
    is_fullhouse1 = False
    is_fullhouse2 = False
    is_3ofakind1 = False
    is_3ofakind2 = False
    is_2pairs1 = False
    is_2pairs2 = False
    is_pair1 = False
    is_pair2 = False
    is_straight_p1 = False
    is_straight_p2 = False
    is_flush_p1 = False
    is_flush_p2 = False
    winner = ""
    poker_event = []
    cards_in_play = []
    # deal hand to player 1
    player1_card1 = ''
    player1_card1 = deal_hands()
    poker_event.append(player1_card1)
    cards_in_play.append(player1_card1)
    player1_card2 = player1_card1
    while player1_card2 in cards_in_play:
        player1_card2 = deal_hands()
    cards_in_play.append(player1_card2)
    poker_event.append(player1_card2)
    player1_hand = [player1_card1, player1_card2]
    # player1_hand = ['KC','9D']
    #deal hand to player 2
    player2_card1 = player1_card2
    while player2_card1 in cards_in_play:
        player2_card1 = deal_hands()
    cards_in_play.append(player2_card1)
    poker_event.append(player2_card1)
    player2_card2 = player2_card1
    while player2_card2 in cards_in_play:
        player2_card2 = deal_hands()
    cards_in_play.append(player2_card2)
    poker_event.append(player2_card2)
    player2_hand = [player2_card1, player2_card2]
    # player2_hand = ['7S', '3C']
    #   THE FLOP
    board = []
    for n in range(1,6):
        flop = player2_card2
        while flop in cards_in_play:
            flop = deal_hands()
        cards_in_play.append(flop)
        board.append(flop)
        poker_event.append(flop)
    player1_hand_value = []
    player2_hand_value = []
    board_value = []
    for card in player1_hand:
        card_value = get_card_value(card)
        player1_hand_value.append(card_value)
    for card in player2_hand:
        card_value = get_card_value(card)
        player2_hand_value.append(card_value)
    for card in board:
        card_value = get_card_value(card)
        board_value.append(card_value)
                #check player1 hand
    is_straight_flush1 = check_if_straight_flush(player1_hand, board)
    is_flush_p1 = check_if_flush(player1_hand, board) # check if flush
    is_straight_p1 = check_if_straight(player1_hand_value, board_value) # check if straight
    if len(is_straight_flush1) > 1:
        straight_card1 = []
        for card in is_straight_flush1[1]:
            straight_card1.append(card[0])
        p1hand = f'Straight flush of {is_straight_flush1[2]} from {straight_card1[0]} to {straight_card1[4]}'
    elif is_flush_p1:
        player1_flush = get_player_flush(player1_hand, board)
        p1hand = f'Flush of {player1_flush}.'
    elif is_straight_p1:
        player1_straight = get_player_straight(player1_hand_value, board_value)
        low_card_straight1 = get_low_card_straight(player1_straight)
        high_card_straight1 = get_high_card_straight(player1_straight)
        p1hand = f'Straight {low_card_straight1} to {high_card_straight1}.'
    else:
        is_quads1 = check_if_quads(player1_hand_value, board_value) # check if quads
        if is_quads1:
            p1hand = f'Quads.'
        else:
            is_fullhouse1 = check_if_fullhouse(player1_hand_value, board_value)
            if is_fullhouse1:
                p1_fullhouse = get_fullhouse_card(player1_hand_value, board_value)
                p1_fullhouse1 = check_high_card(p1_fullhouse[0])
                p1_fullhouse2 = check_high_card(p1_fullhouse[1])
                p1hand = f'Full house of {p1_fullhouse1} and {p1_fullhouse2}.'
            else:
                is_3ofakind1 = check_if_3ofakind(player1_hand_value, board_value)
                if is_3ofakind1:
                    player1_3ofakind = get_player_3ofakind(player1_hand_value, board_value)
                    player1_3ofakind1 = check_high_card(player1_3ofakind)
                    p1hand = f'3 of a kind {player1_3ofakind1}.'
                else:
                    is_2pairs1 = check_if_2pairs(player1_hand_value, board_value)
                    if is_2pairs1:
                        player1_2pairs = get_player_2pairs(player1_hand_value,board_value)
                        player1_2pairs1 = check_high_card(player1_2pairs[0])
                        player1_2pairs2 = check_high_card(player1_2pairs[1])
                        p1hand = f'2 pairs of {player1_2pairs1} and {player1_2pairs2}.'
                    else:
                        is_pair1 = check_if_pair(player1_hand_value, board_value)
                        if is_pair1:
                            player1_pair = get_player_pair(player1_hand_value, board_value)
                            high_card = check_high_card(player1_pair)
                            p1hand = f"Pair of {high_card}."
                        else:
                            if min(player1_hand_value) == 1:
                                high_card = 'A'
                            else:
                                high_card = check_high_card(max(player1_hand_value))
                            p1hand = f"High card {high_card}."
    poker_event.append(p1hand)
    # #check player 2 hand
    is_straight_flush2 = check_if_straight_flush(player2_hand, board)
    is_flush_p2 = check_if_flush(player2_hand, board) # check if flush
    is_straight_p2 = check_if_straight(player2_hand_value, board_value) # check if straight
    if len(is_straight_flush2) > 1:
        straight_card2 = []
        for card in is_straight_flush1[1]:
            straight_card1.append(card[0])
        p2hand = f'Straight flush of {is_straight_flush2[2]} from {straight_card2[0]} to {straight_card2[4]}'
    elif is_flush_p2:
        player2_flush = get_player_flush(player2_hand, board)
        p2hand = f'Flush of {player2_flush}.'
    elif is_straight_p2:
        player2_straight = get_player_straight(player2_hand_value, board_value)
        low_card_straight2 = get_low_card_straight(player2_straight)
        high_card_straight2 = get_high_card_straight(player2_straight)
        p2hand = f'Straight from {low_card_straight2} to {high_card_straight2}.'

    else:
        is_quads2 = False
        is_quads2 = check_if_quads(player2_hand_value, board_value) # check if quads
        if is_quads2:
            p2hand = 'Quads.'
        else:
            is_fullhouse2 = check_if_fullhouse(player2_hand_value,board_value)
            if is_fullhouse2:
                p2_fullhouse = get_fullhouse_card(player2_hand_value, board_value)
                p2_fullhouse1 = check_high_card(p2_fullhouse[0])
                p2_fullhouse2 = check_high_card(p2_fullhouse[1])
                p2hand = f'Full house of {p2_fullhouse1} and {p2_fullhouse2}.'
            else:
                is_3ofakind2 = check_if_3ofakind(player2_hand_value,board_value)
                if is_3ofakind2:
                    player2_3ofakind = get_player_3ofakind(player2_hand_value,board_value)
                    player2_3ofakind1 = check_high_card(player2_3ofakind)
                    p2hand = f'3 of a kind {player2_3ofakind1}.'
                else:
                    is_2pairs2 = check_if_2pairs(player2_hand_value, board_value)
                    if is_2pairs2:
                        player2_2pairs = get_player_2pairs(player2_hand_value,board_value)
                        player2_2pairs1 = check_high_card(player2_2pairs[0])
                        player2_2pairs2 = check_high_card(player2_2pairs[1])
                        p2hand = f'2 pairs of {player2_2pairs1} and {player2_2pairs2}.'
                    else:
                        is_pair2 = check_if_pair(player2_hand_value, board_value)
                        if is_pair2:
                            player2_pair = get_player_pair(player2_hand_value, board_value)
                            high_card = check_high_card(player2_pair)
                            p2hand = f"Pair of {high_card}."
                        else:
                            if min(player2_hand_value) == 1:
                                high_card = 'A'
                            else:
                                high_card = check_high_card(max(player2_hand_value))
                            p2hand = f'High card {high_card}.'
    poker_event.append(p2hand)
    # DETERMINE THE WINNER
    is_board_flush = check_board_flush(player1_hand, player2_hand, board)
    is_board_straight = check_board_straight(player1_hand_value, player2_hand_value, board_value)
    is_board_quads = check_board_quads(player1_hand_value, player2_hand_value, board_value)
    is_board_fullhouse = check_board_fullhouse(player1_hand_value, player2_hand_value, board_value)
    is_board_3ofakind = check_board_3ofakind(player1_hand_value, player2_hand_value, board_value)
    is_board_2pairs = check_board_2pairs(player1_hand_value, player2_hand_value, board_value)
    if is_board_flush or is_board_straight or is_board_quads or is_board_fullhouse or is_board_3ofakind or is_board_2pairs:
        winner = "It's a draw!"
    elif len(is_straight_flush1)== 3 and len(is_straight_flush2) == 1:
        winner = 'Player'
    elif len(is_straight_flush1)== 1 and len(is_straight_flush2) == 3:
        winner = 'Dealer'
    elif len(is_straight_flush1) == 3 and len(is_straight_flush2) == 3:
        if min(straight_card1) == 1 and max(straight_card1) == 13:
            if max(straight_card2) != 13:
                winner = 'Player'
            elif min(straight_card2) != 1:
                winner = 'Player'
            else:
                winner = "It's a draw!"
        elif min(straight_card2) == 1 and max(straight_card2) == 13:
            if max(straight_card1) != 13:
                winner = 'Dealer'
            elif min(straight_card1) != 1:
                winner = 'Dealer'
            else:
                winner = "It's a draw!"
        elif max(straight_card1) > max(straight_card2):
            winner = 'Player'
        elif max(straight_card1) < max(straight_card2):
            winner = 'Dealer'
        else:
            winner = "It's a draw!"
    elif is_quads1 and not is_quads2:
        winner = 'Player'
    elif is_quads2 and not is_quads1:
        winner = 'Dealer'
    elif is_quads1 and is_quads2:
        winner = compare_high_cards(player1_hand_value, player2_hand_value, board_value)
    elif is_fullhouse1 and not is_fullhouse2:
        winner = 'Player'
    elif is_fullhouse2 and not is_fullhouse1:
        winner = 'Dealer'
    elif is_fullhouse1 and is_fullhouse2:
        if p1_fullhouse[0] == 1 and p2_fullhouse[0] != 1:
            winner = 'Player'
        elif p1_fullhouse[0] != 1 and p2_fullhouse[0] == 1:
            winner = 'Dealer'
        elif p1_fullhouse[0] > p2_fullhouse[0]:
            winner = 'Player'
        elif p1_fullhouse[0] < p2_fullhouse[0]:
            winner = 'Dealer'
        elif p1_fullhouse[1] == 1 and p2_fullhouse[1] != 1:
            winner = 'Player'
        elif p1_fullhouse[1] != 1 and p2_fullhouse[1] == 1:
            winner = 'Dealer'
        elif p1_fullhouse[1] > p2_fullhouse[1]:
            winner = 'Player'
        elif p1_fullhouse[1] < p2_fullhouse[1]:
            winner = 'Dealer'
        else:
            winner = "It's a draw!"
    elif is_flush_p1 and not is_flush_p2:
        winner = 'Player'
    elif not is_flush_p1 and is_flush_p2:
        winner = 'Dealer'
    elif is_flush_p1 and is_flush_p2:
        winner = compare_flush_cards(player1_hand, player2_hand, player1_flush)
    elif is_straight_p1 and not is_straight_p2:
        winner = 'Player'
    elif is_straight_p2 and not is_straight_p1:
        winner = 'Dealer'
    elif is_straight_p1 and is_straight_p2:
        if high_card_straight1 == 'A' and high_card_straight2 != 'A':
            winner = 'Player'
        elif high_card_straight1 != 'A' and high_card_straight2 == 'A':
            winner = 'Dealer'
        elif max(player1_straight) > max(player2_straight):
            winner = 'Player'
        elif max(player1_straight) < max(player2_straight):
            winner = 'Dealer'
        else:
            winner = "It's a draw!"
    elif is_3ofakind1 and not is_3ofakind2:
        winner = 'Player'
    elif is_3ofakind2 and not is_3ofakind1:
        winner = 'Dealer'
    elif is_3ofakind1 and is_3ofakind2:
        winner = compare_high_cards(player1_hand_value,player2_hand_value, board_value)
    elif is_2pairs1 and not is_2pairs2:
        winner = 'Player'
    elif is_2pairs2 and not is_2pairs1:
        winner = 'Dealer'
    elif is_2pairs1 and is_2pairs2:
        if min(player1_2pairs) == 1 and min(player2_2pairs) != 1:
            winner = 'Player'
        elif min(player1_2pairs) != 1 and min(player2_2pairs) == 1:
            winner = 'Dealer'
        elif max(player1_2pairs) > max(player2_2pairs):
            winner = 'Player'
        elif max(player1_2pairs) < max(player2_2pairs):
            winner = 'Dealer'
        elif min(player1_2pairs) > min(player2_2pairs):
            winner = 'Player'
        elif min(player1_2pairs) < min(player2_2pairs):
            winner = 'Dealer'
        elif min(player1_hand_value) == min(player2_hand_value) and max(player1_hand_value) == max(player2_hand_value):
            winner = "It's a draw!"
        else:
            if player1_2pairs.count(player1_hand_value[0]) == 0:
                kicker1 = player1_hand_value[0]
                if kicker1 == 1:
                    pass
                else:
                    for card in board_value:
                        if card == player1_2pairs[0] or card == player1_2pairs[1] or board_value.count(card) == 2:
                            pass
                        elif card > kicker1 or card == 1:
                            kicker1 = card
            elif player1_2pairs.count(player1_hand_value[1]) == 0:
                kicker1 = player1_hand_value[1]
                if kicker1 == 1:
                    pass
                else:
                    for card in board_value:
                        if card == player1_2pairs[0] or card == player1_2pairs[1] or board_value.count(card) == 2:
                            pass
                        elif card > kicker1 or card == 1:
                            kicker1 = card
            if player2_2pairs.count(player2_hand_value[0]) == 0:
                kicker2 = player2_hand_value[0]
                if kicker2 == 1:
                    pass
                else:
                    for card in board_value:
                        if card == player2_2pairs[0] or card == player2_2pairs[1] or board_value.count(card) == 2:
                            pass
                        elif card > kicker2 or card == 1:
                            kicker2 = card
            elif player2_2pairs.count(player2_hand_value[1]) == 0:
                kicker2 = player1_hand_value[1]
                if kicker2 == 1:
                    pass
                else:
                    for card in board_value:
                        if card == player2_2pairs[0] or card == player2_2pairs[1] or board_value.count(card) == 2:
                            pass
                        elif card > kicker2 or card == 1:
                            kicker2 = card
            if kicker1 == 1 and kicker2 != 1:
                winner = 'Player'
            elif kicker1 != 1 and kicker2 == 1:
                winner = 'Dealer'
            elif kicker1 > kicker2:
                winner = 'Player'
            elif kicker1 < kicker2:
                winner = 'Dealer'
            else:
                winner = "It's a draw!"
    elif is_pair1 and not is_pair2:
        winner = 'Player'
    elif is_pair2 and not is_pair1:
        winner = 'Dealer'
    elif is_pair1 and is_pair2:
        if player1_pair == 1 and player2_pair != 1:
            winner = 'Player'
        elif player1_pair != 1 and player2_pair == 1:
            winner = 'Dealer'
        elif player1_pair > player2_pair:
            winner = 'Player'
        elif player1_pair < player2_pair:
            winner = 'Dealer'
        elif player1_pair == player2_pair:
            winner = compare_high_cards(player1_hand_value, player2_hand_value, board_value)
    else:
        winner = compare_high_cards(player1_hand_value, player2_hand_value, board_value)
    poker_event.append(winner)
    return poker_event

################################FLASK AND TABLES###################################

app = Flask(__name__)

app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
##CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://qcfbrvhrgylqsw:6a0e02ae287651979d4ad4298efa5781c5671e473b04011ea0fcb1aba583c482@ec2-52-206-182-219.compute-1.amazonaws.com:5432/df8vobp56a27au'
app.config['SQLALCHEMY_BINDS'] = {'posts':'postgresql://nyyigjicgszqod:67d0258845d6de6609fd9efbbc326432ad6af2486f50d70e1ef759c1386cd222@ec2-52-206-182-219.compute-1.amazonaws.com:5432/degoenmn35rpoe'}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

##CREATE USERS TABLE IN DB
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000), nullable=False)
    date_registered = db.Column(db.String(250))
    date_last_loggedin = db.Column(db.String(250))
    player_stack = db.Column(db.Integer)
# db.create_all()

class PokerDeck(db.Model):
    __bind_key__ = "posts"
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(250), unique=True, nullable=False)
    street = db.Column(db.Integer)
    img1 = db.Column(db.String(250), nullable=False)
    img2 = db.Column(db.String(250), nullable=False)
    img3 = db.Column(db.String(250), nullable=False)
    img4 = db.Column(db.String(250), nullable=False)
    img5 = db.Column(db.String(250), nullable=False)
    img6 = db.Column(db.String(250), nullable=False)
    img7 = db.Column(db.String(250), nullable=False)
    img8 = db.Column(db.String(250), nullable=False)
    img9 = db.Column(db.String(250), nullable=False)
    player1_hand = db.Column(db.String(250), nullable=False)
    player2_hand = db.Column(db.String(250), nullable=False)
    winner = db.Column(db.String(250), nullable=False)
    player_stack = db.Column(db.Integer, nullable=False)
# db.create_all(bind=['posts'])


#Line below only required once, when creating DB.
# db.create_all()

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if not user:
            flash("Email does not exist. Please try again.")
            return redirect(url_for('login'))
        elif not check_password_hash(user.password, password):
            flash("Incorrect password.  Please try again.")
            return redirect(url_for('login'))
        else:
            login_user(user)
            user.date_last_loggedin = datetime.datetime.now().strftime("%x")
            db.session.commit()
            return redirect(url_for('about'))
    return render_template("login.html", logged_in=current_user.is_authenticated)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        if User.query.filter_by(email=request.form['email']).first():
            flash("You already signed up with that email.  Login instead.")
            return redirect(url_for('login'))
        hash_password=generate_password_hash(request.form['password'],method='pbkdf2:sha256', salt_length=8)
        date = datetime.datetime.now()
        date_registered = date.strftime("%x")
        new_user = User(
        name = request.form["name"],
        email = request.form["email"],
        password = hash_password,
        date_registered = date_registered,
        date_last_loggedin = date_registered,
        player_stack = 5000
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for("about"))
    return render_template("register.html", logged_in=current_user.is_authenticated)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('about'))



@app.route('/start_game')
@login_required
def start_game():
# for i in range(2):
    user_id = current_user.get_id()
    user = User.query.get(user_id)
    poker = []
    poker = poker_game()
    street = 1
    img1 = '/static/images/' + poker[0] + '.png'
    img2 = '/static/images/' + poker[1] + '.png'
    img3 = '/static/images/' + poker[2] + '.png'
    img4 = '/static/images/' + poker[3] + '.png'
    img5 = '/static/images/' + poker[4] + '.png'
    img6 = '/static/images/' + poker[5] + '.png'
    img7 = '/static/images/' + poker[6] + '.png'
    img8 = '/static/images/' + poker[7] + '.png'
    img9 = '/static/images/' + poker[8] + '.png'
    player1 = poker[9]
    player2 = poker[10]
    winner = poker[11]
    print (player1, player2, winner)
    poker_update = PokerDeck.query.filter_by(user=user_id).first()
    if poker_update:
        if poker_update.player_stack < 400:
            poker_update.player_stack = 5000
        poker_update.player_stack -= 20
        poker_update.street = street
        poker_update.img1 = img1
        poker_update.img2 = img2
        poker_update.img3 = img3
        poker_update.img4 = img4
        poker_update.img5 = img5
        poker_update.img6 = img6
        poker_update.img7 = img7
        poker_update.img8 = img8
        poker_update.img9 = img9
        poker_update.player1_hand = player1
        poker_update.player2_hand = player2
        poker_update.winner = winner
        db.session.commit()
    else:
        player_stack = user.player_stack - 20
        new_post = PokerDeck(
        user = user_id,
        street = street,
        img1 = img1,
        img2 = img2,
        img3 = img3,
        img4 = img4,
        img5 = img5,
        img6 = img6,
        img7 = img7,
        img8 = img8,
        img9 = img9,
        player1_hand = player1,
        player2_hand = player2,
        winner = winner,
        player_stack = player_stack,

        )
        db.session.add(new_post)
        db.session.commit()
    print(player1, player2, winner)
    post = PokerDeck.query.filter_by(user=user_id).first()
    user.player_stack = post.player_stack
    db.session.commit()
    stack = str(post.player_stack)
    return render_template("index.html", post=post, stack=stack)

@app.route('/the_flop')
@login_required
def the_flop():
    global player_stack
    user_id = current_user.get_id()
    post_flop = PokerDeck.query.filter_by(user=user_id).first()
    post_flop.street = 2
    stack = str(post_flop.player_stack)
    db.session.commit()
    return render_template('index.html', post=post_flop, stack=stack)

@app.route('/the_turn')
@login_required
def the_turn():
    global player_stack
    user_id = current_user.get_id()
    user = User.query.get(user_id)
    post_flop = PokerDeck.query.filter_by(user=user_id).first()
    if post_flop.street != 2:
        return redirect((url_for('start_game')))
    post_flop.player_stack = post_flop.player_stack - 30
    post_flop.street = 3
    db.session.commit()
    stack = str(post_flop.player_stack)
    user.player_stack = post_flop.player_stack
    db.session.commit()
    return render_template('index.html', post=post_flop, stack=stack)

@app.route('/the_river')
@login_required
def the_river():
    global player_stack
    user_id = current_user.get_id()
    user = User.query.get(user_id)
    post_flop = PokerDeck.query.filter_by(user=user_id).first()
    if post_flop.street != 3:
        return redirect((url_for('start_game')))
    post_flop.player_stack = post_flop.player_stack - 50
    post_flop.street = 4
    db.session.commit()
    user.player_stack = post_flop.player_stack
    db.session.commit()
    stack = str(post_flop.player_stack)
    return render_template('index.html', post=post_flop, stack=stack)

@app.route('/the_showdown')
@login_required
def the_showdown():
    user_id = current_user.get_id()
    user = User.query.get(user_id)
    post_flop = PokerDeck.query.filter_by(user=user_id).first()
    if post_flop.street != 4:
        return redirect((url_for('start_game')))
    post_flop.street = 5
    if post_flop.winner == "Player":
        post_flop.player_stack += 300
    elif post_flop.winner == 'Dealer':
        post_flop.player_stack -= 100
    else:
        post_flop.player_stack += 100
    db.session.commit()
    user.player_stack = post_flop.player_stack
    db.session.commit()
    stack = str(post_flop.player_stack)
    return render_template('index.html', post=post_flop, stack=stack)

@app.route('/exit_game')
@login_required
def exit_game():
    return render_template('exit_game.html')

@app.route('/')
def about():
    return render_template('pokerplay.html',logged_in = current_user.is_authenticated)

if __name__ == "__main__":
    app.run(debug=True)