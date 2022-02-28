from tkinter import *
from tkinter import messagebox
from tkinter import ttk
import numpy as np
import sympy
from sympy.abc import x

def solve():
    dataT = []
    dataC = []
    for line in trv1.get_children():
        data = []
        for value in trv1.item(line)['values']:
            data.append(value)
        dataT.append(data)

    for line in trv2.get_children():
        data = []
        for value in trv2.item(line)['values']:
            data.append(value)
        dataC.append(data)

    try:
        baseBeam = float(base.get())
        f_cBeam = float(f_c.get())
        f_yBeam = float(f_y.get())
    except ValueError:
        messagebox.showerror("Check Values", "Check Inputed Values!")
        return

    # Beta Value
    if f_cBeam <= 4000:
        beta = 0.85
    elif f_cBeam < 8000:
        beta = 0.85-(0.05*((f_cBeam-4000)/1000))
    else:
        beta = 0.65

    # DRB
    if dataT and dataC:
        depthT = np.array(dataT, dtype=float)[:,0]
        depthC = np.array(dataC, dtype=float)[:,0]
        nT = np.array(dataT, dtype=float)[:,1]
        nC = np.array(dataC, dtype=float)[:,1]
        diamT = np.array(dataT, dtype=float)[:,2]
        diamC = np.array(dataC, dtype=float)[:,2]

        steel_areaT = nT.astype(np.float)*(np.pi/4)*np.power(diamT.astype(np.float), 2)
        steel_areaC = nC.astype(np.float)*(np.pi/4)*np.power(diamC.astype(np.float), 2)
        equation = 0.85*f_cBeam*beta*x*baseBeam + np.sum(steel_areaC*f_yBeam) - np.sum(steel_areaT*f_yBeam)
        c_values = np.array(sympy.solve(equation, x))
        c_val = float(np.min(c_values[c_values>0]))
        a_val = beta*c_val

        stress_Tension = 87000*((depthT.astype(np.float)-c_val) / c_val)
        stress_Compression = 87000*((c_val-depthC.astype(np.float)) / c_val)
        stressT = []
        stressC = []
        if any(stress_Tension < 0):
            messagebox.showerror("Invalid Beam", "One Tension Layer is Compression!")
            return

        elif any(stress_Compression < 0):
            messagebox.showerror("Invalid Beam", "One Compression Layer is Tension!")
            return

        elif all(np.logical_and(stress_Tension >= f_yBeam, stress_Compression >= f_yBeam)):
            for i in range(len(stress_Tension)):
                stressT.append(f_yBeam)
            for i in range(len(stress_Compression)):
                stressC.append(f_yBeam)

        else:
            for i in range(len(stress_Tension)):
                if stress_Tension[i] < f_yBeam:
                    stressT.append(87000*((float(depthT[i])-x)/x))
                if stress_Tension[i] >= f_yBeam:
                    stressT.append(f_yBeam)

            for i in range(len(stress_Compression)):
                if stress_Compression[i] < f_yBeam:
                    stressC.append(87000*((x-float(depthC[i]))/x))
                if stress_Compression[i] >= f_yBeam:
                    stressC.append(f_yBeam)

            equation = 0.85*f_cBeam*beta*x*baseBeam + np.sum(steel_areaC*stressC) - np.sum(steel_areaT*stressT)
            c_values = np.array(sympy.solve(equation, x))
            c_val = float(np.min(c_values[c_values>0]))
            a_val = beta*c_val

            stressT = []
            for i in range(len(stress_Tension)):
                if stress_Tension[i] < f_yBeam:
                    stressT.append(87000*((float(depthT[i])-c_val)/c_val))
                if stress_Tension[i] >= f_yBeam:
                    stressT.append(f_yBeam)

            stressC = []
            for i in range(len(stress_Compression)):
                if stress_Compression[i] < f_yBeam:
                    stressC.append(87000*((c_val-float(depthC[i]))/c_val))
                if stress_Compression[i] >= f_yBeam:
                    stressC.append(f_yBeam)


        # Solving for d
        stressT = np.array(stressT, dtype=np.float)
        stressC = np.array(stressC, dtype=np.float)
        depthBeamT = np.sum(stressT*depthT.astype(np.float)) / np.sum(stressT)
        max_capacity = 0.85*f_cBeam*beta*c_val*baseBeam*(depthBeamT-((beta*c_val)/2)) + np.sum(steel_areaC*stressC*(depthBeamT-depthC))
        

    # SRB
    elif dataT:
        depthT = np.array(dataT, dtype=object)[:,0]
        nT = np.array(dataT, dtype=object)[:,1]
        diamT = np.array(dataT, dtype=object)[:,2]

        steel_areaT = nT.astype(np.float)*(np.pi/4)*np.power(diamT.astype(np.float), 2)
        a_val = np.sum(steel_areaT*f_yBeam) / (0.85*f_cBeam*baseBeam)
        c_val = a_val / beta

        # Checking for Yield
        stress_Tension = 87000*((depthT.astype(np.float)-c_val) / c_val)
        stressT = []
        if any(stress_Tension < 0):
            messagebox.showerror("Invalid Beam", "One Tension Layer is Compression!")
            return
            
        if any(np.logical_and(stress_Tension > 0, stress_Tension < f_yBeam)):
            for i in range(len(stress_Tension)):
                if stress_Tension[i] < f_yBeam:
                    stressT.append(87000*((float(depthT[i])-x)/x))
                if stress_Tension[i] >= f_yBeam:
                    stressT.append(f_yBeam)

            equation = 0.85*f_cBeam*beta*x*baseBeam - np.sum(steel_areaT*stressT)
            c_values = np.array(sympy.solve(equation, x))
            c_val = float(np.min(c_values[c_values>0]))
            a_val = beta*c_val

            stressT = []
            for i in range(len(stress_Tension)):
                if stress_Tension[i] < f_yBeam:
                    stressT.append(87000*((float(depthT[i])-c_val)/c_val))
                if stress_Tension[i] >= f_yBeam:
                    stressT.append(f_yBeam)
        else:
            for i in range(len(stress_Tension)):
                stressT.append(f_yBeam)
                
        # Solving for d
        stressT = np.array(stressT, dtype=np.float)
        depthBeamT = np.sum(stressT*depthT.astype(np.float)) / np.sum(stressT)
        max_capacity = 0.85*f_cBeam*beta*c_val*baseBeam*(depthBeamT-((beta*c_val)/2))
        
        # For the values not needed
        steel_areaC = np.array(0)

    elif dataC:
        messagebox.showerror("Invalid Beam", "Add tension bars")
        return

    else:
        messagebox.showerror("Invalid Beam", "Please add steel bars")
        return


    # Solving For reduction factor
    deflection_T = 0.003*((depthBeamT-c_val) / c_val)
    if deflection_T >= 0.005:
        red_factor = 0.9
    elif deflection_T < (f_yBeam / 29000000):
        red_factor = 0.65
    else:
        red_factor = 0.65 + (deflection_T-(f_yBeam / 29000000)) * (0.25/(0.005-(f_yBeam / 29000000)))

    capacity = red_factor*max_capacity

    label_1.config(text=np.round(max_capacity/12000, 10))
    label_2.config(text=np.round(capacity/12000, 10))
    label_3.config(text=np.round(beta, 10))
    label_4.config(text=np.round(red_factor, 10))
    label_5.config(text=np.round(a_val, 10))
    label_6.config(text=np.round(c_val, 10))
    label_7.config(text=np.round(np.sum(steel_areaT), 10))
    label_8.config(text=np.round(np.sum(steel_areaC), 10))
    label_9.config(text=np.round(deflection_T, 10))
    label_10.config(text=np.round(depthBeamT, 10))

