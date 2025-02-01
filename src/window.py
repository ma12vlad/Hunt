import random
import string

from gi.repository import Adw
from gi.repository import Gtk, Gdk, Gio, GLib
from .resources import *

@Gtk.Template(resource_path='/io/github/swordpuffin/hunt/window.ui')
class HuntWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'HuntWindow'

    #All relevant items from window.ui that are used here
    grid = Gtk.Template.Child()
    main_box = Gtk.Template.Child()
    frame = Gtk.Template.Child()
    #start_box = Gtk.Template.Child()
    custom_box = Gtk.Template.Child()
    clock = Gtk.Template.Child()
    option_grid = Gtk.Template.Child()
    words_value = Gtk.Template.Child()
    height_value = Gtk.Template.Child()
    length_value = Gtk.Template.Child()
    time_value = Gtk.Template.Child()
    category_list = Gtk.Template.Child()
    search_entry = Gtk.Template.Child()
    active_category = Gtk.Template.Child()
    main_window_content = Gtk.Template.Child()
    sidebar_view = Gtk.Template.Child()
    theme_selector = Gtk.Template.Child()
    game_selector = Gtk.Template.Child()
    custom_settings = Gtk.Template.Child()
    recommended_settings = Gtk.Template.Child()
    gamemode = Gtk.Template.Child()
    gamemode_timed = Gtk.Template.Child()
    gamemode_blitz = Gtk.Template.Child()

    found_words = []
    words = []
    word_buttons = []
    colors = ["red1", "red2", "red3", "orange3", "purple2", "blue1", "blue2", "blue3", "blue4", "blue5", "yellow1", "yellow2", "yellow3", "yellow4", "green1"]

    length = 10
    height = 10
    word_count = 3
    timer = 10
    saved_time = 10

    timed_game = False
    game_over = False
    fast = False

    grid_data = None
    current_word = None
    timer_id = None
    random_key = None
    dialog = None
    divided_timer = None
    selected_category = "RANDOM"


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(css.encode('utf-8')) #fetches the css from resources.py.
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(), css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER
        )

        from .main import HuntApplication

        #Connect each button to its designated function
        HuntApplication.create_action(self, 'reload', self.reload)
        HuntApplication.create_action(self, 'small', self.small)
        HuntApplication.create_action(self, 'medium', self.medium)
        HuntApplication.create_action(self, 'large', self.large)
        HuntApplication.create_action(self, 'custom', self.custom)
        HuntApplication.create_action(self, 'back', self.back)
        HuntApplication.create_action(self, 'custom_start', self.custom_start)
        HuntApplication.create_action(self, 'restart', self.back_to_main_menu)
        self.theme_selector.connect("toggled",  lambda cb: self.on_row_activated(cb, "Random") if cb.get_active() else None)
        self.gamemode.connect("toggled",  lambda cb: self.normal() if cb.get_active() else None)
        self.gamemode_timed.connect("toggled",  lambda cb: self.timed() if cb.get_active() else None)
        self.gamemode_blitz.connect("toggled",  lambda cb: self.speed() if cb.get_active() else None)

        for item in sorted(list(related_words.keys())):
            listEntry = Gtk.ListBoxRow()
            actionEntry = Adw.ActionRow()

            listEntry.set_child(actionEntry)
            actionEntry.set_title(item.capitalize())

            checkbox = Gtk.CheckButton()
            if self.selected_category == actionEntry.get_title().upper():
                checkbox.set_active(True)
            else:
                checkbox.set_active(False)
            checkbox.set_group(self.theme_selector)
            actionEntry.add_suffix(checkbox)
            actionEntry.set_activatable_widget(checkbox)
            checkbox.connect("toggled", lambda cb, actName: self.on_row_activated(cb, actName) if cb.get_active() else None, actionEntry.get_title())

            self.category_list.append(listEntry)
        self.category_list.connect("row-selected", lambda _, row: row.get_child().activate() if row else None)
        self.search_entry.connect("search-changed", self.list_changed)

    def list_changed(self, search_entry):
        # Get the query from the search box and convert it to lowercase
        query = search_entry.get_text().lower()

        # Filter the categories based on the query
        filtered_categories = filter(lambda c: query in c.lower(), related_words.keys())

        # Clear existing rows in the ListBox
        while(self.category_list.get_first_child() is not None):
            self.category_list.remove(self.category_list.get_first_child())

        # Add rows for the filtered categories
        for category in sorted(filtered_categories):
            listEntry = Gtk.ListBoxRow()
            actionEntry = Adw.ActionRow()

            listEntry.set_child(actionEntry)
            actionEntry.set_title(category.capitalize())

            checkbox = Gtk.CheckButton()
            if self.selected_category == actionEntry.get_title().upper():
                checkbox.set_active(True)
            else:
                checkbox.set_active(False)
            checkbox.set_group(self.theme_selector)
            actionEntry.add_suffix(checkbox)
            actionEntry.set_activatable_widget(checkbox)
            checkbox.connect("toggled", lambda cb, actName: self.on_row_activated(cb, actName) if cb.get_active() else None, actionEntry.get_title())

            self.category_list.append(listEntry)

    #Changes the active category depending on what row in self.category_list is selected
    def on_row_activated(self, checkbox, actionName):
        self.selected_category = actionName.upper()
        self.active_category.set_title(actionName)
        self.sidebar_view.pop()

    #back_to_main_menus the game
    def reload(self, action, _):
        if(self.timed_game or self.fast):
            GLib.Source.remove(self.timer_id)
            self.timer = self.saved_time
        self.found_words.clear()
        self.make_grid("clicked", _)

    #No timer and not in blitz mode
    def normal(self):
        self.clock.set_visible(False)
        self.timed_game = False
        self.fast = False

    #With timer, but not blitz
    def timed(self):
        self.clock.set_visible(True)
        self.timed_game = True
        self.fast = False

    #Blitz mode, gives words one at a time, sets the timer at: length of time/# of words
    def speed(self):
        self.clock.set_visible(True)
        self.timed_game = False
        self.fast = True

    #8 x 8 grid, 30 seconds
    def small(self, action, _):
        self.word_count = 5
        self.length = 8
        self.height = 8
        self.timer = self.saved_time = 30
        self.make_grid("activate", _)
        self.grid.set_size_request(400, 400)

    #12 x 12 grid, 60 seconds
    def medium(self, action, _,):
        self.word_count = 8
        self.length = 12
        self.height = 12
        self.timer = self.saved_time = 60
        self.make_grid("activate", _)
        self.grid.set_size_request(600, 600)

    #16 x 16 grid, 80 seconds
    def large(self, action, _):
        self.word_count = 10
        self.length = 16
        self.height = 16
        self.timer = self.saved_time = 80
        self.make_grid("activate", _)
        self.grid.set_size_request(800, 800)

    #Player wants a custom game, display the options menu
    def custom(self, action, _):
        self.game_selector.scroll_to(self.custom_settings, True)

    #Pull back from the custom game options menu to the main menu
    def back(self, action, _):
        self.game_selector.scroll_to(self.recommended_settings, True)

    #Start the game with the custom values set by the player in self.custom_box
    def custom_start(self, action, _):
        self.word_count = int(self.words_value.get_value())
        self.height = int(self.height_value.get_value())
        self.length = int(self.length_value.get_value())
        self.timer = self.saved_time = int(self.time_value.get_value())
        self.make_grid("activate", _)
        self.grid.set_size_request(400 + (self.length - 8) / 2 * 100, 400 + (self.height - 8) / 2 * 100)

    #Back from a running game to the main menu
    def back_to_main_menu(self, action, _):
        if(self.clock.is_visible()):
            GLib.Source.remove(self.timer_id)
        self.found_words.clear()
        self.set_default_size(700, 450)
        self.main_window_content.pop()

    #Function that is the timer of the game. Return false/return true ends or continues the function
    def update(self):
        if(self.timer <= 0.1 and self.grid.is_visible):
            self.end_dialogue()
            return False
        else: #Reduces timer by 0.1 seconds every (obviously) 0.1 seconds
            self.timer -= 0.1
            self.clock.set_label("Time: " + str(round(self.timer, 1)) + "s")
            return True

    #Main function that is the start of the game. As the name suggests, makes the grid for all the letters
    def make_grid(self, action, _):
        self.game_over = False
        if(len(self.found_words) == 0): #Only run at game start, this is here because the blitz mode will call this function to rebuild the grid every time a player finds a new word
            self.make_word_list()
        if(self.timed_game and len(self.found_words) == 0 or self.fast and len(self.found_words) == 0): #Create a timer only on first execution of timed or blitz games
            if(self.timer_id is not None): #Remove the active timer, as if the grid failed to generate, it would create multiple timers at once
                GLib.Source.remove(self.timer_id)
            self.timer_id = GLib.timeout_add(100, self.update, "12")
            self.clock.set_visible(True)
            self.timer = self.saved_time
            if(self.fast):
                self.divided_timer = self.timer / self.word_count
                self.timer = 0 #Reset timer so it will be equal to self.divided_timer on first execution

        self.main_window_content.push_by_tag("game")
        self.grid.set_visible(True)
        while(self.grid.get_child_at(0,0) is not None): #Clear the entire main grid where all the letters are
            self.grid.remove_row(0)
        while(self.frame.get_first_child() is not None): #Clear the GTKListBox that is to the left of the grid
            self.frame.remove(self.frame.get_first_child())

        row = 0
        col = 0
        self.buttons = []
        for i in range(1, self.length * self.height + 1): #Generate the grid with all the buttons in it
            button = Gtk.Button(hexpand=True, vexpand=True)
            self.grid.attach(button, col, row, 1, 1)
            self.buttons.append(button)
            self.grid.add_css_class("frame")
            button.add_css_class("flat")
            button.set_size_request(12, 12)
            button.connect("clicked", self.letter_selected, _, button)

            motion_controller = Gtk.EventControllerMotion() #Uses an event controller for when is hovering over buttons on the grid when they have selected their first letter
            motion_controller.connect("enter", self.on_button_hovered)
            button.add_controller(motion_controller)

            import os
            locale = os.environ.get("LANG", "C")

            if(locale not in letters.keys()): #Use the correct alphabet for the user's language
                button.set_label(random.choice(letters['en_US.UTF-8'])) #defaults to English if not defined in resources.py
            else:
                button.set_label(random.choice(letters[locale]))

            col += 1
            if(i % self.length == 0):
                col = 0
                row += 1

        if(not self.fast):
            #Add each word the the GTKListBox, and place each word in the grid. Does not run in blitz mode because only one word needs to be in the grid and in the GTKListBox at a time
            used_words = set()
            for word in self.words:
                label = Gtk.Label()
                label.set_label(word)
                label.set_margin_bottom(14)
                label.set_margin_top(14)
                self.place_word_in_grid(word)
                used_words.add(label.get_label())
                #This is needed because sometimes words would be added to self.frame that are not in self.words, or words that are in self.frame are placed in multiple times
                #Occurs with words that fail to be placed
                if(label.get_label().lower() in related_words[self.random_key] and all(child.get_first_child().get_title().upper() != label.get_label() for child in self.frame)):
                    listbox = Gtk.ListBoxRow()
                    listbox.set_selectable(False)
                    listbox.set_activatable(False)
                    actionRow = Adw.ActionRow()
                    checkbutton = Gtk.CheckButton()

                    listbox.set_child(actionRow)
                    actionRow.add_suffix(checkbutton)
                    checkbutton.set_visible(False)

                    actionRow.set_title(label.get_label().capitalize())

                    self.frame.append(listbox)
        else: #Add self.divided_timer to however much it was before, and place the one new word into the grid as well as onto the GTKListBox.
            self.timer += self.divided_timer
            self.clock.set_label(str(round(self.timer, 1)))
            self.frame.append(Gtk.Label(label=self.words[len(self.found_words)], margin_bottom=14, margin_top=14))
            self.place_word_in_grid(self.words[len(self.found_words)])

    def make_word_list(self): #Creates the list of words for the player to search for.
        self.words.clear()
        if(self.selected_category == "RANDOM"):
            self.random_key = random.choice(list(related_words.keys()))
            value = related_words[self.random_key]
        else:
            value = related_words[self.selected_category]
            self.random_key = self.selected_category #For the end dialog when stating the category
        self.grid_data = [[' ' for _ in range(self.length)] for _ in range(self.height)]
        for i in range(self.word_count):
            self.words.append(value[i].upper())
        random.shuffle(self.words)

    # Places the words in self.words into the grid in random places and in random directions
    def place_word_in_grid(self, word):
        placed = False
        attempts = 0
        max_attempts = 200  # Maximum attempts to prevent infinite loop

        while(not placed and attempts < max_attempts):
            attempts += 1
            direction = random.choice(['horizontal', 'vertical', 'diagonal'])
            row = random.randint(0, self.height - 1)  # Random start position
            col = random.randint(0, self.length - 1)
            # Check horizontal placement with intersection allowed
            if(direction == 'horizontal' and col + len(word) <= self.length):
                if(all(self.grid_data[row][col + i] == ' ' or self.grid_data[row][col + i] == word[i].upper() for i in range(len(word)))):
                    for i in range(len(word)):
                        self.grid_data[row][col + i] = word[i].upper()
                        self.buttons[row * self.length + col + i].set_label(word[i].upper())
                    placed = True

            # Check vertical placement with intersection allowed
            elif(direction == 'vertical' and row + len(word) <= self.height):
                if(all(self.grid_data[row + i][col] == ' ' or self.grid_data[row + i][col] == word[i].upper() for i in range(len(word)))):
                    for i in range(len(word)):
                        self.grid_data[row + i][col] = word[i].upper()
                        self.buttons[(row + i) * self.length + col].set_label(word[i].upper())
                    placed = True

            # Check diagonal placement with intersection allowed
            elif(direction == 'diagonal' and row + len(word) <= self.height and col + len(word) <= self.length):
                if(all(self.grid_data[row + i][col + i] == ' ' or self.grid_data[row + i][col + i] == word[i].upper() for i in range(len(word)))):
                    for i in range(len(word)):
                        self.grid_data[row + i][col + i] = word[i].upper()  # Use uppercase for consistency
                        self.buttons[(row + i) * self.length + (col + i)].set_label(word[i].upper())
                    placed = True

        if(not placed):
            print(f"Failed to place word '{word}' after {max_attempts} attempts.")
            self.make_grid("activate", _)

    #Fetches the word in between the two selected buttons. Also checks if the word that is made is one of words the player is supposed to find
    def letter_selected(self, action, _, button):
        if(not self.current_word and self.game_over == False):
            self.current_word = button
            button.add_css_class("green_button")
        elif(self.current_word and self.game_over == False):
            first_pos = self.grid.query_child(self.current_word) #Grab the position of the first selected button
            second_pos = self.grid.query_child(button) #Grab the position of the second selected button
            word = self.get_selected_word(first_pos, second_pos) #Find the word between the two

            if(word in self.words and word not in self.found_words):
                for child in self.frame:
                    if(child.get_first_child().get_title().upper() == word):
                        child.get_first_child().add_css_class("success")
                        child.get_first_child().set_sensitive(False)
                        child.get_first_child().set_title(f"<s>{child.get_first_child().get_title()}</s>")

                        checkIcon = Gtk.CheckButton()
                        checkIcon.set_active(True)
                        checkIcon.add_css_class("selection-mode")
                        child.get_first_child().add_suffix(checkIcon)
                color = random.choice(self.colors)
                for child in self.word_buttons:
                    child.remove_css_class("green_button")
                    for css_classes in child.get_css_classes():
                        # Remove the color class if it is at an intersection point to that it always uses the most recently added color, sometimes it ignores the newer color.
                        if(css_classes in self.colors):
                            child.remove_css_class(css_classes)
                    child.add_css_class(f"{color}")
                self.found_words.append(word)
                if(len(self.found_words) == self.word_count): #End the game if the player has found all the words
                    self.end_dialogue()
                    return
                if(self.fast):
                    self.make_grid("activate", _)
            else:
                self.current_word.remove_css_class("green_button")
                for child in self.word_buttons:
                    child.remove_css_class("green_button")
            self.current_word = None

    #This function runs when the player selects two letters, and then creates the word from their location
    def get_selected_word(self, first_pos, second_pos):
        row1, col1 = first_pos[1], first_pos[0]
        row2, col2 = second_pos[1], second_pos[0]
        row_min, row_max = sorted([row1, row2])
        col_min, col_max = sorted([col1, col2])
        word = ""

        #If the selected buttons are in the same row
        if(row1 == row2):
            for col in range(col_min, col_max + 1):
                child = self.grid.get_child_at(col, row1)
                if(child):
                    child.add_css_class("green_button")
                    self.word_buttons.append(child)
                    word += child.get_label()
        #If the two selected buttons are in the same column
        elif(col1 == col2):
            for row in range(row_min, row_max + 1):
                child = self.grid.get_child_at(col1, row)
                if(child):
                    child.add_css_class("green_button")
                    self.word_buttons.append(child)
                    word += child.get_label()
        #If the two selected buttons are diagonal to eachother
        elif(abs(row1 - row2) == abs(col1 - col2)):
            row_step = 1 if row2 > row1 else -1
            col_step = 1 if col2 > col1 else -1
            for step in range(abs(row2 - row1) + 1):
                child = self.grid.get_child_at(col1 + step * col_step, row1 + step * row_step)
                if(child):
                    child.add_css_class("green_button")
                    self.word_buttons.append(child)
                    word += child.get_label()
        return word


    def on_button_hovered(self, controller, event, _):
        if(not self.current_word):
            return  # No starting button selected yet

        hovered_button = controller.get_widget()
        first_pos = self.grid.query_child(self.current_word)
        second_pos = self.grid.query_child(hovered_button)

        if(not first_pos or not second_pos):
            return  # Ensure positions are valid

        # Clear previous highlights
        for button in self.word_buttons:
            if(button is not self.current_word):
                button.remove_css_class("green_button")
        self.word_buttons = []

        # Get all buttons along the path
        path_buttons = self.get_path_buttons(first_pos, second_pos)

        # Highlight the path
        for button in path_buttons:
            button.add_css_class("green_button")
            self.word_buttons.append(button)

    #Grab all the buttons between the two selected ones
    def get_path_buttons(self, first_pos, second_pos):
        row1, col1 = first_pos[1], first_pos[0]
        row2, col2 = second_pos[1], second_pos[0]
        row_min, row_max = sorted([row1, row2])
        col_min, col_max = sorted([col1, col2])
        path_buttons = []

        # Horizontal path
        if(row1 == row2):
            for col in range(col_min, col_max + 1):
                button = self.grid.get_child_at(col, row1)
                if(button):
                    path_buttons.append(button)
        # Vertical path
        elif(col1 == col2):
            for row in range(row_min, row_max + 1):
                button = self.grid.get_child_at(col1, row)
                if(button):
                    path_buttons.append(button)
        # Diagonal path
        elif(abs(row1 - row2) == abs(col1 - col2)):
            row_step = 1 if row2 > row1 else - 1 #Either moves upwards or downwards depending on the difference in location
            col_step = 1 if col2 > col1 else - 1
            for step in range(abs(row2 - row1) + 1):
                button = self.grid.get_child_at(col1 + step * col_step, row1 + step * row_step) #I don't understand how this works, but it does
                if(button):
                    path_buttons.append(button)

        return path_buttons

    #Dialog that runs when the player has found all the words or run out of time.
    def end_dialogue(self):
        game_over = True
        #If the player back_to_main_menus the game, self.current_word gets set to the first button and returns errors. Don't know why it happens, so this is the fix ¯\_(ツ)_/¯
        self.current_word = None
        if(self.clock.is_visible()):
            GLib.Source.remove(self.timer_id)
        self.dialog = Gtk.Dialog(title=(_("Game Over")), transient_for=self, modal=True)
        self.dialog.set_default_size(300, 200)
        self.dialog.set_decorated(False)

        # Apply the title-4 CSS class to make the text bigger
        self.dialog.get_style_context().add_class("title-4")

        # Dialog content area
        content_area = self.dialog.get_content_area()

        # Create a box to vertically center the content
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        vbox.set_valign(Gtk.Align.CENTER)
        vbox.set_halign(Gtk.Align.CENTER)
        content_area.append(vbox)

        # Create a label to display the end-game message
        message = Gtk.Label(
            label=f"\nCategory: {self.random_key}\n\nGrid size: {self.length} x {self.height} tiles\n\nTotal words:  {self.word_count}\n# of words found:  {len(self.found_words)}",
            halign=Gtk.Align.CENTER,
            valign=Gtk.Align.CENTER,
            margin_start=30,
            margin_end=30,
            justify=Gtk.Justification.CENTER
        )
        vbox.append(message)

        # Create a button box to center the buttons
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        button_box.set_halign(Gtk.Align.CENTER)

        # Add buttons to the button box
        new_game_button = Gtk.Button(label=(_("New Game")))
        new_game_button.connect("clicked", lambda _: self.back_to_main_menu_game("activate", _))
        button_box.append(new_game_button)

        close_button = Gtk.Button(label=(_("Close")))
        close_button.connect("clicked", lambda _: self.close_end_dialogue("activate", _))
        button_box.append(close_button)
        button_box.set_margin_bottom(15)

        # Add the button box to the vbox
        vbox.append(button_box)
        self.dialog.show()
        self.found_words.clear()

    #back_to_main_menu the game when it ends
    def back_to_main_menu_game(self, action, _):
        self.dialog.destroy()
        self.make_grid("activate", _)

    #Destroy the dialogue so that the player can see the grid
    def close_end_dialogue(self, action, _):
        self.dialog.destroy()

