import random
import string
from gi.repository import Adw
from gi.repository import Gtk, Gdk
from .words import related_words

@Gtk.Template(resource_path='/io/github/swordpuffin/hunt/window.ui')
class HuntWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'HuntWindow'

    grid = Gtk.Template.Child()
    frame = Gtk.Template.Child()
    frame_label = Gtk.Template.Child()
    grid_size = 18
    words = []
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

        random_key = random.choice(list(related_words.keys()))
        random_value = related_words[random_key]

        for i in range(10):
            self.words.append(random_value[i].upper())

        self.grid_data = [[' ' for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        self.make_grid(self.grid_size, self.grid_size)

    def make_grid(self, length, height):
        self.grid.set_row_spacing(0)
        self.grid.set_column_spacing(0)
        row = 0
        col = 0
        self.buttons = []

        for i in range(1, length * height + 1):
            button = Gtk.Button()
            button.set_hexpand(True)
            button.set_vexpand(True)
            self.grid.attach(button, col, row, 1, 1)
            self.buttons.append(button)
            self.grid.add_css_class("frame")
            button.add_css_class("flat")
            button.connect("clicked", self.letter_selected, _, button)
            button.connect("notify::hover", self.hover, button)
            button.set_label(random.choice(string.ascii_uppercase))
            col += 1
            if i % length == 0:
                col = 0
                row += 1

        for word in self.words:
            self.place_word_in_grid(word)
            label = Gtk.Label()
            label.set_label(word)
            label.set_margin_bottom(7)
            label.set_margin_top(7)
            self.frame.append(label)
        self.frame.remove(self.frame.get_first_child())

    def place_word_in_grid(self, word):
        placed = False
        while not placed:
            direction = random.choice(['horizontal', 'vertical', 'diagonal'])
            row = random.randint(0, self.grid_size - 1)
            col = random.randint(0, self.grid_size - 1)

            if (direction == 'horizontal' and col + len(word) <= self.grid_size and all(self.grid_data[row][col + i] == ' ' for i in range(len(word)))):
                for i in range(len(word)):
                    self.grid_data[row][col + i] = word[i]
                    self.buttons[row * self.grid_size + col + i].set_label(word[i])
                placed = True

            elif (direction == 'vertical' and row + len(word) <= self.grid_size and all(self.grid_data[row + i][col] == ' ' for i in range(len(word)))):
                for i in range(len(word)):
                    self.grid_data[row + i][col] = word[i]
                    self.buttons[(row + i) * self.grid_size + col].set_label(word[i])
                placed = True

            elif (direction == 'diagonal' and row + len(word) <= self.grid_size and col + len(word) <= self.grid_size and all(self.grid_data[row + i][col + i] == ' ' for i in range(len(word)))):
                for i in range(len(word)):
                    self.grid_data[row + i][col + i] = word[i]
                    self.buttons[(row + i) * self.grid_size + (col + i)].set_label(word[i])
                placed = True

    def letter_selected(self, action, _, button):
        if not self.current_word:
            self.current_word = button
            button.add_css_class("green_button")
            button.set_sensitive(False)
        else:
            first_pos = self.grid.query_child(self.current_word)
            second_pos = self.grid.query_child(button)
            word = self.get_selected_word(first_pos, second_pos)

            self.current_word.set_sensitive(True)
            button.set_sensitive(True)

            if(word in self.words):
                print("Found a word:", word)
                for child in self.frame:
                    if(child.get_first_child().get_label() == word):
                        child.add_css_class("green_button")
            else:
                print("Not a valid word:", word)
                self.current_word.remove_css_class("green_button")
                for child in self.word_buttons:
                    child.remove_css_class("green_button")
            self.word_buttons = []
            self.current_word = None

    def hover(self, button):
        print("hovered")
        if(self.current_word):
            button.add_css_class("green_button")

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