def editSteel():
    def add_tension():
        try:
            values = [float(depth.get()), float(no_of_bars.get()), float(diameter.get())]
            trv1.insert('', 'end', values=values)
            trv3.insert('', 'end', values=values)
        except ValueError:
            messagebox.showerror("Value Error", "Check Inputed Values!")
            return

    def add_compression():
        try:
            values = [float(depth.get()), float(no_of_bars.get()), float(diameter.get())]
            trv2.insert('', 'end', values=values)
            trv4.insert('', 'end', values=values)
        except ValueError:
            messagebox.showerror("Value Error", "Check Inputed Values!")
            return

    def remove_tension():
        try:
            trv1.delete(trv3.selection()[0])
            trv3.delete(trv3.selection()[0])
        except IndexError:
            messagebox.showerror("Index Error", "Select a value to remove!")
            return

    def remove_compression():
        try:
            trv2.delete(trv4.selection()[0])
            trv4.delete(trv4.selection()[0])
        except IndexError:
            messagebox.showerror("Index Error", "Select a value to remove!")
            return

    newWindow = Toplevel(mainWindow)
    newWindow.title("Steel Parameters")
    newWindow.geometry("500x690+500+0")
    newWindow.resizable(width=0, height=0)

    wrapper5 = LabelFrame(newWindow, text="Steel Parameters")
    wrapper6 = LabelFrame(newWindow, text="Tension Steel Parameters")
    wrapper7 = LabelFrame(newWindow, text="Compression Steel Parameters")

    wrapper5.place(x=10, y=10, width=480, height=130)
    wrapper6.place(x=10, y=150, width=480, height=250)
    wrapper7.place(x=10, y=410, width=480, height=270)

    Label(wrapper5, text="Depth:").place(x=10, y=10)
    Label(wrapper5, text="No. of Bars:").place(x=10, y=40)
    Label(wrapper5, text="Diameter:").place(x=10, y=70)

    Entry(wrapper5, textvariable=depth).place(x=80, y=10, width=90)
    Entry(wrapper5, textvariable=no_of_bars).place(x=80, y=40, width=90)
    Entry(wrapper5, textvariable=diameter).place(x=80, y=70, width=90)

    Label(wrapper5, text="in").place(x=180, y=10)
    Label(wrapper5, text="bars").place(x=180, y=40)
    Label(wrapper5, text="in").place(x=180, y=70)

    # Tension
    trv3 = ttk.Treeview(wrapper6, columns=(1,2,3), show="headings", height=9)
    trv3.place(x=5, y=10, width=465)
    trv3.heading(1, text='Depth (in)')
    trv3.heading(2, text='No. of Bars')
    trv3.heading(3, text='Diameter (in)')
    trv3.column(1, width=154, anchor="c")
    trv3.column(2, width=154, anchor="c")
    trv3.column(3, width=154, anchor="c")
    vsb3 = ttk.Scrollbar(wrapper6, orient="vertical", command=trv3.yview)
    vsb3.place(x=452, y=11, height=205)
    trv3.configure(yscrollcommand=vsb3.set)

    # Compression
    trv4 = ttk.Treeview(wrapper7, columns=(1,2,3), show="headings", height=10)
    trv4.place(x=5, y=10, width=465)
    trv4.heading(1, text='Depth (in)')
    trv4.heading(2, text='No. of Bars')
    trv4.heading(3, text='Diameter (in)')
    trv4.column(1, width=154, anchor="c")
    trv4.column(2, width=154, anchor="c")
    trv4.column(3, width=154, anchor="c")
    vsb4 = ttk.Scrollbar(wrapper7, orient="vertical", command=trv4.yview)
    vsb4.place(x=452, y=11, height=225)
    trv4.configure(yscrollcommand=vsb4.set)

    showBtn3 = Button(wrapper5, text="Add Tension", command=add_tension, width=15)
    showBtn3.place(x=230, y=5)

    showBtn4 = Button(wrapper5, text="Add Comp", command=add_compression, width=15)
    showBtn4.place(x=230, y=40)

    showBtn5 = Button(wrapper5, text="Remove Tension", command=remove_tension, width=15)
    showBtn5.place(x=350, y=5)

    showBtn6 = Button(wrapper5, text="Remove Comp", command=remove_compression, width=15)
    showBtn6.place(x=350, y=40)


    for line in trv1.get_children():
        data = []
        for value in trv1.item(line)['values']:
            data.append(value)
        trv3.insert('', 'end', values=data)

    for line in trv2.get_children():
        data = []
        for value in trv2.item(line)['values']:
            data.append(value)
        trv4.insert('', 'end', values=data)


