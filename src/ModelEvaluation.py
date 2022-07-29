import numpy as np
from pathlib import Path
import pickle
from matplotlib.ticker import (MultipleLocator,
                               FormatStrFormatter,
                               AutoMinorLocator)

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
        
        for grid_ind in network.grid_inds:
            self.output[grid_ind] = {}
            self.output[grid_ind]["avg_clearance_rate_ns"] = {}
            self.output[grid_ind]["avg_clearance_rate_ew"] = {}
            self.output[grid_ind]["tot_switches_ns"] = {}
            self.output[grid_ind]["tot_switches_ew"] = {}
            self.output[grid_ind]["arrivals_on_green_rate"] = {}
            self.output[grid_ind]["num_queued_vehicles"] = {}
            self.output[grid_ind]["avg_wait_time"] = {}
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
            self.output[grid_ind]["tot_switches_ns"][trial] = network.intersections[grid_ind].traffic_light_ns.num_cycles[-1]
            self.output[grid_ind]["tot_switches_ew"][trial] = network.intersections[grid_ind].traffic_light_ew.num_cycles[-1]
            self.output[grid_ind]["arrivals_on_green_rate"][trial] = network.intersections[grid_ind].arrivals_on_green_rate
            self.output[grid_ind]["num_queued_vehicles"][trial] = network.intersections[grid_ind].num_queued_vehicles[1:]
            self.output[grid_ind]["avg_wait_time"][trial] = network.intersections[grid_ind].avg_wait_time
            
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
        
        self.average["avg_wait_time"] = sum(self.output["avg_wait_time"].values())/self.num_trials
        
        for grid_ind in self.network.grid_inds:
            self.average[grid_ind] = {}
            
            self.average[grid_ind]["avg_clearance_rate_ns"] = sum(self.output[grid_ind]["avg_clearance_rate_ns"].values())/self.num_trials
            self.average[grid_ind]["avg_clearance_rate_ew"] = sum(self.output[grid_ind]["avg_clearance_rate_ew"].values())/self.num_trials
            self.average[grid_ind]["avg_clearance_rate"] = (self.average[grid_ind]["avg_clearance_rate_ns"]+self.average[grid_ind]["avg_clearance_rate_ew"])/2
            self.average[grid_ind]["num_queued_vehicles"] = [sum([num[i]/self.num_trials for num in self.output[grid_ind]["num_queued_vehicles"].values()]) for i in range(data_length)]
            self.average[grid_ind]["avg_num_queued_vehicles"] = sum([sum(self.output[grid_ind]["num_queued_vehicles"][i])/data_length for i in range(self.num_trials)])/self.num_trials
            self.average[grid_ind]["avg_queue_length"] = self.average[grid_ind]["avg_num_queued_vehicles"]/4
            
            self.average[grid_ind]["avg_wait_time"] = sum(self.output[grid_ind]["avg_wait_time"].values())/self.num_trials
            
            self.average[grid_ind]["tot_switches_ns"] = sum(self.output[grid_ind]["tot_switches_ns"].values())/self.num_trials
            self.average[grid_ind]["tot_switches_ew"] = sum(self.output[grid_ind]["tot_switches_ew"].values())/self.num_trials
            
            self.average[grid_ind]["arrivals_on_green_rate"] = sum(self.output[grid_ind]["arrivals_on_green_rate"].values())/self.num_trials
            
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
            
            
    def plot_avg_wait_times_over_time(self, plt, fig_size: (float, float)):
        fig,ax = plt.subplots(figsize=fig_size, dpi=90)
        t = np.arange(0.,self.end_time,self.delta_t)

        ax.plot(t,self.average_over_time["avg_wait_time"])

        ax.set(xlabel="time [s]", ylabel="avg. wait time [s]")
        ax.set_title("average wait time over time")
        
        return fig,ax
    
    def plot_avg_clearance_rate(self, plt, grid_ind, fig_size: (float, float)):
        fig, ax = plt.subplots(figsize=fig_size, dpi=90)
        
        t = np.arange(0.,self.end_time,self.delta_t)
        
        ax.plot(t, self.average_over_time[grid_ind]["avg_clearance_rate_ns"], label="NS")
        ax.plot(t, self.average_over_time[grid_ind]["avg_clearance_rate_ew"], label="EW")
        ax.set(xlabel="time [s]", ylabel='avg. clearance rate')
        ax.set_title('average_over_time clearance rate over time')
        ax.label_outer()
        ax.legend()

        return fig, ax
    
    def plot_avg_arrivals_on_green_rate(self, plt, grid_ind, fig_size: (float, float)):
        fig,ax = plt.subplots(figsize=fig_size, dpi=90)
        t = np.arange(0.,self.end_time,self.delta_t)

        ax.plot(t,self.average_over_time[grid_ind]["arrivals_on_green_rate"])

        ax.set(xlabel="time [s]", ylabel="avg. wait time [s]")
        ax.set_title("average_over_time proportion arriving on green over time")
        
        return fig,ax
        
    def plot_queue_lengths(self, plt, grid_ind: (int, int), fig_size: (float, float)):
        fig,axs = plt.subplots(4, figsize=fig_size, dpi=90, sharex=True)
        t = np.arange(0.,self.end_time,self.delta_t)

        axs[0].plot(t,self.average_over_time[grid_ind]["N"]["queue_length"])
        axs[1].plot(t,self.average_over_time[grid_ind]["E"]["queue_length"])
        axs[2].plot(t,self.average_over_time[grid_ind]["S"]["queue_length"])
        axs[3].plot(t,self.average_over_time[grid_ind]["W"]["queue_length"])

        axs[0].set(ylabel="avg. wait time [s]")
        axs[0].set_title("average_over_time length of northbound queue over time")
        axs[1].set(ylabel="avg. wait time [s]")
        axs[1].set_title("average_over_time length of eastbound queue over time")
        axs[2].set(ylabel="avg. wait time [s]")
        axs[2].set_title("average_over_time length of southbound queue over time")
        axs[3].set(xlabel="time [s]", ylabel="avg. wait time [s]")
        axs[3].set_title("average_over_time length of westbound queue over time")
        
        return fig,axs
    
    def save_to_file(self, file_name: str, output_destination="../data/evals/") -> None:
        dim = str(self.network.grid_dimensions[0]+1)+"x"+str(self.network.grid_dimensions[1]+1)
        f = open(Path(output_destination) / dim / file_name,"wb")
        pickle.dump(self,f)
        f.close()
        
    def read_file(self, file_name: str, grid_dim: str, destination="../data/evals/"):
        with open(Path(destination) / grid_dim / file_name, 'rb') as f:
            return pickle.load(f)
            
