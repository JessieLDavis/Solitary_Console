from random import shuffle,choice
import tomllib
from pathlib import Path

DECK_SETTINGS_PATH = Path(f'deck_generator/deck_settings.toml')
STACK_SETTINGS_PATH = Path(f'deck_generator/stack_settings.toml')

#ANSI codes
RED = "\033[0;31m"
LIGHT_RED = "\033[1;31m"
BLUE = "\033[0;34m"
LIGHT_BLUE = "\033[1;34m"
BLACK = "\033[0;30m"
DARK_GRAY = "\033[1;30m"
LIGHT_GRAY = "\033[0;37m"
RESET = "\033[0m"

class DeckObj:
    """This is the parent Deck object. This allows for shuffling, dealing, and some global functions."""
    deck_settings = None
    stacking_settings = None
    def __init__(self,deck_type):
        self.deck_type:str = deck_type
        self.settings: dict = {}
        self.stacking: dict = {}
        self.board_locations:list = []
        self.full_deck:list = self.set_deck()


    def set_deck(self,shuffle:bool=True):
        #load settings
        settings = DeckObj.deck_settings
        if settings is None:
            settings = DeckObj.load_deck_settings()
        
        stacking = DeckObj.stacking_settings
        if stacking is None:
            stacking = DeckObj.load_stack_settings()
        
        deck_type_settings = settings.get(self.deck_type)
        if deck_type_settings is None:
            print(f'Requested settings could not be found.')
            raise KeyError
        self.settings = deck_type_settings
        #set stacking rules
        board_locations = self.board_locations
        if len(board_locations) == 0:
            board_locations = deck_type_settings.get('board_locations',[])
            self.board_locations = board_locations
        board_dict = {}
        for loc in board_locations:
            loc_dict = stacking.get(loc)
            if loc != None:
                board_dict[loc] = loc_dict
        self.stacking = board_dict
        
        #generate cards
        deck_count = deck_type_settings.get('deck_count')
        total_cards = deck_type_settings.get('total_cards',0)
        if deck_count is None:
            deck_list = self.generate_deck(deck_type_settings)
        else:
            total_cards
            deck_list = []
            for d in range(deck_count):
                deck_list.extend(self.generate_deck(deck_type_settings))
        if len(deck_list) != total_cards:
            # return deck_list
        # else:
            print('Deck card count does not match expected total!')
            raise ValueError
        
        if shuffle:
            DeckObj.shuffle_deck(deck_list)
        return deck_list

    def generate_deck(self,dt_set):
        """Using the passed deck template, generate card set."""
        deck_list = []
        hasJokers = dt_set.get('hasJokers')
        colors = dt_set.get('colors')
        number_options = dt_set('number_options')
        suits = dt_set.get('suits')
        if hasJokers:
            joker_ct = dt_set.get('joker_count')
            for jo in range(joker_ct):
                jo_obj = Joker(jo, colors)
                # jo_obj.set_stacking(b_set)
                deck_list.append(jo_obj)
        for s in suits:
            for n in number_options:
                color,emoji = dt_set.get(f'suit_{s}',[None,None])
                if color is None or emoji is None:
                    raise KeyError
                card = CardObj(color,s,n,emoji)
                # card.set_stacking(b_set)
                deck_list.append(card)

    def check_valid_move(self,board_destination,moving_card,location_card)->bool:
        if moving_card.visible == False:
            #cant move nonvisible card / trapped
            return False
        if moving_card.movable == False:
            return False
        if location_card == moving_card:
            #cant move onto same card
            return False
        if board_destination not in self.board_locations:
            #could not find location
            return False
        loc_rules = self.stacking.get(board_destination)
        if loc_rules == False:
            #no rules found?
            return False
        if location_card is None:
            #check if card can move to empty
            moveEmpty_list = loc_rules.get('moveEmpty',[])
            if moving_card.number in moveEmpty_list:
                return True
            else:
                return False
        color_move = self.translate_settings(loc_rules.get('color_stack'),self.settings.get('colors'),moving_card,'color')
        if location_card.color not in color_move:
            return False
        
        suit_move = self.translate_settings(loc_rules.get('suit_stack'),self.settings.get('suits'),moving_card,'suit')
        if suit_move == 'color override':
            pass
        elif location_card.suit not in suit_move:
            return False
        
        number_move = self.translate_numbers(loc_rules.get('number_stack'),self.settings.get('number_options',[]),moving_card,loc_rules.get('canWrap',[]))
        if number_move == 'color override':
            pass
        elif number_move == None:
            #joker card
            pass
        elif location_card.number not in number_move:
            return False
        
        #if all pass
        return True


        

    def translate_settings(self,category,opt_list,moving_card,target):
        if moving_card.number == '0':
            #is joker
            return
        if category is None or category == 'any':
            return opt_list
        if category == 'none':
            return []
        if category == 'equal':
            return [o for o in opt_list if o.get(target) == moving_card.get(target)]
        if category == 'diff':
            return [o for o in opt_list if o.get(target) != moving_card.get(target)]
        if category == 'color override':
            if target == 'color':
                #cant color override color rule
                raise KeyError
            else:
                return category
        return False
    
    def translate_numbers(self,category,opt_list,moving_card,canWrap_list):
        last_val = None
        next_val = None
        if category == 'any':
            return self.translate_settings(category,opt_list,moving_card,None)
        if category == 'ascending' or category == 'descending':
            
            try:
                card_loc = opt_list.index(moving_card.number)
            except IndexError:
                #Card num not in list?
                raise IndexError
            
            try:
                if category == 'ascending':
                    next_val = opt_list[card_loc+1]
                else:
                    next_val = opt_list[card_loc-1]
            except IndexError:
                if moving_card.number not in canWrap_list:
                    # raise IndexError
                    #return None
                    pass
                else:
                    if category == 'ascending':
                        next_val = opt_list[0]
                    else:
                        next_val = opt_list[-1]
            try:
                if category == 'ascending':
                    last_val = opt_list[card_loc-1]
                else:
                    last_val = opt_list[card_loc+1]
            except IndexError:
                if moving_card.number not in canWrap_list:
                    # return None
                    pass
                else:
                    if category == 'ascending':
                        last_val = opt_list[-1]
                    else:
                        last_val = opt_list[0]
        return [last_val,next_val]


        


    @classmethod
    def load_deck_settings(cls):
        with open(DECK_SETTINGS_PATH, encoding='utf8') as f:
            deck_settings = tomllib.load(f)
        cls.deck_settings = deck_settings
        return deck_settings
    
    @classmethod
    def load_stack_settings(cls):
        with open(STACK_SETTINGS_PATH, encoding='utf8') as f:
            stack_settings = tomllib.load(f)
        cls.stacking_settings = stack_settings
        return stack_settings
    
    @staticmethod
    def shuffle_deck(list_obj:list):
        if len(list_obj)<=1:
            #too short to shuffle
            return list_obj
        # backup_list = list_obj.copy()
        for turn in range(7):
            shuffle(list_obj)
        # split the deck
        if len(list_obj)>10:
            split = list_obj.index(choice(list_obj))
            list_A = list_obj[:split]
            list_B = list_obj[split:]
            for l in [list_A,list_B]:
                shuffle(l)
            list_obj = list_B + list_A
        return list_obj






