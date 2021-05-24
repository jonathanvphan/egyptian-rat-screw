from card import Deck
from collections import Counter
from operator import itemgetter
from win32api import GetSystemMetrics
from graphics import *
import random


class EgyptianRatScrew:
    def __init__(self):
        self._game_deck = Deck()
        
    @property
    def game_deck(self):
        return self._game_deck
        
    def start_game(self, players):
        self.players = players
        self.player_turn = 0
        
        # shuffle the game deck
        self._game_deck.shuffle()
        # deal cards
        self.deal_cards()
        self.select_rules_graphics()
        # initialize the graphics
        self.initial_graphics()
        self.check_cards()
        
        # play a round
        self.play_round()
        # check everyone's balance again

        # ends the game once one player has all the money
        #self.end_game()

    def deal_cards(self):
        self.hands = [[] for players in range(self.players)]
        for index, cards in enumerate(self._game_deck.cards):
            self.hands[index % self.players].append(cards)
    
    def play_round(self):
        self.player_challenger = -1
        self.card_pile = []
        self.cards_in_play = True
        self.decision = [-1, -1]
        self.slappable = [0]
        self.slapped = 0
        count = 0
        while self.sum_players > 1:
            if self.players_in_play[self.player_turn] == True:
                self.draw_card()
                self.player_challenger = self.player_turn
                if self.slapped == 0:
                    self.player_turn = (self.player_turn + 1) % self.players
                else:
                    self.slapped = 0
                if len(self.card_pile) > 0 and self.player_challenger != -1:
                    if self.card_pile[0].value in [11, 12, 13, 14]:
                        self.face_card_challenge()
                        if self.slapped == 1:
                            self.slapped = 0
                self.update_turn_indicator(self.player_turn)
            else:
                self.player_turn = (self.player_turn + 1) % self.players
                self.update_turn_indicator(self.player_turn)
        print('Player ' + str(self.player_turn+1) + ' wins')

    def draw_card(self):
        valid = 0
        while valid == 0:
            self.decision = self.get_input()
            self.update_player_action_text('')
            if self.decision[0] == 0:
                valid = 1
                self.card_pile.insert(0, self.hands[self.player_turn][0])
                self.hands[self.player_turn].pop(0)
                self.check_if_slappable()
                self.check_cards()
                self.show_pile_card()
                self.update_player_card_count_text(self.player_turn)
                self.update_pile_card_count_text()
                print('Player ' + str(self.player_turn + 1) + ' played ' + str(self.card_pile[0]))
                print(self.card_pile)
            elif self.decision[0] == 1 and self.slappable[0] == 1:
                valid = 1
                self.slap_pile(self.decision[1])
            elif self.decision[0] == 1 and self.slappable[0] != 1:
                valid = 0
                self.slap_pile(self.decision[1])

    def collect_pile(self, player):
        print('Player ' + str(player + 1) + ' collected')
        cards = self.card_pile
        cards.reverse()
        self.update_player_action_text('Player ' + str(player + 1) + ' collected ' + str(len(self.card_pile)) + ' cards')
        self.hands[player] += cards
        self.hide_pile_card()
        self.card_pile = []
        self.player_turn = player
        self.update_player_card_count_text(self.player_turn)
        self.update_pile_card_count_text()
        self.player_challenger = -1

    def face_card_challenge(self):
        if self.players_in_play[self.player_turn] == True:
            self.update_turn_indicator(self.player_turn)
            turns = self.card_pile[0].value - 10

            for tries in range(turns):
                if self.players_in_play[self.player_turn] == True and self.player_challenger != -1:
                    self.draw_card()
                    if len(self.card_pile) > 0:
                        if self.card_pile[0].value in [11, 12, 13, 14]:
                            break
                else:
                    break

            if len(self.card_pile) > 0:
                if self.card_pile[0].value in [11, 12, 13, 14]:
                    self.player_challenger = self.player_turn
                    self.player_turn = (self.player_turn + 1) % self.players
                    self.face_card_challenge()
                else:
                    valid = 0
                    while valid == 0:
                        self.decision = self.get_input()
                        if self.decision[0] == 0:
                            valid = 1
                            self.collect_pile(self.player_challenger)
                        if self.decision[0] == 1:
                            valid = 1
                            self.slap_pile(self.decision[1])
                            if self.slappable[0] == 0:
                                self.collect_pile(self.player_challenger)
        else:
            self.player_turn = (self.player_turn + 1) % self.players
            self.face_card_challenge()

    def slap_pile(self, player):
        print('Player ' + str(player + 1) + ' slapped')
        if len(self.card_pile) > 0:
            if self.slappable[0] == 1:
                self.collect_pile(player)
                self.check_cards()
                self.update_turn_indicator(player)
                self.slapped = 1
            else:
                self.card_pile.append(self.hands[player][0])
                self.hands[player].pop(0)
                self.check_cards()
                self.update_player_card_count_text(player)
                self.update_pile_card_count_text()
                print('Not slappable, Player ' + str(player + 1) + ' burns a card')
                self.update_player_action_text('Not slappable, Player ' + str(player + 1) + ' burns a card')
        else:
            print('Cannot slap nothing')
            self.update_player_action_text('Cannot slap nothing')

    def check_if_slappable(self):
        self.slappable = [0]
        # 10s
        if self.card_pile[0].value == 10 and self.selected_rules[0] == 1:
            self.slappable = [1, '10s']
        # queen of hearts
        elif self.card_pile[0].value == 12 and self.card_pile[0].suit == 'Hearts' and self.selected_rules[1] == 1:
            self.slappable = [1, 'Queen of Hearts']
        if len(self.card_pile) > 1:
            # pair
            if self.card_pile[0].value == self.card_pile[1].value and self.selected_rules[2] == 1:
                self.slappable = [1, 'Pair']
            # adds to 10
            elif ((self.card_pile[0].value + self.card_pile[1].value) == 10 or (self.card_pile[0].value in [9, 14] and self.card_pile[1].value in [9, 14])) and self.selected_rules[3] == 1:
                self.slappable = [1, 'Adds to 10']
            # marriage
            elif self.card_pile[0].value == 13 and self.card_pile[1] == 12 and self.selected_rules[4] == 1:
                self.slappable = [1, 'Marriage']
            # 69
            elif self.card_pile[0].value == 6 and self.card_pile[1] == 9 and self.selected_rules[5] == 1:
                self.slappable = [1, '69']
        if len(self.card_pile) > 2:
            # sandwich
            if self.card_pile[0].value == self.card_pile[2].value and self.selected_rules[6] == 1:
                self.slappable = [1, 'Sandwich']
            # ascending straight
            elif (((self.card_pile[0].value + 1) == self.card_pile[1].value and (self.card_pile[1].value + 1) == self.card_pile[2].value) or (self.card_pile[0].value == 14 and self.card_pile[1].value == 2 and self.card_pile[2].value == 3)) and self.selected_rules[7] == 1:
                self.slappable = [1, 'Ascending Straight']
            # descending straight
            elif (((self.card_pile[0].value - 1) == self.card_pile[1].value and (self.card_pile[1].value - 1) == self.card_pile[2].value) or (self.card_pile[0].value == 3 and self.card_pile[1].value == 2 and self.card_pile[2].value == 14)) and self.selected_rules[8] == 1:
                self.slappable = [1, 'Descending Straight']
            # flush
            elif self.card_pile[0].suit == self.card_pile[1].suit and self.card_pile[1].suit == self.card_pile[2].suit and self.selected_rules[9] == 1:
                self.slappable = [1, 'Flush']
        if len(self.card_pile) > 3:
            # hoagie
            if self.card_pile[0].value == self.card_pile[3].value and self.selected_rules[10] == 1:
                self.slappable = [1, 'Hoagie']

    def check_cards(self):
        self.hide_back_card(self.player_turn)
        self.players_in_play = [True if len(self.hands[participants]) != 0 else False for participants in range(self.players)]
        if self.players_in_play[self.player_turn] == True:
            self.show_back_card(self.player_turn)
        self.sum_players = sum(self.players_in_play)
    
    def convert_face(self, card):
        if card in [14]:
            card_converted = 'Ace'
        elif card in [13]:
            card_converted = 'King'
        elif card in [12]:
            card_converted = 'Queen'
        elif card in [11]:
            card_converted = 'Jack'
        else:
            card_converted = card
        return card_converted

    def select_rules_graphics(self):
        self.win = GraphWin('Egyptian Rat Screw', GetSystemMetrics(0)-100, GetSystemMetrics(1)-100)
        self.win.setBackground('green')

        self.rules_button = [None for buttons in range(12)]
        self.rules_text = [None for buttons in range(12)]
        self.selected_rules = [0 for selected in range(11)]

        rules = ['10s', 'Queen of Hearts', 'Pair', 'Adds to 10', 'Marriage (K over Q)', '69', 'Sandwich', 'Asc. Straight', 'Dsc. Straight', 'Flush', 'Hoagie', 'OK']

        i = 0
        for rows in range(3):
            for columns in range(4):
                self.rules_button[i] = Rectangle(Point(((self.win.getWidth()/(4)*(columns))+50), ((self.win.getHeight()/(3)*(rows))+100)), Point(((self.win.getWidth()/(4)*(columns))+250), ((self.win.getHeight()/(3)*(rows))+150)))
                if i != 12:
                    self.rules_button[i].setFill('blue')
                if i == 11:
                    self.rules_button[i].setFill('red')
                self.rules_button[i].draw(self.win)
                self.rules_text[i] = Text(Point(((self.win.getWidth()/(4)*(columns))+150), ((self.win.getHeight()/(3)*(rows))+125)), rules[i])
                self.rules_text[i].setSize(15)
                self.rules_text[i].draw(self.win)
                i += 1

        button_clicked = ''
        while button_clicked != 'OK':
            button_clicked = ''
            input = self.win.getMouse()
            j = 0
            for rows in range(3):
                for columns in range(4):
                    if input.getX() >= ((self.win.getWidth()/(4)*(columns))+50) and input.getX() <= ((self.win.getWidth()/(4)*(columns))+250):
                        if input.getY() >= ((self.win.getHeight()/(3)*(rows))+100) and input.getY() <= ((self.win.getHeight()/(3)*(rows))+150):
                            button_clicked = rules[j]
                            if button_clicked != 'OK' and self.selected_rules[j] == 0:
                                self.selected_rules[j] = 1
                                self.rules_button[j].undraw()
                                self.rules_button[j] = Rectangle(Point(((self.win.getWidth()/(4)*(columns))+50), ((self.win.getHeight()/(3)*(rows))+100)), Point(((self.win.getWidth()/(4)*(columns))+250), ((self.win.getHeight()/(3)*(rows))+150)))
                                self.rules_button[j].setFill('red')
                                self.rules_button[j].draw(self.win)
                                self.rules_text[j].undraw()
                                self.rules_text[j] = Text(Point(((self.win.getWidth()/(4)*(columns))+150), ((self.win.getHeight()/(3)*(rows))+125)), rules[j])
                                self.rules_text[j].setSize(15)
                                self.rules_text[j].draw(self.win)
                            elif button_clicked != 'OK' and self.selected_rules[j] == 1:
                                self.selected_rules[j] = 0
                                self.rules_button[j].undraw()
                                self.rules_button[j] = Rectangle(Point(((self.win.getWidth()/(4)*(columns))+50), ((self.win.getHeight()/(3)*(rows))+100)), Point(((self.win.getWidth()/(4)*(columns))+250), ((self.win.getHeight()/(3)*(rows))+150)))
                                self.rules_button[j].setFill('blue')
                                self.rules_button[j].draw(self.win)
                                self.rules_text[j].undraw()
                                self.rules_text[j] = Text(Point(((self.win.getWidth()/(4)*(columns))+150), ((self.win.getHeight()/(3)*(rows))+125)), rules[j])
                                self.rules_text[j].setSize(15)
                                self.rules_text[j].draw(self.win)
                    j += 1

        k = 0
        for rows in range(3):
            for columns in range(4):
                self.rules_button[k].undraw()
                self.rules_text[k].undraw()
                k += 1

    def initial_graphics(self):
        self.back_card = [None for player in range(self.players)]
        self.pile_card = []
        self.draw_button = [None for player in range(self.players)]
        self.draw_text = [None for player in range(self.players)] 
        self.slap_button = [None for player in range(self.players)]
        self.slap_text = [None for player in range(self.players)] 
        self.player_card_count = [None for player in range(self.players)]
        self.pile_card_draw_count = 0

        self.player_action_text = Text(Point(1000, self.win.getHeight()-350), '')
        self.player_action_text.setSize(20)
        self.player_action_text.setTextColor('red')
        self.player_action_text.draw(self.win)

        self.turn_indicator = Polygon([Point((self.win.getWidth()/(self.players+1)), self.win.getHeight()-100), Point((self.win.getWidth()/(self.players+1))-50, self.win.getHeight()-50), Point((self.win.getWidth()/(self.players+1))+50, self.win.getHeight()-50)])
        self.turn_indicator.setFill('red')
        self.turn_indicator.setWidth(4)  # width of boundary line
        self.turn_indicator.draw(self.win)

        self.pile_card_count = Text(Point((self.win.getWidth()/2)-100, self.win.getHeight()/2-150), '')
        self.pile_card_count.setSize(20)
        self.pile_card_count.draw(self.win)

        for player in range(self.players):
            self.show_back_card(player)
            self.player_card_count[player] = Text(Point((self.win.getWidth()/(self.players+1)*(player+1))+150, self.win.getHeight()-275), str(len(self.hands[player])))
            self.player_card_count[player].setSize(20)
            self.player_card_count[player].draw(self.win)

            self.draw_button[player] = Rectangle(Point(((self.win.getWidth()/(self.players+1)*(player+1))+100), self.win.getHeight()-300), Point(((self.win.getWidth()/(self.players+1)*(player+1))+200), self.win.getHeight()-350))
            self.draw_button[player].setFill('blue')
            self.draw_button[player].draw(self.win)
            self.draw_text[player] = Text(Point(((self.win.getWidth()/(self.players+1)*(player+1))+150), self.win.getHeight()-325), 'Draw')
            self.draw_text[player].setSize(20)
            self.draw_text[player].draw(self.win)

            self.slap_button[player] = Rectangle(Point(((self.win.getWidth()/(self.players+1)*(player+1))+100), self.win.getHeight()-200), Point(((self.win.getWidth()/(self.players+1)*(player+1))+200), self.win.getHeight()-250))
            self.slap_button[player].setFill('red')
            self.slap_button[player].draw(self.win)
            self.slap_text[player] = Text(Point(((self.win.getWidth()/(self.players+1)*(player+1))+150), self.win.getHeight()-225), 'Slap')
            self.slap_text[player].setSize(20)
            self.slap_text[player].draw(self.win)

    def show_pile_card(self):
        self.pile_card.insert(0, Image(Point((self.win.getWidth()/2), self.win.getHeight()/2-150), self.card_pile[0].image_file))
        self.pile_card[0].draw(self.win)
        self.pile_card_draw_count += 1

    def hide_pile_card(self):
        for cards in range(self.pile_card_draw_count):
            self.pile_card[cards].undraw()
        self.pile_card_draw_count = 0

    def show_back_card(self, player):
        self.back_card[player] = Image(Point((self.win.getWidth()/(self.players+1)*(player+1)), self.win.getHeight()-250), 'backCard.ppm')
        self.back_card[player].draw(self.win)

    def hide_back_card(self, player):
        self.back_card[player].undraw()
        self.back_card[player].undraw()

    def update_turn_indicator(self, player):
        player = player % self.players
        self.turn_indicator.undraw()
        self.turn_indicator = Polygon([Point((self.win.getWidth()/(self.players+1)*(player+1)), self.win.getHeight()-100), Point((self.win.getWidth()/(self.players+1)*(player+1))-50, self.win.getHeight()-50), Point((self.win.getWidth()/(self.players+1)*(player+1))+50, self.win.getHeight()-50)])
        self.turn_indicator.setFill('red')
        self.turn_indicator.setWidth(4)  # width of boundary line
        self.turn_indicator.draw(self.win)

    def update_pile_card_count_text(self):
        self.pile_card_count.undraw()
        self.pile_card_count = Text(Point((self.win.getWidth()/2)-100, self.win.getHeight()/2-150), str(len(self.card_pile)))
        self.pile_card_count.setSize(20)
        self.pile_card_count.draw(self.win)

    def update_player_card_count_text(self, player):
        self.player_card_count[player].undraw()
        self.player_card_count[player] = Text(Point((self.win.getWidth()/(self.players+1)*(player+1))+150, self.win.getHeight()-275), str(len(self.hands[player])))
        self.player_card_count[player].setSize(20)
        self.player_card_count[player].draw(self.win)

    def update_player_action_text(self, action):
        self.player_action_text.undraw()
        self.player_action_text = Text(Point(self.win.getWidth()-300, self.win.getHeight()/2), action)
        self.player_action_text.setSize(20)
        self.player_action_text.setTextColor('red')
        self.player_action_text.draw(self.win)

    def get_input1(self):
        decision = [-1, -1]
        #decision = [0, 0]
        input = self.win.getMouse()
        for player in range(self.players):
            if input.getX() >= ((self.win.getWidth()/(self.players+1)*(player+1))+100) and input.getX() <= ((self.win.getWidth()/(self.players+1)*(player+1))+200):
                if input.getY() >= (self.win.getHeight()-350) and input.getY() <= (self.win.getHeight()-300):
                    decision = [0, player]
                elif input.getY() >= (self.win.getHeight()-250) and input.getY() <= (self.win.getHeight()-200):
                    decision = [1, player]
        return decision

    def get_input(self):
        decision = [-1, -1]
        #decision = [0, 0]
        input = self.win.getKey()
        if input == 'space':
            decision = [0, 0]
        elif input == 'Shift_L':
            decision = [1, 0]
        elif input == 'Shift_R':
            decision = [1, 1]

        return decision

    def end_game(self):
        winning_player = 0
        for players, money in enumerate(self.wallet):
            if money > self.wallet[winning_player]:
                winning_player = players
        self.player_action_text = Text(Point(self.win.getWidth()/2, self.win.getHeight()/2), 'Player ' + str(winning_player+1) + ' wins it all' )
        self.player_action_text.setSize(36)
        self.player_action_text.setTextColor('blue')
        self.player_action_text.draw(self.win)
        self.win.getMouse()
        self.win.close()


game = EgyptianRatScrew()
game.start_game(2)
