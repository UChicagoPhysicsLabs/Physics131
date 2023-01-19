from IPython import get_ipython

def on_voltage_change(change):
#    try:
    linebuilder.voltages[change.owner.id] = float(change['new'])
    linebuilder.lines[change.owner.id].set_color(get_color(float(change['new'])))
    voltages[change.owner.id]= float(change['new'])
    print(linebuilder.lines[change.owner.id].set_label("{} V".format(change['new'])))
    ax.legend()
    fig.canvas.draw()
    plt.show()
    save_data()
#    except:
#        pass

def new_tab(holder=0,newv=None):
    id_value = len(holder.children)
    newout = widgets.Output()
    if (newv is None):
        newv = linebuilder.voltages[id_value]
    newvoltage = widgets.FloatSlider(value=newv,min=0,max=10.0,step=0.1,description='Voltage:',disabled=False,continuous_update=False,orientation='horizontal',readout=True,readout_format='.1f')
    holder.children += (widgets.VBox([newvoltage,newout]),)
    newvoltage.observe(on_voltage_change, names='value')
    newvoltage.id = id_value
    with newout:
        newout.clear_output()
        for n in range(len(x_data[id_value])):
            print("{:0.2f} , {:0.2f}".format(x_data[id_value][n],y_data[id_value][n]))
    
    holder.set_title(id_value,"Line {}".format(id_value+1))
    holder.selected_index=id_value


def on_value_change(change):
    try:
        linebuilder.index = int(change['new'])
    except:
        pass

def newline_clicked(b):
    global voltages
    ln, = ax.plot([], [], linestyle="", marker="o",label ="{:0.2f} V".format(voltages[-1]))
    linebuilder.newline(ln)
    new_tab(Show_Voltages)
    linebuilder.lines[-1].set_color(get_color(linebuilder.voltages[-1]))
    linebuilder.lines[-1].set_label("{:0.2f} V".format(linebuilder.voltages[-1]))
    ax.legend()

def save_figure(b):
	fname = time.strftime("%b%d_Time_%H_%M_%S",time.gmtime())
	figname=fname+".png"
	datname=fname+".csv"
	plt.savefig(figname)
	with output: print("Saved as ",figname)
	global x_data
	global y_data
	global voltages
	save_data(datname)

def save_data(fname="latest.csv"):
    global x_data
    global y_data
    global voltages
    xd = (sum(x_data,[]))
    yd = (sum(y_data,[]))
    vd = []
    for index, item in enumerate(x_data):
        vd.append(list(np.full_like(item,voltages[index])))
    vd = (sum(vd,[]))
    np.savetxt(fname,[xd,yd,vd],delimiter=",")

def load_data(fname="latest.csv"):
    xd = []
    yd = []
    vd = []
    try:
        a,b,c=np.loadtxt(fname,delimiter = ",")
        for volt in np.unique(c):
            xd.append(list(a[c==volt]))
            yd.append(list(b[c==volt]))
            vd.append(volt)
    except:
        pass
    return(xd,yd,vd)    

def restore_data(b):
    global x_data
    global y_data
    global voltages
    global Show_Voltages
    Show_Voltages.children = []
    x_data,y_data,voltages = load_data()
    line, = ax.plot(x_data[0], y_data[0], linestyle="", marker="o",label = "{:0.2f} V".format(voltages[0]),color=get_color(voltages[0]))
    linebuilder.reset(line,x_data[0],y_data[0],voltages[0])
    new_tab(Show_Voltages,voltages[0])
    for index in range(1,len(voltages)):
        ln, = ax.plot(x_data[index], y_data[index], linestyle="", marker="o",label ="{:0.2f} V".format(voltages[index]),color=get_color(voltages[index]))
        linebuilder.restoreline(ln)
        new_tab(Show_Voltages,voltages[index])
    linebuilder.draw()
    ax.legend()
    
