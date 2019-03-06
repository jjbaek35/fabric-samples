import numpy as np
import opendssdirect as dss
import random


def lossless_distribution_power_flow(dflow, inverter_list, total_iteration=300, tol=1e-3):
    # voltage=dflow.slack_voltage**2 + dflow.R.dot(np.transpose(dflow.pc-pg)) + dflow.X.dot(np.transpose(dflow.qc-qg))
    # voltage=np.sqrt(np.insert(voltage, 0, dflow.slack_voltage**2))
    v = np.zeros(shape=(total_iteration, dflow.nb))
    pg = np.zeros(dflow.pc.shape)
    qg = np.zeros(dflow.qc.shape)

    for iteration in range(0, total_iteration):
        if iteration == 0:
            voltage = dflow.slack_voltage ** 2 + dflow.R.dot(np.transpose(dflow.pc)) + dflow.X.dot(
                np.transpose(dflow.qc))
            voltage = np.sqrt(np.insert(voltage, 0, dflow.slack_voltage ** 2))
        else:
            for i in range(len(inverter_list)):
                n = inverter_list[i].node
                pg[n] = inverter_list[i].p_curve(voltage[n])
                qg[n] = inverter_list[i].q_curve(voltage[n])
            voltage = dflow.slack_voltage ** 2 + dflow.R.dot(np.transpose(dflow.pc - pg)) + dflow.X.dot(
                np.transpose(dflow.qc - qg))
            voltage = np.sqrt(np.insert(voltage, 0, dflow.slack_voltage ** 2))
        v[iteration, :] = voltage
        # print('Iteration:'+ str(itr))
        # print('Voltage:'+str(voltage))
        if iteration > 0:
            diff_voltage = abs(v[iteration, :] - v[iteration - 1, :])
            if max(diff_voltage) < tol:
                for inverter in inverter_list:
                    inverter.update_voltage(voltage[inverter.node])
                    # inverterlist[i].updateRegister()
                break
    return voltage


def opendss_power_flow(filename='Inverter_PMU.dss'):

    dss.run_command('Compile ' + filename)
    # dss.Text.Command('Set Loadmult= {}'.format(random.uniform(0.85,1.15)))
    # dss.Text.Command('BatchEdit PVSystem..* pctPmpp={}'.format(random.uniform(80,95)))
    dss.Solution.Solve()

    return dss
