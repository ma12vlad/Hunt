# main.py
#
# Copyright 2025 Nathan Perlman
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later

import sys

import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Gio, Adw
from .window import HuntWindow

class HuntApplication(Adw.Application):
    def __init__(self):
        super().__init__(application_id='io.github.swordpuffin.hunt',
                         flags=Gio.ApplicationFlags.DEFAULT_FLAGS)
        self.create_action('quit', lambda *_: self.quit(), ['<primary>q'])
        self.create_action('about', self.on_about_action)
        self.create_action('help', self.help_action, ['<primary>h'])

    def do_activate(self):
        win = self.props.active_window
        if(not win):
            win = HuntWindow(application=self)
        win.present()

    def on_about_action(self, *args):
        about = Adw.AboutDialog(application_name='Hunt',
                                application_icon='io.github.swordpuffin.hunt',
                                developer_name='Nathan Perlman',
                                version='1.0.5',
                                issue_url='https://github.com/SwordPuffin/Hunt/issues',
                                developers=['Nathan Perlman'],
                                copyright='© 2025 Nathan Perlman')
        about.present(self.props.active_window)

    def help_action(self, *args):
        dialog = Gtk.MessageDialog(
            transient_for=HuntWindow(),
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.CLOSE,
        )
        dialog.get_message_area().get_first_child().set_markup(_("<span size=\"large\"><big><b>How to play:</b></big>\n______________________________________________________________________\n\nTo start, select one of the four grid sizes: \n\n○  8 × 8 board with 5 words \n○  12 × 12 board with 8 words \n○  16 × 16 board with 10 words \n○  Custom board, where you choose the size and the number of words\n\nTo choose a term from the grid, click the first and the last letter of the word you want, and all letters in between the two is what Hunt will take as selected.\n\nTo win, you must find all words that are hidden in the grid.\n\nAvoid minimizing the grid size, and maximizing the word count, as it can occasionally lead to game crashes if some words are unable to be placed.\n\n</span><span size=\"large\"><big><b>Blitz Mode:</b></big>\n______________________________________________________________________\n\nBlitz mode reduces the amount of time the player has per word, and words in that category are given one at a time.\n\nFor example, with 60 seconds for 5 words, each word would only be available for 12 seconds (60 ÷ 5 = 12) before game over.\n\nWhenever a word is found, the amount of time the game started with gets added to the remaining time the player has. \n\n</span><span size=\"large\"><big><b>Get Involved:</b></big>\n______________________________________________________________________\n\nEveryone is welcome to participate in Hunt's development, whether by improving the game's code, or adding more language support.</span>"))
        dialog.get_message_area().get_first_child().set_justify(Gtk.Justification.LEFT)
        link = Gtk.LinkButton.new_with_label(
            uri="https://github.com/SwordPuffin/Hunt",
        )
        link.get_first_child().set_markup(_("<span size=\"large\"><b>You can contribute here</b></span>"))
        dialog.get_message_area().append(link)
        dialog.present()
        dialog.connect("response", self.response)

    def response(self, dialog, response_id):
        dialog.close()

    def create_action(self, name, callback, shortcuts=None):
        action = Gio.SimpleAction.new(name, None)
        action.connect("activate", callback)
        self.add_action(action)
        if(shortcuts):
            self.set_accels_for_action(f"app.{name}", shortcuts)

def main(version):
    app = HuntApplication()
    return app.run(sys.argv)
