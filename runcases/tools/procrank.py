# --*-- encoding:utf-8 --*--
'''
Created on Mar 20, 2014

@author: liujian
'''

import Tkinter
import re,sys,os

def getMaxFromList(l):
    max_value = l[0]
    for i in range(1, len(l)):
        if l[i] > max_value:
            max_value = l[i]
    #print max_value, min_value
    return max_value

def list_Pss(process, filename):
    fp = open(filename,'r')
    total_pss=[]
    try:
        for line in fp.readlines():
            match_pss = re.compile(r'\s*\d+\s+\d+K\s+\d+K\s+(\d+)K\s+\d+K\s+%s$' %process).match(line)
            if match_pss:
                o = match_pss.group(1)
                total_pss.append(int(o))
        fp.close()
        return total_pss
    except:fp.close()
    finally:fp.close()
    
def get_top(filename):
    fp = open(filename,'r')
    try:
        all_lines = fp.readlines()
        lines = []
        times = 0
        for i in range(len(all_lines)):
            m = re.search(r'(\s+PID\s+Vss\s+Rss\s+Pss\s+Uss\s+cmdline)',all_lines[i])
            if m:
                times += 1
                for j in range(1, 10):
                    lines.append(all_lines[i+j])
        pname=[]
        for line in lines:
            m = re.search(r'(?P<PID>\d+)\s+(?P<Vss>\d+K)\s+(?P<Rss>\d+K)\s+(?P<Pss>\d+K)\s+(?P<Uss>\d+K)\s+(?P<Pname>\S+)',line)
            if m:
                pname.append(m.groupdict()['Pname'])
        
        max=0
        l = list(set(pname))
        for each in list(set(pname)):
            length = 0
            for i in all_lines:
                m = re.search(r'(?P<PID>\d+)\s+(?P<Vss>\d+)K\s+(?P<Rss>\d+)K\s+(?P<Pss>\d+)K\s+(?P<Uss>\d+)K\s+(?P<Pname>%s$)' %each,i)
                if m:
                    if int(m.groupdict()['Pss'])>max:
                        max = int(m.groupdict()['Pss'])
                    length += 1
            if length < times:
                l.remove(each)
        l.append(times)
        l.append(max)
        return l
        
    except:fp.close()
    finally:fp.close()
    

def create_process_line(canvas, data_list, process_name, color, left):
    for i in range(len(data_list)-1):
        j = i + 1
        #print '%s,%s %s,%s' %(x_wap*i+left, 440-y_wap*data_list[i], x_wap*j+left, 440-y_wap*data_list[j])
        canvas.create_line(x_wap*i+left, 440-y_wap*data_list[i], x_wap*j+left, 440-y_wap*data_list[j], fill=color)
    canvas.pack()


if len(sys.argv) != 2:
    print 'Input Error: please double check input log file'
    sys.exit()
filename = sys.argv[1]
if not os.path.isfile(filename):
    print 'Input Error: Input not a file'
    sys.exit()

tk = Tkinter.Tk()
tk.title("procrank")
canvas = Tkinter.Canvas(tk, bg='white', width = 760, height = 480)
rgb = ['red','#708069','#FFFF00','#802A2A','#FF00FF','#9ACD32','#822d2d', '#4dbc4d','#8B6508','#388E8E', '#EE00EE', '#0A0A0A', '#008B8B']


start_end_process = get_top(filename)
max_data = start_end_process.pop()
length = start_end_process.pop()

top = start_end_process[0]
x_wap = 520.0/length
y_wap=400.0/max_data
left_skip = 50
canvas.create_line(left_skip,440, 580,440)
canvas.create_line(left_skip,440, left_skip,30)
canvas.create_text(left_skip, 440-y_wap*float(max_data),text=max_data,anchor='e')
canvas.create_text(left_skip, 440-y_wap*float(max_data)/2,text=int(max_data)/2,anchor='e')
canvas.create_text(left_skip, 447,text=0)
canvas.create_text(left_skip+520, 447,text=length)
canvas.create_text(left_skip+520/2, 447,text=int(length)/2)

i=0
for ol in start_end_process:
    l_d = list_Pss(ol, filename)
    create_process_line(canvas,l_d,ol,rgb[i],left_skip)
    canvas.create_line(580, 200+i*10, 595,200+i*10, fill=rgb[i])
    canvas.create_text(600,200+i*10,text=ol,anchor='w')
    i=i+1

tk.mainloop()


        
    
    
