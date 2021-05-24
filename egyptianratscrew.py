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
        # displays the graphics to select the rule set to play by
        self.select_rules_graphics()
        # initialize the graphics
        self.initial_graphics()
        # sets everyone as in play
        self.check_cards()
        # play a round
        self.play_round()

    def deal_cards(self):
        # sets up the empty list for each player in the game
        self.hands = [[] for players in range(self.players)]
        # deals one card at a time to each player in the game until the deck is empty
        for index, cards in enumerate(self._game_deck.cards):
            self.hands[index % self.players].append(cards)
    
    def play_round(self):
        # sets necessary variables to defaults
        self.player_challenger = -1
        self.card_pile = []
        self.cards_in_play = True
        self.decision = [-1, -1]
        self.slappable = [0]
        self.slapped = 0
        # while there are more than 1 players in play, continue the game
        while self.sum_players > 1:
            # if the player that has the turn is still in play, play
            if self.players_in_play[self.player_turn] == True:
                # draw a card
                self.draw_card()
                # set the player challenger to the current player in case there is a face card
                self.player_challenger = self.player_turn
                # if the pile was not slapped just now, continue to the next player
                if self.slapped == 0:
                    self.player_turn = (self.player_turn + 1) % self.players
                # if the pile was slapped and collected, stay on the same player
                else:
                    self.slapped = 0
                # if a face card was drawn and the pile wasn't just slapped, begin the face card challenge
                if len(self.card_pile) > 0 and self.player_challenger != -1:
                    if self.card_pile[0].value in [11, 12, 13, 14]:
                        self.face_card_challenge()
                        # set the slapped variable to 0 if slapped during the challenge
                        if self.slapped == 1:
                            self.slapped = 0
                # graphically update the turn indicator
                self.update_turn_indicator(self.player_turn)
            else:
                # if the player isn't in play, go to the next player and update the turn indicator
                self.player_turn = (self.player_turn + 1) % self.players
                self.update_turn_indicator(self.player_turn)
        # if there are no players left in player, the last player wins
        print('Player ' + str(self.player_turn+1) + ' wins')

    def draw_card(self):
        # variable to check to make sure the decision is a valid move
        valid = 0
        while valid == 0:
            # gets the input from the players
            self.decision = self.get_input()
            # updates the player action text to be empty
            self.update_player_action_text('')
            # if the decision is to draw, then draw the next card
            if self.decision[0] == 0:
                # it is a valid decision
                valid = 1
                # add the card from the top of their hand to the pile
                self.card_pile.insert(0, self.hands[self.player_turn][0])
                # delete the card from the top of their hand
                self.hands[self.player_turn].pop(0)
                # check if the current pile is slappable
                self.check_if_slappable()
                # check who is still left in play
                self.check_cards()
                # show the new pile card
                self.show_pile_card()
                # update the card counter for the player
                self.update_player_card_count_text(self.player_turn)
                # update the card counter for the pile
                self.update_pile_card_count_text()
                print('Player ' + str(self.player_turn + 1) + ' played ' + str(self.card_pile[0]))
                print(self.card_pile)
            # if the decision is to slap and it is a valid slap
            elif self.decision[0] == 1 and self.slappable[0] == 1:
                # it is a valid decision
                valid = 1
                # slap the pile and collect the cards
                self.slap_pile(self.decision[1])
            # if the decision is to slap and it is an invalid slap
            elif self.decision[0] == 1 and self.slappable[0] != 1:
                # it is an invalid decision, so this loop repeats
                valid = 0
                # slap the pile and burn a card
                self.slap_pile(self.decision[1])

    def collect_pile(self, player):
        print('Player ' + str(player + 1) + ' collected')
        # reverses the cards in the pile to put them into the player's hand in reverse
        cards = self.card_pile
        cards.reverse()
        self.update_player_action_text('Player ' + str(player + 1) + ' collected ' + str(len(self.card_pile)) + ' cards')
        # add the cards to the player's hand but reversed
        self.hands[player] += cards
        # hide the graphic for the pile card
        self.hide_pile_card()
        # set the card pile to empty
        self.card_pile = []
        # the player who just collected has the next turn
        self.player_turn = player
        # update the card counter for the player 
        self.update_player_card_count_text(self.player_turn)
        # update the card counter for the pile
        self.update_pile_card_count_text()
        # set the player challenger for face card challenges to 0
        self.player_challenger = -1

    def face_card_challenge(self):
        # if the player is still in play, continue with the face card challenge
        if self.players_in_play[self.player_turn] == True:
            # update the turn indicator
            self.update_turn_indicator(self.player_turn)
            # the number of chances given is dependent on the face card drawn: A = 4, K = 3, Q = 2, J = 1
            turns = self.card_pile[0].value - 10

            # for the number of chances given, the next player must try to draw a face card as well
            for tries in range(turns):
                # if the player is in play still and the pile was not just slapped, draw a card
                if self.players_in_play[self.player_turn] == True and self.player_challenger != -1:
                    self.draw_card()
                    # if the pile has cards and the top card is a face card, break out of the loop
                    if len(self.card_pile) > 0:
                        if self.card_pile[0].value in [11, 12, 13, 14]:
                            break
                # if the player ran out of cards of the pile was just slapped, break out of the loop
                else:
                    break

            # if the pile has cards
            if len(self.card_pile) > 0:
                # if the top card is a face card, the challenge moves on to the next player
                if self.card_pile[0].value in [11, 12, 13, 14]:
                    # the new challenger is the player who just played the face card
                    self.player_challenger = self.player_turn
                    self.player_turn = (self.player_turn + 1) % self.players
                    self.face_card_challenge()
                # otherwise there is a potential to slap or the challenger just collects the cards
                else:
                    # checks to make sure it is a valid move
                    valid = 0
                    while valid == 0:
                        # get input from the players
                        self.decision = self.get_input()
                        # if the input is nothing, the challenger collects the piles
                        if self.decision[0] == 0:
                            # it is a valid move
                            valid = 1
                            # collect the pile for the challenger
                            self.collect_pile(self.player_challenger)
                        # if the input is slap
                        if self.decision[0] == 1:
                            # it is a valid move if the pile is slappable
                            valid = 1
                            # perform the slap action
                            self.slap_pile(self.decision[1])
                            # if the pile was not slappable, the slapper burns a card
                            if self.slappable[0] == 0:
                                # it is an invalid move if not slappable
                                valid = 0

        # if the player is not in play, move on the next player and recall the face card challenge
        else:
            self.player_turn = (self.player_turn + 1) % self.players
            self.face_card_challenge()

    def slap_pile(self, player):
        print('Player ' + str(player + 1) + ' slapped')
        # if the pile has cards in it
        if len(self.card_pile) > 0:
            # if the pile is slappable
            if self.slappable[0] == 1:
                # the player who slapped collects the cards
                self.collect_pile(player)
                # checks to see which players are still left in play
                self.check_cards()
                # updates the turn indicator
                self.update_turn_indicator(player)
                # changes the pile to just slapped
                self.slapped = 1
            # if the pile is not slappable
            else:
                # player who slapped burns one card to the pile
                self.card_pile.append(self.hands[player][0])
                # player loses that card
                self.hands[player].pop(0)
                # checks to see which players are still left in play
                self.check_cards()
                # update the player card counter
                self.update_player_card_count_text(player)
                # update the pile card counter
                self.update_pile_card_count_text()
                print('Not slappable, Player ' + str(player + 1) + ' burns a card')
                # update the player action text
                self.update_player_action_text('Not slappable, Player ' + str(player + 1) + ' burns a card')
        # if the deck is empty, warn the player
        else:
            print('Cannot slap nothing')
            self.update_player_action_text('Cannot slap nothing')

    def check_if_slappable(self):
        # defaults slappable to 0
        self.slappable = [0]
        # if the rule is selected at the beginning of the game
        # if the pile is slappable, sets slappable[0] to 1 and slappable[1] to the type of hand
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
            # adds to 10 (accounting for aces as 1s)
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
            # ascending straight (accounting for aces as 1s)
            elif (((self.card_pile[0].value + 1) == self.card_pile[1].value and (self.card_pile[1].value + 1) == self.card_pile[2].value) or (self.card_pile[0].value == 14 and self.card_pile[1].value == 2 and self.card_pile[2].value == 3)) and self.selected_rules[7] == 1:
                self.slappable = [1, 'Ascending Straight']
            # descending straight (accounting for aces as 1s)
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
        # hides the back card of each player in case they are out of play
        self.hide_back_card(self.player_turn)
        # checks if the player still has cards in their hands and sets their in play to True, else False
        self.players_in_play = [True if len(self.hands[participants]) != 0 else False for participants in range(self.players)]
        # if the player is in play, reshow their back card
        if self.players_in_play[self.player_turn] == True:
            self.show_back_card(self.player_turn)
        # sums all the players in play to know when the game is done
        self.sum_players = sum(self.players_in_play)

    def select_rules_graphics(self):
        # sets up the initial window
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
