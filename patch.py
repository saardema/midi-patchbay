import midi_parser
import rtmidi
from dataclasses import dataclass

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

    def create_patch(self, id, enabled, in_name, out_name, input_channel, output_channel, sync):
        in_port_nr = self.get_in_port_nr_by_device_name(in_name)
        out_port_nr = self.get_out_port_nr_by_device_name(out_name)
        patch = PatchBay.Patch(id, enabled, in_name, out_name, input_channel, output_channel, in_port_nr, out_port_nr, sync)
        self.patches.append(patch)
        # self.log_patches()

    def remove_patch(self, patch):
        patch.in_port.close_port()
        patch.out_port.close_port()
        self.patches.remove(patch)
        # self.log_patches()

    def log_patches(self):
        print('------PATCHES-----')
        for patch in self.patches:
            print(
                patch.id,
                patch.enabled,
                patch._in_name,
                patch._out_name,
                patch.input_channel,
                patch.output_channel,
                patch._sync,
            )

    def set_patch_input_device(self, patch, device_name):
        in_port_nr = self.get_in_port_nr_by_device_name(device_name)
        patch.in_port.close_port()
        patch._in_name = device_name
        if in_port_nr: patch.in_port.open_port(in_port_nr, name=device_name)
    
    def set_patch_output_device(self, patch, device_name):
        out_port_nr = self.get_out_port_nr_by_device_name(device_name)
        patch.out_port.close_port()
        patch._outname = device_name
        if out_port_nr: patch.out_port.open_port(out_port_nr, name=device_name)

    def parse(self):
        for patch in self.patches:
            message = patch.in_port.get_message()
            
            if message:
                self.on_patch_input(patch, message[0])

    def on_patch_input(self, patch, bytes_message):
        # self.log_patches()
        if not patch.enabled: return

        message = midi_parser.from_bytes(bytes_message)

        if not message['channel']:
            patch.out_port.send_message(bytes_message)

        elif not patch.input_channel or message['channel'] == patch.input_channel:
            if patch.output_channel:
                message['channel'] = patch.output_channel
                bytes_message = midi_parser.to_bytes(message)
            patch.out_port.send_message(bytes_message)

    def stop(self):
        for patch in self.patches:
            patch.in_port.close_port()
            patch.out_port.close_port()

    @dataclass
    class Patch:
        id: str
        enabled: bool
        _in_name: str
        _out_name: str
        input_channel: int
        output_channel: int
        _in_port_nr: int
        _out_port_nr: int
        _sync: bool

        def __post_init__(self):
            self.in_port = rtmidi.MidiIn()
            self.out_port = rtmidi.MidiOut()
            if self._in_port_nr: self.in_port.open_port(self._in_port_nr)
            if self._out_port_nr: self.out_port.open_port(self._out_port_nr)

        def set_sync(self, value):
            self._sync = value
            self.in_port.ignore_types(timing=not value)
    
    # class Patch:
    #     def __init__(self, id, enabled, in_name, out_name, input_channel, output_channel, in_port_nr, out_port_nr, sync):
    #         self.id = id
    #         self.enabled = enabled
    #         self._in_name = in_name
    #         self._out_name = out_name
    #         self.input_channel = input_channel
    #         self.output_channel = output_channel
    #         self._sync = sync

    #         def __post_init__(self):
    #             self.in_port = rtmidi.MidiIn()
    #             self.out_port = rtmidi.MidiOut()
    #             if in_port_nr: self.in_port.open_port(in_port_nr)
    #             if out_port_nr: self.out_port.open_port(out_port_nr)