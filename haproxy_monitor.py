#!/usr/bin/env python

import subprocess
import urllib2
import sys
import os
import time
import re
from bs4 import BeautifulSoup

def _poll(p):
    u = urllib2.urlopen(p)
    return u.read()

def _format_data(d):
    csv_split = []
    rd = ()
    for r in d.splitlines():
        csv_split = r.split(',')
        rd += (csv_split,) 
    return rd 

def _main():  
    port = int(sys.argv[1])
    url =  "http://127.0.0.1:%d/stats" %(port+10000)
    tmp_file = "/tmp/haproxy%s.tmp1" %port
    fd = open(tmp_file,'w+')
    try:    
        csv_data = _poll("%s/;csv" % url)
    except:
        print "-1,csv"
        sys.exit(0)
    try:
        global_data = _poll("%s" % url)
    except:
        print "-1,global"
        sys.exit(0)
    result = _format_data(csv_data)
    soup = BeautifulSoup(global_data)

#get monitor items    
    #process health
   
    ppid=soup.findAll(text=re.compile("process #"))[0]
    pid=str(ppid).split(' ')[1]
    proc_num = str(ppid).split(' ')[6].split(')')[0]
    
    pids_cmd=" ps -ef | grep 'haproxy%s.cfg'| grep -v grep | awk '{print $2}'"%port
    pids_list=list(str(os.popen(pids_cmd).read()).split('\n'))[0:-1]
    pid_num=len(pids_list)
    
    #debug info#print proc_num,pid_num
    if int(pid_num) == int(proc_num):
       health = 0
       print health
    else:
       health = int(proc_num)-int(pid_num)
       print -1
       sys.exit(0)
    str_health = "proc_health " + str(health) +'\n'
#    print str_health
    fd.write(str_health) 
    #pid
    str_pid="pid "+str(ppid).replace(' ','')+'\n'
#    print str_pid
    fd.write(str_pid)
    #cpu
    index = 0
    sum_cpu = 0
    for i in pids_list:
        cpu_cmd="top -c -b -n 1 -p %s |tail -2|awk '{print $9}'|awk -F. '{print $1}'" % i
        cpu = os.popen(cpu_cmd).readlines()[0]
        sum_cpu = sum_cpu + int(cpu)
        index = index + 1
    avg_cpu = round(sum_cpu/index,2) 
    str_cpu='avg_cpu '+str(avg_cpu)+'\n' 
#    print str_cpu  
    fd.write(str_cpu)
       
    #uptime
    uptime=soup.findAll(text=re.compile("[0-9]*d [0-9]*h[0-9]*m[0-9]*s"))[0]
    str_uptime="uptime "+str(uptime).replace(' ','')+'\n'
#    print str_uptime
    fd.write(str_uptime)
    #memmax
    memmax=soup.findAll(text=re.compile("memmax ="))[0].split(";")[0].split("=")[1]
    str_memmax="memmax "+memmax+'\n'
#    print str_memmax
    fd.write(str_memmax)
    #ulimitn
    ulimitn=soup.findAll(text=re.compile("ulimit-n ="))[0].split(";")[1].split("=")[1]
    str_ulimit= "ulimit-n"+ulimitn+'\n'
#    print str_ulimit
    fd.write(str_ulimit)
    #maxsock
    maxsock=re.findall("<b>maxsock = </b> [0-9]*",global_data)[0].split(" ")[3]
    str_maxsock="maxsock "+maxsock+'\n'
#    print str_maxsock
    fd.write(str_maxsock)
    #maxconn
    maxconn=re.findall("<b>maxconn = </b> [0-9]*",global_data)[0].split(" ")[3]
    str_maxconn="maxconn "+maxconn+'\n'
#    print  str_maxconn
    fd.write(str_maxconn)
    #maxpipes
    maxpipes=re.findall("<b>maxpipes = </b> [0-9]*",global_data)[0].split(" ")[3]
    str_maxpipes="maxpipes "+maxpipes+'\n'
#    print str_maxpipes
    fd.write(str_maxpipes)
    #curconns
    curconns=re.findall("current conns = [0-9]*",global_data)[0].split(" ")[3]
    str_curconns="curconns "+curconns+'\n'
#    print str_curconns
    fd.write(str_curconns)
    #curpipes
    curpipes=re.findall("current pipes = [0-9]*/[0-9]*",global_data)[0].split(" ")[3]
    str_curpipes="curpipes "+curpipes+'\n'
#    print str_curpipes
    fd.write(str_curpipes)

    #node health
    key = 'status'
    health = 0
    index = result[0].index(key)
    li=range(len(result))
    nli=li[2:-3]
    for i in nli: 
        if result[i][index] != "UP":
           health = health + 1
    str_health="node_health "+str(health)+'\n'
#    print str_health
    fd.write(str_health)
    
    #node_health
    key = 'status'
    health = 0
    index = result[0].index(key)
    li = range(len(result))
    nli = li[2:-3]
    for i in nli:
        if result[i][index] != "UP":
           health = 1
        str_health='nd_health '+result[i][0]+':'+result[i][1]+' '+str(health)+'\n'
#        print str_health
        fd.write(str_health)
        health = 0
    #queue_cur
    key = 'qcur'
    index = result[0].index(key)
    li = range(len(result))
    nli = li[2:-3]
    for i in nli:
        str_qcur = 'queue_cur '+result[i][0]+':'+result[i][1]+' '+result[i][index]+'\n' 
#        print str_qcur
        fd.write(str_qcur)
    #queue_max
    key = 'qmax'
    index = result[0].index(key)
    li = range(len(result))
    nli = li[2:-3]
    for i in nli:
        str_qmax = 'queue_max '+result[i][0]+':'+result[i][1]+' '+result[i][index]+'\n'
#        print str_qmax
        fd.write(str_qmax)
    #Session rate cur
    key = 'scur'
    index = result[0].index(key)
    li = range(len(result))
    nli = li[2:-3]
    for i in nli:
        str_scur = 'session_cur '+result[i][0]+':'+result[i][1]+' '+result[i][index]+'\n'
#        print str_scur
        fd.write(str_scur)
    _tmp_file="/tmp/haproxy%s.tmp" %port
    os.rename(tmp_file,_tmp_file)
    fd.close()
if __name__ == '__main__':
     _main()

