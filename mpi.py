import numpy as np
from mpi4py import MPI
import time
from random import randint

comm = MPI.COMM_WORLD
totalprocess = comm.Get_rank()
#total de processos usados no calculo
worldSize = comm.Get_size() - 1

#setando o resultado final como vazio
finalresult = None

# N se iguala a quantidade de matrizes
N = 60

#criacao das N's matrizes
def generate_matrix():
    globalmatrix = list()
    for i in range(N):
        obj = [[randint(1,9), randint(1,9), randint(1,9), randint(1,9), randint(1,9)],
        [randint(1,9), randint(1,9), randint(1,9), randint(1,9), randint(1,9)],
        [randint(1,9), randint(1,9), randint(1,9), randint(1,9), randint(1,9)],
        [randint(1,9), randint(1,9), randint(1,9) ,randint(1,9) ,randint(1,9)],
        [randint(1,9), randint(1,9), randint(1,9), randint(1,9), randint(1,9)]]
        globalmatrix.append(obj)
    return globalmatrix
  

#todo resultado é incrementado na matriz 5x5 result
def multiply_matrix(X,Y):
    result =    [[0,0,0,0,0],
                [0,0,0,0,0],
                [0,0,0,0,0],
                [0,0,0,0,0],
                [0,0,0,0,0]]
    for i in range(len(X)):
        for j in range(len(Y[0])):
            for k in range(len(Y)):
                result[i][j] += X[i][k] * Y[k][j]
    return result


#matrizes = generate_matrix()

#uso dos processadores para os calculos
def master():
    global finalresult
    for x in range(1,worldSize+1):
        if finalresult is None:
            finalresult = comm.recv(tag=x)
        else:
            value = comm.recv(tag=x)
            finalresult = multiply_matrix(finalresult, value)
            # finalresult = sorted(mult)

globalmatrix = generate_matrix()
def first_check_sum():
    checkresult = None
    for testmatrix in globalmatrix:
        if checkresult is None:
            checkresult = testmatrix
        else:
            checkresult = multiply_matrix(checkresult, testmatrix)
    return checkresult

def matrix_div():
    matrix_div = int(len(globalmatrix)/worldSize)
    position = 0
    for x in range(1, worldSize + 1):
        data = globalmatrix[position : position + matrix_div]
        comm.send(data, dest=x, tag=x)
        position = position + matrix_div


if __name__ == '__main__':
    if totalprocess == 0: #o processo 0 cuida e abastecer os outros 4 processos
        checkresult = first_check_sum()
        matrix_div()
        
        master()
        print('===============================================')
        print(finalresult)
        print('===============================================')
        print('\n')
        print("Os resultados coincidem" if finalresult==checkresult else "Os resultados nao coincidem")

    else: #onde ocorre os calculos nos processos
        process = comm.recv(source=0, tag=totalprocess)
        result = None
        for x in process:
            if result is None:
                result = x
            else:
                result = multiply_matrix(result, x)
        time.sleep(1)
        comm.send(result, dest=0, tag=totalprocess)