mainWindow = Tk()
mainWindow.title("Rectangular Beam Capacity Solver (English Units)")
mainWindow.geometry("500x690+0+0")
mainWindow.resizable(width=0, height=0)


wrapper1 = LabelFrame(mainWindow, text="Beam Properties")
wrapper2 = LabelFrame(mainWindow, text="Tension Steel Properties")
wrapper3 = LabelFrame(mainWindow, text="Compression Steel Properties")
wrapper4 = LabelFrame(mainWindow, text="Design Properties")

wrapper1.place(x=10, y=10, width=480, height=130)
wrapper2.place(x=10, y=150, width=480, height=120)
wrapper3.place(x=10, y=280, width=480, height=120)
wrapper4.place(x=10, y=410, width=480, height=270)

trv1 = ttk.Treeview(wrapper2, columns=(1,2,3), show="headings", height=3, selectmode="none")
trv1.place(x=5, y=5, width=465)
trv1.heading(1, text='Depth (in)')
trv1.heading(2, text='No. of Bars')
trv1.heading(3, text='Diameter (in)')
trv1.column(1, width=154, anchor="c")
trv1.column(2, width=154, anchor="c")
trv1.column(3, width=154, anchor="c")
vsb1 = ttk.Scrollbar(wrapper2, orient="vertical", command=trv1.yview)
vsb1.place(x=452, y=6, height=84)
trv1.configure(yscrollcommand=vsb1.set)


