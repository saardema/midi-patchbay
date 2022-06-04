import tkinter as tk
from tkinter import Canvas
from tkinter import ttk
import json, time, random

app = tk.Tk()
app.title('MIDI Patchbay')

row = 0
gui_patches = []
input_devices = []
output_devices = []
queue = None

class GuiPatch():
    grid_args = dict(padx=5, pady=(15, 0), sticky=tk.W)
    channel_list = [i+1 for i in range(16)]
    
    def __init__(self, id, values=None):
        rnd = str(random.random())[2:]
        self.id = id
        self.vars = {}
        self.vars['enabled'] = tk.BooleanVar(name='enabled_' + rnd)
        self.vars['input_device'] = tk.StringVar(name='input_device_' + rnd)
        self.vars['input_device_sync'] = tk.BooleanVar(name='input_device_sync_' + rnd)
        self.vars['input_channel'] = tk.StringVar(name='input_channel_' + rnd)
        self.vars['output_device'] = tk.StringVar(name='output_device_' + rnd)
        self.vars['output_channel'] = tk.StringVar(name='output_channel_' + rnd)
        self.vars['output_device_sync'] = tk.BooleanVar(name='output_device_sync_' + rnd)
        self.vars['is_return'] = tk.BooleanVar(name='is_return_' + rnd)
        self.vars['return_output_channel'] = tk.StringVar(name='return_output_channel_' + rnd)
        self.vars['return_input_channel'] = tk.StringVar(name='return_input_channel_' + rnd)
        self.__main_elements = []
        self.__return_elements = []

        if values:
            for key, value in values.items():
                self.vars[key].set(value)
        else:
            self.vars['enabled'].set(True)
            self.vars['input_device'].set(input_devices[0])
            self.vars['input_device_sync'].set(False)
            self.vars['input_channel'].set('All')
            self.vars['output_device'].set(output_devices[0])
            self.vars['output_channel'].set('Same')
            self.vars['output_device_sync'].set(False)
            self.vars['is_return'].set(False)
            self.vars['return_output_channel'].set('Same')
            self.vars['return_input_channel'].set('All')
        
        self.create_elements()
        self.toggle_return()

        for var in self.vars.values():
            var.trace = var.trace_add('write', self.handle_input)

    def handle_input(self, name, b, mode):
        for key, var in self.vars.items():
            if name == var._name:
                value = var.get()
                if value != '':
                    queue.put((self.id, key, value))
                break

    def create_elements(self):
        global row
        row = max(self.id, row)
        row += 1
        column = 0
        grid_args = GuiPatch.grid_args.copy()
        if row == 1: grid_args['pady'] = 0

        enabledCheck = tk.Checkbutton(app, width=2, var=self.vars['enabled'])
        enabledCheck.grid(column=column, row=row, **grid_args)
        self.__main_elements.append(enabledCheck)

        column += 1
        input_device_combo = ttk.Combobox(app, textvariable=self.vars['input_device'], state='readonly', width=20)
        input_device_combo['values'] = input_devices
        input_device_combo.grid(column=column, row=row, **grid_args)
        self.__main_elements.append(input_device_combo)

        column += 1
        input_channel_combo = ttk.Combobox(app, textvariable=self.vars['input_channel'], width=5)
        input_channel_combo['values'] = ['All'] + GuiPatch.channel_list
        input_channel_combo.grid(column=column, row=row, **grid_args)
        self.__main_elements.append(input_channel_combo)

        column += 1
        h = 8
        w = 80
        canvas = Canvas(app, width=w, height=h)
        canvas.create_line(1, h/2+3, w, h/2+3, arrow=tk.LAST)
        canvas.grid(column=column, row=row, **grid_args)
        self.__main_elements.append(canvas)

        column += 1
        output_channel_combo = ttk.Combobox(app, textvariable=self.vars['output_channel'], width=5)
        output_channel_combo['values'] = ['Same'] + GuiPatch.channel_list
        output_channel_combo.grid(column=column, row=row, **grid_args)
        self.__main_elements.append(output_channel_combo)

        column += 1
        output_device_combo = ttk.Combobox(app, textvariable=self.vars['output_device'], state='readonly', width=20)
        output_device_combo['values'] = output_devices
        output_device_combo.grid(column=column, row=row, **grid_args)
        self.__main_elements.append(output_device_combo)

        column += 1
        input_sync_check = tk.Checkbutton(app, width=5, var=self.vars['input_device_sync'])
        input_sync_check.grid(column=column, row=row, **grid_args)
        self.__main_elements.append(input_sync_check)

        column += 1
        returnCheck = tk.Checkbutton(app, width=5, var=self.vars['is_return'], command=self.toggle_return)
        returnCheck.grid(column=column, row=row, **grid_args)
        self.__main_elements.append(returnCheck)
        
        column += 1
        removeBtn = tk.Button(app, text='x', height=1, command= lambda: clear_gui_patch(self))
        btn_grid_args = GuiPatch.grid_args.copy()
        btn_grid_args['sticky'] = tk.E
        removeBtn.grid(column=column, row=row, **grid_args)
        self.__main_elements.append(removeBtn)

        row += 1
        column = 2
        return_grid_args = GuiPatch.grid_args.copy()
        return_grid_args['pady'] = (5, 0)

        return_output_channel_combo = ttk.Combobox(app, textvariable=self.vars['return_output_channel'], state='readonly', width=5)
        return_output_channel_combo['values'] = ['Same'] + GuiPatch.channel_list
        return_output_channel_combo.grid(column=column, row=row, **return_grid_args)
        self.__return_elements.append(return_output_channel_combo)

        column += 1
        h = 8
        w = 80
        canvas = Canvas(app, width=w, height=h)
        canvas.create_line(1, h/2+3, w, h/2+3, arrow=tk.FIRST)
        canvas.grid(column=column, row=row, **return_grid_args)
        self.__return_elements.append(canvas)

        column += 1
        return_input_channel_combo = ttk.Combobox(app, textvariable=self.vars['return_input_channel'], state='readonly', width=5)
        return_input_channel_combo['values'] = ['All'] + GuiPatch.channel_list
        return_input_channel_combo.grid(column=column, row=row, **return_grid_args)
        self.__return_elements.append(return_input_channel_combo)

        column += 2
        output_sync_check = tk.Checkbutton(app, width=5, var=self.vars['output_device_sync'])
        output_sync_check.grid(column=column, row=row, **grid_args)
        self.__return_elements.append(output_sync_check)

    def destroy(self):
        for var in self.vars.values():
            var.trace_remove('write', var.trace)

        for element in self.__main_elements:
            element.destroy()

        for element in self.__return_elements:
            element.destroy()

    def toggle_return(self):
        if self.vars['is_return'].get():
            for element in self.__return_elements:
                element.grid()
        else:
            for element in self.__return_elements:
                element.grid_remove()
                
