"""
Created on Wed Feb 20 01:03:54 2019

@author: Shammya Saha
         Graduate Research Assistant, Laboratory for Energy and Power Solutions, Arizona State University
"""

import warnings

import pandas as pd

from DistributionPoweFlow import *
from Inverter import *
from Peer import *
from power_flow_solution import lossless_distribution_power_flow

warnings.filterwarnings("ignore")


def create_inverter_list(file_name, simulate_bf_chip=False):
    device = pd.read_csv(file_name)
    if len(device) > NUMBER_OF_INVERTERS:
        raise SystemExit

    inverter_list = [Inverter(serial_no=count, simulate_bf_chip=simulate_bf_chip) for count in range(len(device))]
    for index, row in device.iterrows():
        # print(index)
        inverter_list[index].node = int(row['Node'])
        inverter_list[index].IP_ADDRESS = row['IP_Address']
        inverter_list[index].DEVICE_ID = row['DEVICE_ID']
        inverter_list[index].MODBUS_PORT = int(row['MODBUS'])
        inverter_list[index].VOLTAGE_R = int(row['VOLTAGE'])
        inverter_list[index].WATT_R = int(row['WATT'])
        inverter_list[index].VAR_R = int(row['VAR'])
        inverter_list[index].smax = int(row['SMAX']) / MULTIPLYING_FACTOR
        inverter_list[index].update_params()
    return inverter_list


def generate_inverter_data(simulate_bf_chip, file_name='Config.csv'):
    inverter_list = create_inverter_list(file_name, simulate_bf_chip)
    dflow = DistributionPowerFlow()
    # Running the power flow and get the voltages
    _ = lossless_distribution_power_flow(dflow, inverter_list)
    if simulate_bf_chip:
        peer = Peer(NUMBER_OF_INVERTERS, simulate_bf_chip)
        for inverter in inverter_list:
            command_from_peer = peer.peer_polling_command()
            response_to_command_from_peer = inverter.response_to_peer_command(command_from_peer)
            # print(response_to_command_from_peer)
            peer.peer_parse_value(response_to_command_from_peer)
        transaction = peer.peer_prepare_transaction_for_endorsing()
        # print('Transaction to be submitted: ', transaction)
        return transaction
    else:
        # Creates list of inverters from the config file
        inverter_data = ''
        for inverter in inverter_list:
            inverter_data += inverter.return_info() + '::'
        # print('Transaction to be submitted: ', inverter_data[:-2])
        return inverter_data[:-2]


if __name__ == '__main__':
    print('Transaction to be submitted: ', generate_inverter_data(simulate_bf_chip=False))

