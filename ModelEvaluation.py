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
        
        for grid_ind in network.grid_inds:
            self.output[grid_ind] = {}
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
            last_trial = trial
            
            self.output["avg_wait_time"][trial] = network.avg_wait_time
            self.output[grid_ind]["N"]["avg_wait_time"][trial] = network.intersections[grid_ind].queue_n.avg_wait_time()
            self.output[grid_ind]["N"]["queue_length"][trial] = network.intersections[grid_ind].queue_n.queue_length[1:]
            self.output[grid_ind]["E"]["avg_wait_time"][trial] = network.intersections[grid_ind].queue_e.avg_wait_time()
            self.output[grid_ind]["E"]["queue_length"][trial] = network.intersections[grid_ind].queue_e.queue_length[1:]
            self.output[grid_ind]["S"]["avg_wait_time"][trial] = network.intersections[grid_ind].queue_s.avg_wait_time()
            self.output[grid_ind]["S"]["queue_length"][trial] = network.intersections[grid_ind].queue_s.queue_length[1:]
            self.output[grid_ind]["W"]["avg_wait_time"][trial] = network.intersections[grid_ind].queue_w.avg_wait_time()
            self.output[grid_ind]["W"]["queue_length"][trial] = network.intersections[grid_ind].queue_w.queue_length[1:]
            
        return self.output
    
    def compute_average(self) -> dict():
        data_length = int(self.end_time/self.delta_t)
        
        self.average["avg_wait_time"] = ([sum([wait_time[i] for wait_time in self.output["avg_wait_time"].values()])/self.num_trials for i in range(data_length)])
        
        for grid_ind in self.network.grid_inds:
            self.average[grid_ind] = {}
            self.average[grid_ind]["N"] = {"avg_wait_time": 0., "avg_queue_length": 0., "queue_length": []}
            self.average[grid_ind]["E"] = {"avg_wait_time": 0., "avg_queue_length": 0., "queue_length": []}
            self.average[grid_ind]["S"] = {"avg_wait_time": 0., "avg_queue_length": 0., "queue_length": []}
            self.average[grid_ind]["W"] = {"avg_wait_time": 0., "avg_queue_length": 0., "queue_length": []}
            
            self.average[grid_ind]["N"]["avg_wait_time"] = sum(self.output[grid_ind]["N"]["avg_wait_time"].values())/self.num_trials
            self.average[grid_ind]["E"]["avg_wait_time"] = sum(self.output[grid_ind]["E"]["avg_wait_time"].values())/self.num_trials
            self.average[grid_ind]["S"]["avg_wait_time"] = sum(self.output[grid_ind]["S"]["avg_wait_time"].values())/self.num_trials
            self.average[grid_ind]["W"]["avg_wait_time"] = sum(self.output[grid_ind]["W"]["avg_wait_time"].values())/self.num_trials
            
            self.average[grid_ind]["N"]["avg_queue_length"] = sum([sum(self.output[grid_ind]["N"]["queue_length"][i])/len(self.output[grid_ind]["N"]["queue_length"][i]) for i in range(self.num_trials)])/self.num_trials
            self.average[grid_ind]["E"]["avg_queue_length"] = sum([sum(self.output[grid_ind]["E"]["queue_length"][i])/len(self.output[grid_ind]["E"]["queue_length"][i]) for i in range(self.num_trials)])/self.num_trials
            self.average[grid_ind]["S"]["avg_queue_length"] = sum([sum(self.output[grid_ind]["S"]["queue_length"][i])/len(self.output[grid_ind]["S"]["queue_length"][i]) for i in range(self.num_trials)])/self.num_trials
            self.average[grid_ind]["W"]["avg_queue_length"] = sum([sum(self.output[grid_ind]["W"]["queue_length"][i])/len(self.output[grid_ind]["W"]["queue_length"][i]) for i in range(self.num_trials)])/self.num_trials
            
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
        
    def plot_avg_queue_length(self, plt, grid_ind: (int, int), fig_size: (float, float)):
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
        
    def plot_avg_queue_lengths(self, plt, grid_ind: (int, int), fig_size: (float, float)):
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
    
    def plot_averages(self, plt, grid_ind: (int, int), fig_size: (float, float)):
        n_avg_wait_time = []
        n_avg_queue_length = []
        e_avg_wait_time = []
        e_avg_queue_length = []
        s_avg_wait_time = []
        s_avg_queue_length = []
        w_avg_wait_time = []
        w_avg_queue_length = []
        avg_queue_length = []

        for label,evaluator in self.evaluators.items():
            n_avg_wait_time += [evaluator.average[grid_ind]["N"]["avg_wait_time"]]
            n_avg_queue_length += [evaluator.average[grid_ind]["N"]["avg_queue_length"]]
            e_avg_wait_time += [evaluator.average[grid_ind]["E"]["avg_wait_time"]]
            e_avg_queue_length += [evaluator.average[grid_ind]["E"]["avg_queue_length"]]
            s_avg_wait_time += [evaluator.average[grid_ind]["S"]["avg_wait_time"]]
            s_avg_queue_length += [evaluator.average[grid_ind]["S"]["avg_queue_length"]]
            w_avg_wait_time += [evaluator.average[grid_ind]["W"]["avg_wait_time"]]
            w_avg_queue_length += [evaluator.average[grid_ind]["W"]["avg_queue_length"]]
            avg_queue_length += [(n_avg_queue_length[-1]+e_avg_queue_length[-1]+s_avg_queue_length[-1]+w_avg_queue_length[-1])/4]
            
            t = np.arange(0., evaluator.end_time, evaluator.delta_t)
        
        fig,axs = plt.subplots(2, figsize=(6,5), dpi=90, sharex=True)

        labels = list(self.evaluators.keys())
        
        axs[0].plot(labels, n_avg_wait_time, label="Northbound")
        axs[0].plot(labels, e_avg_wait_time, label="Eastbound")
        axs[0].plot(labels, s_avg_wait_time, label="Southbound")
        axs[0].plot(labels, w_avg_wait_time, label="Westbound")
        axs[0].set(ylabel="avg. wait time [s]")
        axs[0].set_title("Average wait time")
        axs[1].plot(labels, n_avg_queue_length, label="Northbound")
        axs[1].plot(labels, e_avg_queue_length, label="Eastbound")
        axs[1].plot(labels, s_avg_queue_length, label="Southbound")
        axs[1].plot(labels, w_avg_queue_length, label="Westbound")
        axs[1].plot(labels, avg_queue_length, '--', label="All")
        axs[1].set(xlabel="parameter value", ylabel="avg. queue length")
        axs[1].set_title("Average queue length")
        
        axs[0].legend()
        axs[1].legend()
        
        return fig,axs