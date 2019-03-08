/*
 * SPDX-License-Identifier: Apache-2.0
 * JJ
 */

'use strict';
const args = process.argv; // for arguments processing


const dt = require('date-utils');
var newDate = new Date();
var time = newDate.toFormat('YYYY-MM-DD-HH24:MI:SS');
//var time = time2.split("-").map(Number);


const { FileSystemWallet, Gateway } = require('fabric-network');
const fs = require('fs'); // global function require() to call module.
const path = require('path');

const ccpPath = path.resolve(__dirname, '..', '..', 'basic-network', 'connection.json');
const ccpJSON = fs.readFileSync(ccpPath, 'utf8');
const ccp = JSON.parse(ccpJSON);

async function main() {
    try {

        // Create a new file system based wallet for managing identities.
        const walletPath = path.join(process.cwd(), 'wallet');
        const wallet = new FileSystemWallet(walletPath);
        console.log(`Wallet path: ${walletPath}`);

        // Check to see if we've already enrolled the user.
        const userExists = await wallet.exists('user1');
        if (!userExists) {
            console.log('An identity for the user "user1" does not exist in the wallet');
            console.log('Run the registerUser.js application before retrying');
            return;
        }

        // Create a new gateway for connecting to our peer node.
        const gateway = new Gateway();
        await gateway.connect(ccp, { wallet, identity: 'user1', discovery: { enabled: false } });

        // Get the network (channel) our contract is deployed to.
        const network = await gateway.getNetwork('mychannel');

        // Get the contract from the network.
        const contract = network.getContract('fabpmu');

	var str = process.argv[2];      
	if (str.indexOf("P",0) == 0) {
 	await contract.submitTransaction('createPMU', time, process.argv[2], process.argv[3], process.argv[4], process.argv[5], process.argv[6], process.argv[7], process.argv[8], process.argv[9], process.argv[10], process.argv[11], process.argv[12], process.argv[13], process.argv[14]);
	} else if (str.indexOf("I",0) == 0) {
        await contract.submitTransaction('createInverter', time, process.argv[2], process.argv[3], process.argv[4], process.argv[5]);
	} else {
	console.log('* Unknown Device ID is submitted *');
	}
        console.log('Transaction has been submitted');



        // Disconnect from the gateway.
        await gateway.disconnect();

    } catch (error) {
        console.error(`Failed to submit transaction: ${error}`);
        process.exit(1);
    }
}

main();
