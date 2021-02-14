#! /usr/bin/env python3

import os, sys, re
pid = os.getpid()

def exec(args):
    if len(args) == 0: #if string length is 0 
        return
    #exits program
    elif args[0].lower() == "exit": #allows user to exit program
        sys.exit(0)
    elif args[0] == "cd": #change directory 
        try:
            if len(args) == 1:
                os.chdir("..") #up one directory
            #go to directory
            else:
                os.chdir(args[1]) #changes to directory specified
        except:
            os.write(1, ("cd %s: no such file/directory" % args[1]).encode())
            pass  
    else:
        rc = os.fork()
        background = True
        if "$" in args: #removes $ 
            args.remove("$")
            background = False
        if rc<0: 
            os.write(2, ("fork failed, returning %d\n" % rc).encode())
            sys.exit(1)
        elif rc == 0:#child process
            os.write(2, ("Child: pid==%d. parent's pid=%d\n" % (os.getpid(),pid)).encode())
            if "/" in args[0]:
                program = args[0]
                try:
                    os.execve(program, args, os.environ)
                except FileNotFoundError:
                    pass
            else:
                for dir in re.split(":", os.environ['PATH']):#split by colon
                    program = "%s/%s" % (dir, args[0])
                    try:
                        os.execve(program, args, os.environ) #exec program
                    except FileNotFoundError:
                        pass #failed
            #command not found
            os.write(2, (arg[0] ,"command not found\n").encode())#print which cmd not found
            sys.exit(0) #exits program
        else:
            if background:
                os.write(1, ("Parent: my pid=%d. Child's pid=%d\n" % (pid,rc)).encode())
                chPID = os.wait() #pid of child

def command(args):
    if "/" in args[0]:
        program = args[0]
        try:
            os.execve(program, args, os.environ)
        except FileNotFoundError:
            pass
    else:
        for dir in re.split(":", os.environ['PATH']):#try next directory
            program = "%s/%s" % (dir, arg[0])
            try:
                os.execve(program, args, os.environ)
            except FileNotFoundError:
                pass #failed
    os.write(2, ("%s: command not found\n" % args[0].encode()))
    sys.exit(0) #exits
while True:
        if 'PS1'in os.environ:
             os.write(1, (os.environ['PS1']).encode())
        else:
             os.write(1, ("$ ").encode())
        args = os.read(0, 1024)# reads a kb 
        #empty
        if len(args) == 0:
             break
        args = args.decode().splitlines() #gets string
        #splits
        for i in args: #splits up string 
             exec(i.split())
            
