import random
import string
# import enchant
from gi.repository import Adw
from gi.repository import Gtk

@Gtk.Template(resource_path='/io/github/swordpuffin/hunt/window.ui')
class HuntWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'HuntWindow'

    grid = Gtk.Template.Child()
    grid_size = 10
    words = ['PYTHON', 'GTK', 'GRID', 'CODE', 'SEARCH']
    grid_data = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.grid_data = [[random.choice(string.ascii_uppercase) for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        self.make_grid(10, 10)

    def make_grid(self, length, height):
        self.grid.set_row_spacing(15)
        self.grid.set_column_spacing(15)
        row = 0
        col = 0
        self.buttons = []

        for i in range(1, length * height + 1):
            button = Gtk.Button()
            button.set_hexpand(True)
            button.set_vexpand(True)
            self.grid.attach(button, col, row, 1, 1)
            self.buttons.append(button)
            button.set_label(random.choice(string.ascii_uppercase))
            col += 1
            if i % length == 0:
                col = 0
                row += 1

        for word in self.words:
            self.place_word_in_grid(word)

    def place_word_in_grid(self, word):
        placed = False

        while(not placed):
            direction = random.choice(['horizontal', 'vertical', 'diagonal'])
            row = random.randint(0, self.grid_size - 1)
            col = random.randint(0, self.grid_size - 1)

            if(direction == 'horizontal' and col + len(word) <= self.grid_size):
                for i in range(len(word)):
                    self.grid_data[row][col + i] = word[i]
                    self.buttons[row * self.grid_size + col + i].set_label(word[i])
                    self.buttons[row * self.grid_size + col + i].add_css_class("destructive-action")
                placed = True

            elif(direction == 'vertical' and row + len(word) <= self.grid_size):
                for i in range(len(word)):
                    self.grid_data[row + i][col] = word[i]
                    self.buttons[(row + i) * self.grid_size + col].set_label(word[i])
                    self.buttons[(row + i) * self.grid_size + col].add_css_class("destructive-action")
                placed = True

            elif(direction == 'diagonal' and row + len(word) <= self.grid_size and col + len(word) <= self.grid_size):
                for i in range(len(word)):
                    self.grid_data[row + i][col + i] = word[i]
                    self.buttons[(row + i) * self.grid_size + (col + i)].set_label(word[i])
                    self.buttons[(row + i) * self.grid_size + (col + i)].add_css_class("destructive-action")
                placed = True



