'''
Created on Mar 20, 2014

@author: liujian
'''

import Tkinter
import re,sys,os

def getMaxMininData(l):
    max_value = l[0]
    min_value = l[0]
    for i in range(1, len(l)):
        if l[i] > max_value:
            max_value = l[i]
        if l[i]<min_value:
            min_value=l[i]
    #print max_value, min_value
    return max_value,min_value

def get_top_six_process(filename):
    six = []
    fp = open(filename,'r')
    p = re.compile(r'^Total\ PSS\ by\ process:')
    #same line will find the first index for method list.index()
    try:
        all_lines = fp.readlines()
        for index in range(len(all_lines)):
            match = p.match(all_lines[index])
            if match:
                for i in range(1,7):
                    l = all_lines[index+i]
                    m = re.compile(r'\s+(\d+)\ kB:\ (.*)\ \(.*\)').match(l)
                    if m:
                        six.append(m.group(2))
        return list(set(six))
        
    except:fp.close()
    finally:fp.close()
                    

def open_meminfo(filename, pat):
    fp = open(filename,'r')
    total_pss=[]
    try:
        for line in fp.readlines():
            match_pss = pat.match(line)
            if match_pss:
                o = match_pss.group(1)
                total_pss.append(o)
        fp.close()
        return total_pss
    except:fp.close()
    finally:fp.close()
    
def deal_data(value, dip):
    l = []
    for v in value:
        v=float(v)
        l.append(v)
    """if dip >= 0:
        for v in value:
            v =float(v)
            l.append(v)
    else:    
        for v in value:
            v=float(v)
            l.append(v/(10**dip))"""
    return l

def create_process_line(canvas, data_list, process_name, color, left):
    for i in range(len(data_list)-1):
        j = i + 1
        canvas.create_line(x_wap*i+left, 440-y_wap*data_list[i], x_wap*j+left, 440-y_wap*data_list[j], fill=color)
        if process_name =='Total PSS':
            k = len(data_list)/5
            if k!=0 and j%k==0:
                canvas.create_text(x_wap*j+left, 445,text=j)
    #canvas.create_text(x_wap*len(data_list)+60, 440-y_wap*data_list[-1], text=process_name)
    canvas.pack()

if len(sys.argv) != 2:
    print 'Input Error: please double check input log file'
    sys.exit()
filename = sys.argv[1]
if not os.path.isfile(filename):
    print 'Input Error: Input not a file'
    sys.exit()

pattern_pss = re.compile(r'^Total\ PSS:\ (\d+)\ kB')
total = open_meminfo(filename, pattern_pss)
max_t,min_t = getMaxMininData(total)
d = len(max_t)-5 if len(max_t) > 5 else 0
list_total = deal_data(total, d)


tk = Tkinter.Tk()
tk.title("meminfo")
canvas = Tkinter.Canvas(tk, bg='white', width = 760, height = 480)

x_wap = 520.0/len(list_total)
y_wap=400/(getMaxMininData(list_total)[0])
left_skip = 60
canvas.create_line(left_skip,440, 580,440)
canvas.create_line(left_skip,440, left_skip,30)
create_process_line(canvas,list_total,'Total PSS', 'red', left_skip)
canvas.create_text(left_skip, 440-y_wap*float(max_t),text=max_t,anchor='e')
canvas.create_text(left_skip, 440-y_wap*float(max_t)/2,text=int(max_t)/2,anchor='e')
canvas.create_line(580, 180, 595,180, fill='red')
canvas.create_text(600,180,text='Total PSS',anchor='w')
"""
max_total, min_total = getMaxMininData(list_total)
for i in range(1,6):
    canvas.create_text(25, 440/5*i, text=int(max_total/i))
"""
top_six = get_top_six_process(filename)
rgb = ['#708069','#FFFF00','#802A2A','#FF00FF','#9ACD32','#822d2d', '#4dbc4d','#8B6508','#388E8E']

i=0
for ol in top_six:
    p = re.compile(r'^\s{3,5}(\d+)\ kB:\ %s.*' %ol)
    l_d = deal_data(open_meminfo(filename,p), d)
    if len(l_d)== len(list_total):
        #print '%s, %s'%(ol, l_d)
        create_process_line(canvas,l_d,ol,rgb[i],left_skip)
        canvas.create_line(580, 200+i*10, 595,200+i*10, fill=rgb[i])
        canvas.create_text(600,200+i*10,text=ol,anchor='w')
        i=i+1

tk.mainloop()



        
    
    
