""" Plots our objective and constraint histories from the current data in
data.dmp. You can do this while the model is running."""

from six.moves import range
import sqlitedict
import numpy as np
from matplotlib import pylab
import matplotlib.pyplot as plt

def extract_all_vars_sql(name):
    """ Reads in the file given in name and extracts all variables."""

    db = sqlitedict.SqliteDict( name, 'openmdao' )

    data = {}
    for iteration in range(len(db)):
        iteration_coordinate = 'SNOPT/{}'.format(iteration + 1 )

        record = db[iteration_coordinate]

        for key, value in record['Unknowns'].items():
            if key not in data:
                data[key] = []
            data[key].append(value)

    return data

def extract_all_vars(name):
    """ Reads in the file given in name and extracts all variables."""

    file = open(name)
    data = {}
    record_flag = False
    for line in file:

        if line.startswith('Unknowns'):
            record_flag = True
            continue
        elif line.startswith('Resids:'):
            record_flag = False
            continue

        if record_flag is True:
            key, value = line.split(':')
            key = key.lstrip()
            if key not in data:
                data[key] = []
            data[key].append(float(value.lstrip().replace('\n', '')))

    return data

#filename = 'data.dmp' # use this when plotting the results of a serial run
#filename = 'data_0.dmp' # use this when plotting the results of a parallel run

filename_sql = 'data.sql'

#data = extract_all_vars(filename) # uncomment and use this if you want to plot a dump recorder file
data = extract_all_vars_sql(filename_sql)

if 'pt1.ConCh' in data:
    serial_run = True
else:
    serial_run = False

if serial_run:
    n_point = (len(data) - 1)/5
    n_point = 6
else:
    n_point = len(data) - 1

# X = data['pt1.P_comm']
# print np.shape(X)

# Plot total data
if 1:
    x = np.arange(0,12,12./1500.)
    plt.figure(1 , figsize=(45,6))
    for ip in range(n_point):
        if serial_run:
            y = data['pt%d.Data' % ip]

        plt.subplot(161+ip)
        plt.plot(x , y[np.shape(y)[0]-1][0]/1000)
        plt.axis([0, 12, 0, 6])
        plt.xlabel('Time [hr] (month %d)' % (ip*2+1))
        if ip==0:
            plt.ylabel('Total data [Gb]')
    plt.savefig('1_Total_data.png', dpi=300)
    #plt.show()

# Plot Comm. power
if 1:
    x = np.arange(0,12,12./300.)
    plt.figure(2, figsize=(45,6))
    for ip in range(n_point):
        if serial_run:
            y = data['pt%d.CP_P_comm' % ip]

        plt.subplot(161+ip)
        plt.plot(x , y[np.shape(y)[0]-1])
        plt.axis([0, 12, 0, 30])
        plt.xlabel('Time [hr] (month %d)' % (ip*2+1))
        if ip==0:
            plt.ylabel('Comm. power [W]')
    plt.savefig('2_Comm_power.png', dpi=300)
    #plt.show()

# Plot transmitter gain
if 1:
    x = np.arange(0,12,12./1500.)
    plt.figure(3, figsize=(45,6))
    for ip in range(n_point):
        if serial_run:
            y = data['pt%d.gain' % ip]

        plt.subplot(161+ip)
        plt.plot(x , y[np.shape(y)[0]-1])
        plt.axis([0, 12, 0, 1.2])
        plt.xlabel('Time [hr] (month %d)' % (ip*2+1))
        if ip==0:
            plt.ylabel('Transmitter gain')
    plt.savefig('3_Transmitter_gain.png', dpi=300)
    #plt.show()

# Plot Roll angle
if 1:
    x = np.arange(0,12,12./300.)
    plt.figure(4, figsize=(45,6))
    for ip in range(n_point):
        if serial_run:
            y = data['pt%d.CP_gamma' % ip]

        plt.subplot(161+ip)
        plt.plot(x , y[np.shape(y)[0]-1]/np.pi*180)
        plt.xlabel('Time [hr] (month %d)' % (ip*2+1))
        plt.plot([0 , 12] , [45 , 45])
        if ip==0:
            plt.ylabel('Roll Angle [deg]')
    plt.savefig('4_Roll_angle.png', dpi=300)
    #plt.show()

# Plot state of charge
if 1:
    x = np.arange(0,12,12./1500.)
    plt.figure(5, figsize=(45,6))
    for ip in range(n_point):
        if serial_run:
            y = data['pt%d.SOC' % ip]

        plt.subplot(161+ip)
        plt.plot(x , y[np.shape(y)[0]-1][0]*100)
        plt.axis([0, 12, 0, 100])
        plt.xlabel('Time [hr] (month %d)' % (ip*2+1))
        if ip==0:
            plt.ylabel('SOC [%]')
    plt.savefig('5_State_of_charge.png', dpi=300)
    #plt.show()

# Plot solar power
if 1:
    x = np.arange(0,12,12./1500.)
    plt.figure(6, figsize=(45,6))
    for ip in range(n_point):
        if serial_run:
            y = data['pt%d.P_sol' % ip]

        plt.subplot(161+ip)
        plt.plot(x , y[np.shape(y)[0]-1])
        plt.xlabel('Time [hr] (month %d)' % (ip*2+1))
        plt.axis([0, 12, -1, 6])
        if ip==0:
            plt.ylabel('Solar power [W]')
    plt.savefig('6_Solar_power.png', dpi=300)
    #plt.show()

