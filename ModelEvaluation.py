import numpy as np

class Evaluator:
    def __init__(self):
        self.network = None
        self.output = dict()
        self.average = dict()
        self.num_trials = 0
        self.end_time = 0.
        self.delta_t = 0.
    
    def initialize(self, network) -> None:
        self.network = network
        self.output["avg_wait_time"] = {}
        # add avg_clearance_rate_xx, arrival_on_green_rate, tot_switches_xx
        
        for grid_ind in network.grid_inds:
            self.output[grid_ind] = {}
            self.output[grid_ind]["avg_clearance_rate_ns"] = {}
            self.output[grid_ind]["avg_clearance_rate_ew"] = {}
            self.output[grid_ind]["tot_switches_ns"] = {}
            self.output[grid_ind]["tot_switches_ew"] = {}
            self.output[grid_ind]["arrivals_on_green_rate"] = {}
            self.output[grid_ind]["N"] = {"avg_wait_time": {}, "queue_length": {}}
            self.output[grid_ind]["E"] = {"avg_wait_time": {}, "queue_length": {}}
            self.output[grid_ind]["S"] = {"avg_wait_time": {}, "queue_length": {}}
            self.output[grid_ind]["W"] = {"avg_wait_time": {}, "queue_length": {}}
        
    def simulate(self, num_trials: int, end_time: float, delta_t: float) -> dict():
        self.num_trials = num_trials
        self.end_time = end_time
        self.delta_t = delta_t
        enumerations = list(zip(np.concatenate([[i]*len(self.network.grid_inds) for i in range(num_trials)]), self.network.grid_inds*num_trials))
        last_trial = -1
        
        for trial, grid_ind in enumerations:
            if trial != last_trial:
                network = self.network.reset()
                network.simulate(delta_t=delta_t, end_time=end_time, animate=False)
                
                if trial != 0 and trial % 10  == 0:
                    print("Finished", trial, "trials.")
            last_trial = trial
            
            self.output["avg_wait_time"][trial] = network.avg_wait_time
            
            self.output[grid_ind]["avg_clearance_rate_ns"][trial] = network.intersections[grid_ind].avg_clearance_rate_ns
            self.output[grid_ind]["avg_clearance_rate_ew"][trial] = network.intersections[grid_ind].avg_clearance_rate_ew
            self.output[grid_ind]["tot_switches_ns"][trial] = network.intersections[grid_ind].traffic_light_ns.num_switches
            self.output[grid_ind]["tot_switches_ew"][trial] = network.intersections[grid_ind].traffic_light_ew.num_switches
            self.output[grid_ind]["arrivals_on_green_rate"][trial] = network.intersections[grid_ind].arrivals_on_green_rate
            
            self.output[grid_ind]["N"]["avg_wait_time"][trial] = network.intersections[grid_ind].queue_n.avg_wait_time()
            self.output[grid_ind]["N"]["queue_length"][trial] = network.intersections[grid_ind].queue_n.queue_length[1:]
            self.output[grid_ind]["E"]["avg_wait_time"][trial] = network.intersections[grid_ind].queue_e.avg_wait_time()
            self.output[grid_ind]["E"]["queue_length"][trial] = network.intersections[grid_ind].queue_e.queue_length[1:]
            self.output[grid_ind]["S"]["avg_wait_time"][trial] = network.intersections[grid_ind].queue_s.avg_wait_time()
            self.output[grid_ind]["S"]["queue_length"][trial] = network.intersections[grid_ind].queue_s.queue_length[1:]
            self.output[grid_ind]["W"]["avg_wait_time"][trial] = network.intersections[grid_ind].queue_w.avg_wait_time()
            self.output[grid_ind]["W"]["queue_length"][trial] = network.intersections[grid_ind].queue_w.queue_length[1:]
            
        print("Finished", self.num_trials, "trials.")
            
        return self.output
    
    def compute_average(self) -> dict():
        data_length = int(self.end_time/self.delta_t)
        
        self.average["avg_wait_time"] = ([sum([wait_time[i] for wait_time in self.output["avg_wait_time"].values()])/self.num_trials for i in range(data_length)])
        
        for grid_ind in self.network.grid_inds:
            self.average[grid_ind] = {}
            
            self.average[grid_ind]["avg_clearance_rate_ns"] = [sum([rate[i]/self.num_trials for rate in self.output[grid_ind]["avg_clearance_rate_ns"].values()]) for i in range(data_length)]
            self.average[grid_ind]["avg_clearance_rate_ew"] = [sum([rate[i]/self.num_trials for rate in self.output[grid_ind]["avg_clearance_rate_ew"].values()]) for i in range(data_length)]
            self.average[grid_ind]["avg_clearance_rate"] = [(self.average[grid_ind]["avg_clearance_rate_ns"][i]+self.average[grid_ind]["avg_clearance_rate_ew"][i])/2 for i in range(data_length)]
            self.average[grid_ind]["tot_switches_ns"] = [sum([switches[i]/self.num_trials for switches in self.output[grid_ind]["tot_switches_ns"].values()]) for i in range(data_length)]
            self.average[grid_ind]["tot_switches_ew"] = [sum([switches[i]/self.num_trials for switches in self.output[grid_ind]["tot_switches_ew"].values()]) for i in range(data_length)]
            self.average[grid_ind]["arrivals_on_green_rate"] = [sum([rate[i]/self.num_trials for rate in self.output[grid_ind]["arrivals_on_green_rate"].values()]) for i in range(data_length)]
            
            self.average[grid_ind]["N"] = {"avg_wait_time": 0., "avg_queue_length": 0., "queue_length": []}
            self.average[grid_ind]["E"] = {"avg_wait_time": 0., "avg_queue_length": 0., "queue_length": []}
            self.average[grid_ind]["S"] = {"avg_wait_time": 0., "avg_queue_length": 0., "queue_length": []}
            self.average[grid_ind]["W"] = {"avg_wait_time": 0., "avg_queue_length": 0., "queue_length": []}
            
            self.average[grid_ind]["N"]["avg_wait_time"] = sum(self.output[grid_ind]["N"]["avg_wait_time"].values())/self.num_trials
            self.average[grid_ind]["E"]["avg_wait_time"] = sum(self.output[grid_ind]["E"]["avg_wait_time"].values())/self.num_trials
            self.average[grid_ind]["S"]["avg_wait_time"] = sum(self.output[grid_ind]["S"]["avg_wait_time"].values())/self.num_trials
            self.average[grid_ind]["W"]["avg_wait_time"] = sum(self.output[grid_ind]["W"]["avg_wait_time"].values())/self.num_trials
            
            #self.average[grid_ind]["avg_wait_time"] = sum([self.average[grid_ind][direction]["avg_wait_time"] for direction in ["N", "E", "S", "W"]])/4
            
            self.average[grid_ind]["N"]["avg_queue_length"] = sum([sum(self.output[grid_ind]["N"]["queue_length"][i])/len(self.output[grid_ind]["N"]["queue_length"][i]) for i in range(self.num_trials)])/self.num_trials
            self.average[grid_ind]["E"]["avg_queue_length"] = sum([sum(self.output[grid_ind]["E"]["queue_length"][i])/len(self.output[grid_ind]["E"]["queue_length"][i]) for i in range(self.num_trials)])/self.num_trials
            self.average[grid_ind]["S"]["avg_queue_length"] = sum([sum(self.output[grid_ind]["S"]["queue_length"][i])/len(self.output[grid_ind]["S"]["queue_length"][i]) for i in range(self.num_trials)])/self.num_trials
            self.average[grid_ind]["W"]["avg_queue_length"] = sum([sum(self.output[grid_ind]["W"]["queue_length"][i])/len(self.output[grid_ind]["W"]["queue_length"][i]) for i in range(self.num_trials)])/self.num_trials
            
            #self.average[grid_ind]["avg_queue_length"] = sum([self.average[grid_ind][direction]["avg_queue_length"] for direction in ["N", "E", "S", "W"]])/4
            
            self.average[grid_ind]["N"]["queue_length"] = [sum([queue_length[i]/self.num_trials for queue_length in self.output[grid_ind]["N"]["queue_length"].values()]) for i in range(data_length)]
            self.average[grid_ind]["E"]["queue_length"] = [sum([queue_length[i]/self.num_trials for queue_length in self.output[grid_ind]["E"]["queue_length"].values()]) for i in range(data_length)]
            self.average[grid_ind]["S"]["queue_length"] = [sum([queue_length[i]/self.num_trials for queue_length in self.output[grid_ind]["S"]["queue_length"].values()]) for i in range(data_length)]
            self.average[grid_ind]["W"]["queue_length"] = [sum([queue_length[i]/self.num_trials for queue_length in self.output[grid_ind]["W"]["queue_length"].values()]) for i in range(data_length)]
            
        return self.average
            
            
    def plot_avg_wait_time(self, plt, fig_size: (float, float)):
        fig,ax = plt.subplots(figsize=fig_size, dpi=90)
        t = np.arange(0.,self.end_time,self.delta_t)

        ax.plot(t,self.average["avg_wait_time"])

        ax.set(xlabel="time [s]", ylabel="avg. wait time [s]")
        ax.set_title("Average wait time over time")
        
        return fig,ax
    
    def plot_avg_clearance_rate(self, plt, grid_ind, fig_size: (float, float)):
        fig, ax = plt.subplots(figsize=fig_size, dpi=90)
        
        t = np.arange(0.,self.end_time,self.delta_t)
        
        ax.plot(t, self.average[grid_ind]["avg_clearance_rate_ns"], label="NS")
        ax.plot(t, self.average[grid_ind]["avg_clearance_rate_ew"], label="EW")
        ax.set(xlabel="time [s]", ylabel='avg. clearance rate')
        ax.set_title('Average clearance rate over time')
        ax.label_outer()
        ax.legend()

        return fig, ax
    
    def plot_avg_arrivals_on_green_rate(self, plt, grid_ind, fig_size: (float, float)):
        fig,ax = plt.subplots(figsize=fig_size, dpi=90)
        t = np.arange(0.,self.end_time,self.delta_t)

        ax.plot(t,self.average[grid_ind]["arrivals_on_green_rate"])

        ax.set(xlabel="time [s]", ylabel="avg. wait time [s]")
        ax.set_title("Average proportion arriving on green over time")
        
        return fig,ax
        
    def plot_queue_lengths(self, plt, grid_ind: (int, int), fig_size: (float, float)):
        fig,axs = plt.subplots(4, figsize=fig_size, dpi=90, sharex=True)
        t = np.arange(0.,self.end_time,self.delta_t)

        axs[0].plot(t,self.average[grid_ind]["N"]["queue_length"])
        axs[1].plot(t,self.average[grid_ind]["E"]["queue_length"])
        axs[2].plot(t,self.average[grid_ind]["S"]["queue_length"])
        axs[3].plot(t,self.average[grid_ind]["W"]["queue_length"])

        axs[0].set(ylabel="avg. wait time [s]")
        axs[0].set_title("Average length of northbound queue over time")
        axs[1].set(ylabel="avg. wait time [s]")
        axs[1].set_title("Average length of eastbound queue over time")
        axs[2].set(ylabel="avg. wait time [s]")
        axs[2].set_title("Average length of southbound queue over time")
        axs[3].set(xlabel="time [s]", ylabel="avg. wait time [s]")
        axs[3].set_title("Average length of westbound queue over time")
        
        return fig,axs
            
