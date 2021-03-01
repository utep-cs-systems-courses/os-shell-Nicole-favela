#! /usr/bin/env python3

import os, sys, re
pid = os.getpid()
start = 0
max = 0
def exec(args): #exec process
    if len(args) == 0: #if string length is 0 
        return
    #exits program
    elif args[0].lower() == "exit": #allows user to exit program
        sys.exit(0)
    elif args[0] == "cd..": #up one directory
        os.chdir("..")
    elif args[0] == "cd": #change dir
        try:
            if len(args) == 1: #change to home
                os.chdir(os.getenv("HOME"))
            #go to directory
            else:
                os.chdir(args[1]) #changes to directory specified
        except:
            os.write(1, ("cd %s: no such file/directory" % args[1]).encode())#writes to display
            pass
    elif "|" in args: #for pipe command
        pipe(args)
    elif "pwd" == args[0]:#prints current working directory 
        path = os.getcwd()
        os.write(1,("%s\n" % path).encode())#string to bits 
    else:
        rc = os.fork()
        if "$" in args: #removes $ 
            args.remove("$")
        if rc<0: 
            os.write(2, ("fork failed, returning %d\n" % rc).encode())
            sys.exit(1)
        elif rc == 0:#child process
            if "/" in args[0]:
                program = args[0]
                os.write(1, ("Child: trying to exec %s\n" % program).encode())
                try:
                    os.execve(program, args, os.environ) #try to exec program
                except FileNotFoundError:
                    pass #...fail quietly
            elif '>' in args or '<' in args:
                redirect(args)
            else:
                for dir in re.split(":", os.environ['PATH']):#try each directory
                    program = "%s/%s" % (dir, args[0])
                    try:
                        os.execve(program, args, os.environ) #exec program
                    except FileNotFoundError:
                        pass #fail quietly
            #command not found
            os.write(2, (args[0] ,"command not found\n").encode())#print which cmd not found
            sys.exit(0) #exits program
        else:
            chPID = os.wait() #pid of child

def command(args):
    if "/" in args[0]:
        program = args[0]
        try:
            os.execve(program, args, os.environ)#try to execute program 
        except FileNotFoundError:
            pass
    elif ">" in args or "<" in args:#for redirection
        redirect(args)
    else:
        for dir in re.split(":", os.environ['PATH']):#try next directory
            program = "%s/%s" % (dir, args[0])
            try:
                os.execve(program, args, os.environ)#try to exec
            except FileNotFoundError:
                pass #fail quietly
    os.write(2, ("%s: command not found\n" % args[0].encode()))#show error message to fd2
    sys.exit(0) #exits
def redirect(args):
    if '>' in args:
        os.close(1) #close fd1 attached to display
        os.open(args[args.index('>')+1], os.O_CREAT | os.O_WRONLY)#create file if there isnt one or write to file
        os.set_inheritable(1,True)#makes fd1 inheritable 
        args.remove(args[args.index('>')+1])# removes value after >
        args.remove('>')#removed goes into
    else: 
        os.close(0) #closes file descriptor 0 attached to standard input of keyboard
        os.open(args[args.index('<')+1], os.O_RDONLY) #read only
        os.set_inheritable(0,True) #make fds inheritable 
        args.remove(args[args.index('<') + 1]) #removes value after comes outta
        args.remove('<') #removes comes outta
    for i in re.split(":", os.environ['PATH']):#goes through path
        program = "%s/%s" % (i, args[0])
        try:
            os.execve(program, args, os.environ) #try to run
        except FileNotFoundError:
            pass #couldnt find file, fail quietly
    os.write(2, ("%s command not found\n" % args[0]).encode())#write error message to display
    sys.exit(0)#exits 

#creates line from chars for use in 
def readLine():
    global start
    global max 
    line = ""
    char = getChar()
    while(char != "EOF" and char != ''):
        line+=char #accumultes chars 
        char = getChar() #gets chars to accumulate in line
    start = 0
    max = 0
    return line #returns string
#gets chars
def getChar():
    #start and max used to indicate start of array and max chars 
    global start
    global max 
    if start== max: #initially 0=0, 
        start = 0
        max = os.read(0,1000) #fill with 1000 bytes
        
        if max == 0:
            return "EOF"
    if start < len(max)-1: #we need to fill array
        charArray = chr(max[start]) #returns string representing a char
        start+=1
        return charArray
    else:
        return "EOF"
 
def pipe(args):
    leftSide = args[0:args.index("|")] #gets command to left of pipe
    rightSide = args[len(leftSide)+1:] #gets command to right of pipe 
    pr,pw = os.pipe() #pipe system call on read and write
    rc = os.fork() 
    if rc < 0: 
        os.write(2,("error: fork failed %d\n" % rc).encode())#error message 
        sys.exit(1)#terminate with error
    elif rc == 0:#child process
        os.close(1) #close fd1 (attached to output)
        os.dup(pw) #duplicate
        os.set_inheritable(1,True) #makes fd inheritable 
        for fd in (pw,pr):#pr for read, pw for write
            os.close(fd) #closes fds for read/write
        command(leftSide) #calls command on left command
    
    else: #parent process
        os.close(0) #close fd 0 attached to kbd
        os.dup(pr)
        os.set_inheritable(0, True)#makes fd inheritable
        for fd in (pw,pr):#closes file descriptors
            os.close(fd)
        if "|" in rightSide: #if more pipes found in the rightside
            pipe(rightSide)
        command(rightSide)#calls command with the rest of the commands/files
            
def prompt():
    
        if 'PS1'in os.environ:
             os.write(1, (os.environ['PS1']).encode())
        else:
             os.write(1, ("$ ").encode())# shows$ prompt if PS1 environ not found

while 1:
    prompt()
    myline = readLine()#reads lines of input from user 
    lineArgs= myline.split()
     
    exec(lineArgs) #executes commnands
