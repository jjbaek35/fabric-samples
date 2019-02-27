/*
 * SPDX-License-Identifier: Apache-2.0
 * JJ
 */

'use strict';
const args = process.argv; // for arguments processing


const dt = require('date-utils');
var newDate = new Date();
var time = newDate.toFormat('MM-DD-YYYY HH24:MI:SS');


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

        // Submit the specified transaction.
        // createCar transaction - requires 5 argument, ex: ('createPMU', 'PMU2', 'Honda', 'Accord', 'Black', 'Tom')
        // changeCarOwner transaction - requires 2 args , ex: ('changePMUOwner', 'CAR1', 'Dave')

        //await contract.submitTransaction('changePMUOwner', 'PMU0', 'SINE');
        // console.log('Transaction has been submitted');        


        // for (let i = 0; i < cars.length; i++) {
            for (let i = 0; i < 10; i++) {
            //cars[i].docType = 'car';
            //await ctx.stub.putState('CAR' + i, Buffer.from(JSON.stringify(cars[i])));
            //console.info('Added <--> ', cars[i]);

            await contract.submitTransaction('createPMU', 'PMU'+i, time, '150.00', '150.00', '150.00');
            console.log('Transaction has been submitted\n');
        } 

//        await contract.submitTransaction('createCar', 'PMU0', 'Honda', 'Accord', 'Black', 'Tom');
       
//        console.log('Transaction has been submitted');

        // arguments
        // await contract.submitTransaction('createPMU', process.argv[2], process.argv[3], process.argv[4], process.argv[5], process.argv[6]);
        

        


        
        console.log('Transaction has been submitted');



        // Disconnect from the gateway.
        await gateway.disconnect();

    } catch (error) {
        console.error(`Failed to submit transaction: ${error}`);
        process.exit(1);
    }
}

main();
