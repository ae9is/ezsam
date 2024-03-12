import sys
import threading
import tkinter as tk

import PIL as pil
import customtkinter as ctk
import tkinterdnd2 as dnd

from ezsam.lib.logger import debug, log
from ezsam.lib.tkutils import create_required_stringvars
from ezsam.lib.path import resource_path
from ezsam.lib.preview import get_preview_image
from ezsam.gui.config import (
  DEFAULT_DEBUG,
  DEFAULT_MODEL,
  WIDTH,
  HEIGHT,
  PREVIEW_WIDTH,
  PREVIEW_HEIGHT,
  APPEARANCE_MODE,
  COLOR_THEME,
)
from ezsam.gui.models import HQ_MODEL_PREFIX, MODEL_NAME_TO_TYPE


class App(ctk.CTk, dnd.TkinterDnD.DnDWrapper):
  NAME = 'ezsam'
  WIDTH = WIDTH
  HEIGHT = HEIGHT
  PREVIEW_WIDTH = PREVIEW_WIDTH
  PREVIEW_HEIGHT = PREVIEW_HEIGHT

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.TkdndVersion = dnd.TkinterDnD._require(self)
    self.setup()
    self.layout()
    self.create_widgets()

  def setup(self):
    self.title(App.NAME)
    self.geometry(f'{App.WIDTH}x{App.HEIGHT}')
    self.minsize(App.WIDTH, App.HEIGHT)
    self.protocol('WM_DELETE_WINDOW', self.quit)
    if sys.platform == 'darwin':
      self.bind('<Command-q>', self.quit)
      self.bind('<Command-w>', self.quit)
      self.createcommand('tk::mac::Quit', self.quit)
    else:
      self.bind('<Control-Key-q>', self.quit)
      self.bind('<Control-Key-w>', self.quit)

  def start(self):
    self.mainloop()

  def quit(self, *args, **kwargs):
    self.destroy()

  def layout(self):
    self.columnconfigure(0, weight=1)
    self.rowconfigure(0, weight=1)

  def create_widgets(self):
    preview_frame = ctk.CTkFrame(self, fg_color='transparent')
    controls_frame = ctk.CTkFrame(self, corner_radius=0)
    self.p = preview_frame
    self.c = controls_frame

    self.debug = tk.BooleanVar(value=DEFAULT_DEBUG)
    self.model = tk.StringVar(value=DEFAULT_MODEL)
    self.prompts_neg = tk.StringVar(value='')

    # The run button is disabled if all the variables aren't defined
    self.run_button = ctk.CTkButton(self.c, text='Run', command=self.on_run, state='disabled')
    self.prompts, self.path = create_required_stringvars(number=2, widget=self.run_button)

    self.model_label = ctk.CTkLabel(self.c, text='Model')
    model_names = [m for m in MODEL_NAME_TO_TYPE]
    self.model_menu = ctk.CTkOptionMenu(self.c, values=model_names, variable=self.model, command=self.on_select_model)
    self.prompts_label = ctk.CTkLabel(self.c, text='Prompts')
    self.prompts_label_neg = ctk.CTkLabel(self.c, text='Negative Prompts')
    self.prompts_entry = ctk.CTkEntry(self.c, textvariable=self.prompts)
    self.prompts_neg = ctk.CTkEntry(self.c)
    self.debug_checkbox = ctk.CTkCheckBox(self.c, text='Debug', variable=self.debug, onvalue=True)

    # Note: CTkLabel doesn't respect text_color_disabled in theme right now
    # ref: https://github.com/TomSchimansky/CustomTkinter/issues/1837
    self.path_label = ctk.CTkLabel(self.p, text='', state='disabled')
    self.preview = ctk.CTkLabel(self.p, text='Drag and drop an input file to preview')
    self.preview.drop_target_register(dnd.DND_ALL)
    self.preview.dnd_bind('<<Drop>>', self.on_drop)

    self.p.grid(row=0, column=0)
    self.p.rowconfigure(0, weight=10)
    self.p.rowconfigure(1, weight=1)
    self.preview.grid(row=0, column=0, sticky=tk.NSEW, padx=0, pady=0)

    self.c.grid(row=1, column=0, sticky=tk.EW)
    self.c.columnconfigure(0, weight=1)
    self.c.columnconfigure(1, weight=10)
    self.prompts_label.grid(row=3, column=0, sticky=tk.E, padx=10, pady=10)
    self.prompts_entry.grid(row=3, column=1, sticky=tk.EW, padx=10, pady=10)
    self.prompts_label_neg.grid(row=4, column=0, sticky=tk.E, padx=10, pady=10)
    self.prompts_neg.grid(row=4, column=1, sticky=tk.EW, padx=10, pady=10)
    self.model_label.grid(row=5, column=0, sticky=tk.E, padx=10, pady=10)
    self.model_menu.grid(row=5, column=1, sticky=tk.EW, padx=10, pady=10)
    self.debug_checkbox.grid(row=6, column=0, sticky=tk.E, padx=10, pady=10)
    self.run_button.grid(row=6, column=1, sticky=tk.EW, padx=10, pady=10)

  def place_path_label(self):
    self.path_label.grid(row=1, column=0, sticky=tk.EW, padx=10, pady=(10, 10))

  def on_select_model(self, model_name):
    log(f'Selected model: {model_name}')

  def on_run(self):
    self.run_button.configure(state='disabled')
    self.config(cursor='watch')
    self.update()
    log('Running job ...')
    model_type = MODEL_NAME_TO_TYPE[self.model.get()]
    model_arg = model_type.replace(HQ_MODEL_PREFIX, '')
    job_args = [
      self.path.get(),
      '--prompts', self.prompts.get(),
      '--model', model_arg,
    ]
    nprompts = self.prompts_neg.get()
    if nprompts and len(nprompts) > 0:
      job_args.extend(['--nprompts', nprompts])
    if HQ_MODEL_PREFIX in model_type:
      job_args.append('--hq')
    if self.debug.get():
      job_args.append('--debug')
    thread = threading.Thread(target=self.job, args=job_args)
    thread.start()

  def job(self, *args):
    from ezsam.cli.app import main as ezsam_job
    
    debug(f'Calling ezsam{args} ...')
    ezsam_job(args)
    self.on_job_end()

  def on_job_end(self):
    log('Job done!')
    self.config(cursor='')
    # Force update before activating run button again to dispose of any queued click events while button disabled
    self.update()
    self.run_button.configure(state='normal')

  def on_choose_file(self):
    ctk.filedialog.askdirectory()

  def on_drop(self, event):
    path = event.data
    self.path.set(path)
    self.path_label.configure(text=path)
    self.place_path_label()
    try:
      preview_image: pil.Image.Image = get_preview_image(path, App.PREVIEW_WIDTH, App.PREVIEW_HEIGHT)
      ctk_preview = ctk.CTkImage(dark_image=preview_image, size=(App.PREVIEW_WIDTH, App.PREVIEW_HEIGHT))
      self.preview.configure(text='')
      self.preview.configure(image=ctk_preview)
    except Exception as err:
      log(err)


def main(argv=None):
  ctk.set_appearance_mode(APPEARANCE_MODE)
  ctk.set_default_color_theme(resource_path(COLOR_THEME))
  app = App()
  app.start()


if __name__ == '__main__':
  main(sys.argv)
