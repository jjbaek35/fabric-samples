/*
 * SPDX-License-Identifier: Apache-2.0
 * by JJ
 */

'use strict';

const { Contract } = require('fabric-contract-api');

class FabPMU extends Contract {

    async initLedger(ctx) {
        console.info('============= START : Initialize Ledger ===========');
        const pmus = [
            {
                dt: '1111/11/11/2019',
                voltage: 10.05,
                current: 10.05,
                resistance: 10.05,
            },
            {
                dt: '1112/11/11/2019',
                voltage: 10.05,
                current: 10.05,
                resistance: 10.05,
            },            
        ];

        for (let i = 0; i < pmus.length; i++) {
            pmus[i].devType = 'pmu';
            await ctx.stub.putState('PMU' + i, Buffer.from(JSON.stringify(pmus[i])));
            console.info('Added <--> ', pmus[i]);
        }
        console.info('============= END : Initialize Ledger ===========');
    }

    async queryPMU(ctx, pmuNumber) {
        const pmuAsBytes = await ctx.stub.getState(pmuNumber); // get the pmu from chaincode state
        if (!pmuAsBytes || pmuAsBytes.length === 0) {
            throw new Error(`${pmuNumber} does not exist`);
        }
        console.log(pmuAsBytes.toString());
        return pmuAsBytes.toString();
    }

    async createPMU(ctx, pmuNumber, dt, voltage, current, resistance) {
        console.info('============= START : Create pmu ===========');

        const pmu = {
            dt,    // date and time
            devType: 'pmu',  // device type
            voltage,
            current,
            resistance,
        };

        await ctx.stub.putState(pmuNumber, Buffer.from(JSON.stringify(pmu)));
        //await ctx.stub.putState(pmuNumber, Buffer.from(pmu);
        console.info('============= END : Create pmu ===========');
    }

    async queryAllPMUs(ctx) {
        const startKey = 'PMU0';
        const endKey = 'PMU999';

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

    async changePMUOwner(ctx, pmuNumber, newOwner) {
        console.info('============= START : changepmuresistance ===========');

        const pmuAsBytes = await ctx.stub.getState(pmuNumber); // get the pmu from chaincode state
        if (!pmuAsBytes || pmuAsBytes.length === 0) {
            throw new Error(`${pmuNumber} does not exist`);
        }
        const pmu = JSON.parse(pmuAsBytes.toString());
        pmu.resistance = newOwner;

        await ctx.stub.putState(pmuNumber, Buffer.from(JSON.stringify(pmu)));
        console.info('============= END : changepmuresistance ===========');
    }

}

module.exports = FabPMU;
