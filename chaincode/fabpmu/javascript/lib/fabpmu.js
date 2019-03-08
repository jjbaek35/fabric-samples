/*
 * SPDX-License-Identifier: Apache-2.0
 * by JJ
 */

'use strict';

const { Contract } = require('fabric-contract-api'); //SDK library to asset with writing the logic

class FabPMU extends Contract {

    async initLedger(ctx) {
        console.info('============= START : Initialize Ledger ===========');
        const pmus = [
         /* {
                dt: '02-13-2019 13:30:44',
                current: 10.05,
                resistance: 10.05,
                voltage: 10.05,  
            },
            {
                dt: '02-13-2019 13:30:44',
                current: 10.05,
                resistance: 10.05,
                voltage: 10.05,                
            },   */       
        ];

        for (let i = 0; i < pmus.length; i++) {
            pmus[i].devType = 'pmu';
            await ctx.stub.putState('PMU' + i, Buffer.from(JSON.stringify(pmus[i])));
            console.info('Added <--> ', pmus[i]);
        }
        console.info('============= END : Initialize Ledger ===========');
    }

    async queryPMU(ctx,devID) {
        const pmuAsBytes = await ctx.stub.getState(devID); // get the pmu from chaincode state
        if (!pmuAsBytes || pmuAsBytes.length === 0) {
            throw new Error(`${devID} does not exist`);
        }
        console.log(pmuAsBytes.toString());
        return pmuAsBytes.toString();
    }


    async createPMU(ctx, dt, devID, V1M, V1A, V2M, V2A, V3M, V3A, I1M, I1A, I2M, I2A, I3M, I3A) {
        console.info('============= START : Create pmu ===========');

        const pmu = {
            devID,    // deviceID (P or I + zip + number)
            devType: 'pmu',  // device type
            V1M,
            V1A,
            V2M,
            V2A,
            V3M,
            V3A,
            I1M,
            I1A,
            I2M,
            I2A,
            I3M,
            I3A,
        };

        await ctx.stub.putState(dt, Buffer.from(JSON.stringify(pmu)));
        console.info('============= END : Create PMU ===========');
    }

    async createInverter(ctx, dt, devID, V, P, Q) {
        console.info('============= START : Create inverter ===========');

        const inverter = {
            devID,    // deviceID (P or I + zip + number)
            devType: 'inverter',  // device type
            V,
            P,
            Q,
        };

        await ctx.stub.putState(dt, Buffer.from(JSON.stringify(inverter)));
        console.info('============= END : Create inverter ===========');
    }

    async queryAllPMUs(ctx) {
        const startKey = '2019-01-01-00:00:00';
        const endKey = '2029-01-01-00:00:00';

        const iterator = await ctx.stub.getStateByRange(startKey, endKey);

        const allResults = [];
        while (true) {
            const res = await iterator.next();

            if (res.value && res.value.value.toString()) {
                console.log(res.value.value.toString('utf8'));
                const Key = res.value.key;
                let Record;
                try {
                    Record = JSON.parse(res.value.value.toString('utf8'));
                } catch (err) {
                    console.log(err);
                    Record = res.value.value.toString('utf8');
                }
                allResults.push({ Key, Record});
            }
            if (res.done) {
                console.log('end of data');
                await iterator.close();
                console.info(allResults);
                return JSON.stringify(allResults);
            }
        }
    }

    async changePMUOwner(ctx, devID, newOwner) {
        console.info('============= START : changepmuresistance ===========');

        const pmuAsBytes = await ctx.stub.getState(devID); // get the devID from chaincode state
        if (!pmuAsBytes || pmuAsBytes.length === 0) {
            throw new Error(`${devID} does not exist`);
        }
        const pmu = JSON.parse(pmuAsBytes.toString());
        pmu.resistance = newOwner;

        await ctx.stub.putState(devID, Buffer.from(JSON.stringify(pmu)));
        console.info('============= END : changepmuresistance ===========');
    }
}

module.exports = FabPMU;
