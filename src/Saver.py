from time import time, sleep, strftime
import config as p
import threading as th

class Saver:

    def __init__(self, monitor, ts=1):
        self.monitor = monitor
        self.file = strftime('data/%Y%m%d_%H%M.csv')
        self.t0 = time()
        self.ts = ts
        
        # Save monitor data to a file
        with open(self.file, 'w') as f:
            f.write(
                'time,' + ','.join([f'Cell{k}_s{i}_spi{j}' for i, j, k in p.RANGE_VBAT])
                + ',' + ','.join([f'ntc{k}_slave{i}_spi{j}' for i, j, k in p.RANGE_TBAT])
                + ',ChargingCurr\n'
            )

    def start(self):
        thread = th.Thread(target=self.save_loop)
        thread.daemon = True
        thread.start()

    def save_loop(self):
        while True:
            sleep(self.ts)
            with open(self.file, 'a') as f:
                row = [str(time()-self.t0)]
                data = self.monitor.get_data()

                # Voltages
                for i, j, k in p.RANGE_VBAT:
                    try: row.append(str(data[f'Cell{k}_s{i}_spi{j}']))
                    except: row.append(str(0))

                # # Temperatures
                # for i, j, k in p.RANGE_TBAT:
        #             try: row.append(str(data[f'ntc{k}_slave{i}_spi{j}']))
        #             except: row.append(str(0))

                # # Current
                # row.append(str(data['ChargingCurr']))

                f.write(','.join(row)+'\n')

if __name__=='__main__':
    from classes.Monitor import CANMonitor
    file = strftime('data/%Y%m%d_%H%M.csv')
    Saver(CANMonitor()).save_loop()