import numpy as np
import argparse
from copy import deepcopy
from collections import defaultdict
from ast import literal_eval as make_tuple
import re
class Stack:
     def __init__(self):
         self.items = []

     def isEmpty(self):
         return self.items == []

     def push(self, item):
         self.items.append(item)

     def pop(self):
         return self.items.pop()

     def peek(self):
         return self.items[len(self.items)-1]

     def size(self):
         return len(self.items)
class DFA:
    def __init__(self):
        self.initialState = None
        self.states = set()
        self.lang = []
        self.nfaStates = dict()
        self.finalState = []
        self.transitions = []

    def display(self):
        print ("states: ", self.states)
        print ("initial state: ", self.initialState)
        print ("lang: ", self.lang)
        print ("nfastates: ", self.nfaStates)
        print ("final states: ", self.finalState)
        print ("transitions: ", self.transitions)
class NFA:
    def __init__(self):
        self.initialState = None
        self.states = set()
        self.lang = []
        self.finalState = None
        self.transitions = []

    def display(self):
        print ("states: ", self.states)
        print ("initial state: ", self.initialState)
        print ("lang: ", self.lang)
        print ("final states: ", self.finalState)
        print ("transitions: ", self.transitions)

def readInput(path):
    input = open(path, 'r')
    input = input.read().splitlines()
    nfa = NFA()
    nfa.states = input[0].split(',')
    nfa.lang = input[1].split(',')
    nfa.initialState = input[2]
    nfa.finalState = input[3].split(',')
    transitions = input[4].replace("),(","|").replace("),  (","|").replace("), (","|")
    transitions = transitions.split('|')
    transitions[0] = transitions[0].strip('(')
    transitions[-1] = transitions[-1].strip(')')
    for transition in transitions:
        transition = transition.split(',')
        if(transition[1] != " "):
            transition[1] = transition[1].strip(" ")
        transition[2] = transition[2].strip(" ")
        nfa.transitions.append({
            "from": transition[0],
            "input": transition[1],
            "to": transition[2]
        })
    # nfa.display()
    # print(nfa.transitions)
    return nfa

def createHashMap(path):
    nfa = readInput(path)
    hashMap = defaultdict(list)
    for transition in nfa.transitions:
        if transition['input'] == ' ':
            hashMap[transition['from']] += [transition['to']]
    return hashMap,nfa

def getEclosure(state,path):
    stack = Stack()
    [hashMap,_] = createHashMap(path)
    closures = list()
    closures.append(state)
    stack.push(state)
    while(not stack.isEmpty()):
        state = stack.pop()
        for eclosure in hashMap[state]:
            stack.push(eclosure)
            closures.append(eclosure)
    return closures

def initializeDFA(path):
    [hashMap, nfa] = createHashMap(path)
    nfaStates = set()
    stack = Stack()
    dfa = DFA()
    dfa.initialState = 'A'
    dfa.states.add(dfa.initialState)
    stack.push(nfa.initialState)
    nfaStates.add(nfa.initialState)
    while(not stack.isEmpty()):
        state = stack.pop()
        for state in hashMap[state]:
            stack.push(state)
            nfaStates.add(state)
    dfa.nfaStates[dfa.initialState] = list(nfaStates)
    # dfa.display()
    return dfa,nfa,hashMap

def writeOutput(dfa):
    string = ""
    output = open('task_2_2_result.txt','w+')
    for state in sorted(dfa.states):
        string+= state+', '
    output.write(string[:-2])
    output.write('\n')
    string = ""
    for lang in sorted(dfa.lang):
        string += lang+', '
    output.write(string[:-2])
    output.write('\n')
    output.write(dfa.initialState)
    output.write('\n')
    string = ""
    for finalstate in sorted(dfa.finalState):
        string += finalstate+', '
    output.write(string[:-2])
    output.write('\n')
    string = ""
    for transition in dfa.transitions:
        string+= '('+transition['from']+', '+transition['input']+', '+transition['to']+')'+', '
    output.write(string[:-2])

def DFA2NFA(path):
    stack = Stack()
    counter = 0
    stateCounter = 0
    [dfa, nfa, _] = initializeDFA(path)
    if " " in nfa.lang:
        nfa.lang.remove(" ")
    dfa.lang = nfa.lang
    stack.push(dfa.nfaStates[dfa.initialState])
    while(not stack.isEmpty()):
        states = stack.pop()
        # print("popped",states)
        # print('=============================================================================')
        # print("iteration number",counter)
        # print('=============================================================================')
        for lang in nfa.lang:
            # print("testing",lang)
            newState = list()
            for state in states:
                for transition in nfa.transitions:
                    if ( (transition['from'] == state) and (transition['input'] == lang) ):
                        to = transition['to']
                        # newState.append(to)
                        closures = getEclosure(to,path)
                        newState += closures
                        # print("newState",newState)
            if(not newState in dfa.nfaStates.values()):
                print("NewState not in stack", newState)
                if(len(newState)>0):
                    dfa.nfaStates[chr(ord('A')+counter+1)] = newState
                    # print(dfa.nfaStates)
                    stack.push(newState)
                    # print("pushed",newState)
                    dfa.states.add(chr(ord('A')+counter+1))
                    dfa.transitions.append({
                        "from": chr(ord('A')+stateCounter),
                        "input": lang,
                        "to": chr(ord('A')+counter+1)
                    })
                    # print('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
                    # print("transition",dfa.transitions)
                    # print('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
                    counter += 1
                #handle dead state dunno what to do
                else:
                    if(['DEAD'] in dfa.nfaStates.values()):
                        dfa.transitions.append({
                            "from": chr(ord('A')+stateCounter),
                            "input": lang,
                            "to": 'DEAD'
                        })
                    else:
                        dfa.nfaStates['DEAD'] = ['DEAD']
                        dfa.states.add('DEAD')
                        dfa.transitions.append({
                            "from": chr(ord('A')+stateCounter),
                            "input": lang,
                            "to": 'DEAD'
                        })
            else:
                dfa.transitions.append({
                    "from": chr(ord('A')+stateCounter),
                    "input": lang,
                    "to": dfa.nfaStates.keys()[dfa.nfaStates.values().index(newState)]
                })
                # print('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
                # print("transition",dfa.transitions)
                # print('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
        stateCounter += 1
    for state in dfa.nfaStates.values():
        # print(nfa.finalState[0])
        if(nfa.finalState[0] in state):
            # print(state)
            dfa.finalState.append(dfa.nfaStates.keys()[dfa.nfaStates.values().index(state)])
    writeOutput(dfa)
    dfa.display()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(add_help=True, description='Sample Commandline')

    parser.add_argument('--file', action="store", help="path of file to take as input", nargs="?",metavar="file")

    args = parser.parse_args()
    DFA2NFA(args.file)

