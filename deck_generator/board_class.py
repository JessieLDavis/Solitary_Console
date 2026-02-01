#moving the gameplay settings out of deck
from deck_generator.deck_class import DeckObj, CardObj
from pathlib import Path
import tomllib

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

class GameBoard:
    board_template = ""
    deck_settings = None
    stacking_settings = None

    def __init__(self):
        self.board_locations = ['tableau','draw','waste']
        self.flip_hand = 1
        self.card_loc = {'tableau':{'1':[]},
                           'draw':[],
                           'waste':[]}
        self.deck = DeckObj('default')
        self.settings = {}
        self.stacking = {}
        pass

    def draw(self):
        draw_list:list = self.card_logic.get('draw',[])
        waste_list:list = self.card_logic.get('waste',[])
        if len(draw_list) == 0 and len(waste_list) == 0:
            #Nothing to draw
            return False
        if len(draw_list) == 0:
            draw_list = waste_list.copy()
            waste_list.clear()
        else:
            try:
                waste_list.extend(draw_list.pop(-self.flip_hand))
            except IndexError:
                waste_list.extend(draw_list.copy())
                draw_list.clear()
        self.card_loc['draw'] = draw_list
        self.card_loc['waste'] = waste_list
        return True
    
    def reset_board(self):
        pass

    def move_card(self,current_location,board_destination,moving_card,col_num=None):
        loc_deck = self.card_loc.get(board_destination)
        cur_deck = self.card_loc.get(current_location)
        error = None
        if loc_deck == None:
            error = "Destination not recognized."
        elif not isinstance(loc_deck,dict) and col_num is not None:
            error = 'Not a valid location. No column names.'
            # return False, error
        if cur_deck == None:
            error = 'Current location not recognized.'
        if moving_card not in self.deck.full_deck:
            error = "Card not in deck."
        if isinstance(cur_deck,dict):
            keyList = [k for k, v in cur_deck.items() if moving_card in v]
            if len(keyList) == 0:
                error = "Can't find source card."
            elif len(keyList) > 1:
                error = "Source card in multiple columns."
            else:
                keyList = keyList[0]
        elif isinstance(cur_deck,list) and moving_card not in cur_deck:
            error = "Can't find source card."
        if not isinstance(cur_deck,dict) or not isinstance(cur_deck,list):
            error = "Current location not recognized."
        if col_num != None and isinstance(loc_deck,dict) and col_num not in loc_deck.keys():
            error = 'Column name not found'

        if error != None:
            return False, error
        
        if isinstance(loc_deck,list):
            try:
                location_card = loc_deck[-1]
            except IndexError:
                location_card = None
        if isinstance(loc_deck,dict):
            try:
                location_card = loc_deck[col_num][-1]
            except IndexError:
                location_card = None
        if isinstance(cur_deck,dict):
            card_index = cur_deck[keyList].index(moving_card)
            card_stack = cur_deck[keyList][card_index:]
            if len(card_stack)>1:
                hasStack = True
            elif len(card_stack) == 1:
                hasStack = False
            else:
                hasStack = False
        else:
            hasStack = False
        valid_move = self.check_valid_move(board_destination,moving_card,location_card,hasStack)
        if valid_move:
            #remove from current
            if hasStack == False:
                move_stack = [moving_card,]
                if isinstance(cur_deck,dict):
                    cur_deck[keyList].remove(moving_card)
                else:
                    cur_deck.remove(moving_card)
                
            else:
                if isinstance(cur_deck,dict):
                    move_stack = card_stack
                    for card in move_stack:
                        cur_deck[keyList].remove(card)
                else:
                    raise TypeError

            #add to new
            if col_num == None:
                loc_deck.extend(move_stack)
            else:
                loc_deck[col_num].extend(move_stack)
            self.card_loc[board_destination] = loc_deck
            self.card_loc[current_location] = cur_deck
            return True, error
        return False, error


    def check_valid_move(self,board_destination,moving_card,location_card,hasStack)->bool:
        if moving_card.visible == False: # or location_card.visible==False:
            #cant move nonvisible card / trapped
            return False
        if hasStack == True and board_destination in ['foundation','deck','waste']:
            #stacks can't move to foundations or deck or waste
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
        if loc_rules is None:
            #no rules found?
            return False
        if location_card is None:
            #check if card can move to empty
            moveEmpty_list = loc_rules.get('moveEmpty',[])
            if moving_card.number in moveEmpty_list:
                return True
            else:
                return False
        if location_card.visible == False:
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


class Klondike(GameBoard):
    def __init__(self):
        self.board_locations = ['foundation','tableau','draw','waste']
        self.flip_hand = 3
        self.card_loc = {
            'foundation':{'h':[],'s':[],'d':[],'c':[]},
            'tableau':{'1':[],'2':[],'3':[],'4':[],'5':[],'6':[],'7':[]},
            'draw':[],
            'waste':[]
        }
        self.deck = DeckObj('klondike')
        self.settings = self.load_deck_settings('klondike')
        self.stacking = self.load_stack_settings()

    def reset_board(self):
        deck_list = self.deck.shuffle_deck(self.deck.full_deck)
        foundation_dict = self.card_loc.get('foundation',{'h':[],'s':[],'d':[],'c':[]})
        tableau_dict = self.card_loc.get('tableau',{'1':[],'2':[],'3':[],'4':[],'5':[],'6':[],'7':[]})
        # draw_dict = self.card_loc.get('draw',[])
        # waste_dict = self.card_loc.get('waste',[])
        # tableau_list = [[0],[1,7],[2,8,13],[3,9,14,18],[4,10,15,19,22],[5,11,16,20,23,25],[6,12,17,21,24,26,27]]
        col_list = ['1','2','3','4','5','6','7']
        # for ind,r in enumerate(tableau_list):
        #     col_name = col_list[ind]
        #     for card_ind in r:

        #         deck_list[card_ind]
        for loop_num in range(7):
            for ind ,col in enumerate(col_list):
                if ind < loop_num:
                    pass
                else:
                    try:
                        tableau_dict[col]
                    except KeyError:
                        tableau_dict[col] = []
                    tableau_dict[col].append(deck_list.pop())
                # loop_num += 1
        self.card_loc = {'foundation':foundation_dict,'tableau':tableau_dict,'draw':deck_list,'waste':[]}
        return
    
    




        

    