def load_from_file(b):
    global x_data
    global y_data
    global voltages
    global Show_Voltages
    Show_Voltages.children = []
    fname = next(iter(b['new']))
    x_data,y_data,voltages = load_data(fname)
    line, = ax.plot(x_data[0], y_data[0], linestyle="", marker="o",label = "{:0.2f} V".format(voltages[0]),color=get_color(voltages[0]))
    linebuilder.reset(line,x_data[0],y_data[0],voltages[0])
    new_tab(Show_Voltages,voltages[0])
    for index in range(1,len(voltages)):
        ln, = ax.plot(x_data[index], y_data[index], linestyle="", marker="o",label ="{:0.2f} V".format(voltages[index]),color=get_color(voltages[index]))
        linebuilder.restoreline(ln)
        new_tab(Show_Voltages,voltages[index])
    linebuilder.draw()
    ax.legend()
    

def clear_data(b):
    save_data()
    global x_data
    global y_data
    global voltages
    global linebuilder
    global ax
    global Show_Voltages
    Show_Voltages.children = []
    
    x_data = [[]]
    y_data = [[]]
    voltages = [0]
    new_tab(Show_Voltages)
    ax.lines = []
    line, = ax.plot(x_data[0], y_data[0], linestyle="", marker="o",label = "{:0.2f} V".format(voltages[0]),color=get_color(voltages[0]))
    linebuilder.reset(line)
    fig.canvas.draw();
    ax.legend()

def undo_clicked(b): linebuilder.undo()

class LineBuilder:
    def __init__(self, line):
        self.ipython = get_ipython()
        self.lines = [line]
        self.voltages = [0]
        self.index = 0
        self.xs = [list(line.get_xdata())]
        self.ys = [list(line.get_ydata())]
        self.cid = line.figure.canvas.mpl_connect('button_press_event', self)
    
    def reset(self,line,startx=[],starty=[],startv=0):
        for l in self.lines:
            del l
        self.lines = [line]
        self.voltages = [startv]
        self.index = 0
        self.xs = [startx]
        self.ys = [starty]
        self.cid = line.figure.canvas.mpl_connect('button_press_event', self)

    def __call__(self, event):
        print('click', event)
        if event.inaxes!=self.lines[self.index].axes: return
        
        self.xs[self.index].append(event.xdata)
        self.ys[self.index].append(event.ydata)
        x_data[self.index].append(event.xdata)
        y_data[self.index].append(event.ydata)
        
        self.lines[self.index].set_data(self.xs[self.index], self.ys[self.index])
        
        with output: print("Point added at (",event.xdata, ", ",event.ydata,")")
        Show_Voltages.children[self.index].children[1].clear_output()
        with Show_Voltages.children[self.index].children[1]:
            output.clear_output()
            for n in range(len(self.xs[self.index])):
                print("{:0.2f} , {:0.2f}".format(self.xs[self.index][n],self.ys[self.index][n]))
        self.draw()
        save_data()
            
    def undo(self):
        try:
            lx = self.xs[self.index].pop()
            x_data[self.index].pop()
            ly = self.ys[self.index].pop()
            y_data[self.index].pop()
            with output: print("Point removed at (",lx, ", ",ly,")")
            self.lines[self.index].set_data(self.xs[self.index], self.ys[self.index])
            self.lines[self.index].figure.canvas.draw()
            save_data()
        except:
            with output: print("Can't remove points now.")
    
    def restoreline(self,line):
        self.lines.append(line)
        self.index = len(self.lines)-1
        self.voltages.append(self.index)
        self.xs.append(list(line.get_xdata()))
        self.ys.append(list(line.get_ydata()))
        
    def newline(self,line):
        global voltages
        self.lines.append(line)
        self.index = len(self.lines)-1
        self.voltages.append(self.index)
        voltages.append(self.index)
        self.xs.append(list(line.get_xdata()))
        x_data.append(list(line.get_xdata()))
        self.ys.append(list(line.get_ydata()))
        y_data.append(list(line.get_ydata()))
        
    def draw(self):
        for n,item in enumerate(self.lines):
            item.set_data(self.xs[n], self.ys[n])
            item.figure.canvas.draw()