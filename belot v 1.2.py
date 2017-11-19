#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""   ======================================================BELOT===============================================
------------------------------------------------------by Miroslav Georgiev--------------------------------------

* Data structures:
- Card class: holds a Card. Attributes: Suit and Rank (both strings). Can get its power according to GameState.currentPower table.
- Deck class: holds the deck and its 32 cards. Handles card distribution, shuffling in the beginning of each game,
    collecting cards after each game and cutting them before the next game.
- Hand class: holds players. Attributes:
    --ID (string) - shows name of the player
    --team (string) - shows to which of the two teams it belongs 
    --hand (list of Cards) - holds the cards the player is holding currently
    --suit power (dict of strings): - holds the analyzed strength of each suit in a player's hand 
    --saved_cards (list of Cards) - holds Cards which have been saved for special strategical reason.
    --winnings (list of Cards) - holds Cards that the player has won up to now
    --announces (list of Anons) - holds announces the player has. This doesn't mean they are in play!
    --rect - player's position on the screen for drawing purposes.
Hand class holds a great number of methods which handle most of the actions in the game, such as playing cards, responding
to other players, betting, etc.

- Anons class: holds an announce. Attributes:.
    --vid (int[3:5})/'belote'/'care' - shows the type of the anons
    --suit (string) - shows the suit of the announce
    --(optional) last card (string) - if sequence, shows which is the last card of the sequence
    --(optional) rank (string) - if care, shows what is the rank of the care

- Strategy class: holds the strategic decisions of a team. Attributes:
    --team (string) - shows which of the two teams the class represents
    --behavior (string) - sets the sort of moves the AI will use during game and betting
    --passed (dict of suit: list of ranks) - holds the cards of each suit that have passed already 
    --interesting suits (list of string) - holds suits of interest for this team
    --partner suits (list of string) - holds the suitsin which the two partners are strong

Strategy class has methods to analyze a hand and its strategic strength, as well as other methods related to AI.

- Game State class: holds a number of global variables for the game, and methods for changing these variables.
- Animation class: handles animations in the game. 

"""

import pygame, sys, random, math, location
from pygame.locals import *

# global constants
WIDTH = 1300
HEIGHT = 900
CENTER = [WIDTH // 2, HEIGHT // 2 - 50]
FPS = 120

# card constants
CARD_SIZE = (72, 96)
CARD_CENTER = (36, 48)
# card orders and powers
SUITS = ('C', 'S', 'H', 'D')
RANKS = ('A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K')
ALL_TRUMP_POWER = {'7': 1, '8': 2, 'Q': 3, 'K': 4,
                    '10': 5, 'A': 6, '9': 7, 'J': 8}
NO_TRUMP_POWER = {'7': 1, '8': 2, 'Q': 5, 'K': 6,
                  '10': 7, 'A': 8, '9': 3, 'J': 4}
BID_ORDER = ('pass', 'C', 'D', 'H', 'S', 'No trumps', 'All trumps')
CARD_VALUE_NO_TRUMP = {'7': 0, '8': 0, '9': 0, 'J': 2,
                       'Q': 3, 'K': 4, '10': 10, 'A': 11}
CARD_VALUE_ALL_TRUMP = {'7': 0, '8': 0, 'Q': 3, 'K': 4,
                        '10' : 10, 'A': 11, '9': 14, 'J': 20}
# announces orders and power
ANNOUNCE_ORDER = ('7', '8', '9', '10', 'J', 'Q', 'K', 'A')
CARE_ORDER = ('Q', 'K', '10', 'A', '9', 'J')
ANNOUNCE_VALUE = {3: 20, 4: 50, 5: 100, 6: 100, 7: 100, 8: 100, 'belote': 20}
CARE_VALUE = {'Q': 100, 'K': 100, '10': 100, 'A': 100, '9': 150, 'J': 200}
STRAT_ORDER = ["commanding", "controlling", "strong block", "long", "blocking", "weak"]
# colors
BLACK   = (  0,   0,   0)
RED     = (227,  32,  81)
ORANGE  = (255, 171,  68)
YELLOW  = (250, 242,   5)
DARKRED = (232,   9,  64)
WHITE   = (255, 255, 255)
SILVER  = (219, 214, 211)
GREEN   = (  7, 138,  80)
BROWN   = (156, 120,  64)
BLUE    = ( 31,  28, 124)
BGCOLOR = BLACK

# class definitions
class Card:
    def __init__(self, suit, rank):
        """ Represents a playing card, with its suit and rank.
            suit -> string; rank -> string. """
        if (suit in SUITS) and (rank in RANKS):
            self.suit = suit
            self.rank = rank
        else:
            self.suit = None
            self.rank = None
            print "Invalid card: ", suit, rank

    def __str__(self):
        return self.suit + self.rank

    def __eq__(self, other):
        return self.suit == other.suit and self.rank == other.rank

    def get_suit(self):
        return self.suit

    def get_rank(self):
        return self.rank

    def get_power(self):
        """ Returns the power of the given card,
        according to the power table currently in force for the
        card's suit """
        if game.currentPower[self.suit] == ALL_TRUMP_POWER:
            return ALL_TRUMP_POWER[self.rank]
        else:
            return NO_TRUMP_POWER[self.rank]

    def draw(self, surface, pos):
        """ Draws a card on a pygame surface. Uses the composite card image """
        card_rect = (CARD_SIZE[0] * RANKS.index(self.rank),
                     CARD_SIZE[1] * SUITS.index(self.suit), CARD_SIZE[0], CARD_SIZE[1])
        surface.blit(CARD_IMAGES, pos, card_rect)

class Deck:   
    def __init__(self):
        """ Represents the playing deck (a collection) of 32 cards. """
        self.deck = []
        exclude = ('2', '3', '4', '5', '6')
