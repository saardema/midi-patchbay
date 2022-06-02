import midi_parser
import rtmidi

class PatchBay:
    def __init__(self, show_devices=False):
        self.patches = []
        self.in_ports = {}
        self.out_ports = {}

        for port_nr, name in enumerate(rtmidi.MidiIn().get_ports()):
            self.in_ports[name] = port_nr
            if show_devices:
                print('FROM "{}"'.format(name))

        for port_nr, name in enumerate(rtmidi.MidiOut().get_ports()):
            self.out_ports[name] = port_nr
            if show_devices:
                print('TO   "{}"'.format(name))
                
    def get_in_port_nr_by_device_name(self, device_name):
        try:
            return self.in_ports[device_name]
        except KeyError as e:
            print(str(e), 'is not an input device')
                
    def get_out_port_nr_by_device_name(self, device_name):
        try:
            return self.out_ports[device_name]
        except KeyError as e:
            print(str(e), 'is not an output device')

    def create_patch(self, id, enabled, in_name, out_name, input_channel=None, output_channel=None):
        in_port_nr = self.get_in_port_nr_by_device_name(in_name)
        out_port_nr = self.get_out_port_nr_by_device_name(out_name)
        patch = PatchBay.Patch(id, enabled, in_port_nr, out_port_nr, in_name, out_name, input_channel, output_channel)
        self.patches.append(patch)
        self.log_patches()

    def remove_patch(self, patch):
        patch.in_port.close_port()
        patch.out_port.close_port()
        self.patches.remove(patch)
        self.log_patches()

    def log_patches(self):
        print('------PATCHES-----')
        for patch in self.patches:
            print(
                patch.id,
                patch.enabled,
                patch.in_name,
                patch.out_name,
                patch.input_channel,
                patch.output_channel,
            )

    def set_patch_input_device(self, patch, device_name):
        in_port_nr = self.get_in_port_nr_by_device_name(device_name)
        patch.in_port.close_port()
        patch.in_name = device_name
        if in_port_nr: patch.in_port.open_port(in_port_nr, name=device_name)
    
    def set_patch_output_device(self, patch, device_name):
        out_port_nr = self.get_out_port_nr_by_device_name(device_name)
        patch.out_port.close_port()
        patch.outname = device_name
        if out_port_nr: patch.out_port.open_port(out_port_nr, name=device_name)

    def parse(self):
        for patch in self.patches:
            message = patch.in_port.get_message()
            
            if message:
                self.on_patch_input(patch, message[0])

    def on_patch_input(self, patch, bytes_message):
        self.log_patches()
        if not patch.enabled: return

        message = midi_parser.from_bytes(bytes_message)

        if not patch.input_channel or message['channel'] == patch.input_channel:
            if patch.output_channel:
                message['channel'] = patch.output_channel
                bytes_message = midi_parser.to_bytes(message)
            patch.out_port.send_message(bytes_message)

    def stop(self):
        for patch in self.patches:
            patch.in_port.close_port()
            patch.out_port.close_port()
    
    class Patch:
        def __init__(self, id, enabled, in_port_nr, out_port_nr, in_name, out_name, input_channel, output_channel):
            self.id = id
            self.enabled = enabled
            self.in_port = rtmidi.MidiIn()
            self.out_port = rtmidi.MidiOut()
            self.in_name = in_name
            self.out_name = out_name
            self.input_channel = input_channel
            self.output_channel = output_channel
            
            if in_port_nr: self.in_port.open_port(in_port_nr)
            if out_port_nr: self.out_port.open_port(out_port_nr)