from prompt_toolkit.completion import Completion, Completer
from pprint import pprint
#!/usr/bin/env python3
import os
from prompt_toolkit.lexers import PygmentsLexer
from pygments.lexers.shell import BashSessionLexer, BashLexer
from prompt_toolkit import PromptSession
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.styles import style_from_pygments_cls, Style
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.shortcuts import CompleteStyle
import re
import os
import shutil


with open('./ord_soumet_help.txt', 'r') as f:
    help_text = f.read()

help_lines = help_text.splitlines()

def read_help_line(line):
    words = line.split()
    return {
        'type': words[0],
        'option': words[1],
        'value': words[2],
        'help': ' '.join(words[3:])
    }

help_data = [read_help_line(l) for l in help_lines]

help_dict = {
    help_datum['option']: help_datum
    for help_datum in help_data
}


class OrdSoumetOptionCompleter(Completer):
    def __init__(self):
        self.help_dict = help_dict
    def get_completions(self, document, complete_event):
        text = document.text_before_cursor
        words = text.split()
        word = document.get_word_before_cursor(pattern=re.compile(r'([-a-zA-Z0-9_/]+|[^a-zA-Z0-9_\s/]+)'))
        # word = document.get_word_before_cursor()
        for option in self.help_dict:
            if option.startswith(word):
                yield Completion(
                    option,
                    start_position=-len(word),
                    display=f'{option} : {self.help_dict[option]["help"]}'
                )

def make_prompt_session():
    # This if I want the help to be displayed
    ord_soumet_completer = OrdSoumetOptionCompleter()
    prompt_style = Style.from_dict({
        'prompt': '#00aa00'
    })
    prompt_string = [
        ('class:username', 'ord_soumet > ')
    ]
    prompt_sesh = PromptSession(
        history=FileHistory(os.path.expanduser('~/.ord_soumet_shell_history')),
        auto_suggest=AutoSuggestFromHistory(),
        completer=ord_soumet_completer,
        reserve_space_for_menu=8,
        lexer=PygmentsLexer(BashLexer),
        style=prompt_style,
        complete_style=CompleteStyle.COLUMN
    )
    bindings = KeyBindings()
    @bindings.add('c-j')
    def _(event):
        event.current_buffer.complete_next()
    @bindings.add('c-k')
    def _(event):
        event.current_buffer.complete_previous()

    def prompt():
        return prompt_sesh.prompt([('class:username', 'ord_soumet > ')])

    return prompt

class REPLDoneError(Exception):
    pass

def read_command_line(prompt):
    try:
        return prompt()
    except EOFError as e:
        raise REPLDoneError("EOF entered")

def REPL():
    prompt = make_prompt_session()
    while True:
        try:
            result = read_command_line(prompt).split()
            print(f'PROMPT FRAMEWORK RETURNED : {result}')
        except REPLDoneError:
            break

try:
    REPL()
except KeyboardInterrupt or EOFError as e:
    quit()