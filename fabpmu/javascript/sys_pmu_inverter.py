from peer_client_application import generate_combined_data
import subprocess


dataset = generate_combined_data()
#print(dataset)
for key, values in dataset.items():
    test_command = 'node send.js ' + key + ' '
    for data in values:
        test_command += str(data) + ' '
    print(test_command)
    # The following line need to be commented out while running the node.js application
    result= subprocess.check_output(test_command,shell=True)
    print(result)


        