def get_new_patch_id():
    highest_id = -1
    
    for patch in gui_patches:
        if patch.id > highest_id: highest_id = patch.id
    
    return highest_id + 1

def print_gui_patches():
    l = str(len(gui_patches))
    print('---' + l + '-GUI PATCHES----')
    for patch in gui_patches:
        o = str(patch.id) + ' '
        for value in patch.vars.values():
            o += str(value.get()) + ' '
        print(o)

def add_gui_patch(patch_values=None):
    id = get_new_patch_id()
    new_patch = GuiPatch(id, patch_values)
    gui_patches.append(new_patch)
    values = {}
    for name, var in new_patch.vars.items():
        values[name] = var.get()
    queue.put((id, 'add_patch', values))

def clear_gui_patch(patch, remove=True):
    id = patch.id
    patch.destroy()
    queue.put((id, 'remove_patch', None))
    if remove: gui_patches.remove(patch)

def save():
    data = []
    
    for patch in gui_patches:
        patch_data = {}
        for key, var in patch.vars.items():
            patch_data[key] = var.get()
        data.append(patch_data)
    
    with open('config.json', 'w') as file:
        json.dump(data, file, indent=4, sort_keys=True)

def clear_patches():
    for patch in gui_patches:
        clear_gui_patch(patch, remove=False)
    gui_patches.clear()

def load():
    with open('config.json') as file:
        global row
        row = 0
        data = json.load(file)
        
        if not len(data): return
        
        clear_patches()

        for patch_values in data:
            add_gui_patch(patch_values)

def on_window_close():
    app.destroy()
    # sys.exit()

def init(in_devices, out_devices, q):
    global input_devices, output_devices, queue
    input_devices = in_devices
    output_devices = out_devices
    queue = q
    app.protocol("WM_DELETE_WINDOW", on_window_close)

    tk.Label(app, text="Input"  ).grid(column=1, row=row, padx=5, sticky=tk.W)
    tk.Label(app, text="Channel").grid(column=2, row=row, padx=5, sticky=tk.W)
    tk.Label(app, text="Channel").grid(column=4, row=row, padx=5, sticky=tk.W)
    tk.Label(app, text="Output" ).grid(column=5, row=row, padx=5, sticky=tk.W)
    tk.Label(app, text="Sync"   ).grid(column=6, row=row, padx=5, sticky=tk.W)
    tk.Label(app, text="Return" ).grid(column=7, row=row, padx=5, sticky=tk.W)

    add_btn = tk.Button(app, text="+ Add patch", command=add_gui_patch)
    add_btn.grid(row=99, column=1, padx=(2, 0), pady=(13, 15), sticky=tk.W)
    save_btn = tk.Button(app, text="Save", command=save)
    save_btn.grid(row=99, column=2, padx=(2, 0), pady=(13, 15), sticky=tk.W)
    load_btn = tk.Button(app, text="Load", command=load)
    load_btn.grid(row=99, column=3, padx=(2, 0), pady=(13, 15), sticky=tk.W)
    print_btn = tk.Button(app, text="Print", command=print_gui_patches)
    print_btn.grid(row=99, column=4, padx=(2, 0), pady=(13, 15), sticky=tk.W)
    # add_gui_patch()
    load()

    app.mainloop()