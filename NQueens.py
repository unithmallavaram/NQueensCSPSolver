import sys
import os.path
from os import path
import copy
import queue
from datetime import datetime
import gc
gc.enable()

#stores the representation of the problem
class QueenGraph:
    #constructor method for QueenGraph
    def __init__(self, n, alg):
        self.n = n
        self.alg = alg
        self.variables = []
        self.domain = []
        self.domains = {}
        # Constraints are maintained as a set of tuples. Each tuple is of the format: (var1, operator, var2, operator, value)
        # For ex: ('Q0', '-', 'Q1', '!=', 1) means that the absolute value of Q0-Q1 is not equal to 1
        self.constraints = []
        # Assignments are maintained as a dictionary with variables as key values
        self.assignment = {}
        self.cFileText = "CSP N-QUEENS PROBLEM \n---------------------\nN = "+str(n)
        self.rFileText = "CSP: N-QUEENS PROBLEM SOLUTIONS \n--------------------------\n"
        self.solutions = []
        self.backtrackingSteps = 0
        self.executionTime = datetime.now()

    #formats the text of RFile
    def FormatRFileText(self, solutionSet):
        solutions = solutionSet[1]
        result = copy.deepcopy(self.rFileText)
        result += "N = " + str(self.n) + "\n"
        if self.alg == 'FOR':
            result += "Algorithm: Forward Checking\n"
        elif self.alg == 'MAC':
            result += "Algorithm: MAC with AC-3\n"
        result += "Number of solutions: "+str(len(solutions))+"\n"
        result += "Number of backtracking steps: "+str(solutionSet[2])+"\n"
        result += "Execution time: "+str(solutionSet[3][0])+" "+solutionSet[3][1]+"\n\n"

        if self.n <= 3:
            result += "No solutions"
        else:
            rows = ["None"]*int(self.n)
            result += "The grids represent "+ str(self.n)+"X"+str(self.n)+" chess boards\n"
            result += "If a square is occupied by a queen, it shows 1, O otherwise\n\n"
            for solution in solutions:
                for item in solution:
                    result += item +" = "+str(solution[item])+"; "
                    rows[solution[item]] = int(item[1:len(item)])
                result += "\n"
                for row in rows:
                    for i in range(int(self.n)):
                        if row == i:
                            result += str(1)+" "
                        else:
                            result += str('O')+" "
                    result += "\n"
                result += "\n"
        return result

    #prints output
    def PrintSolutions(self, solutionSet):
        print("CSP: NQueens problem")
        print("N = "+str(self.n))
        print("Number of solutions: "+str(len(solutionSet[1])))
        print("Algorithm: "+self.alg)
        print("Number of backtracking steps: "+str(self.backtrackingSteps))
        print("Execution time: "+str(solutionSet[3][0])+" "+solutionSet[3][1])

    #defines variables based on the value of n
    def SetVariables(self):
        self.cFileText += "\n\nVARIABLES:"
        for i in range(n):
            self.variables.append("Q"+str(i))
            self.cFileText += "\n"+"Q"+str(i)
        self.cFileText += "\nwhere Qi (i runs from 0 to "+str(self.n - 1)+") is the position(row) of the Queen in i-th column"

    #sets the initial domains for the variables
    def SetDomains(self):
        self.cFileText += "\n\nDOMAINS:"
        temp = []
        domain = "{"
        for i in range(n):
            temp.append(i)
            if i != n-1:
                domain += str(i)+", "
            else:
                domain += str(i)
        domain += "}"
        #check
        self.domain = copy.deepcopy(temp)
        #check
        for i in range(n):
            id = "Q"+str(i)
            self.domains[id] = copy.deepcopy(temp)
            self.cFileText += "\n"+id+": "+domain

    #sets the constrainsts for the CSP problem
    def SetConstraints(self):
        self.cFileText += "\n\nCONSTRAINTS: "
        for i in range(n):
            #constraints telling that no two queens should be in the same row or diagonal
            for j in range(i+1, n):
                constraint = "|" + "Q" + str(j) + "-" + "Q" + str(i) + "|" + " " + "!=" + " " + str(0)
                constraintTuple = ("Q" + str(i), '-', "Q" + str(j), '!=', 0)
                self.constraints.append(constraintTuple)
                self.cFileText += "\n" + constraint
                constraint = "|" + "Q" + str(j) + "-" + "Q" + str(i) + "|" + " " + "!=" + " " + str(abs(i - j))
                constraintTuple = ("Q" + str(i), '-', "Q" + str(j), '!=', abs(i - j))
                self.constraints.append(constraintTuple)
                self.cFileText += "\n" + constraint

    #sets the initial assignments of all the variables to none
    def SetInitialAssignment(self):
        for i in self.variables:
            self.assignment[i] = 'None'

    #checks if all the variables in the assignment are assigned
    def IsComplete(self, assignment):
        for i in assignment:
            if assignment[i] == 'None':
                return 0
        return 1

    #returns the next unassigned variable
    def SelectUnassignedVariable(self, assignment):
        for item in assignment:
            if assignment[item] == 'None':
                return item

    #returns the domain values of the argument variable
    def OrderDomainValues(self, var):
        return self.domains[var]

    #checks if the assignment is consistent
    def IsConsistent(self, var, value, assignment):
        #check column consistency
        for item in self.assignment:
            if item != var:
                if assignment[item] == value:
                    return 0
        #check diagonal consistency
        for item in self.assignment:
            if item != var:
                if assignment[item] != "None":
                    if abs(int(item[1:len(item)]) - int(var[1:len(var)])) == abs(assignment[item] - value):
                        return 0
        return 1

    #assigns the given value to var in the assignment
    def Assign(self, var, value, assignment):
        assignment[var] = value

    #removes the assignment of value to the var in the assignment
    def Unassign(self, var, assignment):
        assignment[var] = "None"

    #returns the initial queue for MAC for a variable
    def GetInitialQueue(self, var):
        i = int(var[1:len(var)])
        macQueue = queue.Queue(0)
        tuple1 = var
        for j in range(i+1, int(self.n)):
            tuple2 = "Q"+str(j)
            #tuple3 = 0
            macQueue.put((tuple2, tuple1))
            #tuple3 = abs(j - i)
            #macQueue.put((tuple2, tuple1))
        return macQueue

    #returns true if no value in domain of var1 is consistent with a value in domain of var2 wrt to the arc
    def NotCompatible(self, val0, arc, tempDomain, removals):
        notCompatible = 0
        if self.assignment[arc[1]] != "None":
            domainVar1 = [self.assignment[arc[1]]]
            for val1 in domainVar1:
                # check row constraints and remove inconsistent values
                if val0 - val1 == 0:
                    if val1 in tempDomain[arc[0]]:
                        notCompatible = 1
                # check diagonal constraint and remove inconsistent values
                elif abs(val0 - val1) == abs(int(arc[0][1:len(arc[0])]) - int(arc[1][1:len(arc[1])])):
                    if val0 in tempDomain[arc[0]]:
                        notCompatible = 1
        else:
            domainVar1 = tempDomain[arc[1]]
            killed = 0
            for val1 in domainVar1:
                # check row constraints and determine if the values are consistent
                if val0 - val1 == 0:
                    if val1 in tempDomain[arc[0]]:
                        killed += 1
                # check diagonal constraint and determine if the values are consistent
                elif abs(val0 - val1) == abs(int(arc[0][1:len(arc[0])]) - int(arc[1][1:len(arc[1])])):
                    if val0 in tempDomain[arc[0]]:
                        killed += 1
            #if there is no consistent value for the second variable, the value is incompatible and should be removed from domain
            if killed == len(domainVar1):
                notCompatible = 1
        return notCompatible

    #Revises the domain of the variables in the arc
    def Revise(self, arc, removals, tempDomains):
        revised = 0
        for val0 in self.domains[arc[0]]:
            if self.NotCompatible(val0, arc, tempDomains, removals):
                #remove the value from the domain if there is no value in the other variable's domain that satisfies the arc
                removals.append((arc[0], val0))
                if val0 in tempDomains[arc[0]]:
                    tempDomains[arc[0]].remove(val0)
                revised = 1
        return [revised, removals]

    #Adds neighbors of the variable to the MAC queue
    def AddNeighbors(self, macQueue, var):
        i = int(var[1:len(var)])
        for j in range(i+1, int(self.n)):
            var2 = "Q"+str(j)
            macQueue.put((var2, var))

    #returns inferences: using forward checking or MAC
    def Inference(self, assignment, domains, var, value, alg):
        #Forward Checking
        if alg == 'FOR':
            #removlas resulting from inference
            removals = []
            #copy the domains and remove elements according to inferences. if the resulting domain is empty, return failure
            tempDomains = copy.deepcopy(domains)
            for item in assignment:
                #for all the variables other than the current variable
                if item != var:
                    #if the variable is unassigned
                    if assignment[item] == 'None':
                        #apply row constrainsts and add domain removals for unassigned varables
                        if value in tempDomains[item]:
                            tempDomains[item].remove(value)
                            removals.append((item, value))
                        #apply diagonal constraints and add domain removals for unassigned variables
                        for d in tempDomains[item]:
                            if abs(d - value) == abs(int(item[1:len(item)]) - int(var[1:len(var)])):
                                tempDomains[item].remove(d)
                                removals.append((item, d))
                        #if the length of any domain resulting from inferences is zero,
                        #if len(tempDomains[item]) == 0:
                            #return [0, []]
            return [1, removals]

        #MAC with AC3
        elif alg == 'MAC':
            removals = []
            tempDomains = copy.deepcopy(self.domains)
            macQueue = self.GetInitialQueue(var)
            while macQueue.qsize() != 0:
                arc = macQueue.get()
                reviseResult = self.Revise(arc, removals, tempDomains)
                if reviseResult[0]:
                    if len(tempDomains[arc[0]]) == 0:
                        return [0, reviseResult[1]]
                    #add other neighbours to the queue
                    self.AddNeighbors(macQueue, arc[0])
            return [1, removals]

    #adds the inferences to the assignment
    def AddInferences(self, inferences, assignment, domains):
        removals = inferences[1]
        #remove values from domains using removals
        for r in removals:
            domains[r[0]].remove(r[1])

    #remvoes inferences from the assignment
    def RemoveInferences(self, inferences, assignment, domains):
        removals = inferences[1]
        #undo the removals from domain using removals
        for r in removals:
            if r[1] not in domains[r[0]]:
                domains[r[0]].append(r[1])

    #performs backtracking search and returns the solutions
    def BacktrackingSearch(self, initialAssignment):
        return self.Backtrack(initialAssignment)

    #recursive backtrack method
    def Backtrack(self, assignment):

        if self.IsComplete(assignment):
            solution = copy.deepcopy(assignment)
            self.solutions.append(solution)
            if len(self.solutions) < 2*self.n:
                return [0, assignment]
            elif len(self.solutions) == 2*self.n:
                return[1, self.solutions, self.backtrackingSteps]
        var = self.SelectUnassignedVariable(assignment)
        for value in self.OrderDomainValues(var):
            if self.IsConsistent(var, value, assignment):
                self.Assign(var, value, assignment)
                domains = self.domains
                #inferences is an array of this format: [isSuccess, removals, assnInferences]
                inferences = self.Inference(assignment, domains, var, value, alg)
                if inferences[0]: #No failure detected by inference
                    self.AddInferences(inferences, assignment, domains)
                    result = self.Backtrack(assignment)
                    if result[0] != 0:
                        return result
                self.RemoveInferences(inferences, assignment, domains)
            self.Unassign(var, assignment)
        self.backtrackingSteps += 1
        return [0, self.solutions, self.backtrackingSteps]


alg = sys.argv[1]
n = int(sys.argv[2])
cFile = sys.argv[3]+".txt"
rFile = sys.argv[4]+".txt"


#Instantiating the representation of NQueens problem
QueenGraph = QueenGraph(n, alg)
QueenGraph.SetVariables()
QueenGraph.SetDomains()
QueenGraph.SetConstraints()
QueenGraph.SetInitialAssignment()

#write to CFile.txt
cFileText = QueenGraph.cFileText
file = open(cFile, "w")
file.write(cFileText)
file.close()

#performing backtrack search on the problem
solution = QueenGraph.BacktrackingSearch(QueenGraph.assignment)

solution.append(((datetime.now() - QueenGraph.executionTime).total_seconds(), "seconds"))
#write to RFile.txt
rFileText = QueenGraph.FormatRFileText(solution)
file = open(rFile, "w")
file.write(rFileText)
file.close()

QueenGraph.PrintSolutions(solution)






