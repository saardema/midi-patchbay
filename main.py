import sys
import time
from patch import PatchBay
import multiprocessing
from multiprocessing import Queue

# TODO
# - Disable return checkbox if one of the device doesn't have an exact i/o match
# - Refresh device list when one is (dis)connected
# - Prevent MIDI echo
# - Note filter option
# - 

queue = Queue()
patchbay = PatchBay()
input_devices = [in_port for in_port in patchbay.in_ports]
output_devices = [out_port for out_port in patchbay.out_ports]

def gui_process(*args):
    import gui
    gui.init(*args)

def get_patches_by_id(id):
    return_patch = None
    patch = None
    
    for p in patchbay.patches:
        if p.id == id:
            patch = p
        elif p.id == id + 'r':
            return_patch = p
    
    return patch, return_patch

def queue_to_patch(name, value):
    if name == 'input_channel' or name == 'return_input_channel':
        value = None if value == 'All' else int(value)
    elif name == 'output_channel' or name == 'return_output_channel':
        value = None if value == 'Same' else int(value)

    return value

def handle_queue():
    if queue.empty(): return
    gui_update = queue.get(block=False)
    # print(gui_update)
    event = gui_update[0]
    id = str(gui_update[1])
    value = gui_update[2]
    value = queue_to_patch(event, value)
    patch, return_patch = get_patches_by_id(id)

    if event == 'print':
        time.sleep(.001)
        patchbay.log_patches()
    
    elif event == 'add_patch':
        for v in value:
            value[v] = queue_to_patch(v, value[v])

        patchbay.create_patch(
            id,
            True,
            value['input_device'],
            value['output_device'],
            value['input_channel'],
            value['output_channel'],
            value['input_device_sync']
        )
        patchbay.create_patch(
            id + 'r',
            value['is_return'],
            value['output_device'],
            value['input_device'],
            value['return_input_channel'],
            value['return_output_channel'],
            value['output_device_sync']
        )

    elif patch and return_patch:
        if event == 'input_device':
            patchbay.set_patch_input_device(patch, value)
            patchbay.set_patch_output_device(return_patch, value)
        elif event == 'output_device':
            patchbay.set_patch_output_device(patch, value)
            patchbay.set_patch_input_device(return_patch, value)
        elif event == 'input_channel':
            patch.input_channel = value
        elif event == 'output_channel':
            patch.output_channel = value
        elif event == 'enabled':
            patch.enabled = value
        elif event == 'return_input_channel':
            return_patch.input_channel = value
        elif event == 'return_output_channel':
            return_patch.output_channel = value
        elif event == 'is_return':
            return_patch.enabled = value
        elif event == 'input_device_sync':
            patch.set_sync(value)
        elif event == 'output_device_sync':
            return_patch.set_sync(value)
        elif event == 'remove_patch':
            patchbay.remove_patch(patch)
            patchbay.remove_patch(return_patch)

if __name__ == '__main__':
    gp = multiprocessing.Process(target=gui_process, args=(input_devices, output_devices, queue))
    gp.start()

    try:
        while 1:
            handle_queue()
            patchbay.parse()
            if not gp.is_alive():
                gp.join()
                sys.exit(0)
    except KeyboardInterrupt:
        sys.exit(0)
    finally:
        print("Closing ports...")
        patchbay.stop()