class CardObj:
    back_color = LIGHT_BLUE
    def __init__(self,color:str,suit:str,number:str,suit_emoji:str):
        self.color:str = color
        self.suit:str = suit
        self.number:str = number
        self.name:str = self.get_name()
        self.emoji:str = suit_emoji
        self.visible:bool = False
        self.canMove:bool = False
    
    def __str__(self):
        if self.color == 'red':
            c = RED
        elif self.color == 'black':
            c = DARK_GRAY
        elif self.color == 'blue':
            c = BLUE
        
        if self.visible:
            if self.number == '10':
                interior = f"{self.number}{self.emoji}"
            elif self.number == '0':
                interior = f"~{self.emoji}~"
            else:
                interior = f"{self.number}-{self.emoji}"
            return f"{RESET}[{c}{interior}{RESET}]"
        else:
            c = CardObj.back_color
            interior = f"---"
            return f"{RESET}{c}[{interior}]{RESET}"
        

    def set_name(self):
        try:
            int(self.number)
            # return f'{self.number} of {self.suit.title()}s'
            name = self.number
        except TypeError:
            name = ''
            if self.number == 'A':
                name = 'Ace'
            elif self.number == 'J':
                name = 'Jack'
            elif self.number == 'Q':
                name = 'Queen'
            elif self.number == 'K':
                name = 'King'
            else:
                raise TypeError
        return f"{name} of {self.suit.title()}s"
    
    def set_visible(self,isVisible:bool=True):
        self.visible = isVisible
        #check movable?
        return
    
    def set_movable(self,isMovable:bool=True):
        self.movable = isMovable
        return



class Joker(CardObj):
    def __init__(self, number,color_opt):
        if number%2 == 0:
            #is color
            self.color = color_opt[0]
        else:
            #no color
            self.color = color_opt[1]
        
        self.suit = 'JOKER'
        self.number = '0'
        self.name = 'Joker'
        self.emoji = "\u2727"
        self.visible = False

