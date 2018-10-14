# Python 3.7+, relies on the new dict behavior

import os, sys
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from tkinter import ttk
from json import dump, load
from copy import copy

import grid_info

default_level_size = {
    "width": 10,
    "height": 2,
}
default_spawn_coords = {
    "x": 1,
    "y": 1,
}
default_tests = []
default_allowed_functions = {
    "up": True,
    "down": True,
    "left": True,
    "right": True,

    "column": True,
    "line": True,

    "on_painted": True,
    "paint": True,

    "grab": True,
    "release": True,

    "read_number": True,
    "write_number": True,

    "on_item": True,
    "on_hole": True,

    "on_triangle": True,
    "on_square": True,
    "on_circle": True,

    "on_filled_shape": True,
    "on_dotted_shape": True,
}
default_allowed_keywords = {
    "for": True,
    "def": True,
    "set": True,
    "list": True,
    "dict": True,
    "if": True,
    "else": True,
    "while": True,
    "not": True,
    "and": True,
    "or": True,
    "break": True,
    "continue": True,
    "[": True,
    "{": True,
}

editor_version = 0
max_tests = 8

level_data = None

level_size = None
spawn_coords = None
tests = None

saved = False

images_folder = os.path.join("AlgorNX", "images")
icon = None

def add_test():
    global tests
    global saved
    level = {
        "shown": [[0]*level_size["width"] for i in range(level_size["height"])],
        "wanted": [[0]*level_size["width"] for i in range(level_size["height"])],
    }
    tests.append(level)
    saved = False

def new_test_from_old_test_and_size(test, old_w, old_h, new_w, new_h):
    new_test = []
    if new_h > old_h:
        new_test = test
        for y in range(old_h, new_h):
            new_test.append([grid_info.grid_types[0] for x in range(old_w)])
    else:
        new_test = test[:new_h]
    
    if new_w > old_w:
        for line in new_test:
            line += [grid_info.grid_types[0] for x in range(old_w, new_w)]
    else:
        for i in range(len(new_test)):
            new_test[i] = new_test[i][:new_w]
    return new_test

def set_tests_size():
    global tests
    old_height = len(tests[0]["shown"])
    old_width = len(tests[0]["shown"][0])
    new_height = level_size["height"]
    new_width = level_size["width"]
    for i in range(len(tests)):
        tests[i]["shown"] = new_test_from_old_test_and_size(tests[i]["shown"], old_width, old_height, new_width, new_height)
        tests[i]["wanted"] = new_test_from_old_test_and_size(tests[i]["wanted"], old_width, old_height, new_width, new_height)

def set_level_to_empty():
    global level_data
    global level_size
    global spawn_coords
    global tests
    global saved

    level_data = {}
    level_size = copy(default_level_size)
    spawn_coords = copy(default_spawn_coords)
    tests = copy(default_tests)

    level_data["size"] = level_size
    level_data["spawn"] = spawn_coords
    level_data["tests"] = tests
    level_data["allowed_functions"] = copy(default_allowed_functions)
    level_data["allowed_keywords"] = copy(default_allowed_keywords)
    level_data["description"] = ""
    level_data["version"] = str(editor_version)

    add_test()

    saved = True

def save_level():
    global saved
    path_to_save = filedialog.askdirectory()
    if path_to_save:
        with open(os.path.join(path_to_save, "level.json"), "w") as f:
            dump(level_data, f, sort_keys=True, indent=4)
        saved = True
        return True  # Saved
    else:
        return False  # Cancelled

def ensure_saved():
    if not saved:
        save = messagebox.askyesnocancel("Warning", "The current level is not saved, do you want to save it before proceeding?")
        if save is None:
            return False  # Cancelled
        else:
            if save:
                if not save_level():
                    return False  # Cancelled
            return True  # Saved or doesn't care
    else:
        return True  # Saved

