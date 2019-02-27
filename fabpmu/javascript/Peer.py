"""
Created on Wed Feb 20 01:03:54 2019

@author: Shammya Saha
         Graduate Research Assistant, Laboratory for Energy and Power Solutions, Arizona State University
"""

import os
from ctypes import *
from shutil import copyfile

from import_constants import *
from supportFunctions import *


class Peer:
    def __init__(self, total_assets, simulate_bf_chip=False):
        self.peer_initialize = False
        self.restart_data_collection = True
        self.collected_data = ''
        self.assets_polled = 0
        self.controllable_assets = total_assets
        self.peer_initialize = False
        self.simulate_bf_chip = simulate_bf_chip
        if self.simulate_bf_chip:
            self.__initialize_chip__()

    def __initialize_chip__(self):
        if os.path.exists('Utility.so'):
            os.remove('Utility.so')
        if not (os.path.exists('Utility.so')):
            copyfile("./libchipsim.so", "./Utility.so")
        self.peer = CDLL("./Utility.so")
        self.peer.initializeChip()
        if self.peer.getChipState() == 31:
            self.peer_initialize = True
            print('Peer chip has been initialized properly.')
        else:
            print('Peer chip initialization Failed.')

    def peer_polling_command(self):
        if self.peer_initialize:
            if self.assets_polled != self.controllable_assets:
                command = PEER_VPQ_COMMAND
                message = create_string_buffer(bytes(command, 'utf-8'), len(command))
                peer_buffer = (c_ubyte * 64)()
                self.peer.createOneTimePad(message, len(message), 1, peer_buffer)
                # print("One Time pad generated for the utility ")
                # Combining two data and send it through TCP Socket
                peer_out = str(len(command)) + ':' + command + ':' + convert_unsigned_byte_array_to_string(peer_buffer)
                return peer_out

    def peer_parse_value(self, inverter_out):
        if self.peer_initialize:
            if self.assets_polled != self.controllable_assets:
                peer_in = inverter_out
                peer_in = peer_in.split(':')
                len_data = int(peer_in[0])
                received_data = peer_in[1]
                inverter_buffer_rec = peer_in[2]
                inverter_buffer_rec = inverter_buffer_rec.split('_')

                message = create_string_buffer(bytes(received_data, 'utf-8'), len(received_data))
                peer_buffer = (c_ubyte * 64)()
                self.peer.createOneTimePad(message, len(message), 1, peer_buffer)
                self.assets_polled += 1
                if compare_string_to_unsigned_byte_array(inverter_buffer_rec, peer_buffer):
                    print('Incoming data from inverter {} is verified.'.format(self.assets_polled - 1))
                    self.collected_data += received_data + '::'
                else:
                    pass
            else:
                return False, ''

    def peer_prepare_transaction_for_endorsing(self):
        if self.peer_initialize:
            if self.assets_polled == self.controllable_assets:
                self.assets_polled = 0
                return self.collected_data[:-2]  # This clears out the last two :
            else:
                print('Polling has not been completed.')
                return ''