class MultiEvaluator:
    def __init__(self):
        self.evaluators = dict()
        self.variable = "variable"
        
    def initialize(self, evaluators, labels: list(), variable: str):
        for i,label in enumerate(labels):
            self.evaluators[label] = evaluators[i]
            
        self.variable = variable
    
    def plot_avg_wait_times(self, plt, fig_size: (float, float)):
        fig,ax = plt.subplots(figsize=fig_size, dpi=90)
        
        avg_wait_times = []
        
        for label,evaluator in self.evaluators.items():
            avg_wait_times += [evaluator.average["avg_wait_time"]]
            
        labels = list(self.evaluators.keys())
        ax.plot(labels, avg_wait_times, '*')
        ax.set(xlabel=self.variable, ylabel="avg. wait time [s]")
        ax.set_title("Average wait time, overall")
        
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
        axs[0].set_title("average length of northbound queue over time")
        axs[1].set(ylabel="avg. queue length")
        axs[1].set_title("average length of eastbound queue over time")
        axs[2].set(ylabel="avg. queue length")
        axs[2].set_title("average length of southbound queue length")
        axs[3].set(xlabel="time [s]", ylabel="avg. queue length")
        axs[3].set_title("average length of westbound queue over time")
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
        avg_queue_length = []
        avg_wait_time = []

        for label,evaluator in self.evaluators.items():
            n_avg_wait_time += [evaluator.average[grid_ind]["N"]["avg_wait_time"]]
            n_avg_queue_length += [evaluator.average[grid_ind]["N"]["avg_queue_length"]]
            e_avg_wait_time += [evaluator.average[grid_ind]["E"]["avg_wait_time"]]
            e_avg_queue_length += [evaluator.average[grid_ind]["E"]["avg_queue_length"]]
            s_avg_wait_time += [evaluator.average[grid_ind]["S"]["avg_wait_time"]]
            s_avg_queue_length += [evaluator.average[grid_ind]["S"]["avg_queue_length"]]
            w_avg_wait_time += [evaluator.average[grid_ind]["W"]["avg_wait_time"]]
            w_avg_queue_length += [evaluator.average[grid_ind]["W"]["avg_queue_length"]]
            avg_queue_length += [evaluator.average[grid_ind]["avg_queue_length"]]
            avg_wait_time += [evaluator.average[grid_ind]["avg_wait_time"]]
            
        t = np.arange(0., evaluator.end_time, evaluator.delta_t)
        
        fig,axs = plt.subplots(2, figsize=fig_size, dpi=90, sharex=True)

        labels = list(self.evaluators.keys())
        
        axs[0].plot(labels, n_avg_wait_time, '*', label="N")
        axs[0].plot(labels, e_avg_wait_time, '*',label="E")
        axs[0].plot(labels, s_avg_wait_time, '*',label="S")
        axs[0].plot(labels, w_avg_wait_time, '*',label="W")
        axs[0].plot(labels, avg_wait_time, '--', label="All")
        axs[0].set(ylabel="avg. wait time [s]")
        axs[0].set_title("Average wait time")
        axs[1].plot(labels, n_avg_queue_length, '*',label="N")
        axs[1].plot(labels, e_avg_queue_length, '*',label="E")
        axs[1].plot(labels, s_avg_queue_length, '*',label="S")
        axs[1].plot(labels, w_avg_queue_length, '*',label="W")
        axs[1].plot(labels, avg_queue_length, '--', label="All")
        axs[1].set(xlabel=self.variable, ylabel="avg. queue length")
        axs[1].set_title("Average queue length")
        
        axs[0].legend(loc='center right', bbox_to_anchor=(1.15, 0.5), ncol=1, fancybox=True, shadow=True)
        axs[1].legend(loc='center right', bbox_to_anchor=(1.15, 0.5), ncol=1, fancybox=True, shadow=True)
        
        return fig,axs
    
    def plot_intersection_averages(self, plt, grid_ind: (int, int), fig_size: (float, float), plot_tot_switches=False):
        avg_clearance_rate_ns = []
        avg_clearance_rate_ew = []
        avg_clearance_rate = []
        tot_switches_ns = []
        tot_switches_ew = []
        arrivals_on_green_rate = []
        avg_wait_time = []
        avg_queue_length = []
        
        for label,evaluator in self.evaluators.items():
            avg_clearance_rate_ns += [evaluator.average[grid_ind]["avg_clearance_rate_ns"]]
            avg_clearance_rate_ew += [evaluator.average[grid_ind]["avg_clearance_rate_ew"]]
            avg_clearance_rate += [evaluator.average[grid_ind]["avg_clearance_rate"]]
            tot_switches_ns += [evaluator.average[grid_ind]["tot_switches_ns"]]
            tot_switches_ew += [evaluator.average[grid_ind]["tot_switches_ew"]]
            arrivals_on_green_rate += [evaluator.average[grid_ind]["arrivals_on_green_rate"]]
            avg_queue_length += [evaluator.average[grid_ind]["avg_queue_length"]]
            avg_wait_time += [evaluator.average[grid_ind]["avg_wait_time"]]
        
        t = np.arange(0., evaluator.end_time, evaluator.delta_t)
        
        fig, ((ax1, ax2),(ax3, ax4)) = plt.subplots(2,2, figsize=fig_size, dpi=90, sharex='col')

        labels = list(self.evaluators.keys())
        
        if plot_tot_switches:
            ax1.plot(labels, tot_switches_ns, '*', label="NS")
            ax1.plot(labels, tot_switches_ew, '*', label="EW")
            ax1.set(ylabel="total switches")
            ax1.set_title("Total green-to-red switches")
        else:
            ax1.plot(labels, avg_queue_length, '*')
            ax1.set(ylabel="avg. queue length")
            ax1.set_title("Average queue length per lane")
        ax2.plot(labels, avg_clearance_rate_ns, '*', label="NS")
        ax2.plot(labels, avg_clearance_rate_ew, '*', label="EW")
        ax2.plot(labels, avg_clearance_rate, '--', label="All")
        ax2.set(ylabel="avg. clearance rate [1/s]")
        ax2.set_title("Average rate of intersection clearance")
        ax3.plot(labels, arrivals_on_green_rate, '*',)
        ax3.set(xlabel=self.variable, ylabel="arrivals on green rate")
        ax3.set_title("Proportion arriving on green light")
        ax4.plot(labels, avg_wait_time, '*',)
        ax4.set(xlabel=self.variable, ylabel="avg. wait time [s]")
        ax4.set_title("Average cumulative waiting time")
        #axs[3].plot(labels, avg_wait_time)
        #axs[3].set(ylabel="avg. wait time [s]")
        #axs[3].set_title("average wait time")
        #axs[4].plot(labels, avg_queue_length)
        #axs[4].set(xlabel="parameter value", ylabel="avg. queue length")
        #axs[4].set_title("average queue length")
        
        
        #ax1.legend(loc='center right', bbox_to_anchor=(1.15, 0.5), ncol=1, fancybox=True, shadow=True)
        ax2.legend(loc='center right', bbox_to_anchor=(1.15, 0.5), ncol=1, fancybox=True, shadow=True)
        #axs[2].legend(loc='center right', bbox_to_anchor=(1.05, 0.5), ncol=1, fancybox=True, shadow=True)
        
        #ax2.yaxis.set_major_locator(MultipleLocator(0.0001))
        #ax2.yaxis.set_major_formatter(FormatStrFormatter('% 1.2f'))
        
        return fig,((ax1,ax2),(ax3,ax4))
    
    def compare_metrics(self, plt, x_axis: str, y_axis: str, grid_ind: (int, int), fig_size: (float, float), ):
        fig,ax = plt.subplots(figsize=fig_size, dpi=90)
        
        for label,evaluator in self.evaluators.items():
            x = evaluator.average[grid_ind][x_axis]
            y = evaluator.average[grid_ind][y_axis]
            
            ax.plot(x, y, '*', label=label)
            
        ax.set(xlabel=x_axis, ylabel=y_axis)
        ax.set_title(y_axis+" vs. "+x_axis)
        ax.legend(loc='center right', bbox_to_anchor=(1.15, 0.5), ncol=1, fancybox=True, shadow=True)
        
        return fig,ax
    
    def save_to_file(self, file_name: str, output_destination="../data/evals/multi/") -> None:
        f = open(Path(output_destination) / file_name,"wb")
        pickle.dump(self,f)
        f.close()
        
    def read_file(self, file_name: str, destination="../data/evals/multi/"):
        with open(Path(destination) / file_name, 'rb') as f:
            return pickle.load(f)