def load_level():
    global level_data
    global level_size
    global spawn_coords
    global tests
    global saved

    if ensure_saved():
        file_to_load = filedialog.askopenfilename(initialdir=os.getcwd(), title="Pick an AlgorNX level to load", filetypes=(("AlgorNX level file", "*.json"),))
        if file_to_load:
            with open(file_to_load) as f:
                level_data = load(f)

                try:
                    level_size = level_data["size"]
                except KeyError:
                    level_size = copy(default_level_size)
                    level_data["size"] = level_size

                try:
                    spawn_coords = level_data["spawn"]
                except KeyError:
                    spawn_coords = copy(default_spawn_coords)
                    level_data["spawn"] = spawn_coords

                try:
                    tests = level_data["tests"]
                except KeyError:
                    tests = copy(default_tests)
                    level_data["tests"] = tests
                    add_test()

            saved = True
            return True  # Loaded
    return False  # Not loaded, either because ensure_saved was false, or user canclled during askopenfilename

def new_level():
    if ensure_saved():
        set_level_to_empty()
        return True
    return False

def exit_function():
    if ensure_saved():
        sys.exit()

def clear_tests():
    global tests
    global level_data

    tests = copy(default_tests)
    level_data["tests"] = tests
    add_test()

    return True

def about_function():
    pass

