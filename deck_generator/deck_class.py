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
        board_locations = deck_type_settings.get('board_locations',[])
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

    def check_valid_move(self,board_loc,moving_card,location_card=None):
        loc_stack = self.stacking.get(board_loc,{})
        if location_card is None:
            moveEmpty = loc_stack.get('moveEmpty',[])
            if isinstance(moveEmpty,list):
                if moving_card.number in moveEmpty:
                    return True
                else:
                    return False
            elif moveEmpty == 'none':
                return False
            elif moveEmpty == 'any':
                return True

        color_list = self.settings.get('colors',[])
        suit_list = self.settings.get('suits',[])
        num_list = self.settings.get('number_options',[])
        
        color_stack = loc_stack.get('color_stack','any')
        number_stack = loc_stack.get('number_stack','any')
        suit_stack = loc_stack.get('suit_stack','any')
        number_wrap = loc_stack.get('num_wrap',[])

        iter_list = [
            [number_wrap,num_list,moving_card.number,location_card.number],
            [suit_stack,suit_list,moving_card.suit,location_card.suit],
            [color_stack,color_list,moving_card.color,location_card.color]
        ]


        def get_options(focus,opt_list,moving_var,num_wrap = number_wrap)->list:
            if focus == 'any':
                return opt_list
            elif focus == 'none':
                return []
            elif focus == 'color override':
                return None
            elif focus == 'equal':
                return [var for var in opt_list if var == moving_var]
            elif focus == 'diff':
                return [var for var in opt_list if var != moving_var]
            elif focus == 'ascending':
                try:
                    return opt_list[opt_list.index(moving_var)+1]
                except IndexError:
                    if moving_var in num_wrap:
                        return [opt_list[0],]
                    return []
            elif focus == 'decending':
                try:
                    return opt_list[opt_list.index(moving_var)+1]
                except IndexError:
                    if moving_var in num_wrap:
                        return [opt_list[-1],]
                    return []
            else:
                print(f"{focus} was not recognized.")
                raise KeyError
        # for mov_var, focus,opt_list in [[moving_card.color]]
        for focus, opt_list, m_var, l_var in iter_list:
            opt = get_options(focus,opt_list,m_var,number_wrap)
            if opt == None:
                #color override
                if moving_card.color == m_var:
                    print("Can't color override the color variable")
                    raise KeyError
            elif isinstance(opt,list):
                if l_var not in opt:
                    return False
        return True






class CardObj:
    back_color = LIGHT_BLUE
    def __init__(self,color:str,suit:str,number:str,suit_emoji:str):
        self.color:str = color
        self.suit:str = suit
        self.number:str = number
        self.name:str = self.get_name()
        self.emoji:str = suit_emoji
        self.visible:bool = False
    
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

