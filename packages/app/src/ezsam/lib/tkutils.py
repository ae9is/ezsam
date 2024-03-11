import tkinter as tk
import typing

import customtkinter as ctk

from ezsam.lib.logger import debug


Disableable = typing.TypeVar(
  'Disableable',
  bound=ctk.CTkButton
  | ctk.CTkRadioButton
  | ctk.CTkCheckBox
  | ctk.CTkComboBox
  | ctk.CTkEntry
  | ctk.CTkOptionMenu
  | ctk.CTkSlider
  | ctk.CTkSwitch
  | ctk.CTkTextbox,
)


def create_required_stringvars(number: int, widget: Disableable) -> tk.StringVar:
  """
  Creates a set of variables that on change disable/enable the CTk widget depending if they're all defined.
  """
  tkvars: list[tk.StringVar] = []
  for n in range(number):
    tkvars.append(tk.StringVar(value=''))

  def on_change(name, index, mode):
    all_defined = True
    for value in [var.get() for var in tkvars]:
      debug(f'Value: {value}')
      if not value or len(value) <= 0:
        all_defined = False
        break
    if all_defined:
      debug('All defined, enable widget')
      widget.configure(state='normal')
    else:
      debug('Not all defined, disable widget')
      widget.configure(state='disabled')

  for var in tkvars:
    var.trace_add('write', on_change)
  return tkvars
