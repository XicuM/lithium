import threading as th
import config as p
from time import sleep
import pandas as pd
from abc import ABC, abstractmethod

class Monitor(ABC):
    def __init__(self):
        self.online = False
        self.thread = None

    def start(self):
        self.online = True
        self.thread = th.Thread(target=self.monitor_loop)
        self.thread.daemon = True
        self.thread.start()
        
    def is_online(self):
        return self.online
    
    @abstractmethod
    def stop(self):
        self.online = False
        pass
    
    @abstractmethod
    def monitor_loop(self): pass

# ----------------------------------------------------------------------
# CAN Monitor

class CANMonitor(Monitor):
    '''
    Monitors the CAN bus to extract data using the canlib library
    '''

    def __init__(self):
        from canlib import canlib, kvadblib

        self.channel = canlib.openChannel(
            channel=0, 
            bitrate=canlib.canBITRATE_500K
        )
        self.channel.setBusOutputControl(canlib.canDRIVER_SILENT)
        self.channel.busOn()
        
        self.db = kvadblib.Dbc('dbc/CAN4DB_CAT16x.dbc')

        self.data = {}
        self.ts = {}

        self.online = False

    # def __del__(self):
    #     self.channel.close()

    def get_data(self):
        return self.data

    def monitor_loop(self, speed):
        while self.online:
            for bsig in self.db.interpret(self.channel.read(timeout=1000)):
                if (
                    bsig.name.startswith('Cell') or # Monitor voltages
                    bsig.name.startswith('ntc') or  # Monitor temperatures
                    bsig.name=='ChargingCurr'       # Monitor charging current
                ):
                    self.data[bsig.name] = bsig.value

# ----------------------------------------------------------------------
# ROS Monitor

class ROSData:

    def __init__(self): self.data = {}

    def save_topic(self, x): 
        # Adapt from ROS nomenclature to our nomenclature
        for label in [
            # Voltage labels
            'V_0_14_Slave1_spi3',       'V_14_27_Slave1_spi2',
            'V_27_40_Slave2_spi3',      'V_40_54_Slave2_spi2',
            'V_54_68_Slave3_spi3',      'V_68_81_Slave3_spi2',
            'V_81_94_Slave4_spi3',      'V_94_108_Slave4_spi2',
            'V_108_122_Slave5_spi3',    'V_122_135_Slave5_spi2',
            # Temperature labels
            'T_cells_Slave1_spi2',      'T_cells_Slave1_spi3',
            'T_cells_Slave2_spi3',      'T_cells_Slave2_spi3',
            'T_cells_Slave3_spi3',      'T_cells_Slave3_spi3',
            'T_cells_Slave4_spi3',      'T_cells_Slave4_spi3',
            'T_cells_Slave5_spi3',      'T_cells_Slave5_spi3'
        ]:
            if label.startswith('V_'):
                # Organize voltages
                for cell in p.RANGE_CELLS:
                    try:
                        new_label = 'Cell{cell}_s{slave}_spi{spi}'.format(
                            cell=cell,                      # Cell number
                            slave=label.split('_')[3][-1],  # Slave number
                            spi=label.split('_')[4][-1]     # SPI number
                        )
                        self.data[new_label] = x[label][cell-1]
                    except: self.data[new_label] = 0

            elif label.startswith('T_'):
                # Organize temperatures
                for ntc in p.RANGE_NTCS:
                    try:
                        new_label = 'ntc{nt}_s{slave}_spi{spi}'.format(
                            ntc=ntc,                        # ntc number
                            slave=label.split('_')[3][-1],  # Slave number
                            spi=label.split('_')[4][-1]     # SPI number
                        )
                        self.data[new_label] = x[label][ntc-1]
                    except: self.data[new_label] = 0

    def obtain(self): return self.data


class ROSMonitor(Monitor):
    '''
    Uses the ROS library to connect to ROS and read from the Accumulator
    Static topic.
    '''
    import roslibpy

    def __init__(self, IP, port=9090):
        self.client = self.roslibpy.Ros(IP, port)
        self.client.run(timeout=0.5)
        self.data = ROSData()
        self.online = False

    def start(self):    # TODO: implement online check
        self.roslibpy.Topic(
            self.client,
            '/EL/Accumulator/AccumulatorStatusDetailed',
            'el_msgs/BatteryStatusDetailed'
        ).subscribe(self.data.save_topic)

    def get_data(self): return self.data.obtain()

    # def __del__(self):
    #     self.client.terminate()

# ----------------------------------------------------------------------
# File Monitor

class FileMonitor(Monitor):
    '''
    Reads a file as it was real time data    
    '''

    def __init__(self, file, speed=1):
        self.df = pd.read_csv(file, index_col=0)
        self.data = {}
        self.speed = speed
        self.online = False
    
    def monitor_loop(self):
        for i in range(len(self.df.index)):
            if not self.online: break
            self.data = self.df.iloc[i].to_dict()
            sleep(1/self.speed)
        self.online = False
    
    def get_data(self): return self.data


class ROSFileMonitor(Monitor):
    '''
    Reads a ROS gemearted file as it was real time data    
    '''

    def __init__(self, file, speed=1):
        self.df = pd.read_csv(file, index_col=0)
        self.data = ROSData()
        self.speed = speed
        self.online = False
    
    def monitor_loop(self):
        for i in range(len(self.df.index)):
            if not self.online: break
            self.data = self.df.iloc[i].to_dict()
            sleep(1/self.speed)
        self.online = False
    
    def get_data(self): return self.data.obtain()