#        not all 52 cards from a standard deck play in Belot
        for suit in SUITS:
            for rank in RANKS:
                if rank in exclude:
                    continue
                
                self.deck.append(Card(suit, rank))
                                    
    def __str__(self):
        return "Deck: " + ", ".join(str(card) for card in self.deck)
    
    def shuffle(self):
        """ Randomly shufles the deck. This is done every time a new round starts. """
        random.shuffle(self.deck)

    def deal_card(self):
        """ Pops a card from the deck and returns it """
        return self.deck.pop()
    
    def collect_cards(self, player_cards):
        """ Add a collection of cards back to the deck (this happens at the end of each game
        to restock the deck) """
        self.deck.extend(player_cards)

    def cut(self):
        """ Divides deck in two, then swaps the two halves; this is
        done every time a new round starts """
        first_half = self.deck[:len(self.deck) // 2]
        second_half = self.deck[len(self.deck) // 2:]
        self.deck = second_half + first_half

class Hand:     
    def __init__(self, identity, team):
        """ Represents each player, his ID (computer or life player) and team.
        Includes all actions the player performs during game. """
        self.id = identity
        self.team = team
        self.hand = []            # -> list of Cards that the player is currently holding 
        self.announces = []       # -> list of Anons that the player has; They still need to be declared!   
        self.belotes = []         # -> list of belotes; they also need to be declared!
        self.suit_power = {}      # -> dict; stores the power of each suit (if any), according to current analysis
        self.saved_cards = []     # -> list of Cards; stores cards from your hand which are important to keep for later
        self.winnings = []        # stores cards won in previous rounds; add these with an .extend method
        self.rect = pygame.Rect(350, 650, 0, 96)
        self.cardDest = [0, 0]    # -> screen coords; holds the destination points for some drawing operations
        self.winDest = [0, 0]     #
        
    def __str__(self):
        info = self.id + ": " + ", ".join(str(card) for card in self.hand)
        if self.announces:
            info += " Announces: " + ", ".join(str(anons) for anons in self.announces)
        return info

    def __iter__(self):
        for card in self.hand:
            yield card

    def add_card(self, card):
        """ Add the given card to the hand """ 
        self.hand.append(card)
          
    def find_card(self, sequence, card):
        """ Finds a particular card in a given sequence; returns its index.
            sequence -> list of Cards
            card -> Card """
        for i in range(len(sequence)):            
            if sequence[i].get_suit() == card.get_suit() and sequence[i].get_rank() == card.get_rank():
                return i
                                     
    def play_card(self, card):
        """ Returns the index of a given card and pops it (removing it from the hand).
            Assume that the given index is not out of range!
            card -> int """
        return card, self.hand.pop(card)

    def take(self, suit, target):
        """ Play a card from the given suit greater in power than target.
            suit -> string
            target -> Card """
        subset = self.separate_suit(suit)
        possibilities = []
        
        for card in subset:
            if card.get_power() > target.get_power():
                possibilities.append(card)
                        
        if len(possibilities) < 2:
            dec = self.find_card(self.hand, possibilities[0])
            return dec, self.hand.pop(dec) 
        else:
            # if you have more than one option, choose the lowest option         
            if suit in self.belotes and (possibilities[-1].get_rank() == 'Q' or possibilities[-1].get_rank() == 'K'):                
                return self.announceBelote(possibilities[-1])   # also announce a belote
            else:
                dec = self.find_card(self.hand, possibilities[-1])
                return dec, self.hand.pop(dec) 
                          
    def respond(self, suit):
        """ Play a low card from the given suit, or announce a belote.
            suit -> string"""
        subset = self.separate_suit(suit)

        if suit in self.belotes:        # check for a belote in this suit; return its card if you have one    
            return self.announceBelote(getBelote(self, suit))
                       
        dec = self.find_card(self.hand, subset[-1])
        return dec, self.hand.pop(dec)        

    def trump(self, trump, other_card):
        """ Play a card from the trump suit; if there's another trump,
            give a higher trump (if you have one). Assume there is a trump in the game.
            This action should only happen in response to previous players' actions, during a trump game.
            trump -> string
            other_card -> list of Player, Card """
        subset = self.separate_suit(trump)

        if other_card[1].get_suit() == trump:
            # there's another trump winning so far
            if other_card[0].team == self.team:
                return self.clean("partner") # it's your partner; don't need to give a trump
            else:        # it's the adversary
                if self.has_higher(subset, other_card[1]):
                    # take with a higher trump
                    for i in xrange(len(subset)):
                        if subset[i].get_power() > other_card[1].get_power():
                            if subset[i].get_rank() == "Q" or subset[i].get_rank() == "K":
                                if self.belotes:   # you have a belote, which is necessarily of the trump suit
                                    return self.announceBelote(subset[i])
                                else:
                                    return i, self.hand.pop(i)
                            else:
                                return i, self.hand.pop(i)
                else:   # give another low card, no need to be a trump
                    return self.clean("adversary")
        else:           # no other trump; take with the lowest trump available, or attempt to belote
            if self.belotes:   # you have a belote, which is necessarily of the trump suit
                return self.announceBelote(getBelote(self, trump))
            else:
                dec = self.find_card(self.hand, subset[-1])
                return dec, self.hand.pop(dec)
            
    def clean(self, mode):
        """ Play a 'useless' card; assume that
            player can't respond to the asked suit. Also update self.belots
            if the chosen card breaks a belot.
            mode -> string"""        
        
        if mode == "adversary":
            # it's the adversary, clean the lowest possible card
            lowest = None
            for card in self.hand:    # find the lowest card; first check if it's saved
                if lowest is None:    
                    if card in self.saved_cards:
                        continue
                    lowest = card
                else:
                    if card in self.saved_cards:
                        continue
                    if card.get_power() < lowest.get_power():
                        lowest = card
                      
            if lowest is None:
                # all cards turned out to be saved; repeat the loop without looking
                for card in self.hand:
                    if lowest is None:
                        lowest = card
                    else:
                        if card.get_power() < lowest.get_power():
                            lowest = card
                            
            chosen_index, chosen = self.find_card(self.hand, lowest), self.hand.pop(self.find_card(self.hand, lowest))
            if (chosen.get_rank() == 'Q' or chosen.get_rank() == 'K') and self.belotes:
                # check if the card cleaned is part of a valid belote; if so, remove the belote from self. belotes
                # because player won't be able to declare it anymore
                for belot in self.belotes:
                    if chosen.get_suit() == belot.suit:
                        self.belotes.remove(belot)
            return chosen_index, chosen    
                    
        elif mode == "partner":
            # it's your partner, clean a card of some value
            subset = []
            for card in self.hand:
                if card.get_power() == 1 or card.get_power() == 2 or card.get_power() == 8:
                    continue    # skip low value cards and J/A                
                subset.append(card)
            if len(subset) < 1:   # all remaining cards are low
                chosen_index, chosen = 0, self.hand.pop(0)
            else:
                chosen_index, chosen = self.find_card(self.hand, subset[-1]), self.hand.pop(self.find_card(self.hand, subset[-1]))
            if (chosen.get_rank() == 'Q' or chosen.get_rank() == 'K') and self.belotes:
                # check if the card cleaned is part of a valid belote; if so, remove the belote from self. belotes,
                # because player won't be able to declare it anymore
                for belot in self.belotes:
                    if chosen.get_suit() == belot.suit:
                        self.belotes.remove(belot)
            return chosen_index, chosen    
        
    def attack(self, suit, mode):
        """ Demand with the strongest card in a suit, or try to 'bore' the suit. 
            Assume you have at least 1 card in this suit.
            suit -> string
            mode -> string """
        subset = self.separate_suit(suit)
        
        if mode == "demand":
            card = subset[0]     # also announce belote if that's the case
            if card.get_rank() == "Q" or card.get_rank() == "K":
                if card.get_suit() in self.belotes:
                    return self.announceBelote(card)
                else:
                    dec = self.find_card(self.hand, subset[0])
                    return dec, self.hand.pop(dec)
            else:
                dec = self.find_card(self.hand, subset[0])
                return dec, self.hand.pop(dec)
        elif mode == "bore":
            # attempt to flush the higher cards in a suit; assume you have more than 1 card in it
            card = subset[1]     # don't use your strongest card, use the next strongest
            if card.get_rank() == "Q" or card.get_rank() == "K":
                if card.get_suit() in self.belotes:                    
                    return self.announceBelote(card)
                else:
                    dec = self.find_card(self.hand, subset[1])
                    return dec, self.hand.pop(dec)
            else:
                dec = self.find_card(self.hand, subset[1])
                return dec, self.hand.pop(dec)
            
    def find_partner(self, no_suit):
        """ Attempt to 'find' your partner (play a card in a suit he's strong in).
            no_suit -> string, which shouldn't be played!"""
        if self.team == "Team 1":
            team = strategy1
        elif self.team == "Team 2":
            team = strategy2
        targetSuit = None
        
        for suit in team.partner_suits:
            if suit == no_suit:
                continue
            else:
                targetSuit = suit
        if targetSuit is None:    # couldn't find, clean instead
            return self.clean("adversary")            
        else:            
            subset = self.separate_suit(targetSuit)
            if len(subset) == 0:      # you don't have a card from the required suit, 
                return self.clean("adversary")              # clean instead
            else:
                dec = self.find_card(self.hand, subset[-1])
                return dec, self.hand.pop(dec)                
        
    def get_announces(self):
        """ Discover any announces the player has;
            append them to self.announces as necessary """
        for suit in SUITS:            
            if len(self.separate_suit(suit)) > 1:     # skip suits that have less than 2 cards
                self.find_sequence(self.separate_suit(suit))
                
        self.find_care(self.hand[0])
        # if player has a carre declaration, check his other declarations for overlapping cards -
        # only one declaration per card can be valid in Belote! 
        if 'care' in self.announces and len(self.announces) > 1:
            for anons in self.announces:
                if anons.vid == 'care':
                    findOverlapSequence(self, anons)            
       
    def find_sequence(self, cards):
        """ Search given cards for a sequence according to ANNOUNCE_ORDER;
            if there is a sequence, append it to self.announces.
            cards -> List of cards"""        
        # make a new sequence of only the card ranks, sort it
        def get_announce_order(card):
            return ANNOUNCE_ORDER.index(card)
        new_cards = [card.get_rank() for card in cards]  
        new_cards = sorted(new_cards, key=get_announce_order)
        
        sequence = []       # -> list; store the final sequences        
        count = 1           # -> int; stores number of sequential cards (one card is always sequential)
        last = None         # -> list; stores the last card's index and card
        
        for card in new_cards:
            if last is None:   # the first card 
                last = [ANNOUNCE_ORDER.index(card), card]
            else:
                if ANNOUNCE_ORDER.index(card) == last[0] + 1:
                    count += 1   # if in order, add to the counter
                    last = [ANNOUNCE_ORDER.index(card), card]
                else:
                    if count >= 3:             # check if we found a sequence already,
                        poredni = Anons(count, cards[0].get_suit(), last[1])
                        self.announces.append(poredni)    # add it to self.announces
                    count = 1                  # if not, reset counter
                    last = [ANNOUNCE_ORDER.index(card), card]
                    
        if count >= 3:
            poredni = Anons(count, cards[0].get_suit(), last[1])
            self.announces.append(poredni)

        # find belotes (Q and K of the same suit);
        # in a trump contract, only a belote from the trump suit is possible        
        if BID_ORDER.index(game.contract[1]) < 5:           
            if cards[0].get_suit() == trump and ("Q" in new_cards and "K" in new_cards):
                belot = Anons("belote", cards[0].get_suit()) 
                self.belotes.append(belot)
        else:
            if "Q" in new_cards and "K" in new_cards:  # find a bellot
                belot = Anons("belote", cards[0].get_suit())
                self.belotes.append(belot)
        
    def find_care(self, anchor):
        """ Search your hand for four equal cards ("carre"); if found, search for another carre
            (you can logically have a maximum of 2 in a single hand);
            append to self.announces as appropriate.
            anchor -> Card"""
        collection = [anchor]  # use the given anchor card as reference
        
        for card in self.hand:
            if card == anchor:  # skip the anchor card
                continue
            if card.get_rank() == anchor.get_rank():
                collection.append(card)   # if ranks match, append to collection
                
        if len(collection) == 4:   # we found a care
            care = Anons("care", collection[0].get_suit(), None, collection[0].get_rank())
            # skip cares of 7 and 8 - they aren't valid in Belote
            if care.rank != "7" and care.rank != "8":
                self.announces.append(care)   
            # attempt to find one more care, without continuing the recursion
            def exclude(card):
                return card.rank != care.rank
            new_set = filter(exclude, self.hand)
            
            def include(card):
                return card.rank == new_set[0].get_rank()
            result = filter(include, new_set)
            if len(result) == 4:
                # found a second carre, register it if not of 7 or 8
                care2 = Anons("care", result[0].get_suit(), None, result[0].get_rank())
                if care2.rank != "7" and care2.rank != "8":
                    self.announces.append(care2)   
        else:
            if self.hand.index(anchor) < len(self.hand) - 1:  # continue recursion
                self.find_care(self.hand[self.hand.index(anchor) + 1])

    def announceBelote(self, belote_card):
        """ Declare a belote, do the necessary stuff and return the belote_card passed;
            assume that the relevant belote is in self.belotes and is valid """        
        for belot in self.belotes:            
            if belot.suit == belote_card.get_suit():
                game.announces.append([self, belot])
                self.belotes.remove(belot)  # remove it so that it doesn't announce it again :)
                if self.id == "Player 1":
                    game.gameMessage = MES.get_game_message("plbelot")
                else:
                    game.gameMessage = MES.get_game_message("compbelot", self.id)
                break  
        
        dec = self.find_card(self.hand, belote_card)
        return dec, self.hand.pop(dec)
    
    def sort_hand(self):
        """ Order the cards in descending order according to power"""
        def get_card_power(card):
            return card.get_suit(), card.get_power()

        result = sorted(self.hand, key=get_card_power)
        result.reverse()        
        self.hand = result

    def separate_suit(self, suit):
        """ Get a subset of cards only from the given suit """
        return filter(lambda card: card.get_suit() == suit, self.hand)

    def has_suit(self, suit):
        for card in self.hand:
            if card.get_suit() == suit:
                return True
        return False
    
    def has_trump(self, trump):
        """ Check if there's a trump in the hand """
        for card in self.hand:
            if card.get_suit() == trump:
                return True
        return False        

    def has_higher(self, hand, winning):
        """ Check if there's a higher value card in the given hand than the given card """
        for card in hand:
            if card.get_power() > winning.get_power():
                return True                
        return False    
        
    def collect_hand(self, hand):
        """ Add the cards in the given dict to the winnings"""
        cards = [card for card in hand.values()]
        self.winnings.extend(cards)
                
    def update(self):
        """ Update the size of the 'player' on-screen as cards in his hand diminish"""
        self.rect[2] = (CARD_SIZE[0] - 20) * len(self.hand)
                
    def draw(self, canvas, pos):
        """ Draw a hand on the canvas, use the draw method for cards """
        card_pos = [0, 0]
                  
        for card in xrange(len(self.hand)):     # players from Team 1 keep their cards organized horizontally 
            if self.team == "Team 1":
                card_pos[0] = pos[0] + card * (CARD_SIZE[0] - 20)
                card_pos[1] = pos[1]
            elif self.team == "Team 2":         # Team 2 - vertically
                card_pos[0] = pos[0]
                card_pos[1] = pos[1] + card * (CARD_SIZE[1] - 40)
            
            if self.id == 'Player 1':
                self.hand[card].draw(canvas, card_pos)
            else:
                canvas.blit(CARD_BACK_IMAGE, card_pos)
                
        if self.winnings:    # draw the 'winnings pile'
            if self.team == "Team 1":
                back_rect = (pos[0] + 600, pos[1], CARD_SIZE[0], CARD_SIZE[1])
            elif self.team == "Team 2":
                back_rect = (pos[0], pos[1]  + 450, CARD_SIZE[0], CARD_SIZE[1])
                     
            canvas.blit(CARD_BACK_IMAGE, back_rect)

class Anons():
    """ Represents declarations in the game:
        sequences of 3 or more cards, belotes and carres """
    def __init__(self, vid, suit, last_card=None, rank=None):
        self.vid = vid   # -> int or string; denotes what type the declaration is, i.e. belote, sequence or carre
        self.suit = suit # -> Suit; the suit of the declaration (doesn't matter if carre)
        self.last_card = last_card   # -> Card; optional for sequences only; denotes how hight the seq is 
        self.rank = rank        # -> Rank; optional for carre only; denotes the rank of the cards of the carre

    def __str__(self):
        info = str(self.vid) + " " + self.suit
        if self.last_card:
            info += " " + self.last_card
        if self.rank:
            info += " " + self.rank
        return info

    def __eq__(self, other):
        if self.vid == other:
            return True
        elif self.suit == other:
            return True
    
class Strategy:
    """ Handles the strategic decisions of computer players """
    def __init__(self, team):
        self.team = team
        self.behavior = "normal"      # -> String; determines if a team will behave "normal",
                                      # "aggressive", "defensive" or "desperate". 
                                      # Starts as "normal" and depends on current result, announces, etc.
        self.interesting_suits = []   # -> list of Strings; suits of interest from strategical point,
                                      # usually held by the adversary, or being fought over
        self.partner_suits = []   # -> list of Strings; partners are strong in these suits
        self.passed = {}          # -> Dict{suit: [list of ranks]}. Stores cards of a particular suit,
                                  # which is of interest for some reason. Use it to keep track
                                  # of which cards have passed in previous rounds and act accordingly.
        self.bid_history = []    # -> List of [Player: bid] lists; stores which player bid what during
                                      #  the last bidding phase 
    def count(self, member1, member2):
        """ Count the values of the cards of the given members and return the result. 
            This is done at the end of each game."""
        members = [member1, member2]
        result = 0
        for player in members:
            if player.winnings:    # count the winnings if any
                for card in player.winnings:
                    result += getCardValue(card)                  
        return result 

    def check_passed(self, suit):
        """ Check the cards of the given suit which have passed already;
            return the current highest card or None if suit isn't being tracked.
            suit -> String"""            
        if suit not in self.passed:   # return None if no info about the suit
            return None
        else:
            power_table = dict(game.currentPower[suit])  # get the current power table
            strongest = None

            for card in self.passed[suit]:               # remove passed cards from power table
                power_table.pop(card)
                
            if len(power_table) > 0:                # if there's still cards in play
                for card in power_table:            # find the strongest of the remaining cards
                    if strongest is None:
                        strongest = card
                    elif power_table[card] > power_table[strongest]:
                        strongest = card
                return Card(suit, strongest)
            
    def get_suit_power(self, hand):
        """ Determine the No trump and All trump power of a given hand (which is always of a single suit);
            return a list [int, int, string], where int1 shows No trump power, int2 shows All trump power, 
            and the string is the result of an analysis of the hand's composition """
        analysis = None    # a variable holding the analysis of the suit's power
        if game.contract[1] == "pass" or len(hand) < 1:    # choose the right table according to contract
            powerTable = NO_TRUMP_POWER    
        else:
            if game.contract[1] == hand[0].get_suit() or game.contract[1] == "All trumps":
                powerTable = ALL_TRUMP_POWER
            else:
                powerTable = NO_TRUMP_POWER        
        
        if len(hand) < 1:     # no cards in this suit
            return None
        elif len(hand) == 1:  # only 1 card
            if hand[0].get_rank() != "J" and hand[0].get_rank() != "A":
                # return 1 power if the card isn't the strongest in the suit
                return [1, 1, "weak"]    
            else:
                # 3 power in the relevant mode if it is
                analysis = 'weak'
                if hand[0].get_rank() == "J":    
                    return [0, 3, analysis]
                elif hand[0].get_rank() == "A":
                    return [3, 0, analysis]
        else:                       # more than 1 card
            no_trump_power = 0      # set variables:  
            all_trump_power = 0     # two integers store total strength cards in the relevant games;
            subset = []             # subset stores a list which helps in analysis
            for card in hand:
                no_trump_power += NO_TRUMP_POWER[card.get_rank()]
                all_trump_power += ALL_TRUMP_POWER[card.get_rank()]
                if powerTable[card.get_rank()] == 8:   # found the strongest in the suit
                    subset.append('first')
                elif powerTable[card.get_rank()] == 7: # found the second strongest
                    subset.append('second')
                elif powerTable[card.get_rank()] == 6: # found the third strongest
                    subset.append('third')    

            if 'first' in subset:               # if we have the strongest
                if 'second' in subset:
                    analysis = 'commanding'     # if we have both strongest cards 
                elif ('third' in subset and len(hand) > 2) or len(hand) > 3:    # if we have either the first and third card
                    analysis = 'controlling'                                    # + one more, or the first + 3 or more
                else:                           # else the hand is weak
                    analysis = 'weak'
            elif 'second' in subset:            # if we have the second, we're blocking that suit
                if len(hand) > 2:
                    analysis = 'strong block'
                else:
                    analysis = 'blocking'
            elif 'third' in subset and len(hand) > 3:
                analysis = 'long'               # If we have the third and many more, we still have a valuable hand
            else:
                analysis = 'weak'

            return [no_trump_power, all_trump_power, analysis]
                            
    def analyze_hand(self, player):
        """ Analyze the player's hand for bidding purposes; return a Dominant suit (if any),
            overal no-trump power and overal all-trump power.
            player -> Hand"""
        dominant = None    # dominant suit is any suit which has all-trump power > 17;
                           # if there's more than one such suit, dominant becomes the more powerful
        no_trump_power = 0
        all_trump_power = 0
                       
        sep_hand = {}    # separate the suits in the hand, form a dict            
        sep_hand["C"] = player.separate_suit("C")
        sep_hand["D"] = player.separate_suit("D")
        sep_hand["H"] = player.separate_suit("H")
        sep_hand["S"] = player.separate_suit("S")
        # get each suit's power analysis
        for suit in sep_hand:     
            sep_hand[suit] = self.get_suit_power(sep_hand[suit])
        
        for suit, value in sep_hand.items():
            if value == None:    # no cards in this suit
                continue
            no_trump_power += value[0]
            all_trump_power += value[1]
            if dominant is None:
                if value[1] > 17:
                    dominant = suit
            else:
                if value[1] > sep_hand[dominant][1]:
                    dominant = suit
                    
        return dominant, no_trump_power, all_trump_power

    def post_analysis(self, playhand, members):
        """ Analyze the cards that just passed; if they're from interesting suits,
            add them to self.passed as a list of ranks.
            playhand -> Dict of {Hand: Card}
            members -> List of Hands """        
        for suit in playhand:
            if rund == 1:       # after the first round, add the card of your teammate to partner_suits
                if suit.team == self.team:                                  # as a precautionary matter
                    if playhand[suit].get_suit() not in self.partner_suits:
                        self.partner_suits.append(playhand[suit].get_suit())
                        
        for card in playhand:
            card_suit = playhand[card].get_suit()
                  
            if card_suit not in self.passed:            # start tracking for the first time
                self.passed[card_suit] = [playhand[card].get_rank()]
                if rund != 1:    # if this is not the first round, there may be other cards already passed;
                    for player in turnOrder:    # check players' winnings to add these cards
                        for passed_card in player.winnings:
                            if passed_card.get_suit() == card_suit:
                                self.passed[card_suit].append(passed_card.get_rank())
                    
            else:
                self.passed[card_suit].append(playhand[card].get_rank())
                if len(self.passed[card_suit]) >= 8:    # all cards of this suit passed,
                    for member in members:              # remove them from the members' suit_power 
                        if card_suit in member.suit_power:
                            member.suit_power.pop(card_suit)
                    if card_suit in self.interesting_suits:
                        self.interesting_suits.remove(card_suit)  # and also from int. and partner suits
                    if card_suit in self.partner_suits:
                        self.partner_suits.remove(card_suit)
               
    def decide_bet(self, player, current_bid):
        """ analyze the hand, the current bet and contract history;
            then return a betting suggestion as a string """
        power_suit, no_trump_power, all_trump_power = self.analyze_hand(player)

        if current_bid[1] == "pass":    # if player is the first to bid, or there are only passes
            if self.behavior == 'desperate':
                return "pass"     # don't say anything if desperate; wait for the other team to raise smt
            elif self.behavior == 'defensive':
                if power_suit:        # be careful on No and All trumps, raise only if the team is first
                    return power_suit
                elif (no_trump_power > 18 and no_trump_power > all_trump_power) and game.first.team == self.team:
                    return "No trumps"
                elif all_trump_power > 18 and game.first.team == self.team:
                    return "All trumps"
                else:
                    return "pass"
            else:       # bid normally according to your cards
                if power_suit:        
                    return power_suit
                elif no_trump_power > 18 and no_trump_power > all_trump_power:
                    return "No trumps"
                elif all_trump_power > 18:
                    return "All trumps"
                else:
                    return "pass"
                
        else:             # if there is another bid already
            if current_bid[0].team == player.team:   # if it's your partner's bid
                if contra:                   # check if there's a contra in the game, which has necessarily been called by the adversary
                    if self.behavior == 'agressive' and game.first.team == self.team:
                        return 're-contra'   # raise if you're particularly cocky (and start first)
                    else:
                        return "pass"
                elif reContra:               # your teammate called this, don't undercut him
                    return "pass"
                else:                    
                    if power_suit:           # if you have a strong suit 
                        if BID_ORDER.index(current_bid[1]) < 5:             # if it's a suit bid still, either declare your suit 
                            if BID_ORDER.index(power_suit) > BID_ORDER.index(current_bid[1]):  # or call All trumps
                                return power_suit
                            else:
                                return "All trumps"
                        elif BID_ORDER.index(current_bid[1]) == 5:          # if your partner has bid No trumps, only raise 
                            if all_trump_power > 25 and game.first.team == self.team: # if you have very strong cards
                                return "All trumps"
                            else:
                                return "pass"
                        elif BID_ORDER.index(current_bid[1]) == 6:
                            return "pass"
                    else:      # no strong suit
                        if (BID_ORDER.index(current_bid[1]) < 6 and all_trump_power > 20) and \
                           game.first.team == self.team:
                            return "All trumps"  # raise only if you have a very strong general All trumps
                        else:
                            return "pass"
                        
            else:             # if it's the adversary's bid
                if contra or reContra:    # this case should mean that your partner has declared the contra,
                    return "pass"         # no need to say anything  
                else:                    
                    if not power_suit and (no_trump_power < 13 and all_trump_power < 13):
                        return "pass"       # pass if you have no good cards
                    else:
                        if power_suit and BID_ORDER.index(current_bid[1]) < 5:  # if you have a suit and
                                                                                # current bid is under No trump
                            if power_suit == current_bid[1]:                    # if you also have the same strong suit                                
                                if self.behavior == "aggressive" or self.behavior == "desperate":
                                    return "contra"
                                else:
                                    return "pass"
                            else:                                
                                for bid in self.bid_history:    # check bids so far
                                    if bid[0].team == player.team:   # if you or your partner had said smt already:
                                        if BID_ORDER.index(power_suit) > BID_ORDER.index(current_bid[1]):
                                            return power_suit   # raise your suit if you can
                                        elif all_trump_power > 17 and game.first.team == self.team:
                                            return "All trumps"    # raise All trumps if you're first
                                # your team hasn't declared anything yet
                                if BID_ORDER.index(power_suit) > BID_ORDER.index(current_bid[1]):
                                    return power_suit   # declare your suit if you can
                                else:
                                    if (self.behavior != "defensive" and self.behavior != "desperate") and \
                                       game.first.team == self.team:
                                        return "All trumps"   # raise All trumps if team isn't defending and is first
                                    else:
                                        if self.behavior == 'desperate':
                                            return "contra"
                                        else:
                                            return "pass"
                                            
                        elif not power_suit and BID_ORDER.index(current_bid[1]) < 5: # if you have no suit and
                                                                                     # current bid is under No trump
                            if no_trump_power > 15 and self.behavior != "defensive": # raise the bet if your team 
                                return "No trumps"                                   # isn't playing defensively and you have cards
                            elif all_trump_power > 15 and self.behavior != "defensive":
                                return "All trumps"
                            elif self.behavior == "desperate":
                                return "No trump"
                            else:                            
                                return "pass"
                            
                        elif BID_ORDER.index(current_bid[1]) == 5:    # if the bid is No trumps
                            if (no_trump_power > 20 and game.first.team == self.team) and \
                               self.behavior == "aggressive":
                                return "contra"
                            else:                                
                                if all_trump_power > 18 and self.behavior != "defensive":
                                    return "All trumps"    # raise if you have cards and not playing defensively
                                elif self.behavior == "desperate":
                                    return "All trumps"    # also raise if you're desperate
                                else:
                                    for bid in self.bid_history:   # check bids
                                        if bid[0].team == player.team and self.behavior != "defensive":
                                            return "All trumps"   # also raise if you (or your partner) have declared
                                                            # a suit before and you're not playing defensively
                                    return "pass"
                                
                        elif BID_ORDER.index(current_bid[1]) == 6:   # if the bid is All trumps
                            if (all_trump_power > 20 and game.first.team == self.team) and \
                               self.behavior == "aggressive":
                                return "contra"
                            else:                                
                                if self.behavior == "desperate":
                                    return "contra"      # raise if you're desperate
                                else:
                                    if all_trump_power > 25 and self.behavior != "defensive":
                                        return "contra" # raise if you have very good cards and not playing defensively
                                    else:
                                        return "pass"
                                    
    def CardStrategy(self, player, stance, lastIter=False):
        """ Decide the strategy for giving a card """                
        action, addon = None, None
        
        for suit in player.suit_power:            
            if player.suit_power[suit] == stance:  # found a matching suit for this stance,
                               # return something according to the stance, or continue the loop
                if stance == "commanding":      # you have a very strong suit!
                    if suit not in self.partner_suits:  # start tracking it
                        self.partner_suits.append(suit)
                    strongest = self.check_passed(suit)   # check the situation
                    if strongest:
                        if strongest in player.hand:      # if you currently hold the strongest card, demand with it
                            action, addon = "demand", suit 
                            break
                        else:    # this should only happen after the first two passes through this suit
                            player.suit_power[suit] = "weak"  # redesignate it as weak
                            if player.belotes:  # attempt to announce any belots
                                action, addon = "belote", getBelote(player)
                                break
                            else:                           # or else, continue the loop to find an alternative play
                                continue
                    else:   # didn't find the strongest card, risk it; this should happen only at the first rotation of this suit
                        action, addon = "demand", suit    # (since you haven't been tracking it, and already are)
                        break    
                elif stance == "controlling":
                    if suit not in self.partner_suits:  
                        self.partner_suits.append(suit)
                    strongest = self.check_passed(suit)   # check the situation
                    if strongest:
                        if strongest in player.hand:      # if it's in your hand, demand it
                            action, addon = "demand", suit
                            break
                        elif len(self.partner_suits) > 1 or self.partner_suits[0] != suit:   # else redesigante the suit, 
                            player.suit_power[suit] = "weak"    # then attempt other strategies
                            action, addon = "partner", suit     # attempt to find your partner
                            break
                        elif player.belotes:  # attempt to announce any belots
                            player.suit_power[suit] = "weak"
                            action, addon = "belote", getBelote(player)
                            break
                        else:
                            cards = player.separate_suit(suit)
                            if len(cards) > 1:           # else, try to bore the suit
                                player.suit_power[suit] = "weak"
                                action, addon = "bore", suit
                                break
                            else:  # if there's only one card left in the suit, redesignate it, then continue the loop
                                player.suit_power[suit] = "weak"
                                continue
                    else:    # no info, risk it
                        action, addon = "demand", suit
                        break
                elif stance == "strong block":
                    if suit not in self.interesting_suits:
                        self.interesting_suits.append(suit)
                    strongest = self.check_passed(suit)   # check the situation
                    if strongest and strongest in player.hand:  # we've bored it successfully before, demand it now
                        action, addon = "demand", suit
                        break
                    else:
                        if len(self.partner_suits) > 1:  # if your partner has something, attempt to find him
                            action, addon = "partner", suit
                            break
                        elif player.belotes:  # attempt to announce any belots
                            action, addon = "belote", getBelote(player)
                            break
                        else:
                            cards = player.separate_suit(suit)
                            if len(cards) > 2:              # if not, attempt to bore the suit
                                action, addon = "bore", suit
                                break
                            elif len(cards) > 1:            # if you only have 2 cards in the suit, redesignate it
                                player.suit_power[suit] = "blocking"  # and attempt a bore
                                action, addon = "bore", suit
                                break
                            else:
                                continue
                elif stance == "long":
                    if suit not in self.interesting_suits:
                        self.interesting_suits.append(suit)
                    strongest = self.check_passed(suit)   # check the situation
                    if strongest and strongest in player.hand:  # we've bored it successfully before, demand it now
                        action, addon = "demand", suit
                        break    
                    elif player.belotes:
                        action, addon = "belote", getBelote(player, suit)
                        break
                    else:   # try to bore the suit, if you still have lots of cards in it, else redesignate as 'weak'
                        cards = player.separate_suit(suit)
                        if len(cards) > 2:
                            action, addon = "bore", suit
                            break
                        else:
                            player.suit_power[suit] = "weak"
                            continue
                elif stance == "blocking":  # if you're only blocking a suit, you shouldn't play it
                    if suit not in self.interesting_suits:
                        self.interesting_suits.append(suit)
                    strongest = self.check_passed(suit)   # check the situation, maybe it's bored already?
                    if strongest and strongest in player.hand:
                        action, addon = "demand", suit
                        break
                    else:
                        cards = player.separate_suit(suit)
                        if lastIter and len(cards) > 1:   # it's a last resort iteration, try to bore the suit
                            action, addon = "bore", suit
                            break
                        elif self.partner_suits and (len(self.partner_suits) > 1 or self.partner_suits[0] != suit):
                            action, addon = "partner", suit  # attempt to find the partner
                            break
                        elif player.belotes:  # attempt to announce any belots
                            action, addon = "belote", getBelote(player)
                            break                        
                        else:
                            player.suit_power[suit] = "weak"
                            continue
                elif stance == "weak":
                    strongest = self.check_passed(suit)
                    if strongest and strongest in player.hand:
                        action, addon = "demand", suit
                        break                        
                    elif player.belotes:  # attempt to announce any belots
                        action, addon = "belote", getBelote(player)
                        break
                    else:
                        action, addon = "pass", "bla"
                        break
        if action is None:
        # no matching suit found for now:
            if stance != 'weak':  # continue the recursion with the next stance
                return self.CardStrategy(player, STRAT_ORDER[STRAT_ORDER.index(stance) + 1])
            else:      # you've exhausted the stance list, make a last recursive call with the 'blocking' stance 
                return self.CardStrategy(player, "blocking", True)
        else:
            return action, addon       
        
class GameState: 
    """ This class holds the states of the game and a number of global variables.
        It also handles all drawing. """
    def __init__(self):
        self.state = 1     # shows the game state: 0 - initial; 1 - bidding phase; 2- preparation phase;
                           # 3 - playing phase; 4 - score calculation
        self.contract = [None, "pass"]  # -> list of [Hand/suit], stores the current contract
                                        # and the player who bid last
        self.currentPower = {'C': NO_TRUMP_POWER, 'S': NO_TRUMP_POWER,    # stores the current power table 
                             'H': NO_TRUMP_POWER, 'D': NO_TRUMP_POWER}    # for each suit; start with the No trump power 
        self.announces = []   # -> a list of [Hand, Anons] which stores announces in the game so far  
        self.first = None     # -> Hand; holds the player which plays first this game
        self.last = None      # -> Hand: holds the player who won the last round in a game 
        self.team1Score = 0   # holds the score and games for each team
        self.team2Score = 0
        self.team1Games = 0
        self.team2Games = 0
        self.remaining = 0    # -> Int; holds points which remain from older games
        self.lastRound = False  # tracks if a last Round needs to be played
        self.gameMessage = None # game messages to be drawn as appropriate
        self.playerMessage = None
        self.bidMessage = None

    def __str__(self):
        if self.announces:
            info = "Anonsi: "
            for anons in self.announces:
                info += " " + anons[0].id + " " + str(anons[1])
            return info
        else:
            return "No announces"
        
    def switch_first(self, order):
        """ Re-arrange the turn order, putting player self.first to be first;
            in a normal game the first advances by 1 player each new round.
            order -> List of Hands"""
        if not self.first:    # set a random first for the beginning of the game
            self.first = random.choice([player1, player2, player3, player4])
        else:            
            new_first = (order.index(self.first) + 1) % 4    # determine the next first and change 
            self.first = order[new_first]                    # turn order accordingly
            
        return self.first

    def switch_currentPower(self, win_contract):
        """ Arrange suit power according to the winning contract.
            win_contract -> String """
        if BID_ORDER.index(win_contract[1]) > 0 and BID_ORDER.index(win_contract[1]) < 5:
            # suit contract
            for suit, mode in self.currentPower.items():
                if suit == win_contract[1]:
                    self.currentPower[suit] = ALL_TRUMP_POWER
                else:
                    self.currentPower[suit] = NO_TRUMP_POWER
        elif win_contract[1] == "No trumps":
            self.currentPower = {'C': NO_TRUMP_POWER, 'S': NO_TRUMP_POWER,
                                 'H': NO_TRUMP_POWER, 'D': NO_TRUMP_POWER}
        elif win_contract[1] == "All trumps":
            self.currentPower = {'C': ALL_TRUMP_POWER, 'S': ALL_TRUMP_POWER,
                                 'H': ALL_TRUMP_POWER, 'D': ALL_TRUMP_POWER}

    def draw(self, canvas):
        # draw interface       
        team1, team1Rect = makeText(MES._teams["T1"], FONT2, WHITE)  
        team2, team2Rect = makeText(MES._teams["T2"], FONT2, WHITE)
        scoreText, scoreTextRect = makeText(MES.make_interface("Score"), FONT1, WHITE)
        score1, score1Rect = makeText(str(self.team1Score), FONT3, WHITE)
        score2, score2Rect = makeText(str(self.team2Score), FONT3, WHITE)
        anonsText, anonsTextRect = makeText(MES.make_interface("Anons"), FONT1, WHITE)
        player1Text, player1TextRect = makeText(MES.make_interface("Pl1"), FONT1, WHITE)
        player2Text, player2TextRect = makeText(MES.make_interface("Pl2"), FONT1, WHITE)
        player3Text, player3TextRect = makeText(MES.make_interface("Pl3"), FONT1, WHITE)
        player4Text, player4TextRect = makeText(MES.make_interface("Pl4"), FONT1, WHITE)
        player2Sign, player2SignRect = makeText("2", FONT2, WHITE)
        player3Sign, player3SignRect = makeText("3", FONT2, WHITE)
        player4Sign, player4SignRect = makeText("4", FONT2, WHITE)
        
        canvas.blit(team1, (60 - team1Rect.centerx, 850))
        canvas.blit(team2, ((WIDTH - 60) - team2Rect.centerx, 850))
        canvas.blit(scoreText, (180 - scoreTextRect.centerx, 810))
        canvas.blit(scoreText, ((WIDTH - 180) - scoreTextRect.centerx, 810))
        canvas.blit(score1, (180 - score1Rect.centerx, 840))
        canvas.blit(score2, ((WIDTH - 180) - score2Rect.centerx, 840))
        canvas.blit(anonsText, (320 - anonsTextRect.centerx, 810))
        canvas.blit(anonsText, ((WIDTH - 320) - anonsTextRect.centerx, 810))
        canvas.blit(player1Text, (265 - player1TextRect.centerx, 835))
        canvas.blit(player3Text, (265 - player3TextRect.centerx, 865))
        canvas.blit(player2Text, ((WIDTH - 265) - player2TextRect.centerx, 835))
        canvas.blit(player4Text, ((WIDTH - 265) - player4TextRect.centerx, 865))
        canvas.blit(player3Sign, ((WIDTH // 2 - 60) - player3SignRect.centerx, 55))
        canvas.blit(player2Sign, (65 - player2SignRect.centerx, HEIGHT // 2 - 40))
        canvas.blit(player4Sign, ((WIDTH - 65) - player4SignRect.centerx, HEIGHT // 2 - 40))
        
        if self.state == 3:   # draw the central contract image
            if BID_ORDER.index(self.contract[1]) < 5:
                canvas.blit(SUIT_IMAGES[self.contract[1]], (CENTER[0] - 50, CENTER[1] - 50))
            else:
                canvas.blit(SUIT_IMAGES[self.contract[1]], (CENTER[0] - 100, CENTER[1] - 100))
                
        if self.first:       # draw a red dot showing who's first this round
            if self.first == player1:
                firstCoords = (335, 640)
            elif self.first == player2:
                firstCoords = (90, 135)
            elif self.first == player3:
                firstCoords = (335, 70)
            elif self.first == player4:
                firstCoords = (1160, 135)
            pygame.draw.circle(canvas, RED, firstCoords, 10) 
            firstText, firstTextRect = makeText(MES.make_interface('first'), FONT6, RED)
            canvas.blit(firstText, (firstCoords[0] + 15, firstCoords[1] - 10))
            

        if self.playerMessage:   # draw messages as appropriate
            playMes, playMesRect = makeText(self.playerMessage, FONT2, ORANGE)
            canvas.blit(playMes, (CENTER[0] - playMesRect.centerx, 760))
        if self.gameMessage:
            gameMes, gameMesRect = makeText(self.gameMessage, FONT4, ORANGE)
            canvas.blit(gameMes, (CENTER[0] - gameMesRect.centerx, 35))
        if self.bidMessage:
            bidMes, bidMesRect = makeText(self.bidMessage, FONT2, BLUE) 
            canvas.blit(bidMes, (CENTER[0] - bidMesRect.centerx, CENTER[1] - 150))    
        if self.state == 3:      # draw a text reminding who called the current contract
            if contra:
                info = MES.make_interface("Raised", self.contract[0].id, "wcontra")
            elif reContra:
                info = MES.make_interface("Raised", self.contract[0].id, "wrecontra")
            else:
                info = MES.make_interface("Raised", self.contract[0].id)
            infoMes, infoMesRect = makeText(info, FONT1, BLACK)
            canvas.blit(infoMes, ((WIDTH - 60) - infoMesRect[2], HEIGHT - 123))

        for player in turnOrder:   # draw the declarations in the interface area
            anonsi = drawAnons(player)
            if anonsi:
                anons, anonsRect = makeText(anonsi, FONT4, RED)                
                if player == player1:
                    canvas.blit(anons, (310, 840))
                elif player == player3:
                    canvas.blit(anons, (310, 870))
                elif player == player2:
                    canvas.blit(anons, ((WIDTH - 310) - anonsRect[2], 840))
                elif player == player4:
                    canvas.blit(anons, ((WIDTH - 310) - anonsRect[2], 870))
              
        pygame.display.update()
        FPSCLOCK.tick(FPS)

class Animation():
    """ Class handling animations in the game """
    def __init__(self, image, pos, cardImage=False, moth=False):
        # set image file to use: if it's a card, choose appropriate part of the tiled image
        if cardImage:
            self.image = Rect(CARD_SIZE[0] * RANKS.index(image.rank),
                     CARD_SIZE[1] * SUITS.index(image.suit), CARD_SIZE[0], CARD_SIZE[1])
        else:
            self.image = image
        self.pos = pos
        # get the rect dimensions
        if isinstance(self.image, Rect):
            self.rect = Rect(self.pos[0], self.pos[1], CARD_SIZE[0], CARD_SIZE[1])
            self.size = [CARD_SIZE[0], CARD_SIZE[1]]
        else:
            self.rect = self.image.get_rect()
            self.size = self.image.get_size()             
        self.vel = [0, 0]
        self.close_vel = [0, 0]   # a 'slowed' velocity, eye candy
        # set flags for movement
        self.in_motion = False
        if moth:
            self.moth = True
        else:
            self.moth = False
        self.growing = False
        self.close = False
        

    def get_distance(self, a, b):
        return math.sqrt(((b[0] - a[0]) ** 2) + ((b[1] - a[1]) ** 2))
    
    def move(self, start, stop, speed):
        """ Move the object from point start to point stop at speed """        
        self.destRect = Rect(stop[0], stop[1], self.rect[2], self.rect[3])   # this is the target position
        # calculate the vector for movement
        distance = [stop[0] - start[0], stop[1] - start[1]]
        norm = math.sqrt(distance[0] ** 2 + distance[1] ** 2)        
        direction = [distance[0] / norm, distance[1] / norm]        
        vector = [direction[0] * math.sqrt(2), direction[1] * math.sqrt(2)]
        self.vel[0] += vector[0] * speed     # now calculate the two velocities: one normal, and one slowed
        self.vel[1] += vector[1] * speed
        self.close_vel[0] = self.vel[0] * .4
        self.close_vel[1] = self.vel[1] * .4
               
        self.in_motion = True
             
    def grow(self, startSize, finalSize, scale):
        """ Grow the object from size startSize to size finalSize by scale (x, y) """
        self.scalar = scale
        self.new_image = pygame.transform.scale(self.image, startSize)
        self.size = self.new_image.get_size()
        self.pos[0] += finalSize[0] // 2 - startSize[0] // 2
        self.pos[1] += finalSize[1] // 2 - startSize[1] // 2
        self.destSize = finalSize    # this is the maximum size we want
        
        self.growing = True
                        
    def draw(self, canvas):
        if isinstance(self.image, Rect):
            canvas.blit(CARD_IMAGES, self.pos, self.image)
        else:
            if self.growing:
                canvas.blit(self.new_image, self.pos)
            else:                
                canvas.blit(self.image, self.pos)

    def update(self):
        if self.in_motion:     # do the movement update, according to how close the card is to destination
            if self.close:     # if it's approaching, slow down
                self.pos[0] += self.close_vel[0]
                self.pos[1] += self.close_vel[1]
            else:              # else move at nominal speed 
                self.pos[0] += self.vel[0]
                self.pos[1] += self.vel[1]
            self.rect[0] = self.pos[0]
            self.rect[1] = self.pos[1]
            # check how close the card is to dest, set the flag            
            if self.get_distance(self.pos, (self.destRect[0], self.destRect[1])) < 80:
                self.close = True                        

            if self.get_distance(self.pos, (self.destRect[0], self.destRect[1])) < 5:
                
                self.pos[0] = self.destRect[0]    # the card arrived, stop it 
                self.pos[1] = self.destRect[1]
                self.vel[0] = 0
                self.vel[1] = 0
                self.in_motion = False
        if self.growing:    # update the size of the card for growing images
            self.new_image = pygame.transform.scale(self.image, (self.size[0] + self.scalar[0],
                                                                 self.size[1] + self.scalar[1]))
            self.size = self.new_image.get_size()
            self.pos[0] -= self.scalar[0] // 2
            self.pos[1] -= self.scalar[1] // 2
                
            if self.size[0] >= self.destSize[0]:    # we reached max size, stop growing
                self.growing = False
                                          
def main():
    global FPSCLOCK, SCREEN, CARD_IMAGES, CARD_BACK_IMAGE, SUIT_IMAGES, LANG_IMAGES, FONT1, FONT2, FONT3, FONT4
    global FONT5, FONT6, BUTTON_IMAGES, BELOTE_PICTURE, MES, animations, stillImages
    global turnOrder, rund, deck, player1, player2, player3, player4, strategy1, strategy2, game, trump, rund 
        
    pygame.init()
    FPSCLOCK = pygame.time.Clock() 
    # initialize some more constants
    FONT1 = pygame.font.SysFont("TimesNewRoman", 22)
    FONT2 = pygame.font.SysFont("ArialRoundedMTBold", 32, True)
    FONT3 = pygame.font.SysFont("Aharoni", 40, True)
    FONT4 = pygame.font.SysFont("Kartika", 26, True)
    FONT5 = pygame.font.SysFont("Castellar", 60, True)
    FONT6 = pygame.font.SysFont("TimesNewRoman", 16)
    
    pygame.display.set_caption("Belote")
    LANG_IMAGES = {'eng': pygame.image.load("eng_flag.png"),
                   'bul': pygame.image.load("bg_flag.png")}
    welcome()   # show the welcome screen
    SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))    

    BELOTE_PICTURE = pygame.image.load('belote_pic.png')
    CARD_IMAGES = pygame.image.load("cards.png")
    CARD_BACK_IMAGE = pygame.image.load("card_back1.png")
    SUIT_IMAGES = {"C": pygame.image.load("club.png"),
                   "D": pygame.image.load("diamond.png"),
                   "H": pygame.image.load("heart.png"),
                   "S": pygame.image.load("spade.png"),
                   "No trumps": pygame.image.load("no.png"),
                   "All trumps": pygame.image.load("all.png")}
    BUTTON_IMAGES = {"large": pygame.image.load("button_large.png"),
                     "medium": pygame.image.load("button_medium.png"),
                     "small": pygame.image.load("button_small.png"),
                     "tiny": pygame.image.load("button_tiny.png")}
    
    # initialize variables
    rund = 1         # -> int, stores the state of the game
    trump = None      # -> suit stores the trump in power according to the announcement
        
    # create players,strategies and the deck
    game = GameState()
    player1 = Hand("Player 1", "Team 1")
    player2 = Hand("Player 2", "Team 2")
    player3 = Hand("Player 3", "Team 1")
    player4 = Hand("Player 4", "Team 2")
    strategy1 = Strategy("Team 1")
    strategy2 = Strategy("Team 2")
    deck = Deck()
    deck.shuffle()
    animations = []     # holds moving images from the Animation class
    stillImages = []    # holds images from Animation class standing still
    # esablish an initial turn order; pick a random player to be first
    turnOrder = [player1, player2, player3, player4]
    first = game.switch_first(turnOrder)
    changeTurnOrder(first)
    
                               
    while True:    # main event loop
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                terminate()

        # main game cycle
        if game.state == 1:
             startBidding(SCREEN, turnOrder)   # do the bidding round
        elif game.state == 2:
            prepare(game.contract)             # make preparations, get announces
        elif game.state == 3:
            while rund < 9:                    # main play - exchange cards
                playRound(SCREEN)                
            game.state = 4    
        elif game.state == 4:                  # terminate the play; reveal announces, count winnings
            finish()                           # adjust scores accordingly and continue with next bidding round
                
        SCREEN.fill(BGCOLOR)        
        display()
        game.draw(SCREEN)
                        
        pygame.display.update()
        FPSCLOCK.tick(FPS)
        
def prepare(current_contract):
    """ Do the preparation for play: give three more cards to each player,
        get announces, set strategy.
        current_contract -> String"""    
    game.bidMessage = None
    for player in turnOrder:
        deal(deck, player, 3)
        player.sort_hand()
        # get declarations if contract is different than No trumps
        # (in No trumps no declarations are valid)
        if current_contract[1] != "No trumps":  
            player.get_announces()                 
        
        if player == player1:   # set AI
            continue
        # set the initial power of each suit in your hand
        for suit in SUITS:                      
            power = strategy1.get_suit_power(player.separate_suit(suit))
            if power:
                player.suit_power[suit] = power[2]
        # set saved_cards        
        for card in player.hand:                
            if game.currentPower[card.get_suit()][card.get_rank()] == 8:
                player.saved_cards.append(card)  # add if the strongest in a suit
            if player.suit_power[card.get_suit()] == "blocking":
                player.saved_cards.append(card)  # save if you're blocking this suit
            if (card.get_rank() == "Q" or card.get_rank() == "K") and player.belotes:
                for belot in player.belotes:
                     # also save a belote so you don't lose it 
                    if belot.suit == card.get_suit():
                        player.saved_cards.append(card)
    # 'save' the info from the bidding phaze for use during the round                    
    if strategy1.bid_history:
        for bid in strategy1.bid_history:    # if there are suits declared as bids earlier, add them to
            if BID_ORDER.index(bid[1]) < 5 and bid[0].team == 'Team 1':  # interesting suits   
                strategy1.partner_suits.append(bid[1])
            elif BID_ORDER.index(bid[1]) < 5 and bid[0].team == 'Team 2':
                strategy1.interesting_suits.append(bid[1])
    if strategy2.bid_history:
        for bid in strategy2.bid_history:
            if BID_ORDER.index(bid[1]) < 5 and bid[0].team == 'Team 2':    
                strategy2.partner_suits.append(bid[1])
            elif BID_ORDER.index(bid[1]) < 5 and bid[0].team == 'Team 1':
                strategy2.interesting_suits.append(bid[1])    

    if BID_ORDER.index(current_contract[1]) < 5:     # if it's a suit game, automatically track it
        if current_contract[1] not in strategy1.interesting_suits:
            strategy1.interesting_suits.append(current_contract[1])
        if current_contract[1] not in strategy2.interesting_suits:
            strategy2.interesting_suits.append(current_contract[1])    
        
    game.state = 3    
    
def finish():
    """ Adjust announces; count the winnings; set the winner and adjust scores
        accordingly. then gather back the cards, etc. """
    result1 = strategy1.count(player1, player3)
    result2 = strategy2.count(player2, player4)
    message = ""

    if game.last == 'Team 1':     # add last 10
        result1 += 10
    elif game.last == 'Team 2':
        result2 += 10

    if game.contract[1] == 'No trumps':  # double the results in No trump game
        result1 *= 2
        result2 *= 2
        
    if game.announces:      # add announces, if any
        compareAnnounces()
        for anons in game.announces:
            if anons[1].vid == 'care':
                if anons[0].team == 'Team 1':
                    result1 += CARE_VALUE[anons[1].rank]
                else:
                    result2 += CARE_VALUE[anons[1].rank]
            else:
                if anons[0].team == 'Team 1':
                    result1 += ANNOUNCE_VALUE[anons[1].vid]
                else:
                    result2 += ANNOUNCE_VALUE[anons[1].vid]
    
    # calculate the outcome of the current round
    if result1 > result2:    # Team 1 has more points and wins
        message = calculateResult('Team 1', result1, result2)
    elif result2 > result1:  # Team 2 has more points and wins
        message = calculateResult('Team 2', result2, result1)
    else:           # the score is even, it 'hangs'
        if not contra or not reContra:
            if game.contract[0].team == 'Team 1':
                game.team2Score += int(round(float(result1) / 10))
                game.remaining += int(round(float(result2) / 10))
                message = MES.make_even_result("T1")
            elif game.contract[0].team == 'Team 2':
                game.team1Score += int(round(float(result2) / 10))
                game.remaining += int(round(float(result1) / 10))
                message = MES.make_even_result("T2")
        else:
            if contra:
                game.remaining += (int(round(float(res1) / 10)) + int(round(float(res2) / 10))) * 2
            elif reContra:
                game.remaining += (int(round(float(res1) / 10)) + int(round(float(res2) / 10))) * 4
            message = MES.make_even_result("Evencontra")    
    # check if any score passed 151, decide if the game ended
    if game.team1Score > 151 and game.team2Score > 151:   # both teams 'exited' at the same time
        if game.team1Score > game.team2Score:             # check who has more points 
            gameOver(strategy1.team)                      # it's not possible that results were equal, because then one result 
        elif game.team2Score > game.team1Score:           # would 'hang'
            gameOver(strategy2.team)
    elif game.team1Score > 151:              
        if result2 == 0 and not game.lastRound:           # team 1 won, but you can't exit with 'capot', play a last round
            game.lastRound = True
        else:
            gameOver(strategy1.team)
    elif game.team2Score > 151 and not game.lastRound:
        if result1 == 0:                                  # team 2 won, but you can't exit with 'capot', play a last round
            game.lastRound = True
        else:
            gameOver(strategy2.team)
    else:       # the game continues, display a message        
        changeTeamStrategy(strategy1, game.team1Score, game.team2Score)
        changeTeamStrategy(strategy2, game.team2Score, game.team1Score)
        mes, mesRect = makeText(message, FONT3, RED)
        endMes, endMesRect = makeText(MES.make_interface("End"), FONT3, YELLOW)
        end = Animation(mes, [CENTER[0] - mesRect.centerx, CENTER[1]])
        end.grow([20, mesRect[3]], [mesRect[2], mesRect[3]], [mesRect[2] // 40, 0])
        animations.append(end)
        end2 = Animation(endMes, [WIDTH + 1, CENTER[1] - 100])
        end2.move([WIDTH + 1, CENTER[1] - 100], [CENTER[0] - endMesRect.centerx, CENTER[1] - 100], 15)
        animations.append(end2)            
               
        SCREEN.fill(BGCOLOR)
        display()
        drawAnimation(animations, stillImages)
        game.draw(SCREEN)    
        pygame.display.update()
        FPSCLOCK.tick(FPS) 
       
        pygame.time.wait(2000)
        
    cleanAll()

def calculateResult(win, res1, res2):
    """ Calculate the final score from the game and add it accordingly to team scores.
        Assume res1 is always the higher of the two.
        win -> String
        re1, res2 -> Int"""
    winner = 0
    loser = 0
    message = ""
    if win == game.contract[0].team:   # the bidding team made their contract
        if res1 == 0 or res2 == 0:     # the 'capot' case; bonus 9 points, but no announce bonuses!
            if BID_ORDER.index(game.contract[1]) < 5:
                winner += 26
                if contra:
                    winner *= 2
                elif reContra:
                    winner *= 2
            else:
                winner += 35
                if contra:
                    winner *= 2
                elif reContra:
                    winner *= 2
            message = MES.make_result("wincapo", win)    
        else:                   # the normal case; all results are added accordingly           
            if contra:
                message = MES.make_result("wincontra", win)
                winner += (int(round(float(res1) / 10)) + int(round(float(res2) / 10))) * 2
            elif reContra:
                message = MES.make_result("winrecontra", win)
                winner += (int(round(float(res1) / 10)) + int(round(float(res2) / 10))) * 4
            else:
                winner += int(round(float(res1) / 10))
                loser += int(round(float(res2) / 10))
                message = MES.make_result("win", win)
    elif win != game.contract[0].team:   # the bidding team is 'inside'
        if res1 == 0 or res2 == 0:       # the 'capo' case; bonus 10 points, but no announce bonuses!
            if BID_ORDER.index(game.contract[1]) < 5:
                winner += 26
                if contra:
                    winner *= 2
                elif reContra:
                    winner *= 2
            else:
                winner += 35
                if contra:
                    winner *= 2
                elif reContra:
                    winner *= 2
            message = MES.make_result("losecapo", game.contract[0].team)
        else:                   # the normal case; all results are added accordingly
            if contra:
                message = MES.make_result("losecontra", game.contract[0].team)
                winner += (int(round(float(res1) / 10)) + int(round(float(res2) / 10))) * 2
            elif reContra:
                message = MES.make_result("loserecontra", game.contract[0].team)
                winner += (int(round(float(res1) / 10)) + int(round(float(res2) / 10))) * 4
            else:
                winner += (int(round(float(res1) / 10)) + int(round(float(res2) / 10)))
                message = MES.make_result("lose", game.contract[0].team)
                
    if game.remaining > 0:    # if there was a 'hanging' result, add it to the winner, clear the 'hanging variable'
        winner += game.remaining
        game.remaining = 0
        
    if win == 'Team 1':
        game.team1Score += winner
        game.team2Score += loser
    elif win == 'Team 2':
        game.team2Score += winner
        game.team1Score += loser

    return message    
        
def changeTeamStrategy(friend, friendScore, enemyScore):
    """ Analyze the scores and change team strategy respectively;
        friend -> Strategy
        scores -> GameState.teamScore """

    if enemyScore >= 151 - 10:
        friend.behavior = 'desperate'
    elif friendScore - enemyScore < -30:
        friend.behavior = 'defensive'        
    elif friendScore - enemyScore > 30:
        friend.behavior = 'aggressive'        
    else:
        friend.behavior = 'normal'
        
def deal(deck, player, num_cards):
    """ deal num_cards to player from the deck """
    global animations, stillImages 
    # calculate positions for animation purposes
    start_pos = [CENTER[0] - CARD_CENTER[0], CENTER[1] - CARD_CENTER[1]]
    if player == player1:
        player_pos = [350, 650]
    elif player == player2:
        player_pos = [80, 150]
    elif player == player3:
        player_pos = [350, 80]
    elif player == player4:
        player_pos = [1150, 150]
        
    for card in xrange(num_cards):    # make dealing animations    
        deal = Animation(CARD_BACK_IMAGE, [start_pos[0], start_pos[1]])
        if player.team == 'Team 1':
            deal.move(start_pos, [player_pos[0] + card * (CARD_SIZE[0] - 20),
                                  player_pos[1]], 15)            
        elif player.team == 'Team 2':
            deal.move(start_pos, [player_pos[0],
                                  player_pos[1] + card * (CARD_SIZE[1] - 40)], 15)
        animations.append(deal)
          
    # draw the dealing animation
    drawAnimation(animations, stillImages)        
    stillImages = []
    
    for card in xrange(num_cards):    # actually deal the cards :)
        player.add_card(deck.deal_card())

def changeTurnOrder(first):
    """ Changes the order in which players will play their hands.
        It will now start from first and continue clockwise.
        first -> Hand """
    global turnOrder    
    new_start = turnOrder[0 : turnOrder.index(first)]
    remain = turnOrder[turnOrder.index(first) : len(turnOrder)]
    turnOrder = remain + new_start
    
    return turnOrder

def checkForClick():
    """ Check the queue for mouseclick events; return a single event.
        This should act only when the game waits for player input, and not 
        when processing computer turns! """    
            
    for event in pygame.event.get():
        if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
            terminate()
        if event.type == MOUSEBUTTONUP:                
            return event
    
def getCardClicked(x):
    """ Returns an index of the card clicked; only applies to player1 """
    return (x - 350) // (CARD_SIZE[0] - 20)

def findCardCoords(player, pos):
    """ Return the screen coords of the top left corner of a given card's index
        in a given player's hand. Use them for animation purposes. """
    
    if player == player1:
        return [350 + ((CARD_SIZE[0] - 20) * pos), 650]
    elif player == player2:
        return  [80, 150 + ((CARD_SIZE[1] - 40) * pos)]
    elif player == player3:
        return [350 + ((CARD_SIZE[0] - 20) * pos), 80]
    elif player == player4:
        return  [1150, 150 + ((CARD_SIZE[1] - 40) * pos)]

def getCardValue(card):
    """ Get the value of a card according to current contract in place """
    if BID_ORDER.index(game.contract[1]) < 5:   # if it's a trump contract, he value table varies
        if card.get_suit() == trump:            # cards of teh trump suit use ALL_TRUMP calue table
            return CARD_VALUE_ALL_TRUMP[card.get_rank()]
        else:
            return CARD_VALUE_NO_TRUMP[card.get_rank()]
    elif game.contract[1] == "No trumps":
        return CARD_VALUE_NO_TRUMP[card.get_rank()]
    elif game.contract[1] == "All trumps":
        return CARD_VALUE_ALL_TRUMP[card.get_rank()]    

def getHighest(hand, suit_required):
    """ Return a list of the most powerful card in a given hand and the player who gave it,
        according to suit_required currently. Assume the hand is a dict.
        hand -> Dict of player: card
        suit_required -> String """
    cards = [card for card in hand.values()]
    
    def power(card):
        """ get the current value of the card; value = value if the card is from the suit required;
           if it's not, value = 0; if it's a trump - value + 10 """
        value = card.get_power()
        if card.get_suit() != suit_required and card.get_suit() == trump:
            value += 10
        elif card.get_suit() != suit_required:
            value = 0        
        return value    
    
    result = sorted(cards, key=power)
    result.reverse()

    for player, card in hand.items():
        if card == result[0]:
            return [player, card]    

def compareAnnounces():
    """ Compare the announces at the end of a game; eliminate lower-order
        sequences if higher order sequence of the same length is present.
        Assume that only competing sequences are left ( 3 - 3, 4 - 4, cares, etc) """
    win_seq = None
    win_care = None
    for anons in game.announces: 
        if anons[1].vid == 'belote':   # skip belotes
            continue
        elif anons[1].vid == 'care':   # check cares
            if win_care is None:
                win_care = anons
            else:
                if CARE_ORDER.index(anons[1].rank) > CARE_ORDER.index(win_care[1].rank):
                    win_care = anons
        else:         # check sequences        
            if win_seq is None:
                win_seq = anons  # set the winning sequence so far
            else:
                if ANNOUNCE_ORDER.index(win_seq[1].last_card) < ANNOUNCE_ORDER.index(anons[1].last_card):
                    win_seq = anons   # switch the winning sequence if its higher than the current one
                if ANNOUNCE_ORDER.index(win_seq[1].last_card) == ANNOUNCE_ORDER.index(anons[1].last_card):# if sequences are equal
                    if BID_ORDER.index(game.contract[1]) < 5 and anons[1].suit == trump:    # if it's a trump game
                        win_seq = anons                        # and one sequence is from the trump suit, it wins
                    elif BID_ORDER.index(win_seq[1].suit) < BID_ORDER.index(anons[1].suit):
                        win_seq = anons       # if not trump game, compare suits
    # now update game.announces - only announces from the team of the winning sequences count (excluding belotes)
    for anons in game.announces[:]:
        if anons[1].vid == 'belote':
            continue
        elif anons[1].vid == 'care':
            if anons[0].team != win_care[0].team:
                game.announces.remove(anons)
        else:
            if anons[0].team != win_seq[0].team:
                game.announces.remove(anons)
                
def findOverlapSequence(player, care):
    """ if a player has both a carre and a sequence, check if
        a card of the carre makes part of the sequence; if so,
        remove the sequence (since even the longest sequence has the same value
        as a carre) """
    check = care.rank   # establish the card against which the sequences are checked
    order = list(ANNOUNCE_ORDER)      # (this is the rank of the card part of a carre anons)
    order.reverse()
        
    for seq in player.announces[:]:
        if seq.vid == 'care':
            continue      # skip cares, only sequences ar subject to this
        else:
            cardList = order[order.index(seq.last_card):order.index(seq.last_card) + seq.vid]
            if check in cardList:
                player.announces.remove(seq)
                
def getBelote(player, suit=None):
    """ Return a card from the player's hand part of a valid belote.
        ASSUME the player has at least one valid belote. 
        suit -> String. Optional, if you want to announce a Belote from a specific suit. """
   
    if not player.belotes:  # sanity check
        return None
    else:
        if suit:
            for card in player.hand:
                if card.get_suit() == suit and \
                card.get_rank() == "K" or card.get_rank() == "Q":
                    return card
        else:
            for card in player.hand:
                if card.get_suit() in player.belotes and \
                card.get_rank() == "K" or card.get_rank() == "Q":
                    return card          

def announce(player):
    """ Аttempt to announce a sequence; you can do this only in the first round,
        and only if player from the other team hasn't announced a longer sequence already.
        Belotes are announced differently. """
    
    if player.announces:
        for anons in player.announces[:]:  
            if not game.announces:        # if there's no announces declared, add automatically
                game.announces.append([player, anons])
            else:        # check existing announces to see if there's no longer sequence
                if anons.vid == 3:   # add it if there isn't, or if its declarator is from your team; 
                    longer = False   # also remove existing shorter sequences if declared by the other team
                    for anons_made in game.announces[:]:
                        if anons_made[0].team != player.team and (anons_made[1].vid == 4 or anons_made[1].vid == 5):
                            longer = True
                    if not longer:
                        game.announces.append([player, anons])
                        player.announces.remove(anons)
                        game.gameMessage = MES.get_game_message("seq3", player.id)
                elif anons.vid == 4:
                    longer = False
                    for anons_made in game.announces[:]:
                        if anons_made[1].vid == 3 and anons_made[0].team != player.team:
                            game.announces.remove(anons_made)
                        if anons_made[0].team != player.team and anons_made[1].vid == 5:
                            longer = True
                    if not longer:
                        game.announces.append([player, anons])
                        player.announces.remove(anons)
                        game.gameMessage = MES.get_game_message("seq4", player.id)
                elif anons.vid >= 5:
                    for anons_made in game.announces[:]:
                        if anons_made[0].team != player.team and (anons_made[1].vid == 3 or anons_made[1].vid == 4):
                            game.announces.remove(anons_made)
                    game.announces.append([player, anons])
                    player.announces.remove(anons)
                    game.gameMessage = MES.get_game_message("seq5", player.id)
                elif anons.vid == 'care':
                    game.announces.append([player, anons])
                    player.announces.remove(anons)
                    game.gameMessage = MES.get_game_message("care", player.id)
                    
def playerAnnounce(surface):
    """ create a new window with buttons for player announces;
        in response to clicks attempt to announce """
    if not player1.announces:
        game.playerMessage = MES.get_player_message("noanons")
    else:     # initialize new interface 
        seqText, seqTextRect = makeText(MES.make_interface("Seq"), FONT2, WHITE)
        doneButton, doneButtonRect = loadButton(MES.get_button(11), BLACK, BUTTON_IMAGES["small"], 190, 750)
        Button3, Rect3 = loadButton("3", BLACK, BUTTON_IMAGES["tiny"], 70, 700)
        Button4, Rect4 = loadButton("4", BLACK, BUTTON_IMAGES["tiny"], 110, 700)
        Button5, Rect5 = loadButton("5", BLACK, BUTTON_IMAGES["tiny"], 150, 700)
        care, careRect = loadButton(MES.get_button(10), BLACK, BUTTON_IMAGES["small"], 70, 750)
        done = False
        
        while not done:
            for event in pygame.event.get():     # event loop
                if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                    terminate()
                if event.type == MOUSEBUTTONUP:
                    x = event.pos[0]
                    y = event.pos[1]
                    
                    if doneButtonRect.collidepoint(x, y):
                        done = True
                    elif careRect.collidepoint(x, y):                                               
                        for anons in player1.announces:
                            if anons.vid == 'care':
                                game.announces.append([player1, anons])
                                player1.announces.remove(anons)
                                game.gameMessage = MES.get_game_message("plcare")
                            else:
                                game.playerMessage = MES.get_player_message("nocare")#                        
                    elif Rect3.collidepoint(x, y):                                              
                        for anons in player1.announces:
                            if anons.vid == 3:              # found a 3, attempt to declare it
                                if not game.announces:      # if no announces, append automatically
                                    game.announces.append([player1, anons])
                                    player1.announces.remove(anons)
                                    game.gameMessage = MES.get_game_message("plseq3")
                                else:    
                                    longer = False
                                    for anons_made in game.announces[:]:      # search game.announces for longer sequences                         
                                        if anons_made[0].team != 'Team 1' and \
                                           (anons_made[1].vid == 4 or anons_made[1].vid == 5):
                                            longer = True
                                    if not longer:
                                        game.announces.append([player1, anons])
                                        player1.announces.remove(anons)
                                        game.gameMessage = MES.get_game_message("plseq3")
                                    else:
                                        game.playerMessage = MES.get_player_message("longer")
                            else:
                                game.playerMessage = MES.get_player_message("noseq3")                        
                    elif Rect4.collidepoint(x, y):                       
                        for anons in player1.announces:
                            if anons.vid == 4:
                                if not game.announces:     
                                    game.announces.append([player1, anons])
                                    player1.announces.remove(anons)
                                    game.gameMessage = MES.get_game_message("plseq4") 
                                else:
                                    longer = False
                                    for anons_made in game.announces:
                                        if anons_made[1].vid == 3 and anons_made[0].team != 'Team 1':
                                            game.announces.remove(anons_made)
                                        if anons_made[0].team != 'Team 1' and anons_made[1].vid == 5:
                                            longer = True
                                    if not longer:
                                        game.announces.append([player1, anons])
                                        player1.announces.remove(anons)
                                        game.gameMessage = MES.get_game_message("plseq4")
                                    else:
                                        game.playerMessage = MES.get_player_message("longer")
                            else:
                                game.playerMessage = MES.get_player_message("noseq4")                       
                    elif Rect5.collidepoint(x, y):                      
                        for anons in player1.announces:
                            if anons.vid >= 5:
                                if not game.announces:
                                    game.announces.append([player1, anons])
                                    player1.announces.remove(anons)
                                else:                                        # there's no longer sequence than 5, append it automatically                                  
                                    for anons_made in game.announces[:]:     # and remove shorter sequences by other team players
                                        if anons_made[0].team != 'Team 1' and \
                                           (anons_made[1].vid == 3 or anons_made[1].vid == 4):  
                                            game.announces.remove(anons_made)
                                    game.announces.append([player1, anons])   
                                    player1.announces.remove(anons)          
                                    game.gameMessage = MES.get_game_message("plseq5")
                            else:
                                game.playerMessage = MES.get_player_message("noseq5")
                
            surface.fill(BGCOLOR)
            display()
            pygame.draw.rect(SCREEN, BLUE, (60, 640, 200, 150))
            pygame.draw.rect(SCREEN, SILVER, (60, 640, 200, 150), 3)
            surface.blit(seqText, (70, 650))
            surface.blit(doneButton, doneButtonRect)
            surface.blit(Button3, Rect3)
            surface.blit(Button4, Rect4)
            surface.blit(Button5, Rect5)
            surface.blit(care, careRect)
            if stillImages:
                for image in stillImages:
                    image.draw(SCREEN)
            game.draw(SCREEN)

            pygame.display.update()
            FPSCLOCK.tick(FPS)
   
def analyze(player, current_playhand, suit_required):
    """ Analyzes the current state of the game, according to the hand being played,
        the cards that the player has, the required suit, etc. Returns a pair
        of suggestions of how the player shoud proceed."""
    global action, addon
    first = False    # a flag to keep track if the player is first this round
    winning = None   # -> list; store the card of the current_playhand which wins up to now;
                     # list[0] is a Hand(player), list[1] is a Card   
    action = None    # stores the recommended action
    addon = None     # stores an additional piece of important info   
    if player.team == "Team 1":
        team = strategy1
    elif player.team == "Team 2":
        team = strategy2
    
    if trump == "all" or trump == "none":
        # there are two general modes of a game - when there's a trump
        # and when there isn't; set a flag to track this
        mode = "normal"
    else:
        mode = "trump"
    
    if suit_required is None:
        # the player will play first this round
        first = True
    
    if not first:
        # set which card of the playhand is winning; winning is a list of [player, Card]
        if len(current_playhand) < 2:   # there's only one card in play; set it as winning
            winning = current_playhand.keys() + current_playhand.values()
        else:                  # there is more than 1 card
            winning = getHighest(current_playhand, suit_required)
       
    if not first:   # if not first, respond to the others' actions
        respond_set = player.separate_suit(suit_required)
                
        if len(respond_set) > 0:
            # if the player has of the required suit
            if player.has_higher(respond_set, winning[1]) and winning[1].get_suit() != trump:
                action = "take"     # take the card if the winning card isn't a trump
                addon = winning[1]  # addon is the card currently winning
            else:
                action = "respond"  # respond by giving a low card of that suit
                addon = winning[0]  # addon shows which player takes for now
        else:
            # player has no cards to respond
            if mode == "normal":    # it's a No trump or All trump contract; no restrictions on responding
                action = "clean"    # clean a card, no other option
                addon = winning[0]  # shows the player
            else:                   # it's a suit contract, there are restrictions on responding
                if winning[0].team != player.team:   # if it's the adversary
                    if player.has_trump(trump):
                        if winning[1].get_suit() == trump and player.has_higher(player.separate_suit(trump), winning[1]):
                            action = "trump"  # give a trump to take the hand, if player has a higher trump
                            addon = winning   # this shows both the player and the card
                        elif winning[1].get_suit() != trump:
                            action = "trump"    # winning card is not a trump
                            addon = winning
                        else:    
                            action = "clean"    # winning card is a trump and you have no higher trump
                            addon = winning[0]
                    else:
                        action = "clean"   
                        addon = winning[0]
                else:
                    action = "clean"   # it's your partner winning, don't have to trump;
                    addon = winning[0] #  get rid of a low card
    else:    # if first, decide what course of action to take; addon in this case is always a Card
        action, addon = team.CardStrategy(player, STRAT_ORDER[0])
        #print action, addon
        
    return action, addon

def makeMove(player, current_playhand, suit_required):
    """ For a computer player, play a suitable card from its hand"""
    global playhand, required
    
    action, add_info = analyze(player, current_playhand, suit_required)
    
    if action == "take":
        pos, card = player.take(suit_required, add_info)
        playhand[player] = card
    elif action == "respond":
        pos, card = player.respond(suit_required)
        playhand[player] = card
    elif action == "trump":
        pos, card = player.trump(trump, add_info)
        playhand[player] = card    
    elif action == "clean":
        if add_info.team == player.team:
            pos, card = player.clean("partner")
            playhand[player] = card
        elif add_info.team != player.team:
            pos, card = player.clean("adversary")
            playhand[player] = card
    elif action == "demand":
        pos, card = player.attack(add_info, action)
        playhand[player] = card
        required = card.get_suit()
    elif action == "bore":
        pos, card = player.attack(add_info, action)
        playhand[player] = card
        required = card.get_suit()
    elif action == "partner":
        pos, card = player.find_partner(add_info)
        playhand[player] = card
        required = card.get_suit()
    elif action == "pass":
        pos, card = player.clean("adversary")
        playhand[player] = card
        required = card.get_suit()
    elif action == 'belote':
        pos, card = player.announceBelote(add_info)
        playhand[player] = card
        required = card.get_suit()
    else:
        pos, card = player.play_card(0)
        required = card.get_suit()
        playhand[player] = card
    # make the necessary animations  
    other_card = Animation(card, findCardCoords(player, pos), True)
    other_card.move(other_card.pos, player.cardDest, 12)
    animations.append(other_card)
    return playhand   
    
def playRound(surface):
    """ Executes a round of Belot. Each player has to play a card,
        cards are compared and the player who gave the strongest card
        takes the hand. """
    global SCREEN, rund, turnOrder, playhand, required, animations, stillImages

    playhand = {}    # -> dict{player: Card}; represents the cards in play and who gave them
    required = None  # -> string; stores the suit that's been asked in this round
    endTurn = [False, False, False, False]   # keep track of who played already
    anonsButton, anonsButtonRect = loadButton(MES.get_button(9), BLACK, BUTTON_IMAGES["large"], 230, 690)
    # map player screen coordinates for drawing purposes
    player1.cardDest = [CENTER[0] - CARD_CENTER[0], CENTER[1] + CARD_CENTER[1] * 2.5]
    player2.cardDest = [CENTER[0] - CARD_SIZE[0] * 2.5, CENTER[1] - CARD_CENTER[1]]
    player3.cardDest = [CENTER[0] - CARD_CENTER[0], CENTER[1] - CARD_CENTER[1] * 4.25]
    player4.cardDest = [CENTER[0] + CARD_SIZE[0] * 1.5, CENTER[1] - CARD_CENTER[1]]
    player1.winDest = [950, 650]
    player2.winDest = [80, 600]
    player3.winDest = [950, 80]
    player4.winDest = [1150, 600]
    highlight = False     # flag for highlighting the card the mouse points
    stillImages = []      # for animation purposes
    done = False
    card_clicked = False
    # this is to prevent unwanted click events 
    pygame.event.clear()
    
    while not done:
        for player in turnOrder:
            # each player plays one card; computer plays automatically while
            # player waits for your input
            pygame.event.clear()
            game.gameMessage = None
            game.playerMessage = None            
            if player == player1:                                
                while not endTurn[turnOrder.index(player1)]:
                    # player interactive loop            
                    card_clicked = False                                        
                    for event in pygame.event.get(MOUSEMOTION):                        
                        x, y = event.pos
                        if player1.rect.collidepoint(x, y):
                            cardPos = getCardClicked(x)
                            highlightPos = 350 + cardPos * (CARD_SIZE[0] - 20)
                            highlight = True
                        else:
                            highlight = False
                    
                    click = checkForClick()
                    if click:
                        mousex, mousey = click.pos
                        if player1.rect.collidepoint(mousex, mousey):  # clicked on a card
                            card_clicked = True                               
                                # clicked on the Declaration button
                        elif anonsButtonRect.collidepoint(mousex, mousey) and \
                                 (rund == 1 and game.contract[1] != "No trumps"):
                            playerAnnounce(SCREEN)
                                                                
                    if card_clicked:
                        # process the card click                        
                        player_card = player1.hand[getCardClicked(mousex)]                   
                                             
                        if True not in endTurn:   # if player is the first to play this round
                            required = player_card.get_suit()  # set required to his card's suit
                        else:           # player isn't first; set some blocks                                    
                            winning = getHighest(playhand, required)
                            # block giving a card other than the suit required, if you have it
                            if player1.has_suit(required) and player_card.get_suit() != required:
                                game.playerMessage = MES.get_player_message("answer")                                
                                continue
                            elif player_card.get_suit() == required:
                                # if you are responding, check the power of the card
                                respond_set = player1.separate_suit(required)
                                if game.contract[1] == "All trumps" or \
                                   (BID_ORDER.index(game.contract[1]) < 5 and required == trump):
                                    # in All trumps and the trump suit of a suit game, you have to go higher if you can
                                    if player_card.get_power() < winning[1].get_power() and \
                                        player1.has_higher(respond_set, winning[1]):
                                        game.playerMessage = MES.get_player_message("higher")                                        
                                        continue
                            elif not player1.has_suit(required):           # if you can't respond
                                if BID_ORDER.index(game.contract[1]) < 5:  # it's a SUIT GAME, YEEEE:                                                                                
                                    if winning[1].get_suit != trump:       # if winning card isn't a trump
                                        if (player1.has_suit(trump) and player_card.get_suit() != trump) and \
                                           winning[0].team != player1.team:
                                            game.playerMessage = MES.get_player_message("trump")                                           
                                            continue
                                    else:                                   # if it IS a trump:
                                        respond_set = player1.separate_suit(trump)
                                        if winning[0].team != player1.team:    # you need to trump if the adversary is winning
                                            if (player1.has_suit(trump) and player1.has_higher(respond_set, winning[1])) and \
                                                player_card.get_suit() != trump:
                                                game.playerMessage = MES.get_player_message("trump")                                                
                                                continue 
                                            elif player_card.get_suit() == trump and \
                                                 (player_card.get_power() < winning[1].get_power() and \
                                                   player1.has_higher(respond_set, winning[1])):
                                                game.playerMessage = MES.get_player_message("hightrump")                                                
                                                continue
                        # do the actual card processing 
                        if player_card.get_rank() == "Q" or player_card.get_rank() == "K":  # check for belote
                            if player_card.get_suit() in player1.belotes and required == player_card.get_suit():                                
                                player_pos, play_card = player1.announceBelote(player_card)
                                playhand[player1] = player_card#                               
                            else:
                                playhand[player1] = player_card
                                player_pos, play_card = player1.play_card(getCardClicked(mousex))
                        else:
                            playhand[player1] = player_card
                            player_pos, play_card = player1.play_card(getCardClicked(mousex))
                    
                        my_card = Animation(player_card, findCardCoords(player1, player_pos), True)
                        my_card.move(my_card.pos, player1.cardDest, 12)
                        animations.append(my_card)
                        endTurn[turnOrder.index(player1)] = True
                                            
                    # drawing; this screen will be visible for the better part of the game
                    SCREEN.fill(BGCOLOR)                   
                    display()
                    if rund == 1 and game.contract[1] != "No trumps":
                        SCREEN.blit(anonsButton, anonsButtonRect)
                    if highlight:
                        if cardPos == len(player1.hand) - 1:
                            pygame.draw.rect(SCREEN, YELLOW, (highlightPos, 650,
                                                 CARD_SIZE[0], CARD_SIZE[1]), 3)
                        else:
                            pygame.draw.rect(SCREEN, YELLOW, (highlightPos, 650,
                                                 CARD_SIZE[0] - 20, CARD_SIZE[1]), 3)
                    
                    drawAnimation(animations, stillImages)
                    if stillImages:
                        for image in stillImages:
                            image.draw(SCREEN)
                    game.draw(SCREEN)
                    pygame.display.update()
                    FPSCLOCK.tick(FPS)
                   
            else:
                # play computer turns
                if rund == 1:
                    announce(player)
                makeMove(player, playhand, required)
                
                if True not in endTurn:
                    # if player is the first to play this round, set required to his card's suit
                    required = playhand[player].get_suit()
                endTurn[turnOrder.index(player)] = True
                 
            # drawing has to be identical to the inner drawing loop
            SCREEN.fill(BGCOLOR)
            display()
            drawAnimation(animations, stillImages)
            if stillImages:
                for image in stillImages:
                    image.draw(SCREEN)            
            game.draw(SCREEN)        
            pygame.display.update()
            FPSCLOCK.tick(FPS)
            pygame.time.wait(500)
#            first_iter = False
                               
        if False not in endTurn:
            # everybody made their move - determine winner, change turn order
            # for next round and terminate the round
            winner = getHighest(playhand, required)[0]
            strategy1.post_analysis(playhand, [player1, player3])
            strategy2.post_analysis(playhand, [player2, player4])
            stillImages = []
            for player, card in playhand.items():
                won_card = Animation(card, player.cardDest, True, True)
                won_card.move(player.cardDest, winner.winDest, 12)
                animations.append(won_card)            
        
            SCREEN.fill(BGCOLOR)
            display()
            drawAnimation(animations, stillImages)
            game.draw(SCREEN)
            pygame.display.update()
            FPSCLOCK.tick(FPS)
            
            winner.collect_hand(playhand)
            changeTurnOrder(winner)
            if rund == 8:
                game.last = winner.team
                                   
            rund += 1
            done = True
        
def makeBid(current_player, current_contract):
    """ Process the bidding phase for a computer player:
        analyze its hand and make a suitable bid """
    global endBid, contra, reContra, stillImages    
    
    if current_player.team == "Team 1":
        team = strategy1
    elif current_player.team == "Team 2":
        team = strategy2
    
    bid = team.decide_bet(current_player, current_contract)
   
    if bid == "pass":    # register a pass, move on
        endBid[turnOrder.index(current_player)] = True
        game.bidMessage = MES.get_bid_message("comppass", current_player.id)        
        
    elif bid == "contra":   # register a contra, restart bidding
        contra = True
        endBid = [False, False, False, False]
        endBid[turnOrder.index(current_player)] = True
        game.bidMessage = MES.get_bid_message("compcontra", current_player.id)
    elif bid == "re-contra":
        if current_contract[1] == "All trumps":   # if it's All trumps, terminate bidding
            reContra = True
            contra = False
            endBid = [True, True, True, True]
            game.bidMessage = MES.get_bid_message("comprecontra", current_player.id)
        else:
            reContra = True
            contra = False
            endBid = [False, False, False, False]
            endBid[turnOrder.index(current_player)] = True
            game.bidMessage = MES.get_bid_message("comprecontra", current_player.id)
    else:      # change the contract, restart bidding
        game.contract = [current_player, bid]
        strategy1.bid_history.append(game.contract)
        strategy2.bid_history.append(game.contract)
        endBid = [False, False, False, False]
        endBid[turnOrder.index(current_player)] = True
        contra = False
        reContra = False
        game.bidMessage = MES.get_bid_message("compraise", current_player.id)
        if BID_ORDER.index(game.contract[1]) < 5:
            grow2 = Animation(SUIT_IMAGES[game.contract[1]], [CENTER[0] - 50,
                                                              CENTER[1] - 50])
            grow2.grow([10, 10], [100, 100],[2, 2])
        else:
            grow2 = Animation(SUIT_IMAGES[game.contract[1]], [CENTER[0] - 100,
                                                              CENTER[1] - 100])
            grow2.grow([20, 20], [200, 200], [4, 4])
        stillImages = []    
        animations.append(grow2)     
   
def startBidding(surface, order):
    """ Run the bidding phase of the game. Deal the cards as necessary,
        establish game mode and set variables appropriately """
    global SCREEN, endBid, contra, reContra, bidMessage, buttons, stillImages

    # create buttons and idiomatic list to access them
    passButton, passButtonRect = loadButton(MES.get_button(0), BLACK, BUTTON_IMAGES["small"], 450, 570)
    cTrumpButton, cTrumpButtonRect = loadButton(MES.get_button(1), BLACK, BUTTON_IMAGES["medium"], 300, 520)
    dTrumpButton, dTrumpButtonRect = loadButton(MES.get_button(2), BLACK, BUTTON_IMAGES["medium"], 400, 520)
    hTrumpButton, hTrumpButtonRect = loadButton(MES.get_button(3), BLACK,BUTTON_IMAGES["medium"], 500, 520)
    sTrumpButton, sTrumpButtonRect = loadButton(MES.get_button(4), BLACK, BUTTON_IMAGES["medium"], 600, 520)
    noTrumpButton, noTrumpButtonRect = loadButton(MES.get_button(5), BLACK, BUTTON_IMAGES["large"], 720, 520)
    allTrumpButton, allTrumpButtonRect = loadButton(MES.get_button(6), BLACK, BUTTON_IMAGES["large"], 850, 520)
    contraButton, contraButtonRect = loadButton(MES.get_button(7), BLACK, BUTTON_IMAGES["medium"], 600, 570)
    reContraButton, reContraButtonRect = loadButton(MES.get_button(8), BLACK, BUTTON_IMAGES["large"], 700, 570)
    
    buttons = ((passButton, passButtonRect), (cTrumpButton, cTrumpButtonRect), (dTrumpButton, dTrumpButtonRect),
               (hTrumpButton, hTrumpButtonRect), (sTrumpButton, sTrumpButtonRect),
               (noTrumpButton, noTrumpButtonRect), (allTrumpButton, allTrumpButtonRect),
               (contraButton, contraButtonRect), (reContraButton, reContraButtonRect))
       
    contra = False               # flags for contra and re - contra games
    reContra = False
    endBid = [False, False, False, False]   # keep track of who made a bid already; this turns True if
                                            # a player either passes or makes a higher bid; in the second case,
                                            # all other players turn False and have to bid again
    highlight = False           # some other flags    
    done = False
    first_iter = True
    stillImages = []            # initialize a list of images to draw for animation purposes
        
    # deal cards according to turn order
    for player in turnOrder:
        deal(deck, player, 3)
        
    for player in turnOrder:
        deal(deck, player, 2)
        player.sort_hand()
        
    while not done:    # circulate players according to turn order, until a bid wins, 
        for player in turnOrder:      # or until everyone has passed
            
            if player == player1:     # if it's the player's turn, wait for his move
                while not endBid[turnOrder.index(player1)]:
                    
                    for event in pygame.event.get():     # event loop
                        if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                            terminate()
                        if event.type == MOUSEMOTION:    # detect the highlight
                            x, y = event.pos
                            for button in range(len(buttons)):
                                if buttons[button][1].collidepoint(x, y):
                                    highlight = True
                                    highlightRect = buttons[button][1]
                                    break
                                else:
                                    highlight = False                                    
                                                
                        if event.type == MOUSEBUTTONUP:                            
                            for button in range(len(buttons)):
                                if buttons[button][1].collidepoint(event.pos[0], event.pos[1]):
                                    if button == 7:   # if a contra was declared:
                                        if game.contract[1] == "pass":
                                            game.bidMessage = MES.get_bid_message("plnocontra")
                                        else:                                            
                                            contra = True
                                            endBid =  [False, False, False, False] 
                                            endBid[turnOrder.index(player1)] = True    # end the loop
                                            game.bidMessage = MES.get_bid_message("plcontra")
                                    elif button == 8:  # if a re-contra was declared
                                        if game.contract[1] == "pass" or not contra:
                                            game.bidMessage = MES.get_bid_message("plnorecontra")
                                        else:                                        
                                            reContra = True
                                            contra = False
                                            endBid =  [False, False, False, False] 
                                            endBid[turnOrder.index(player1)] = True    # end the loop
                                            game.bidMessage = MES.get_bid_message("plrecontra")
                                    elif BID_ORDER[button] == "pass":                                        
                                        endBid[turnOrder.index(player1)] = True    # end the loop
                                        game.bidMessage = MES.get_bid_message("plpas")                                   
                                    else:
                                        if game.contract[1] == "pass":
                                            # no one has bidded yet, assign bid automatically
                                            game.contract = [player1, BID_ORDER[button]]
                                            strategy1.bid_history.append(game.contract)
                                            strategy2.bid_history.append(game.contract)
                                            endBid =  [False, False, False, False] 
                                            endBid[turnOrder.index(player1)] = True    # end the loop
                                            game.bidMessage = MES.get_bid_message("plraise")
                                            if BID_ORDER.index(game.contract[1]) < 5:
                                                grow1 = Animation(SUIT_IMAGES[game.contract[1]], [CENTER[0] - 50,
                                                                                                  CENTER[1] - 50])
                                                grow1.grow([10, 10], [100, 100], [2, 2])
                                            else:
                                                grow1 = Animation(SUIT_IMAGES[game.contract[1]], [CENTER[0] - 100,
                                                                                                  CENTER[1] - 100])
                                                grow1.grow([20, 20], [200, 200], [4, 4])
                                            animations.append(grow1)                                                                                                                               
                                        else:
                                            if button < BID_ORDER.index(game.contract[1]):
                                                game.bidMessage = MES.get_bid_message("pllowbid")
                                            elif button == BID_ORDER.index(game.contract[1]):
                                                game.bidMessage = MES.get_bid_message("plsamebid")
                                            else:
                                                game.contract = [player1, BID_ORDER[button]]
                                                strategy1.bid_history.append(game.contract)
                                                strategy2.bid_history.append(game.contract)
                                                contra = False           # raising cancels previous contra and re-contra
                                                reContra = False
                                                endBid = [False, False, False, False] 
                                                endBid[turnOrder.index(player1)] = True    # end the loop
                                                game.bidMessage = MES.get_bid_message("plraise")
                                                # create Animations
                                                if BID_ORDER.index(game.contract[1]) < 5:
                                                    grow1 = Animation(SUIT_IMAGES[game.contract[1]], [CENTER[0] - 50,
                                                                                                      CENTER[1] - 50])
                                                    grow1.grow([10, 10], [100, 100], [2, 2])
                                                else:
                                                    grow1 = Animation(SUIT_IMAGES[game.contract[1]], [CENTER[0] - 100,
                                                                                                      CENTER[1] - 100])
                                                    grow1.grow([20, 20], [200, 200], [4, 4])
                                                   
                                                stillImages = []    
                                                animations.append(grow1)
                                                                                                
                    SCREEN.fill(BGCOLOR)
                    display()                                         
                    for button, buttonRect in buttons:
                        SCREEN.blit(button, buttonRect)
                        
                    if highlight:                        
                        pygame.draw.rect(SCREEN, YELLOW, highlightRect, 2)                   
                            
                    drawAnimation(animations, stillImages, buttons)   
                    if stillImages:
                        for image in stillImages:
                            image.draw(SCREEN) 
                    game.draw(SCREEN)
                    pygame.display.update()
                    FPSCLOCK.tick(FPS)
                    first_iter = False
            else:                          # process computer moves
                if False not in endBid:    # everyone has finished bidding, terminate the bidding phase                    
                    pygame.time.wait(700)
                    terminateBidding(game.contract)
                    done = True 
                    break
                else:
                    if not first_iter:
                        pygame.time.wait(700)
                    makeBid(player, game.contract)   # do the bid

                SCREEN.fill(BGCOLOR)                
                display()             
                for button, buttonRect in buttons:
                    SCREEN.blit(button, buttonRect)                
                drawAnimation(animations, stillImages, buttons)        
                if stillImages:
                    for image in stillImages:
                        image.draw(SCREEN)    
                game.draw(SCREEN)
      
                pygame.display.update()
                FPSCLOCK.tick(FPS)
                first_iter = False
    
def terminateBidding(winning_contract):
    """ Terminate the bidding phase, set variables accordingly.
        winning_contract -> list of [Hand, String]"""
    global trump
    if winning_contract[1] == "pass":
        # if it was a pass game, change who's first, collect the cards and restart bidding         
        for player in turnOrder:
            deck.collect_cards(player.hand)   # gather back all cards
            player.hand = []  # reset the hand 

        deck.cut()    # cut the deck
        game.bidMessage = None       
        first = game.switch_first(turnOrder)   # determine the next first and change 
        changeTurnOrder(first)                 # turn order accordingly
        game.state = 1
        
    elif BID_ORDER.index(winning_contract[1]) < 5:
        # if it's a suit contract        
        trump = winning_contract[1]
        game.switch_currentPower(winning_contract)
        game.state = 2
    elif BID_ORDER.index(winning_contract[1]) == 5:   # it's No trumps contract        
        trump = "none"
        game.switch_currentPower(winning_contract)
        game.state = 2
    elif BID_ORDER.index(winning_contract[1]) == 6:    # All trumps contract        
        trump = "all"
        game.switch_currentPower(winning_contract)
        game.state = 2
        
def cleanAll():
    """ Collect the cards, cut them, reset all variables for a new game """
    global trump, rund
    for player in turnOrder:
        if player.winnings:
            deck.collect_cards(player.winnings)
            player.winnings = []
        player.hand = []
        player.announces = []
        player.belotes = []
        player.saved_cards = []
        player.suit_power = {}
    
    deck.cut()    
    game.currentPower = {'C': NO_TRUMP_POWER, 'S': NO_TRUMP_POWER,   
                         'H': NO_TRUMP_POWER, 'D': NO_TRUMP_POWER}
    game.contract = [None, "pass"]
    game.announces = []
    strategy1.bid_history = []
    strategy1.passed = {}
    strategy2.bid_history = []
    strategy2.passed = {}
    
    first = game.switch_first(turnOrder)   # determine the next first and change 
    changeTurnOrder(first)                 # turn order accordingly
    trump = None
    rund = 1    
    game.state = 1
    
def welcome():
    """ Display the welcome screen in the beginning of the game.
        Select language for the game interface. """
    global MES
    width = 700
    height = 500
    center = (width // 2, height // 2)
    welcomeScreen = pygame.display.set_mode((width, height))
    line1, line1Rect = makeText("single player", FONT1, BLACK)
    belot, belotRect = makeText("BELOTE", FONT5, RED)
    line2, line2Rect = makeText("by Miroslav Georgiev", FONT2, BLACK)
    line3, line3Rect = makeText("Select your language below to continue", FONT1, BLACK)
    eng_but, eng_but_rect = loadButton("", WHITE, LANG_IMAGES['eng'], center[0] - 100, center[1] + 100)
    bul_but, bul_but_rect = loadButton("", WHITE, LANG_IMAGES['bul'], center[0], center[1] + 100)

    done = False
    while not done:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                terminate()
            if event.type == MOUSEBUTTONUP:
                if eng_but_rect.collidepoint(event.pos):                    
                    MES = location.English()
                    done = True
                elif bul_but_rect.collidepoint(event.pos):                    
                    MES = location.Bulgarian()
                    done = True
        
        welcomeScreen.fill(WHITE)        
        pygame.draw.rect(welcomeScreen, GREEN, (0, 0, 700, 500), 5)       
        welcomeScreen.blit(line1, (center[0] - line1Rect.centerx, 100))
        welcomeScreen.blit(belot, (center[0] - belotRect.centerx, 130))
        welcomeScreen.blit(line2, (center[0] - line2Rect.centerx, 240))
        welcomeScreen.blit(line3, (center[0] - line3Rect.centerx, 300)) 
        welcomeScreen.blit(eng_but, eng_but_rect)
        welcomeScreen.blit(bul_but, bul_but_rect)
        

        pygame.display.update()     
    
def gameOver(team):
    """ Display the end of game dialog window, according to which team won.
        Team -> String"""
    result = ""
    if team == 'Team 1':
        game.team1Games += 1
        result = MES.game_over_mes("Team 1", game)
    elif team == "Team 2":
        game.team2Games += 1
        result = MES.game_over_mes("Team 2", game)
    # create interface objects    
    yesButton, yesButtonRect = loadButton(MES._end_messages["ya"], BLACK, BUTTON_IMAGES["small"], 550, 500)
    quitButton, quitButtonRect = loadButton(MES._end_messages["no"], BLACK, BUTTON_IMAGES["medium"], 650, 500)
    gameOver, gameOverRect = makeText("GAME OVER!", FONT5, RED)
    resultMes, resultMesRect = makeText(result, FONT4, WHITE)
    playAgain, playAgainRect = makeText(MES._end_messages["continue"], FONT3, WHITE)    
    done = False
    
    while not done:
        for event in pygame.event.get():     # event loop
            if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                terminate()
            if event.type == MOUSEBUTTONUP:
                if yesButtonRect.collidepoint(event.pos):   # reset variables, start a new game
                    cleanAll()
                    game.team1Score = 0
                    game.team2Score = 0
                    strategy1.behavior = "normal"
                    strategy2.behavior = "normal"
                    
                    done = True
                elif quitButtonRect.collidepoint(event.pos):
                    terminate()
                    
        SCREEN.fill(BGCOLOR)
        display()
        pygame.draw.rect(SCREEN, SILVER, (CENTER[0] - 305, CENTER[1] - 205,
                                        610, 410))
        pygame.draw.rect(SCREEN, BLUE, (CENTER[0] - 300, CENTER[1] - 200,
                                        600, 400))
        SCREEN.blit(gameOver, (CENTER[0]-gameOverRect.centerx, 250))
        SCREEN.blit(resultMes, (CENTER[0]-resultMesRect.centerx, 350))
        SCREEN.blit(playAgain, (CENTER[0]-playAgainRect.centerx, 430))
        SCREEN.blit(yesButton, yesButtonRect)
        SCREEN.blit(quitButton, quitButtonRect)
        
        pygame.display.update()
        FPSCLOCK.tick(FPS)

def makeText(text, font, color):
    """ Create a pygame text object in the given font and color.
        Return a tuple of the object and its rectangle. """
    textSurf = font.render(text, True, color)
    textRect = textSurf.get_rect()
    textRect.centerx = textRect.width // 2
    textRect.centery = textRect.height // 2
    return (textSurf, textRect)

def loadButton(text, textColor, image, top, left):
    """ Create a Pygame Surface object and Rectangle object with the given top, left coords.
        Draw the given image and text onto the surface.
        Returns a tuple of the image surface and rectancle object"""
    textSurf, textRect = makeText(text, FONT1, textColor)
    imageRect = image.get_rect()
    imageRect.center = (imageRect[2] // 2, imageRect[3] // 2)
    imageSurf = pygame.Surface ((imageRect[2], imageRect[3]))
    imageSurf.blit(image, imageRect)
    imageSurf.blit(textSurf, (imageRect.center[0] - textRect.centerx,
                                      imageRect.center[1] - textRect.centery))
    imageRect.topleft = (top, left)
          
    return (imageSurf, imageRect)

def display():
    """ displays redundand stuff """

    pygame.draw.rect(SCREEN, BROWN, (CENTER[0] - 605, CENTER[1] - 380,
                                                     1210, 785))   
    pygame.draw.rect(SCREEN, GREEN, (CENTER[0] - 600, CENTER[1] - 375,
                                     1200, 775))
    SCREEN.blit(BELOTE_PICTURE, (CENTER[0] - BELOTE_PICTURE.get_size()[0] // 2,
                                 CENTER[1] - BELOTE_PICTURE.get_size()[1] // 2))
    player1.draw(SCREEN, (350, 650))
    player2.draw(SCREEN, (80, 150))
    player3.draw(SCREEN, (350, 80))
    player4.draw(SCREEN, (1150, 150))
    player1.update()

def drawAnimation(animation_list, images_list, button_list=None):
    """ Process the animations for the game.
        animation_list -> List of Animations
        images_list -> list of still images, to be drawn as animations end
        button_list -> list of images, to be drawn during bidding phase"""    
    
    while animation_list:
        SCREEN.fill(BGCOLOR)
        display()
        if button_list:
            for button, button_rect in buttons:
                SCREEN.blit(button, button_rect)
        for anim in animation_list[:]:
            
            if not anim.in_motion and not anim.growing:
                animation_list.remove(anim)
                if not anim.moth:
                    images_list.append(anim)
            else:                                    
                anim.draw(SCREEN)
                anim.update()
            if images_list:
                for image in images_list:
                    image.draw(SCREEN)                                       
        game.draw(SCREEN)    
        pygame.display.update()
        FPSCLOCK.tick(FPS)
    
    
def drawAnons(player):
    """ Check game.announces for announces of the given player;
        return them as a string; if no announces - return None.
        player -> Hand """
    anonsList = []
    result = ""
    for anons in game.announces:   #check anonses made and sift out the ones the player made
        if anons[0] == player:
            anonsList.append(anons[1])
    if not anonsList:
        return None
    seq = []
    cares = []
    belotes = []
    final = []
        
    for anons in anonsList:
        if anons.vid == 'care':
            cares.append(MES._interface['care'])
        elif anons.vid == 3 or anons.vid == 4 or anons.vid == 5:
            seq.append(str(anons.vid))
        elif anons.vid == 'belote':
            belotes.append(MES._interface['belot'])
            
    if player.team == 'Team 1':
        final = cares + seq + belotes
    elif player.team == 'Team 2':
        final = belotes + seq + cares
      
    return ', '.join(final)    
    
def terminate():
    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
