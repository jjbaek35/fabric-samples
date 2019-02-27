"""
Created on Wed Feb 20 01:03:54 2019

@author: Shammya Saha
         Graduate Research Assistant, Laboratory for Energy and Power Solutions, Arizona State University
"""

import os
from ctypes import *
from shutil import copyfile

import math
import numpy as np
from pymodbus.client.sync import ModbusTcpClient
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder

from import_constants import *
from supportFunctions import *


class Inverter:
    DEVICE_ID, IP_ADDRESS, MODBUS_PORT, VOLTAGE_R = '', '', 0, 0
    WATT_R, VAR_R = 0, 0

    # Define Random Inverter Capacity and Random Uniform Number
    def __init__(self, serial_no=0, simulate_bf_chip=False, mu=0.9, minimun_power_factor=0.5,
                 set_point=np.asarray([0.9, 0.95, 1.05, 1.1, 1.08, 1.1])):

        self.node = 0
        self.set_point = set_point
        self.smax = 0
        self.mu = mu
        self.minimum_power_factor = np.random.uniform(0.2, 0.85)
        self.pout = 0
        self.qout = 0
        self.v = 1.0
        self.received_command = ''
        self.chip_initialize = False
        self.simulate_bf_chip = simulate_bf_chip
        if self.simulate_bf_chip:
            self.__initialize_chip__(serial_no)

    def __initialize_chip__(self, serial_no):
        if os.path.exists('inverter' + str(serial_no) + '.so'):
            os.remove('inverter' + str(serial_no) + '.so')
        if not os.path.exists('inverter' + str(serial_no) + '.so'):
            copyfile("./libchipsim.so", './inverter' + str(serial_no) + '.so')
            self.chip = CDLL('./inverter' + str(serial_no) + '.so')
            self.chip.initializeChip()
            if self.chip.getChipState() == 31:
                self.chip_initialize = True
                print('Chip of inverter {} has been initialized properly.'.format(serial_no))
            else:
                print('Chip Initialization Failed')

    def __parse_peer_command__(self, peer_command):
        if self.chip_initialize:
            inverter_in = peer_command
            inverter_in = inverter_in.split(':')
            len_command = int(inverter_in[0])
            received_command = inverter_in[1]
            peer_buffer_rec = inverter_in[2]  # this utility buffer is not a character array, rather a string
            peer_buffer_rec = peer_buffer_rec.split('_')
            message = create_string_buffer(bytes(received_command, 'utf-8'), len(received_command))
            # Check whether the one time pad matches
            # create buffer for the one time pad pertaining to the inverter
            inverter_buffer = (c_ubyte * 64)()
            self.chip.createOneTimePad(message, len(message), 1, inverter_buffer)
            # Check whether the buffers matched
            if compare_string_to_unsigned_byte_array(peer_buffer_rec, inverter_buffer):
                self.received_command = received_command
                print('Incoming request from the Utility is Verified.')
            else:
                print('Incoming Source Not Verified.')
                self.received_command = ''

    def response_to_peer_command(self, peer_command):
        if self.chip_initialize:
            self.__parse_peer_command__(peer_command)
            if len(self.received_command) != 0:
                # data = 'ID1001_V0.95_P0.25_Q0.75'
                data = self.return_info()
                message = create_string_buffer(bytes(data, 'utf-8'), len(data))
                inverter_buffer = (c_ubyte * 64)()
                self.chip.createOneTimePad(message, len(message), 1, inverter_buffer)
                inverter_out = str(len(data)) + ':' + data + ':' + convert_unsigned_byte_array_to_string(
                    inverter_buffer)
                return inverter_out

    def update_params(self):
        # self.Smax=Smax
        self.pmax = self.mu * self.smax
        self.qlim = self.smax * math.sin(math.acos(self.minimum_power_factor))
        self.q_available = np.sqrt(self.smax ** 2 - self.pmax ** 2)

    def qmax_calculation(self, p):
        return min(abs(self.qlim), math.sqrt(self.smax * self.smax - p * p))

    def p_curve(self, v):
        # defines the Pcurve at various voltage points v given user specified inputs
        # VOLT-WATT POINTS
        vbreakp = self.set_point[4]
        vmaxp = self.set_point[5]

        if v <= vbreakp:
            self.pout = self.pmax
        elif (v > vbreakp) and (v <= vmaxp):
            self.pout = (vmaxp - v) / (vmaxp - vbreakp) * self.pmax
        else:
            self.pout = 0.0
        return self.pout

    def q_curve(self, v):
        # VOLT-VAR POINTS
        vminq = self.set_point[0]
        vdead1 = self.set_point[1]
        vdead2 = self.set_point[2]
        vmaxq = self.set_point[3]

        # points below vminq,
        if v <= vminq:
            self.qout = self.qmax_calculation(self.p_curve(v))
        # linearly decrease Qinj between vminq and vdead1
        elif (v > vminq) and (v <= vdead1):
            self.qout = (vdead1 - v) / (vdead1 - vminq) * self.qmax_calculation(self.p_curve(v))
        # zero in the dead-band
        elif (vdead1 == vdead2) or ((v > vdead1) & (v <= vdead2)):
            self.qout = 0.0
        # linearly decrease Qinj between vdead2 and vmaxq
        elif (v > vdead2) and (v <= vmaxq):
            self.qout = (vdead2 - v) / (vmaxq - vdead2) * self.qmax_calculation(self.p_curve(v))
        # maintain the maximum (negative) injection given the watt injection at the given voltage
        elif v > vmaxq:
            self.qout = -self.qmax_calculation(self.p_curve(v))
        return self.qout

    def update_voltage(self, v):
        self.v = v

    def return_node(self):
        return self.node

    def return_info(self):

        data = self.DEVICE_ID
        data += '_V'
        data += str(round(INVERTER_BASE_VOLTAGE * self.v, 3))
        data += '_P'
        data += str(round(self.pout * MULTIPLYING_FACTOR, 2))
        data += '_Q'
        data += str(round(self.qout * MULTIPLYING_FACTOR, 2))
        return data

    def update_register(self):
        if SIMULATE_MODBUS:
            client = ModbusTcpClient(self.IP_ADDRESS, self.MODBUS_PORT, timeout=3)
            client.connect()
            client.write_registers(self.VOLTAGE_R, int(self.v * MULTIPLYING_FACTOR))
            client.write_registers(self.WATT_R, int(self.pout * MULTIPLYING_FACTOR))
            client.write_registers(self.VAR_R, int(self.qout * MULTIPLYING_FACTOR))
            client.close()

    def read_register(self, register):
        if SIMULATE_MODBUS:
            client = ModbusTcpClient(self.IP_ADDRESS, self.MODBUS_PORT, timeout=3)
            client.connect()
            response = client.read_holding_registers(register, unit=1)
            value = BinaryPayloadDecoder.fromRegisters(response.registers, byteorder=Endian.Big).decode_16bit_uint()
            client.close()
            return value / MULTIPLYING_FACTOR