class Application():
    def on_closing(self):
        if ensure_saved():
            self.root.destroy()

    def set_widgets_to_level_data(self, complete_load=True):
        global saved

        self.update_size_labels()
        self.update_spawn_label()

        tests_amount = len(tests)
        tests_in_listbox = self.tests_listbox.size()

        if tests_in_listbox > tests_amount:
            self.tests_listbox.delete(tests_amount, tests_in_listbox)
        elif tests_in_listbox < tests_amount:
            for i in range(tests_in_listbox, tests_amount):
                self.tests_listbox.insert(i, "Test {}".format(i+1))

        if tests_amount == max_tests:
            self.edit_menu.entryconfig("Add test", state="disabled")
        else:
            self.edit_menu.entryconfig("Add test", state="normal")

        if tests_amount == 1:
            self.edit_menu.entryconfig("Remove last test", state="disabled")
        else:
            self.edit_menu.entryconfig("Remove last test", state="normal")

        if complete_load:
            self.description_text.delete(1.0, tk.END)
            self.description_text.insert(tk.END, level_data["description"])
            self.select_keyword()
            self.select_function()
            self.tests_listbox.select_set(0)
            self.selected_test = 0
            self.editor_canvas_set_grid_size("shown")
            self.editor_canvas_set_grid_size("wanted")
            self.editor_canvas_set_grid_contents("shown")
            self.editor_canvas_set_grid_contents("wanted")
            saved = True

    def update_size_labels(self):
        self.width_label["text"] = str(level_size["width"])
        self.height_label["text"] = str(level_size["height"])

    def update_spawn_label(self):
        self.spawn_label["text"] = "{}, {}".format(*spawn_coords.values())

    def edit_level_size(self):
        win = tk.Toplevel(self.root)
        win.wm_title("Pick the level size")

        win.grid_columnconfigure(0, uniform="uni")
        win.grid_columnconfigure(1, uniform="uni")

        width_label = tk.Label(win, text="Width:")
        width_label.grid(row=0, column=0, sticky="NWSE")
        height_label = tk.Label(win, text="Height:")
        height_label.grid(row=1, column=0, sticky="NWSE")

        width_var = tk.StringVar()
        width_var.set(str(level_size["width"]))
        width_spinbox = tk.Spinbox(win, from_=2, to=grid_info.LEVEL_MAX_SIZE, textvariable=width_var, justify=tk.RIGHT)
        width_spinbox.grid(row=0, column=1, sticky="W")

        height_var = tk.StringVar()
        height_var.set(str(level_size["height"]))
        height_spinbox = tk.Spinbox(win, from_=2, to=grid_info.LEVEL_MAX_SIZE, textvariable=height_var, justify=tk.RIGHT)
        height_spinbox.grid(row=1, column=1, sticky="W")

        def edit_level_size_internal():
            global saved
            global level_size
            global spawn_coords

            level_size["width"] = int(width_var.get())
            level_size["height"] = int(height_var.get())

            if level_size["width"] > spawn_coords["x"]:
                spawn_coords["x"] = level_size["width"]

            if level_size["height"] > spawn_coords["y"]:
                spawn_coords["y"] = level_size["height"]

            self.update_size_labels()
            self.update_spawn_label()
            
            set_tests_size()

            self.editor_canvas_set_grid_size("shown")
            self.editor_canvas_set_grid_size("wanted")
            self.editor_canvas_set_grid_contents("shown")
            self.editor_canvas_set_grid_contents("wanted")

            saved = False
            win.destroy()

        enter_button = tk.Button(win, text="Enter", command=edit_level_size_internal)
        enter_button.grid(row=2, column=0,sticky="NWSE")
        cancel_button = tk.Button(win, text="Cancel", command=win.destroy)
        cancel_button.grid(row=2, column=1,sticky="NWSE")

        win.resizable(False, False)

    def edit_spawn_coords(self):
        win = tk.Toplevel(self.root)
        win.wm_title("Pick the spawn coords")

        win.grid_columnconfigure(0, uniform="uni")
        win.grid_columnconfigure(1, uniform="uni")

        width_label = tk.Label(win, text="X coord:")
        width_label.grid(row=0, column=0, sticky="NWSE")
        height_label = tk.Label(win, text="Y coord:")
        height_label.grid(row=1, column=0, sticky="NWSE")

        x_var = tk.StringVar()
        x_var.set(str(spawn_coords["x"]))
        x_spinbox = tk.Spinbox(win, from_=1, to=int(level_size["width"]), textvariable=x_var, justify=tk.RIGHT)
        x_spinbox.grid(row=0, column=1, sticky="W")

        y_var = tk.StringVar()
        y_var.set(str(spawn_coords["y"]))
        y_spinbox = tk.Spinbox(win, from_=1, to=int(level_size["height"]), textvariable=y_var, justify=tk.RIGHT)
        y_spinbox.grid(row=1, column=1, sticky="W")

        def edit_spawn_coords_internal():
            global saved
            global spawn_coords

            spawn_coords["x"] = int(x_var.get())
            spawn_coords["y"] = int(y_var.get())

            self.update_spawn_label()
            saved = False
            win.destroy()

        enter_button = tk.Button(win, text="Enter", command=edit_spawn_coords_internal)
        enter_button.grid(row=2, column=0,sticky="NWSE")
        cancel_button = tk.Button(win, text="Cancel", command=win.destroy)
        cancel_button.grid(row=2, column=1,sticky="NWSE")

        win.resizable(False, False)

    def append_to_tests_listbox(self):
        self.tests_listbox.insert(tk.END, "Test {}".format(len(tests)))

    def add_test(self):
        add_test()
        self.set_widgets_to_level_data(False)
    def remove_last_test(self):
        global tests
        tests.pop()
        self.set_widgets_to_level_data(False)

    def clear_tests(self):
        if clear_tests():
            self.set_widgets_to_level_data(False)

    def save_level(self):
        global level_data
        level_data["description"] = self.description_text.get(1.0, tk.END)[:-1]
        save_level()

    def load_level(self):
        if load_level():
            self.set_widgets_to_level_data()

    def new_level(self):
        if new_level():
            self.set_widgets_to_level_data()

    def select_function(self, *args):
        global saved
        temp = saved
        self.function_allow_var.set(level_data["allowed_functions"][str(self.selected_function.get())])
        saved = temp

    def allow_function(self, *args):
        global saved
        level_data["allowed_functions"][str(self.selected_function.get())] = bool(self.function_allow_var.get())
        saved = False

    def allow_all_functions(self):
        global saved
        global level_data
        level_data["allowed_functions"] = {k: True for k in level_data["allowed_functions"]}
        self.function_allow_var.set(True)
        saved = False

    def disable_all_functions(self):
        global saved
        global level_data
        level_data["allowed_functions"] = {k: False for k in level_data["allowed_functions"]}
        self.function_allow_var.set(False)
        saved = False

    def select_keyword(self, *args):
        global saved
        temp = saved
        self.keyword_allow_var.set(level_data["allowed_keywords"][str(self.selected_keyword.get())])
        saved = temp

    def allow_keyword(self, *args):
        level_data["allowed_keywords"][str(self.selected_keyword.get())] = bool(self.keyword_allow_var.get())
        saved = False

    def allow_all_keywords(self):
        global saved
        global level_data
        level_data["allowed_keywords"] = {k: True for k in level_data["allowed_keywords"]}
        self.keyword_allow_var.set(True)
        saved = False

    def disable_all_keywords(self):
        global saved
        global level_data
        level_data["allowed_keywords"] = {k: False for k in level_data["allowed_keywords"]}
        self.keyword_allow_var.set(False)
        saved = False

    def init_menus(self):
        self.top_menu = tk.Menu(self.root)

        self.root.config(menu=self.top_menu)

        self.file_menu = tk.Menu(self.top_menu, tearoff=False)
        self.edit_menu = tk.Menu(self.top_menu, tearoff=False)
        self.help_menu = tk.Menu(self.top_menu, tearoff=False)

        self.top_menu.add_cascade(label="File", menu=self.file_menu)
        self.top_menu.add_cascade(label="Edit", menu=self.edit_menu)
        self.top_menu.add_cascade(label="Help", menu=self.help_menu)

        self.file_menu.add_command(label="Save", command=self.save_level)
        self.file_menu.add_command(label="Load", command=self.load_level)
        self.file_menu.add_command(label="New", command=self.new_level)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=exit_function)

        self.edit_menu.add_command(label="Set level size", command=self.edit_level_size)
        self.edit_menu.add_command(label="Set spawn coords", command=self.edit_spawn_coords)
        self.edit_menu.add_separator()
        self.edit_menu.add_command(label="Allow all functions", command=self.allow_all_functions)
        self.edit_menu.add_command(label="Disable all functions", command=self.disable_all_functions)
        self.edit_menu.add_separator()
        self.edit_menu.add_command(label="Allow all keywords", command=self.allow_all_keywords)
        self.edit_menu.add_command(label="Disable all keywords", command=self.disable_all_keywords)
        self.edit_menu.add_separator()
        self.edit_menu.add_command(label="Add test", command=self.add_test)
        self.edit_menu.add_command(label="Remove last test", command=self.remove_last_test)
        self.edit_menu.add_command(label="Clear tests", command=self.clear_tests)

        self.help_menu.add_command(label="About", command=about_function)

    def add_frame(self, name):
        frame = tk.Frame(self.notebook)
        self.notebook.add(frame, text=name)
        return frame

    def init_info_editor_description(self):
        self.description_frame = tk.LabelFrame(self.info_panel_frame, text="Description")
        self.description_frame.grid(column=0, sticky="NWSE")

        self.description_text = tk.Text(self.description_frame, wrap=tk.WORD, spacing3=2, height=5, width=50)
        self.description_scrollbar = tk.Scrollbar(self.description_frame)

        self.description_text.config(yscrollcommand=self.description_scrollbar.set)
        self.description_scrollbar.config(command=self.description_text.yview)

        self.description_text.grid(row=0, column=0, sticky="NWSE")
        self.description_scrollbar.grid(row=0, column=1, sticky="NES")

    def init_info_editor_success(self):
        self.success_frame = tk.LabelFrame(self.info_panel_frame, text="Success message")
        self.success_frame.grid(column=0, sticky="NWSE")

        self.success_text = tk.Text(self.success_frame, wrap=tk.WORD, spacing3=2, height=1, width=50)
        self.success_scrollbar = tk.Scrollbar(self.success_frame)

        self.success_text.config(yscrollcommand=self.success_scrollbar.set)
        self.success_scrollbar.config(command=self.success_text.yview)

        self.success_text.grid(row=0, column=0, sticky="NWSE")
        self.success_scrollbar.grid(row=0, column=1, sticky="NES")

    def init_info_editor_allowed_functions(self):
        self.allowed_functions_frame = tk.LabelFrame(self.info_panel_frame, text="Allowed functions")
        self.allowed_functions_frame.grid(column=0, sticky="NWSE")

        self.allowed_functions_frame.grid_columnconfigure(0, uniform="uni", weight=1)
        self.allowed_functions_frame.grid_columnconfigure(1, uniform="uni", weight=1)

        self.selected_function = tk.StringVar(self.allowed_functions_frame)
        self.function_selector = tk.OptionMenu(self.allowed_functions_frame, self.selected_function, *default_allowed_functions.keys())
        self.selected_function.set(list(default_allowed_functions.keys())[0])

        self.selected_function.trace("w", self.select_function)

        self.function_allow_var = tk.BooleanVar()
        self.function_allow = tk.Checkbutton(self.allowed_functions_frame, text="Allow", variable=self.function_allow_var, onvalue=True, offvalue=False)
        self.function_allow_var.trace("w", self.allow_function)

        self.function_selector.grid(row=0, column=0, sticky="NWSE")
        self.function_allow.grid(row=0, column=1)

    def init_info_editor_allowed_keywords(self):
        self.allowed_keywords_frame = tk.LabelFrame(self.info_panel_frame, text="Allowed keywords")
        self.allowed_keywords_frame.grid(column=0, sticky="NWSE")

        self.allowed_keywords_frame.grid_columnconfigure(0, uniform="uni", weight=1)
        self.allowed_keywords_frame.grid_columnconfigure(1, uniform="uni", weight=1)

        self.selected_keyword = tk.StringVar(self.allowed_keywords_frame)
        self.keyword_selector = tk.OptionMenu(self.allowed_keywords_frame, self.selected_keyword, *default_allowed_keywords.keys())
        self.selected_keyword.set(list(default_allowed_keywords.keys())[0])
        self.selected_keyword.trace("w", self.select_keyword)

        self.keyword_allow_var = tk.BooleanVar()
        self.keyword_allow = tk.Checkbutton(self.allowed_keywords_frame, text="Allow", variable=self.keyword_allow_var, onvalue=True, offvalue=False)
        self.keyword_allow_var.trace("w", self.allow_keyword)

        self.keyword_selector.grid(row=0, column=0, sticky="NWSE")
        self.keyword_allow.grid(row=0, column=1)

    def init_info_editor(self):
        self.info_panel_frame = self.add_frame("Info")

        self.init_info_editor_description()
        self.init_info_editor_success()
        self.init_info_editor_allowed_functions()
        self.init_info_editor_allowed_keywords()

    def init_level_editor_info(self):
        self.coords_and_size_frame = tk.LabelFrame(self.editor_panel_frame, text="Info")
        self.coords_and_size_frame.grid(row=0, column=0, sticky="NWSE")

        self.width_label_name = tk.Label(self.coords_and_size_frame, text="Level width:")
        self.width_label_name.grid(row=0,column=0,sticky="E")
        self.width_label = tk.Label(self.coords_and_size_frame)
        self.width_label.grid(row=0,column=1,sticky="W")

        self.height_label_name = tk.Label(self.coords_and_size_frame, text="Level height:")
        self.height_label_name.grid(row=1,column=0,sticky="E")
        self.height_label = tk.Label(self.coords_and_size_frame)
        self.height_label.grid(row=1,column=1,sticky="W")

        self.spawn_label_name = tk.Label(self.coords_and_size_frame, text="Spawn coordinates:")
        self.spawn_label_name.grid(row=2,column=0,sticky="E")
        self.spawn_label = tk.Label(self.coords_and_size_frame)
        self.spawn_label.grid(row=2,column=1,sticky="W")

    def level_editor_select(self, event):
        self.selected_test = int(self.tests_listbox.curselection()[0])
        self.editor_canvas_set_grid_contents("shown")
        self.editor_canvas_set_grid_contents("wanted")

    def init_level_editor_tests(self):
        self.tests_frame = tk.LabelFrame(self.editor_panel_frame, text="Tests")
        self.tests_frame.grid(row=1,column=0,sticky="NWSE")

        self.tests_listbox = tk.Listbox(self.tests_frame, selectmode=tk.SINGLE, height=max_tests, exportselection=False)
        self.tests_scrollbar = tk.Scrollbar(self.tests_frame)

        self.tests_listbox.bind("<<ListboxSelect>>", self.level_editor_select)
        self.tests_listbox.config(yscrollcommand=self.tests_scrollbar.set)
        self.tests_scrollbar.config(command=self.tests_listbox.yview)

        self.tests_listbox.grid(row=0, column=0, rowspan=4, sticky="NWS")
        self.tests_scrollbar.grid(row=0, column=1, rowspan=4, sticky="NES")

    def add_image(self, image_name):
        self.images[image_name] = tk.PhotoImage(file=os.path.join(images_folder, "{}.gif".format(image_name)))

    def init_level_images(self):
        self.images = {}
        for image_name in grid_info.images_names:
            self.add_image(image_name)

    def editor_selector_handler_radio(self):
        self.selected_piece = int(self.selector_var.get())

    def editor_selector_handler_canvas(self, num):
        self.selector_var.set(num)
        self.selected_piece = num

    def editor_selector_handler_last(self, *args):
        return self.editor_selector_handler_canvas(len(self.images))

    def init_level_editor_selector(self):
        self.editor_selector_frame = tk.LabelFrame(self.editor_panel_frame, text="Pieces")
        self.editor_selector_frame.grid(row=0, column=1, sticky="NWSE")
        
        self.selector_frames = []
        self.selector_canvases = []
        self.selector_radios = []
        self.selector_var = tk.IntVar()
        for i, image in enumerate(self.images.values()):
            self.selector_frames.append(tk.Frame(self.editor_selector_frame))
            self.selector_canvases.append(tk.Canvas(self.selector_frames[-1], width=grid_info.IMAGE_SIZE, height=grid_info.IMAGE_SIZE, borderwidth=0))
            self.selector_radios.append(tk.Radiobutton(self.selector_frames[-1], variable=self.selector_var, value=i, command=self.editor_selector_handler_radio))

            self.selector_frames[-1].grid(row=0, column=i, sticky="NWS")
            self.selector_canvases[-1].create_image(0, 0, image=image, anchor="nw")
            
            def handler(event, self=self, i=i):
                return self.editor_selector_handler_canvas(i)

            self.selector_canvases[-1].bind("<Button-1>", handler)
            self.selector_canvases[-1].grid(row=0, column=0, sticky="NWSE")
            self.selector_radios[-1].grid(row=1, column=0, sticky="NWSE")

        self.selector_frames.append(tk.Frame(self.editor_selector_frame))
        self.selector_canvases.append(tk.Canvas(self.selector_frames[-1], width=grid_info.IMAGE_SIZE, height=grid_info.IMAGE_SIZE, borderwidth=0))
        self.selector_radios.append(tk.Radiobutton(self.selector_frames[-1], variable=self.selector_var, value=len(self.images), command=self.editor_selector_handler_radio))

        self.selector_frames[-1].grid(row=0, column=len(self.images), sticky="NWS")
        self.selector_canvases[-1].create_image(0, 0, image=self.images[grid_info.get_image_from_type(grid_info.EMPTY)], anchor="nw")
        self.selector_canvases[-1].create_text(grid_info.IMAGE_SIZE//2, grid_info.IMAGE_SIZE//2, font=("Helvetica ", 10), justify="center", text="0")

        self.selector_canvases[-1].bind("<Button-1>", self.editor_selector_handler_last)
        self.selector_canvases[-1].grid(row=0, column=0, sticky="NWSE")
        self.selector_radios[-1].grid(row=1, column=0, sticky="NWSE")
    
        self.selected_piece = 0

    def editor_canvas_set_grid_contents(self, grid_type):
        if grid_type == "shown":
            canvas, images, text = self.editor_shown_canvas, self.editor_shown_canvas_images, self.editor_shown_canvas_text
        elif grid_type == "wanted":
            canvas, images, text = self.editor_wanted_canvas, self.editor_wanted_canvas_images, self.editor_wanted_canvas_text
        else:
            raise Exception("Invalid grid type")

        for y in range(level_size["height"]):
            for x in range(level_size["width"]):
                square_type = tests[self.selected_test][grid_type][y][x]
                if square_type & grid_info.NUMBER:
                    canvas.itemconfig(images[x][y], image=self.images[grid_info.get_image_from_type(grid_info.EMPTY)])
                    canvas.itemconfig(text[x][y], text=str(grid_info))
                else:
                    canvas.itemconfig(images[x][y], image=self.images[grid_info.get_image_from_type(square_type)])

    def editor_canvas_set_grid_size(self, grid_type):
        if grid_type == "shown":
            canvas, images, text = self.editor_shown_canvas, self.editor_shown_canvas_images, self.editor_shown_canvas_text
        elif grid_type == "wanted":
            canvas, images, text = self.editor_wanted_canvas, self.editor_wanted_canvas_images, self.editor_wanted_canvas_text
        else:
            raise Exception("Invalid grid type")

        for y in range(grid_info.LEVEL_MAX_SIZE):
            for x in range(grid_info.LEVEL_MAX_SIZE):
                image_type = "grid_empty"
                if y >= level_size["height"] or x >= level_size["width"]:
                    image_type = "grid_painted"
                canvas.itemconfig(images[x][y], image=self.images[image_type])
                canvas.itemconfig(images[x][y], image=self.images[image_type])

    def get_wanted_number_for_square(self):
        win = tk.Toplevel(self.root)
        win.wm_title("Pick the square's number")

        win.grid_columnconfigure(0, uniform="uni")
        win.grid_columnconfigure(1, uniform="uni")

        width_label = tk.Label(win, text="Number:")
        width_label.grid(row=0, column=0, sticky="NWSE")

        var = tk.StringVar()
        var.set("0")
        max_num = 99
        min_num = -99
        spinbox = tk.Spinbox(win, from_=min_num, to=max_num, textvariable=var, justify=tk.RIGHT)
        spinbox.grid(row=0, column=1, sticky="W")

        number = None

        def set_number_value():
            nonlocal number
            nonlocal max_num
            nonlocal min_num
            number = int(var.get())
            if number > max_num:
                number = max_num
            elif number < min_num:
                number = min_num
            win.destroy()

        enter_button = tk.Button(win, text="Enter", command=set_number_value)
        enter_button.grid(row=1, column=0,sticky="NWSE")
        cancel_button = tk.Button(win, text="Cancel", command=win.destroy)
        cancel_button.grid(row=1, column=1,sticky="NWSE")

        win.resizable(False, False)
        self.root.wait_window(win)
        return number

    def editor_edit_grid(self, x, y, grid_type):
        global saved
        global tests
        if x >= 1 and x <= level_size["width"] and y >= 1 and y <= level_size["height"]:
            if grid_type == "shown":
                canvas, images, text = self.editor_shown_canvas, self.editor_shown_canvas_images, self.editor_shown_canvas_text
            elif grid_type == "wanted":
                canvas, images, text = self.editor_wanted_canvas, self.editor_wanted_canvas_images, self.editor_wanted_canvas_text
            else:
                raise Exception("Invalid grid type")
            
            x -= 1
            y -= 1
            try:
                image = self.images[grid_info.images_names[self.selected_piece]]
                square_type = grid_info.grid_types[self.selected_piece]
                number = ""
            except IndexError:
                image = self.images[grid_info.get_image_from_type(grid_info.EMPTY)]
                number = self.get_wanted_number_for_square()
                if number is None:
                    print("cancelled")
                    return
                square_type = grid_info.square_number_set(number)
                number = str(number)
                
            canvas.itemconfig(images[x][y], image=image)
            tests[self.selected_test][grid_type][y][x] = square_type
            canvas.itemconfig(text[x][y], text=number)
            
            saved = False

    def editor_shown_handler(self, event):
        self.editor_edit_grid(event.x//grid_info.IMAGE_SIZE, event.y//grid_info.IMAGE_SIZE, "shown")

    def editor_wanted_handler(self, event):
        self.editor_edit_grid(event.x//grid_info.IMAGE_SIZE, event.y//grid_info.IMAGE_SIZE, "wanted")

    def init_level_editor_editor(self):
        self.editor_notebook = ttk.Notebook(self.editor_panel_frame)
        self.editor_notebook.grid(row=1, column=1, sticky="NWSE")

        self.editor_shown_frame = tk.Frame(self.editor_notebook)
        self.editor_notebook.add(self.editor_shown_frame, text="Shown")

        self.editor_shown_canvas = tk.Canvas(self.editor_shown_frame, width=grid_info.IMAGE_SIZE*(grid_info.LEVEL_MAX_SIZE+1), height=grid_info.IMAGE_SIZE*(grid_info.LEVEL_MAX_SIZE+1))
        self.editor_shown_canvas_images = [[None]*grid_info.LEVEL_MAX_SIZE for i in range(grid_info.LEVEL_MAX_SIZE)]
        self.editor_shown_canvas_text = [[None]*grid_info.LEVEL_MAX_SIZE for i in range(grid_info.LEVEL_MAX_SIZE)]
        for y in range(grid_info.LEVEL_MAX_SIZE):
            self.editor_shown_canvas.create_text(grid_info.IMAGE_SIZE//2, (y+1)*grid_info.IMAGE_SIZE + grid_info.IMAGE_SIZE//2, font=("Helvetica ", 10), text=str(y+1), justify="center")
            self.editor_shown_canvas.create_text((y+1)*grid_info.IMAGE_SIZE + grid_info.IMAGE_SIZE//2, grid_info.IMAGE_SIZE//2, font=("Helvetica ", 10), text=str(y+1), justify="center")
            for x in range(grid_info.LEVEL_MAX_SIZE):
                image_type = grid_info.get_image_from_type(grid_info.EMPTY)
                if y >= level_size["height"] or x >= level_size["width"]:
                    image_type = grid_info.get_image_from_type(grid_info.PAINTED)
                self.editor_shown_canvas_images[x][y] = self.editor_shown_canvas.create_image((x+1)*grid_info.IMAGE_SIZE, (y+1)*grid_info.IMAGE_SIZE, image=self.images[image_type], anchor="nw")
                self.editor_shown_canvas_text[x][y] = self.editor_shown_canvas.create_text((x+1)*grid_info.IMAGE_SIZE + grid_info.IMAGE_SIZE//2, (y+1)*grid_info.IMAGE_SIZE + grid_info.IMAGE_SIZE//2, font=("Helvetica ", 10), text="", justify="center")
        self.editor_shown_canvas.grid(row=0, column=0, sticky="NWSE")

        self.editor_shown_canvas.bind("<Button-1>", self.editor_shown_handler)

        self.editor_wanted_frame = tk.Frame(self.editor_notebook)
        self.editor_notebook.add(self.editor_wanted_frame, text="Wanted")

        self.editor_wanted_canvas = tk.Canvas(self.editor_wanted_frame, width=grid_info.IMAGE_SIZE*(grid_info.LEVEL_MAX_SIZE+1), height=grid_info.IMAGE_SIZE*(grid_info.LEVEL_MAX_SIZE+1))
        self.editor_wanted_canvas_images = [[None]*grid_info.LEVEL_MAX_SIZE for i in range(grid_info.LEVEL_MAX_SIZE)]
        self.editor_wanted_canvas_text = [[None]*grid_info.LEVEL_MAX_SIZE for i in range(grid_info.LEVEL_MAX_SIZE)]
        for y in range(grid_info.LEVEL_MAX_SIZE):
            self.editor_wanted_canvas.create_text(grid_info.IMAGE_SIZE//2, (y+1)*grid_info.IMAGE_SIZE + grid_info.IMAGE_SIZE//2, font=("Helvetica ", 10), text=str(y+1), justify="center")
            self.editor_wanted_canvas.create_text((y+1)*grid_info.IMAGE_SIZE + grid_info.IMAGE_SIZE//2, grid_info.IMAGE_SIZE//2, font=("Helvetica ", 10), text=str(y+1), justify="center")
            for x in range(grid_info.LEVEL_MAX_SIZE):
                image_type = "grid_empty"
                if y >= level_size["height"] or x >= level_size["width"]:
                    image_type = "grid_painted"
                self.editor_wanted_canvas_images[x][y] = self.editor_wanted_canvas.create_image((x+1)*grid_info.IMAGE_SIZE, (y+1)*grid_info.IMAGE_SIZE, image=self.images[image_type], anchor="nw")
                self.editor_wanted_canvas_text[x][y] = self.editor_wanted_canvas.create_text((x+1)*grid_info.IMAGE_SIZE + grid_info.IMAGE_SIZE//2, (y+1)*grid_info.IMAGE_SIZE + grid_info.IMAGE_SIZE//2, font=("Helvetica ", 10), text="", justify="center")
        self.editor_wanted_canvas.grid(row=0, column=0, sticky="NWSE")

        self.editor_wanted_canvas.bind("<Button-1>", self.editor_wanted_handler)

    def init_level_editor(self):
        self.editor_panel_frame = self.add_frame("Editor")

        self.init_level_editor_info()
        self.init_level_editor_tests()
        
        self.init_level_images()

        self.init_level_editor_selector()
        self.init_level_editor_editor()

    def init_frames(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.grid(row=0, column=0, sticky="NWSE")

        self.init_info_editor()
        self.init_level_editor()
        self.set_widgets_to_level_data()

    def __init__(self, root):   
        self.root = root

        self.init_menus()
        self.init_frames()

def main():
    global icon
    root = tk.Tk()
    icon = tk.PhotoImage(file=os.path.join(images_folder, "robot.gif"))
    root.title("AlgorNX level editor")
    root.iconphoto(True, icon)
    root.resizable(False, False)

    app = Application(root)

    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    set_level_to_empty()
    main()