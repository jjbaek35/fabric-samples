from peer_client_application import generate_inverter_data
import subprocess

zipcode_list = ['85281', '85212']

for zipcode in zipcode_list:
    inverter_data = generate_inverter_data(simulate_bf_chip=False, file_name=zipcode + '.csv')
    parsed_data = inverter_data.split('::')
    for inverter_data in parsed_data:
        inverter_data_split = inverter_data.split('_')
        test_command = 'node send.js '
        for data in inverter_data_split:
            test_command += data[1:] + ' '
        print(test_command)
    # The following line need to be commented out while running the node.js application
    # result= subprocess.check_output(test_command,shell=True)
