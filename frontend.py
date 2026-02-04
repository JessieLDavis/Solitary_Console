import pygame as pg
import pygame_gui as pi
from game_main import Solitare_game, playing_game, draw_cards

def set_menu(menu_options):
    menu_buttons = []
    location_x = 100
    location_y = 500

    for opt in menu_options:
        opt_button = pi.elements.UIButton(relative_rect=pg.Rect((location_x, location_y), (100, 50)),text=opt.title(),manager=manager)
        menu_buttons.append(opt_button)
        location_x += 100
    return menu_buttons

def make_card(card_obj,location_x,location_y):
    if (location_x,location_y) != card_obj.location:
        card_obj.location = (location_x,location_y)
    if card_obj.button == None:
        button = pi.elements.UIButton(pg.Rect((location_x,location_y),(30,50)),text=card_obj.shortForm,manager=manager)
        card_obj.button = button
    else:
        card_obj.button.set_postition(card_obj.location)
    return card_obj
    

def make_tableau(gameDeck):
    location_x = 50
    location_y = 150
    for col, card_list in gameDeck.deckPlayBoard.items():
        if len(card_list) == 0:
            card_obj = make_slot(col,[],location_x,location_y)
        else:
            for card in card_list:
                
                if card.button == None:
                    card.button = make_card(card,0,0)
                card.button.set_position((location_x,location_y))
                location_y += 10




def make_column(col_name, card_list,location_x,location_y):
    pass

def make_slot(slot_name,card_list,location_x,location_y):
    pass


pg.init()
SCREEN_SIZE = (800, 600)

pg.display.set_caption('Quick Start')
window_surface = pg.display.set_mode(SCREEN_SIZE)

background = pg.Surface((800, 600))
background.fill(pg.Color('#000000'))

# manager = pi.UIManager((800, 600))
manager = pi.UIManager((800, 600), theme_path="templates/gui/quick_start.json")
# manager.get_theme()

play_button = pi.elements.UIButton(relative_rect=pg.Rect((350, 275), (100, 50)),text='Play Solitare',manager=manager)
menu_buttons = set_menu(['draw','play','autocomplete','quit'])
# play_button.set_position
draw_button, play_cards, autocomplete_button, quit_button = menu_buttons
# play_button.set_position()

clock = pg.time.Clock()
is_running = True

while is_running:
    time_delta = clock.tick(60)/1000.0
    for event in pg.event.get():
        if event.type == pg.QUIT:
            is_running = False

        if event.type == pi.UI_BUTTON_PRESSED:
            if event.ui_element == play_button:
                play_button.disable()
                gameDeck = Solitare_game(pg)
                gameDeck = playing_game(gameDeck)
                
            if event.ui_element == draw_button:
                gameDeck = draw_cards(gameDeck)
        render_all_cards(gameDeck)
        manager.process_events(event)

    manager.update(time_delta)

    window_surface.blit(background, (0, 0))
    manager.draw_ui(window_surface)

    pg.display.update()