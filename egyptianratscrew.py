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
        self.players_in_play = [True for participants in range(self.players)]
        self.player_turn = 0
        # initialize the graphics
        #self.initial_graphics()
        # continue until one player has all the money

        # shuffle the game deck
        self._game_deck.shuffle()
        # deal cards
        self.deal_cards()
        # play a round
        self.play_round()
        # check everyone's balance again

        # ends the game once one player has all the money
        #self.end_game()

    def deal_cards(self):
        self.hands = [[] for players in range(self.players)]
        for index, cards in enumerate(self._game_deck.cards):
            self.hands[index % self.players].append(cards)
        print(self.hands)
        print(str(len(self.hands[0])) + ', ' + str(len(self.hands[1])) + ', ' + str(len(self.hands[2])))
    
    def play_round(self):
        self.player_challenger = -1
        self.card_pile = []
        self.cards_in_play = True
        count = 0
        while self.cards_in_play == True:
            if self.players_in_play[self.player_turn] == True:
                self.draw_card()
                self.player_challenger = self.player_turn
                self.player_turn = (self.player_turn + 1) % self.players
                if self.card_pile[0].value in [11, 12, 13, 14]:
                    self.face_card_challenge()
            else:
                self.player_turn = (self.player_turn + 1) % self.players

        print(self.card_pile)
        
    def draw_card(self):
        print(self.player_challenger)
        self.card_pile.insert(0, self.hands[self.player_turn][0])
        self.hands[self.player_turn].pop(0)
        self.check_if_slappable()
        self.check_cards()
        #print(self.slappable)
        print(self.card_pile)
        print(str(len(self.hands[0])) + ', ' + str(len(self.hands[1])) + ', ' + str(len(self.hands[2])))

        print('Player ' + str(self.player_turn + 1))
        pause = input('')

    def collect_pile(self):
        print('Player ' + str(self.player_turn + 1) + ' collected')
        self.hands[self.player_turn] += self.card_pile
        self.card_pile = []
        self.player_challenger = -1

    def face_card_challenge(self):
        if self.players_in_play[self.player_turn] == True:
            turns = self.card_pile[0].value - 10

            for tries in range(turns):
                if self.players_in_play[self.player_turn] == True:
                    self.draw_card()
                    if self.card_pile[0].value in [11, 12, 13, 14]:
                        break
                else:
                    break

            if self.card_pile[0].value in [11, 12, 13, 14]:
                self.player_challenger = self.player_turn
                self.player_turn = (self.player_turn + 1) % self.players
                self.face_card_challenge()
            else:
                self.player_turn = self.player_challenger
                self.collect_pile()
        else:
            self.player_turn = (self.player_turn + 1) % self.players
            self.face_card_challenge()

    def check_if_slappable(self):
        self.slappable = [0]
        # 10s
        if self.card_pile[0].value == 10:
            self.slappable = [1, '10s']
        # queen of hearts
        elif self.card_pile[0].value == 12 and self.card_pile[0].suit == 'Hearts':
            self.slappable = [1, 'Queen of Hearts']
        if len(self.card_pile) > 1:
            # pair
            if self.card_pile[0].value == self.card_pile[1].value:
                self.slappable = [1, 'Pair']
            # adds to 10
            elif (self.card_pile[0].value + self.card_pile[1].value) == 10:
                self.slappable = [1, 'Adds to 10']
            # marriage
            elif self.card_pile[0].value == 13 and self.card_pile[1] == 12:
                self.slappable = [1, 'Marriage']
            # 69
            elif self.card_pile[0].value == 6 and self.card_pile[1] == 9:
                self.slappable = [1, '69']
        if len(self.card_pile) > 2:
            # sandwich
            if self.card_pile[0].value == self.card_pile[2].value:
                self.slappable = [1, 'Sandwich']
            # ascending straight
            elif (self.card_pile[0].value + 1) == self.card_pile[1].value and (self.card_pile[1].value + 1) == self.card_pile[2].value:
                self.slappable = [1, 'Ascending Straight']
            # descending straight
            elif (self.card_pile[0].value - 1) == self.card_pile[1].value and (self.card_pile[1].value - 1) == self.card_pile[2].value:
                self.slappable = [1, 'Descending Straight']
            # flush
            elif self.card_pile[0].suit == self.card_pile[1].suit and self.card_pile[1].suit == self.card_pile[2].suit:
                self.slappable = [1, 'Flush']
        if len(self.card_pile) > 3:
            # hoagie
            if self.card_pile[0].value == self.card_pile[3].value:
                self.slappable = [1, 'Hoagie']

    def check_cards(self):
        print(self.players_in_play)
        self.players_in_play = [True if len(self.hands[participants]) != 0 else False for participants in range(self.players)]
    
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

    def initial_graphics(self):
        self.balances_text = [None for players in range(self.players)]
        self.hole_card_1 = [None for players in range(self.players)]
        self.hole_card_2 = [None for players in range(self.players)]
        self.back_card_1 = [None for players in range(self.players)]
        self.back_card_2 = [None for players in range(self.players)]
        self.hand_text = ['' for players in range(self.players)]
        self.win = GraphWin('Poker', GetSystemMetrics(0)-100, GetSystemMetrics(1)-100)
        self.win.setBackground('green')

        check_rectangle = Rectangle(Point((self.win.getWidth()/2)-450, self.win.getHeight()-175), Point((self.win.getWidth()/2)-350, self.win.getHeight()-125))
        check_rectangle.setFill('blue')
        check_rectangle.draw(self.win)
        check_text = Text(Point((self.win.getWidth()/2)-400, self.win.getHeight()-150), 'Check')
        check_text.setSize(20)
        check_text.draw(self.win)

        call_rectangle = Rectangle(Point((self.win.getWidth()/2)-250, self.win.getHeight()-175), Point((self.win.getWidth()/2)-150, self.win.getHeight()-125))
        call_rectangle.setFill('yellow')
        call_rectangle.draw(self.win)
        call_text = Text(Point((self.win.getWidth()/2)-200, self.win.getHeight()-150), 'Call')
        call_text.setSize(20)
        call_text.draw(self.win)
        
        raise_rectangle = Rectangle(Point((self.win.getWidth()/2)+50, self.win.getHeight()-175), Point((self.win.getWidth()/2)-50, self.win.getHeight()-125))
        raise_rectangle.setFill('purple')
        raise_rectangle.draw(self.win)
        raise_text = Text(Point((self.win.getWidth()/2), self.win.getHeight()-150), 'Raise')
        raise_text.setSize(20)
        raise_text.draw(self.win)

        fold_rectangle = Rectangle(Point((self.win.getWidth()/2)+250, self.win.getHeight()-175), Point((self.win.getWidth()/2)+150, self.win.getHeight()-125))
        fold_rectangle.setFill('red')
        fold_rectangle.draw(self.win)
        fold_text = Text(Point((self.win.getWidth()/2)+200, self.win.getHeight()-150), 'Fold')
        fold_text.setSize(20)
        fold_text.draw(self.win)

        show_cards_rectangle = Rectangle(Point((self.win.getWidth()/2)+550, self.win.getHeight()-175), Point((self.win.getWidth()/2)+350, self.win.getHeight()-125))
        show_cards_rectangle.setFill('orange')
        show_cards_rectangle.draw(self.win)
        show_cards_text = Text(Point((self.win.getWidth()/2)+450, self.win.getHeight()-150), 'Show Cards')
        show_cards_text.setSize(20)
        show_cards_text.draw(self.win)

        allin_rectangle = Rectangle(Point((self.win.getWidth()/2)+50, self.win.getHeight()-75), Point((self.win.getWidth()/2)-50, self.win.getHeight()-25))
        allin_rectangle.setFill('purple')
        allin_rectangle.draw(self.win)
        allin_text = Text(Point(self.win.getWidth()/2, self.win.getHeight()-50), 'All In')
        allin_text.setSize(20)
        allin_text.draw(self.win)

        self.jackpot_text = Text(Point(200, self.win.getHeight()-350), 'Current pot: $0')
        self.jackpot_text.setSize(20)
        self.jackpot_text.setTextColor('red')
        self.jackpot_text.draw(self.win)

        self.showing_cards = False

        self.current_bet_text = Text(Point(200, self.win.getHeight()-400), 'Current bet: $0')
        self.current_bet_text.setSize(20)
        self.current_bet_text.setTextColor('red')
        self.current_bet_text.draw(self.win)

        self.player_action_text = Text(Point(1000, self.win.getHeight()-350), '')
        self.player_action_text.setSize(20)
        self.player_action_text.setTextColor('red')
        self.player_action_text.draw(self.win)

        for players in range(self.players):
            self.balances_text[players] = Text(Point((self.win.getWidth()/(self.players+1)*(players+1)), self.win.getHeight()-250), 'Player ' + str(players+1) + ' Balance: $' + str(self.wallet[players]))
            self.balances_text[players].setTextColor('red')
            self.balances_text[players].setSize(20)
            self.balances_text[players].draw(self.win)

    def show_hole_cards(self, player):
        self.showing_cards = True
        self.hole_card_1[player] = Image(Point((self.win.getWidth()/(self.players+1)*(player+1))-25, 150), self.player_hands[player][0].image_file)
        self.hole_card_1[player].draw(self.win)
        self.hole_card_2[player] = Image(Point((self.win.getWidth()/(self.players+1)*(player+1))+25, 150), self.player_hands[player][1].image_file)
        self.hole_card_2[player].draw(self.win)

    def hide_hole_cards(self, player):
        self.showing_cards = False
        self.hole_card_1[player].undraw()
        self.hole_card_2[player].undraw()

    def show_back_cards(self, player):
        self.back_card_1[player] = Image(Point((self.win.getWidth()/(self.players+1)*(player+1))-25, 150), 'backCard.ppm')
        self.back_card_1[player].draw(self.win)
        self.back_card_2[player] = Image(Point((self.win.getWidth()/(self.players+1)*(player+1))+25, 150), 'backCard.ppm')
        self.back_card_2[player].draw(self.win)

    def hide_back_cards(self, player):
        self.back_card_1[player].undraw()
        self.back_card_2[player].undraw()

    def show_the_flop(self):
        self.community_card_1 = Image(Point(self.win.getWidth()/2-100, self.win.getHeight()/2), self.community_cards[0].image_file)
        self.community_card_2 = Image(Point((self.win.getWidth()/2)-50, self.win.getHeight()/2), self.community_cards[1].image_file)
        self.community_card_3 = Image(Point((self.win.getWidth()/2), self.win.getHeight()/2), self.community_cards[2].image_file)
        self.community_card_1.draw(self.win)
        self.community_card_2.draw(self.win)
        self.community_card_3.draw(self.win)

    def show_the_turn(self):
        self.community_card_4 = Image(Point((self.win.getWidth()/2)+50, self.win.getHeight()/2), self.community_cards[3].image_file)
        self.community_card_4.draw(self.win)
        
    def show_the_river(self):
        self.community_card_5 = Image(Point((self.win.getWidth()/2)+100, self.win.getHeight()/2), self.community_cards[4].image_file)
        self.community_card_5.draw(self.win)

    def hide_community_cards(self):
        self.community_card_1.undraw()
        self.community_card_2.undraw()
        self.community_card_3.undraw()
        self.community_card_4.undraw()
        self.community_card_5.undraw()

    def show_hand_text(self, player):
        self.hand_text[player] = Text(Point((self.win.getWidth()/(self.players+1)*(player+1)), 30), self.hand_value_string[player])
        for players in self.winning_player:
            if (players-1) == player:
                if self.kicker != '':
                    self.hand_text[player] = Text(Point((self.win.getWidth()/(self.players+1)*(player+1)), 30), self.hand_value_string[player] + ' with ' + str(self.kicker) + ' kicker')
                self.hand_text[player].setTextColor('red')
        self.hand_text[player].draw(self.win)

    def hide_hand_text(self, player):
        self.hand_text[player].undraw()

    def update_balances_text(self):
        for players in range(self.players):
            self.balances_text[players].undraw()
            self.balances_text[players] = Text(Point((self.win.getWidth()/(self.players+1)*(players+1)), self.win.getHeight()-250), 'Player ' + str(players+1) + ' Balance: $' + str(self.wallet[players]))
            self.balances_text[players].setTextColor('red')
            self.balances_text[players].setSize(20)
            self.balances_text[players].draw(self.win)

    def update_current_bet_text(self):
        self.current_bet_text.undraw()
        self.current_bet_text = Text(Point(200, self.win.getHeight()/2), 'Current bet: $' + str(self.current_bet))
        self.current_bet_text.setSize(20)
        self.current_bet_text.setTextColor('red')
        self.current_bet_text.draw(self.win)

    def update_jackpot_text(self):
        self.jackpot_text.undraw()
        self.jackpot_text = Text(Point(200, (self.win.getHeight()/2)-50), 'Current pot: $' + str(self.jackpot))
        self.jackpot_text.setSize(20)
        self.jackpot_text.setTextColor('red')
        self.jackpot_text.draw(self.win)

    def update_player_action_text(self, action):
        self.player_action_text.undraw()
        self.player_action_text = Text(Point(self.win.getWidth()-300, self.win.getHeight()/2), action)
        self.player_action_text.setSize(20)
        self.player_action_text.setTextColor('red')
        self.player_action_text.draw(self.win)

    def get_input(self):
        decision = ''
        input = self.win.getMouse()
        if input.getY() >= (self.win.getHeight()-175) and input.getY() <= (self.win.getHeight()-125):
            if input.getX() >= ((self.win.getWidth()/2)-450) and input.getX() <= ((self.win.getWidth()/2)-350):
                decision = 'check'
            elif input.getX() >= ((self.win.getWidth()/2)-250) and input.getX() <= ((self.win.getWidth()/2)-150):
                decision = 'call'
            elif input.getX() >= ((self.win.getWidth()/2)-50) and input.getX() <= ((self.win.getWidth()/2)+50):
                decision = 'raise'
            elif input.getX() >= ((self.win.getWidth()/2)+150) and input.getX() <= ((self.win.getWidth()/2)+250):
                decision = 'fold'
            elif input.getX() >= ((self.win.getWidth()/2)+350) and input.getX() <= ((self.win.getWidth()/2)+550):
                decision = 'show cards'
        elif input.getY() >= (self.win.getHeight()-75) and input.getY() <= (self.win.getHeight()-25):
            if input.getX() >= ((self.win.getWidth()/2)-50) and input.getX() <= ((self.win.getWidth()/2)+50):
                decision = 'all in'
        return decision

    def get_keyboard(self):
        amount = ''
        current_key = ''
        while current_key != 'Return':
            current_key = self.win.getKey()        
            if current_key == 'BackSpace':
                string_list = list(amount)
                print(string_list)
                del(string_list[len(string_list)-1])
                print(string_list)
                amount = ''.join(string_list)
                self.update_player_action_text('Bet amount?: $' + amount)
            elif current_key != 'Return':
                amount += current_key
                self.update_player_action_text('Bet amount?: $' + amount)
        if amount == '':
            amount = '0'
        return amount

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
game.start_game(3)