trv2 = ttk.Treeview(wrapper3, columns=(1,2,3), show="headings", height=3, selectmode="none")
trv2.place(x=5, y=5, width=465)
trv2.heading(1, text='Depth (in)')
trv2.heading(2, text='No. of Bars')
trv2.heading(3, text='Diameter (in)')
trv2.column(1, width=154, anchor="c")
trv2.column(2, width=154, anchor="c")
trv2.column(3, width=154, anchor="c")
vsb2 = ttk.Scrollbar(wrapper3, orient="vertical", command=trv2.yview)
vsb2.place(x=452, y=6, height=84)
trv2.configure(yscrollcommand=vsb2.set)



# Variables
base = StringVar()
depth = StringVar()
no_of_bars = StringVar()
diameter = StringVar()
f_c = StringVar()
f_y = StringVar()


Label(wrapper1, text="Base:").place(x=10, y=10)
Label(wrapper1, text="f'c:").place(x=10, y=40)
Label(wrapper1, text="fy:").place(x=10, y=70)


Entry(wrapper1, textvariable=base).place(x=80, y=10)
Entry(wrapper1, textvariable=f_c).place(x=80, y=40)
Entry(wrapper1, textvariable=f_y).place(x=80, y=70)

Label(wrapper1, text="in").place(x=210, y=10)
Label(wrapper1, text="psi").place(x=210, y=40)
Label(wrapper1, text="psi").place(x=210, y=70)

showBtn1 = Button(wrapper1, text="Solve", command=solve, width=15)
showBtn1.place(x=300, y=10)

showBtn2 = Button(wrapper1, text="Edit Steel", command=editSteel, width=15)
showBtn2.place(x=300, y=50)


# 2nd Window
Label(wrapper4, text="Nominal Moment (Mn):").place(x=10, y=10)
Label(wrapper4, text="Ultimate Moment (Mu):").place(x=10, y=30)
Label(wrapper4, text="Beta (β):").place(x=10, y=50)
Label(wrapper4, text="Reduction Factor (Φ):").place(x=10, y=70)
Label(wrapper4, text="Height of compression block (a) - mm:").place(x=10, y=90)
Label(wrapper4, text="Height of Centroid (c):").place(x=10, y=110)
Label(wrapper4, text="Area of Tension Steel (As):").place(x=10, y=130)
Label(wrapper4, text="Area of Compression Steel (As'):").place(x=10, y=150)
Label(wrapper4, text="Deflection of Steel (ε):").place(x=10, y=170)
Label(wrapper4, text="Depth of Tension Steel (d):").place(x=10, y=190)

label_1 = Label(wrapper4, text="")
label_2 = Label(wrapper4, text="")
label_3 = Label(wrapper4, text="")
label_4 = Label(wrapper4, text="")
label_5 = Label(wrapper4, text="")
label_6 = Label(wrapper4, text="")
label_7 = Label(wrapper4, text="")
label_8 = Label(wrapper4, text="")
label_9 = Label(wrapper4, text="")
label_10 = Label(wrapper4, text="")

label_1.place(x=300, y=10)
label_2.place(x=300, y=30)
label_3.place(x=300, y=50)
label_4.place(x=300, y=70)
label_5.place(x=300, y=90)
label_6.place(x=300, y=110)
label_7.place(x=300, y=130)
label_8.place(x=300, y=150)
label_9.place(x=300, y=170)
label_10.place(x=300, y=190)

Label(wrapper4, text="ft-k").place(x=430, y=10)
Label(wrapper4, text="ft-k").place(x=430, y=30)
Label(wrapper4, text="in").place(x=430, y=90)
Label(wrapper4, text="in").place(x=430, y=110)
Label(wrapper4, text="in²").place(x=430, y=130)
Label(wrapper4, text="in²").place(x=430, y=150)
Label(wrapper4, text="in").place(x=430, y=170)
Label(wrapper4, text="in").place(x=430, y=190)

mainWindow.mainloop()