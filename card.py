import random

class Card:
    
    def __init__(self, number, suit):
        suit = suit.capitalize()
        number = number.capitalize()
        
        if number in ['Ace', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King', 'A', 'J', 'Q', 'K']:
            self._number = number
        else:
            self._number = '0'
            print('Invalid number')
            
        if self.number in ['Ace', 'A']:
            self._value = 14
        elif self.number in ['Jack', 'J']:
            self._value = 11
        elif self.number in ['Queen', 'Q']:
            self._value = 12
        elif self.number in ['King', 'K']:
            self._value = 13
        else:
            self._value = int(self.number)
            
        if suit in ['Clubs', 'Diamonds', 'Hearts', 'Spades']:
            self._suit = suit
        else:
            self._suit = 'Nothing'
            print('Invalid suit')
        
    def __repr__(self):
        return self.number + ' of ' + self.suit
    
    @property
    def suit(self):
        return self._suit
    
    @suit.setter
    def suit(self, suit):
        suit = suit.capitalize()
        if suit in ['Clubs', 'Diamonds', 'Hearts', 'Spades']:
            self._suit = suit
        else:
            print('Invalid suit')
    
    @property
    def number(self):
        return self._number    

    @number.setter
    def number(self, number):
        number = number.capitalize()
        if number in ['Ace', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King']:
            self._number = number
        else:
            print('Invalid number')
        
        if self.number in ['Ace']:
            self._value = 14
        elif self.number in ['Jack']:
            self._value = 11
        elif self.number in ['Queen']:
            self._value = 12
        elif self.number in ['King']:
            self._value = 13
        else:
            self._value = int(self.number)
            
    @property
    def value(self):
        return self._value

    @property
    def image_file(self):
        return str(self._value) + self._suit + '.ppm'

class Deck:
    
    def __init__(self):
        self._cards = []
        self.populate()
        
    def __repr__(self):
        deck = ', '.join([str(card) for card in self._cards])
        return deck
    
    @property
    def cards(self):
        return self._cards
        
    def populate(self):
        suits = ['Clubs', 'Diamonds', 'Hearts', 'Spades']
        numbers = ['Ace', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King']
        self._cards = [Card(n, s) for s in suits for n in numbers]
    
    def shuffle(self):
        random.shuffle(self._cards)