#Plot Isetpt
if 1:
    x = np.arange(0,12,12./300.)
    yy = np.zeros(300)
    plt.figure(7, figsize=(45,6))
    for ip in range(n_point):
        if serial_run:
            y = data['pt%d.CP_Isetpt' % ip]

        for i in range(300): # Find max current at each time instance
            s = np.shape(y)[0]-1
            yy[i] = max(y[s][0][i] , y[s][1][i] , y[s][2][i] , y[s][3][i] ,
                        y[s][4][i] , y[s][5][i] , y[s][6][i] , y[s][7][i] ,
                        y[s][8][i] , y[s][9][i] , y[s][10][i] , y[s][11][i])

        plt.subplot(161+ip)
        plt.plot(x , yy)
        plt.plot([0 , 12] , [0.2 , 0.2])
        plt.axis([0, 12, 0, 0.4])
        plt.xlabel('Time [hr] (month %d)' % (ip*2+1))
        if ip==0:
            plt.ylabel('Max. panel curr. [A]')
    plt.savefig('7_Max_panel_curr.png', dpi=300)
    #plt.show()

#Plot Exp. area
if 1:
    x = np.arange(0,12,12./1500.)
    plt.figure(8, figsize=(45,6))
    for ip in range(n_point):
        yy = np.zeros(1500)
        if serial_run:
            y = data['pt%d.exposedArea' % ip]
            s = np.shape(y)[0]-1
        for i in range(1500):
            for j in range(7):
                for k in range(12):
                    yy[i] += y[s][j][k][i]

        plt.subplot(161+ip)
        plt.plot(x , yy*1000)
        plt.axis([0, 12, 30, 70])
        plt.xlabel('Time [hr] (month %d)' % (ip*2+1))
        if ip==0:
            plt.ylabel('Exp. area [10e-3 m^2]')
    plt.savefig('8_Exp_area.png', dpi=300)
    #plt.show()

# Plot body temp
if 1:
    x = np.arange(0,12,12./1500.)
    plt.figure(9, figsize=(45,6))
    for ip in range(n_point):
        if serial_run:
            y = data['pt%d.temperature' % ip]

        plt.subplot(161+ip)
        plt.plot(x , y[np.shape(y)[0]-1][4])
        plt.axis([0, 12, 230, 310])
        plt.xlabel('Time [hr] (month %d)' % (ip*2+1))
        if ip==0:
            plt.ylabel('Body temp. [K]')
    plt.savefig('9_Body_temp.png', dpi=300)
    #plt.show()

# Plot transmitter gain
if 1:
    x = np.arange(0,12,12./1500.)
    plt.figure(10, figsize=(45,6))
    for ip in range(n_point):
        if serial_run:
            y = data['pt%d.I_bat' % ip]

        plt.subplot(161+ip)
        plt.plot(x , y[np.shape(y)[0]-1])
        plt.axis([0, 12, -10, 2.5])
        plt.xlabel('Time [hr] (month %d)' % (ip*2+1))
        if ip==0:
            plt.ylabel('Battery current [A]')
    plt.savefig('10_Battery_current.png', dpi=300)
    #plt.show()

# Y = []
# Z = []
# for ic in range(ncase):
#     c1 = c2 = c3 = c4 = c5 = 0
#     for ip in range(n_point):
#         if serial_run:
#             c1 += data['pt%d.ConCh' % ip][ic]
#             c2 += data['pt%d.ConDs' % ip][ic]
#             c3 += data['pt%d.ConS0' % ip][ic]
#             c4 += data['pt%d.ConS1' % ip][ic]
#         c5 += data['pt%d_con5.val' % ip][ic]
#
#     if serial_run:
#         feasible = [c1, c2, c3, c4, c5]
#     else:
#         feasible = [c5,]
#
#     Y.append(sum(feasible))
#     Z.append(feasible)

# Z = np.array(Z)
# if not len(Z):
#     print "no data yet..."
#     quit()
# pylab.figure()
# pylab.subplot(311)
# pylab.title("total data")
# pylab.plot(X, 'b')
# #pylab.plot([0, len(X)], [3e4, 3e4], 'k--', marker="o")
# pylab.subplot(312)
# pylab.title("Sum of Constraints")
# pylab.plot([0, len(Y)], [0, 0], 'k--', marker="o")
# pylab.plot(Y, 'k')
# pylab.subplot(313)
# pylab.title("Max of Constraints")
# pylab.plot([0, len(Z)], [0, 0], 'k--')
# if serial_run:
#     pylab.plot(Z[:, 0], marker="o", label="ConCh")
#     pylab.plot(Z[:, 1], marker="o", label="ConDs")
#     pylab.plot(Z[:, 2], marker="o", label="ConS0")
#     pylab.plot(Z[:, 3], marker="o", label="ConS1")
#     pylab.plot(Z[:, 4], marker="o", label="c5")
# else:
#     pylab.plot(Z[:, 0], marker="o", label="c5")
#
# pylab.legend(loc="best")
#
# pylab.show()
