import random
import string
from gi.repository import Adw
from gi.repository import Gtk, Gdk, Gio
from .words import related_words

@Gtk.Template(resource_path='/io/github/swordpuffin/hunt/window.ui')
class HuntWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'HuntWindow'

    grid = Gtk.Template.Child()
    frame = Gtk.Template.Child()
    frame_label = Gtk.Template.Child()
    grid_size = 18
    words = []
    colors = ["red1", "red2", "red3", "red4", "red5", "blue1", "blue2", "blue3", "blue4", "blue5", "yellow1", "yellow2", "yellow3", "yellow4", "yellow5"]
    word_buttons = []

    grid_data = None
    current_word = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        css_provider = Gtk.CssProvider()
        css_provider.load_from_path("/app/share/hunt/hunt/styles.css")
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(), css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER
        )

        reload_action = Gio.SimpleAction(name="reload")
        reload_action.connect("activate", self.make_grid)
        self.add_action(reload_action)
        self.make_grid("activate", _)

    def make_grid(self, action, _):
        self.words.clear()
        random_key = random.choice(list(related_words.keys()))
        random_value = related_words[random_key]
        self.grid_data = [[' ' for _ in range(self.grid_size)] for _ in range(self.grid_size)]

        for i in range(10):
            self.words.append(random_value[i].upper())

        while(True):
            if(self.grid.get_child_at(0,0) != None):
                self.grid.remove_row(0)
            else:
                break
        self.grid.set_row_spacing(0)
        self.grid.set_column_spacing(0)
        row = 0
        col = 0
        self.buttons = []
        length = self.grid_size
        height = self.grid_size

        for i in range(1, length * height + 1):
            button = Gtk.Button()
            button.set_hexpand(True)
            button.set_vexpand(True)
            self.grid.attach(button, col, row, 1, 1)
            self.buttons.append(button)
            self.grid.add_css_class("frame")
            button.add_css_class("flat")
            button.connect("clicked", self.letter_selected, _, button)

            motion_controller = Gtk.EventControllerMotion()
            motion_controller.connect("enter", self.on_button_hovered)
            button.add_controller(motion_controller)

            button.set_label(random.choice(string.ascii_uppercase))
            col += 1
            if i % length == 0:
                col = 0
                row += 1

        while(self.frame.get_first_child() != None):
            self.frame.remove(self.frame.get_first_child())
        for word in self.words:
            self.place_word_in_grid(word)
            label = Gtk.Label()
            label.set_label(word)
            label.set_margin_bottom(14)
            label.set_margin_top(14)
            self.frame.append(label)
        self.frame.remove(self.frame.get_first_child())

    def place_word_in_grid(self, word):
        placed = False
        while(not placed):
            direction = random.choice(['horizontal', 'vertical', 'diagonal'])
            row = random.randint(0, self.grid_size - 1)
            col = random.randint(0, self.grid_size - 1)

            if (direction == 'horizontal' and col + len(word) <= self.grid_size and all(self.grid_data[row][col + i] == ' ' for i in range(len(word)))):
                for i in range(len(word)):
                    self.grid_data[row][col + i] = word[i].upper()
                    self.buttons[row * self.grid_size + col + i].set_label(word[i])
                placed = True

            elif (direction == 'vertical' and row + len(word) <= self.grid_size and all(self.grid_data[row + i][col] == ' ' for i in range(len(word)))):
                for i in range(len(word)):
                    self.grid_data[row + i][col] = word[i].upper()
                    self.buttons[(row + i) * self.grid_size + col].set_label(word[i])
                placed = True

            elif (direction == 'diagonal' and row + len(word) <= self.grid_size and col + len(word) <= self.grid_size and all(self.grid_data[row + i][col + i] == ' ' for i in range(len(word)))):
                for i in range(len(word)):
                    self.grid_data[row + i][col + i] = word[i].lower()
                    self.buttons[(row + i) * self.grid_size + (col + i)].set_label(word[i])
                placed = True

    def letter_selected(self, action, _, button):
        if(not self.current_word):
            self.current_word = button
            button.add_css_class("green_button")
        else:
            first_pos = self.grid.query_child(self.current_word)
            second_pos = self.grid.query_child(button)
            word = self.get_selected_word(first_pos, second_pos)

            if(word in self.words):
                for child in self.frame:
                    if(child.get_first_child().get_label() == word):
                        child.add_css_class("green_button")
                color = random.choice(self.colors)
                for child in self.word_buttons:
                    child.remove_css_class("green_button")
                    child.add_css_class(f"{color}")
            else:
                self.current_word.remove_css_class("green_button")
                for child in self.word_buttons:
                    child.remove_css_class("green_button")
            self.word_buttons = []
            self.current_word = None

    def get_selected_word(self, first_pos, second_pos):
        row1, col1 = first_pos[1], first_pos[0]
        row2, col2 = second_pos[1], second_pos[0]
        row_min, row_max = sorted([row1, row2])
        col_min, col_max = sorted([col1, col2])
        word = ""

        if(row1 == row2):
            for col in range(col_min, col_max + 1):
                child = self.grid.get_child_at(col, row1)
                if(child):
                    child.add_css_class("green_button")
                    self.word_buttons.append(child)
                    word += child.get_label()
        elif(col1 == col2):
            for row in range(row_min, row_max + 1):
                child = self.grid.get_child_at(col1, row)
                if(child):
                    child.add_css_class("green_button")
                    self.word_buttons.append(child)
                    word += child.get_label()
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
            if(button != self.current_word):
                button.remove_css_class("green_button")
        self.word_buttons = []

        # Get all buttons along the path
        path_buttons = self.get_path_buttons(first_pos, second_pos)

        # Highlight the path
        for button in path_buttons:
            button.add_css_class("green_button")
            self.word_buttons.append(button)

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
        elif abs(row1 - row2) == abs(col1 - col2):
            row_step = 1 if row2 > row1 else -1
            col_step = 1 if col2 > col1 else -1
            for step in range(abs(row2 - row1) + 1):
                button = self.grid.get_child_at(col1 + step * col_step, row1 + step * row_step)
                if(button):
                    path_buttons.append(button)

        return path_buttons