class MultiEvaluator:
    def __init__(self):
        self.evaluators = dict()
        
    def initialize(self, evaluators, labels):
        for i,label in enumerate(labels):
            self.evaluators[label] = evaluators[i]
            
    def plot_avg_wait_times(self, plt, fig_size: (float, float)):
        fig,ax = plt.subplots(figsize=fig_size, dpi=90)
        
        for label,evaluator in self.evaluators.items():
            t = np.arange(0., evaluator.end_time, evaluator.delta_t)
            ax.plot(t,evaluator.average["avg_wait_time"], label=label)

        ax.set(xlabel="time [s]", ylabel="avg. wait time [s]")
        ax.set_title("Average wait time over time")
        ax.legend()
        
        return fig,ax
    
    def plot_avg_clearance_rates(self, plt, grid_ind: (int, int), fig_size: (float, float)):
        fig,axs = plt.subplots(2, figsize=fig_size, dpi=90, sharex=True)
        
        for label,evaluator in self.evaluators.items():
            t = np.arange(0., evaluator.end_time, evaluator.delta_t)
            axs[0].plot(t,evaluator.average[grid_ind]["avg_clearance_rate_ns"], label=label)
            axs[1].plot(t,evaluator.average[grid_ind]["avg_clearance_rate_ew"], label=label)

        axs[0].set(ylabel="avg. clearance rate")
        axs[0].set_title("Average clearance rate over time (NS)")
        axs[1].set(xlabel="time [s]", ylabel="avg. clearance rate")
        axs[1].set_title("Average clearance rate over time (EW)")
        axs[0].legend()
        
        return fig,axs
    
    def plot_avg_arrivals_on_green_rate(self, plt, grid_ind, fig_size: (float, float)):
        fig,ax = plt.subplots(figsize=fig_size, dpi=90)
        
        for label,evaluator in self.evaluators.items():
            t = np.arange(0., evaluator.end_time, evaluator.delta_t)
            ax.plot(t,evaluator.average[grid_ind]["arrivals_on_green_rate"], label=label)

        ax.set(xlabel="time [s]", ylabel="avg. arrivals on green rate")
        ax.set_title("Average proportion arriving on green over time")
        ax.legend()
        
        return fig,ax
        
    def plot_queue_lengths(self, plt, grid_ind: (int, int), fig_size: (float, float)):
        fig,axs = plt.subplots(4, figsize=fig_size, dpi=90, sharex=True)
        
        for label,evaluator in self.evaluators.items():
            t = np.arange(0., evaluator.end_time, evaluator.delta_t)
            axs[0].plot(t,evaluator.average[grid_ind]["N"]["queue_length"], label=label)
            axs[1].plot(t,evaluator.average[grid_ind]["E"]["queue_length"], label=label)
            axs[2].plot(t,evaluator.average[grid_ind]["S"]["queue_length"], label=label)
            axs[3].plot(t,evaluator.average[grid_ind]["W"]["queue_length"], label=label)

        axs[0].set(ylabel="avg. queue length")
        axs[0].set_title("Average length of northbound queue over time")
        axs[1].set(ylabel="avg. queue length")
        axs[1].set_title("Average length of eastbound queue over time")
        axs[2].set(ylabel="avg. queue length")
        axs[2].set_title("Average length of southbound queue length")
        axs[3].set(xlabel="time [s]", ylabel="avg. queue length")
        axs[3].set_title("Average length of westbound queue over time")
        axs[0].legend()
        
        return fig,axs
    
    def plot_queue_averages(self, plt, grid_ind: (int, int), fig_size: (float, float)):
        n_avg_wait_time = []
        n_avg_queue_length = []
        e_avg_wait_time = []
        e_avg_queue_length = []
        s_avg_wait_time = []
        s_avg_queue_length = []
        w_avg_wait_time = []
        w_avg_queue_length = []
        #avg_queue_length = []
        #avg_wait_time = []

        for label,evaluator in self.evaluators.items():
            n_avg_wait_time += [evaluator.average[grid_ind]["N"]["avg_wait_time"]]
            n_avg_queue_length += [evaluator.average[grid_ind]["N"]["avg_queue_length"]]
            e_avg_wait_time += [evaluator.average[grid_ind]["E"]["avg_wait_time"]]
            e_avg_queue_length += [evaluator.average[grid_ind]["E"]["avg_queue_length"]]
            s_avg_wait_time += [evaluator.average[grid_ind]["S"]["avg_wait_time"]]
            s_avg_queue_length += [evaluator.average[grid_ind]["S"]["avg_queue_length"]]
            w_avg_wait_time += [evaluator.average[grid_ind]["W"]["avg_wait_time"]]
            w_avg_queue_length += [evaluator.average[grid_ind]["W"]["avg_queue_length"]]
            #avg_queue_length += [(n_avg_queue_length[-1]+e_avg_queue_length[-1]+s_avg_queue_length[-1]+w_avg_queue_length[-1])/4]
            #avg_wait_time += [(n_avg_wait_time[-1]+e_avg_wait_time[-1]+s_avg_wait_time[-1]+w_avg_wait_time[-1])/4]
            
        t = np.arange(0., evaluator.end_time, evaluator.delta_t)
        
        fig,axs = plt.subplots(2, figsize=fig_size, dpi=90, sharex=True)

        labels = list(self.evaluators.keys())
        
        axs[0].plot(labels, n_avg_wait_time, label="N")
        axs[0].plot(labels, e_avg_wait_time, label="E")
        axs[0].plot(labels, s_avg_wait_time, label="S")
        axs[0].plot(labels, w_avg_wait_time, label="W")
        #axs[0].plot(labels, avg_wait_time, '--', label="All")
        axs[0].set(ylabel="avg. wait time [s]")
        axs[0].set_title("Average wait time")
        axs[1].plot(labels, n_avg_queue_length, label="N")
        axs[1].plot(labels, e_avg_queue_length, label="E")
        axs[1].plot(labels, s_avg_queue_length, label="S")
        axs[1].plot(labels, w_avg_queue_length, label="W")
        #axs[1].plot(labels, avg_queue_length, '--', label="All")
        #axs[1].set(xlabel="parameter value", ylabel="avg. queue length")
        axs[1].set_title("Average queue length")
        
        axs[0].legend()
        axs[1].legend()
        
        return fig,axs
    
    def plot_intersection_averages(self, plt, grid_ind: (int, int), fig_size: (float, float)):
        avg_clearance_rate_ns = []
        avg_clearance_rate_ew = []
        avg_clearance_rate = []
        tot_switches_ns = []
        tot_switches_ew = []
        arrivals_on_green_rate = []
        #avg_wait_time = []
        #avg_queue_length = []
        
        for label,evaluator in self.evaluators.items():
            avg_clearance_rate_ns += [evaluator.average[grid_ind]["avg_clearance_rate_ns"][-1]]
            avg_clearance_rate_ew += [evaluator.average[grid_ind]["avg_clearance_rate_ew"][-1]]
            avg_clearance_rate += [evaluator.average[grid_ind]["avg_clearance_rate"][-1]]
            tot_switches_ns += [evaluator.average[grid_ind]["tot_switches_ns"][-1]]
            tot_switches_ew += [evaluator.average[grid_ind]["tot_switches_ew"][-1]]
            arrivals_on_green_rate += [evaluator.average[grid_ind]["arrivals_on_green_rate"][-1]]
            #avg_queue_length += [evaluator.average[grid_ind]["avg_queue_length"]]
            #avg_wait_time += [evaluator.average[grid_ind]["avg_wait_time"]]
        
        t = np.arange(0., evaluator.end_time, evaluator.delta_t)
        
        fig,axs = plt.subplots(3, figsize=fig_size, dpi=90, sharex=True)

        labels = list(self.evaluators.keys())
        
        axs[0].plot(labels, avg_clearance_rate_ns, label="NS")
        axs[0].plot(labels, avg_clearance_rate_ew, label="EW")
        #axs[0].plot(labels, avg_clearance_rate, '--', label="All")
        axs[0].set(ylabel="avg. clearance rate")
        axs[0].set_title("Average clearance rate")
        axs[1].plot(labels, tot_switches_ns, label="NS")
        axs[1].plot(labels, tot_switches_ew, label="EW")
        axs[1].set(ylabel="total switches")
        axs[1].set_title("Total red-to-green switches")
        axs[2].plot(labels, arrivals_on_green_rate)
        axs[2].set(ylabel="arrivals on green rate")
        axs[2].set_title("Proportion arriving on green light")
        #axs[3].plot(labels, avg_wait_time)
        #axs[3].set(ylabel="avg. wait time [s]")
        #axs[3].set_title("Average wait time")
        #axs[4].plot(labels, avg_queue_length)
        #axs[4].set(xlabel="parameter value", ylabel="avg. queue length")
        #axs[4].set_title("Average queue length")
        
        axs[0].legend()
        axs[1].legend()
        
        return fig,axs