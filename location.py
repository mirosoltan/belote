#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 09 10:18:09 2017

@author: Miroslav Georgiev

The Message class implements language switch for Belote. Each child of the main class represents a different language,
and forms messages in the respective form. 
"""

class Message():
    def __init__(self):
       self._teams = {}
       self._bid_messages = {}
       self._game_messages = {}
       self._player_messages = {}  
       self._buttons = {}
       self._interface = {}
       self._final = {}
       
    def get_button(self, button):
        return self._buttons[button]
            
    def get_bid_message(self, message, player=None):
        """ Return the message corresponding to the string 'message';
            If a player is passed, join his id to the message string. """
        if player:
            return player + self._bid_messages[message]
        return self._bid_messages[message]
    
    def get_game_message(self, message, player=None):
        """ Return the message corresponding to the string 'message'.
            If a player is passed, join his id to the message string."""
        if player:
            return player + self._game_messages[message]
        return self._game_messages[message]
    
    def get_player_message(self, message):
        """ Return the message corresponding to the string 'message'"""
        return self._player_messages[message]
    
    def make_interface(self, element, player=None, addon=None):
        """ Form interface texts for drawing. Optional Player and Addon variables 
            may complicate the original interface element. """
        if player:  # a player needs to be concatenated
            if addon:  # the contra and recontra need to be added
                return self._interface[element] + player + self._interface[addon]
            else:
                return self._interface[element] + player
        return self._interface[element]  
    
    def make_result(self, message, team):
        """ Build the message for final result (essentialy who won the game). """
        return team + self._end_messages[message]
        
    
    def make_even_result(self, team=False):
        """ Build the message for even result - the contract team's poins 'hang'.
            If there was contra or recontra, both results hang."""
        if not team:
            return self._end_messages['evencontra']
        else:
            # the typical case - one team's result 'hangs'
            return self._end_messages['evenone'] + self._teams[team] + self._end_messages['hang']
        
    def game_over_mes(self, team, game_result):
        """ Build the Game Over message. Announce who won, and 
            what is the current overal result """
        return team + self._end_messages["result"] + str(game_result.team1Games) + " to " + str(game_result.team2Games) 
    
            
       
class English(Message):
    def __init__(self):
        Message.__init__(self)
        self._teams = {"T1": "Team 1",   # map teams
                       "T2": "Team 2"
                }
        self._buttons = {0: "pass",      # map interface button texts
                         1: "Clubs",
                         2: "Diamonds",
                         3: "Hearts",
                         4: "Spades",
                         5: "No Trumps",
                         6: "All Trumps",
                         7: "Contra",
                         8: "Re-Contra",
                         9: "Declare",
                         10: u"Carré",
                         11: "Done"
                }
        self._interface = {"Score": "Score",    # other interface messages
                           "Anons": "Declarations",
                           "Pl1": "Player 1",
                           "Pl2": "Player 2",
                           "Pl3": "Player 3",
                           "Pl4": "Player 4",
                           "Raised": "Raised by ",
                           "wcontra": " with contra!",
                           "wrecontra": " with re-contra !",
                           "Seq": "Sequences",
                           "End": "ROUND ENDS.",
                           "care": u"carré",
                           "belot": "belote",
                           'first': 'first'                           
                }
        self._end_messages = {'hang': "'s points hang!",     # messages for the end of a round
                              'evenone': "Result is even! ",
                              'evencontra': "Result is even! All points, including the contra bonus, hang!",
                              'win': " wins their contract.",
                              'wincapo': " wins their contract with capot!",
                              'wincontra': " wins their contract with contra!",
                              'winrecontra': " wins their contract with re-contra!",
                              'lose': " lost the contract!",
                              'losecapo': " not only lost the contract, they are capot!",
                              'losecontra': " lost the contract with contra!",
                              'loserecontra': ' lost the contract with re-contra!',
                              'result': " wins the game! Games are now ",
                              'continue': "Continue playing?",
                              'ya': "YES!",
                              'no': "No, quit"
                              }
        self._bid_messages = {"comppass": " passes",     # messages for the bidding phase
                              "compraise": " raises:",
                              "compcontra": " declares CONTRA!",
                              "comprecontra": " declares RE-CONTRA!",
                              "plpas": "You pass",
                              "plraise": "You raise:",
                              "plcontra": "You declare CONTRA!",
                              "plrecontra": "You declare RE-CONTRA!",
                              "plnocontra": "You can't declare contra yet!",
                              "plnorecontra": "You can't declare re-contra yet!",
                              "pllowbid": "You cannot bid lower than the current bid!",
                              "plsamebid": "This contract has already been proposed! Either pass or raise or declare contra."
                              }
        
        self._game_messages = {"compbelot": " declares a belote.",     # general messages displayed during play
                              "seq3": " declares a sequence of three.",
                              "seq4": " declares a sequence of four.",
                              "seq5": " declares a sequence of five!",
                              "care": u" declares a carré!",
                              "plbelot": "You declare belote.",                              
                              "plseq3": "You declare a sequence of three.",
                              "plseq4": "You declare a sequence of four.",
                              "plseq5": "You declare a sequence of five!",
                              "plcare": u"You declare a carré!!!"                       
                              }
        self._player_messages = {"noanons": "You don't have any announces to declare!",    # messages refering to the player's actions during play
                                 "noseq3": "You need three sequential cards of the same suit!",
                                 "noseq4": "You need four sequential cards of the same suit!",
                                 "noseq5": "You need five sequential cards of the same suit!",
                                 "nocare": u"You need four cards of the same rank to declare a carré",
                                 "longer": "A longer sequence was declared already",
                                 "answer": "You need to answer the required suit!",
                                 "higher": "You need to give a higher card!",
                                 "trump": "You need to trump!",
                                 "hightrump": "You need to trump higher!"
                }
        
    
    

class Bulgarian(Message):
    def __init__(self):
        Message.__init__(self)
        self._players = {"Player 1": u"Играч 1",
                         "Player 2": u"Играч 2",
                         "Player 3": u"Играч 3",
                         "Player 4": u"Играч 4"
                         } 
        self._teams = {"T1": u"Отбор 1",
                       "T2": u"Отбор 2"}
        self._buttons = {0: u"пас",
                         1: u"Спатии",
                         2: u"Кари",
                         3: u"Купи",
                         4: u"Пики",
                         5: u"Без коз",
                         6: u"Всичко коз",
                         7: u"Контра",
                         8: u"Ре-контра",
                         9: u"Анонси",
                         10: u"Каре",
                         11: "OK"
                         }
        self._interface = {"Score": u"Резултат",
                           "Anons": u"Анонси",
                           "Pl1": u"Играч 1",
                           "Pl2": u"Играч 2",
                           "Pl3": u"Играч 3",
                           "Pl4": u"Играч 4",
                           "Raised": u"Взета от ",
                           "wcontra": u" с контра!",
                           "wrecontra": u" с реконтра!",
                           "Seq": u"Поредни",
                           "End": u"КРАЙ НА РАЗДАВАНЕТО.",
                           "care": u"каре",
                           "belot": u"белот",
                           'first': u'първи'                           
                }
        self._bid_messages = {"comppass": u" пасува",
                              "compraise": u" вдига:",
                              "compcontra": u" обявява КОНТРА!",
                              "comprecontra": u" обявява РЕКОНТРА!",
                              "plpas": u"Пасуваш.",
                              "plraise": u"Вдигаш:",
                              "plcontra": u"Обявяваш КОНТРА!",
                              "plrecontra": u"Обявяваш РЕКОНТРА!",
                              "plnocontra": u"Още не можеш да обявиш контра!",
                              "plnorecontra": u"Още не можеш да обявиш реконтра!",
                              "pllowbid": u"Не можеш обявиш цвят по-нисък от текущия!",
                              "plsamebid": u"Това вече е обявено от друг играш! Обяви друго, или контра."
                              }
        self._game_messages = {"compbelot": u" обявява белот.",
                              "seq3": u" обявява терца.",
                              "seq4": u" обявява петдесет.",
                              "seq5": u" обявява сто!",
                              "care": u" обявява каре!",
                              "plbelot": u"Обявяваш белот.",                              
                              "plseq3": u"Обявяваш терца.",
                              "plseq4": u"Обявяваш петдесет.",
                              "plseq5": u"Обявяваш сто!",
                              "plcare": u"Обявяваш каре!!!"                       
                              }
        self._player_messages = {"noanons": u"Нямаш нищо за обявяване!",
                                 "noseq3": u"За терца ти трябват ти три поредни от един цвят.",
                                 "noseq4": u"За петдесет ти трябват четири поредни от един цвят.",
                                 "noseq5": u"За сто ти трябват пет поредни от един цвят.",
                                 "nocare": u"Трябват ти четири еднакви за да обявиш каре!",
                                 "longer": u"Вече е обявен по-висок анонс.",
                                 "answer": u"Трябва да отговориш!",
                                 "higher": u"Трябва да се качиш!",
                                 "trump": u"Трябва да цакаш!",
                                 "hightrump": u"Трябва да надцакаш!"
                }
        self._end_messages = {'evenone': u"Равен резултат! Точките на ",
                              'evencontra': u"Равен резултат! Всички точки висят, включително контрата!",
                              'win': u" изкарва играта си.",
                              'wincapo': u" изкарва играта с капо!",
                              'wincontra': u" изкарва играта с контра!",
                              'winrecontra': u" изкарва играта с реконтра!",
                              'lose': u" е вътре!",
                              'losecapo': u" не само е вътре, но е и капо!",
                              'losecontra': u" е вътре с контра!",
                              'loserecontra': u' е вътре с реконтра!',
                              'result': u" печели играта! Игрите сега са ",
                              'continue': u"Ще играете ли още?",
                              'ya': u"ДА!",
                              'no': u"Не, изход"
                              }
        
    def get_bid_message(self, message, player=None):
        """ Return the message corresponding to the string 'message';
            If a player is passed, join his id to the message string. """
        if player:            
            return self._players[player] + self._bid_messages[message]
        return self._bid_messages[message]
    
    def get_game_message(self, message, player=None):
        """ Return the message corresponding to the string 'message'.
            If a player is passed, join his id to the message string."""
        if player:
            return self._players[player] + self._game_messages[message]
        return self._game_messages[message]
    
    def make_result(self, message, team):
        """ Build the message for final result."""
        if team == "Team 1":
            return self._teams["T1"] + self._end_messages[message]
        else:
            return self._teams["T2"] + self._end_messages[message] 
        
    def make_even_result(self, team=False):
        """ Build the message for even result - the contract team's poins 'hang'.
            If there was contra or recontra, both results hang."""
        if not team:
            return self._end_messages['evencontra']
        else:
            # the typical case - one team's result 'hangs'
            return self._end_messages['evenone'] + self._teams[team] + ' висят!'  
        
    def make_interface(self, element, player=None, addon=None):
        """ Form interface texts for drawing """
        if player:  # a player needs to be concatenated
            if addon:  # the contra and recontra need to be added
                return self._interface[element] + self._players[player] + self._interface[addon]
            else:
                return self._interface[element] + self._players[player]
        return self._interface[element]      

