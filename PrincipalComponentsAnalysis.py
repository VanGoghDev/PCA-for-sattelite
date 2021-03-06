from ISZ import *
from ISZInView import ISZInView
from Satellite import *
from DormanPrins_lab2 import TDP
from numpy import linalg


class PCA:
    def __init__(self, result, obj):

        """
        :param result: выборка элементов. В данном случае, result модели в интервале времени когда ИСЗ был замечен НИПом
        """
        self.dormanPrins = TDP()  # интегратор
        self.dormanPrins.geps = 1e-8

        self.deltaXYZ = 100  # разброс для координат
        self.deltaV = 1  # разброс для скоростей
        self.count = result.shape[0]
        self.n = result.shape[1] - 1

        self.result = result[0]
        self.X1 = np.zeros((0, 0))

        for i in range(3):
            self.result[i + 1] += self.deltaXYZ
            self.result[i + 4] += self.deltaV

        self.resultForIsz = np.zeros(6)
        for i in range(6):
            self.resultForIsz[i] = self.result[i + 1]

        self.Sputnik = Satellite()
        # self.modelPlus = ISZ(0, self.count, 1, self.n, self.resultChangePlus[0], self.Sputnik)
        # self.modelMinus = ISZ(0, self.count, 1, self.n, self.resultChangeMinus[0], self.Sputnik)
        self.ISZ = ISZ(0, self.count, 1, self.n, self.resultForIsz, self.Sputnik)
        self.modelPlus = ISZ(0, self.count, 1, self.n, self.resultForIsz, self.Sputnik)
        self.modelMinus = ISZ(0, self.count, 1, self.n, self.resultForIsz, self.Sputnik)

        self.Hm = np.zeros((self.count + self.count, self.n))
        self.D = np.zeros((self.count + self.count, self.count + self.count))
        self.iscElAz = np.zeros((self.count, 1))  # матрица искаженных значений элевации и азимута
        # self.countD()  # считаем матрицу D

    def countD(self):
        disp = 3.3
        for i in range(self.D.shape[0]):
            for j in range(self.D.shape[1]):
                if i != j:
                    self.D[i][j] = 0
                else:
                    self.D[i][j] = disp

    def countH(self):
        true = True
        self.X1 = self.resultForIsz
        while true:
            self.ISZ = ISZInView(0, self.count, 1, self.n, self.X1, self.Sputnik)  # опорная траектория
            self.dormanPrins.run(self.ISZ)  # интегрирование опорной траектории
            resultChangePlus = np.zeros((6, self.n))
            resultChangeMinus = np.zeros((6, self.n))

            for j in range(6):
                for k in range(6):
                    # self.resultChangePlus[j][k] = self.result[k + 1]
                    # self.resultChangeMinus[j][k] = self.result[k + 1]
                    resultChangePlus[j][k] = self.X1[k]
                    resultChangeMinus[j][k] = self.X1[k]

            for k in range(3):
                resultChangePlus[k][k] += self.deltaXYZ
                resultChangePlus[k + 3][k + 3] += self.deltaV
                resultChangeMinus[k][k] -= self.deltaXYZ
                resultChangeMinus[k + 3][k + 3] -= self.deltaV

            self.modelPlus = ISZInView(0, self.count, 1, self.n, resultChangePlus[0], self.Sputnik)
            self.modelMinus = ISZInView(0, self.count, 1, self.n, resultChangeMinus[0], self.Sputnik)

            self.count = self.ISZ.count
            self.Hm = np.zeros((self.count + self.count, self.n))
            self.D = np.zeros((self.count + self.count, self.count + self.count))
            self.iscElAz = np.zeros((self.count, 1))

            self.countD()  # считаем матрицу D

            column = 0
            while column < self.n:  # до нужного количства диф. уравнений (или столбцов)
                self.modelPlus = ISZ(0, self.count, 1, self.n, resultChangePlus[column], self.Sputnik)
                self.modelMinus = ISZ(0, self.count, 1, self.n, resultChangeMinus[column], self.Sputnik)
                self.dormanPrins.run(self.modelPlus)
                self.dormanPrins.run(self.modelMinus)
                rs = np.zeros((self.ISZ.count, 3))
                for j in range(self.modelPlus.count):
                    for i in range(3):
                        rs[j][i] = self.modelPlus.result[j][i+1]
                rn = self.ISZ.rn
                d = self.ISZ.d
                dt = self.ISZ.dt

                for row in range(self.count):  # количество измерений

                    dxtecdx = np.zeros(self.n)
                    dfidxtec = np.zeros(self.n)
                    dfidxtec1 = np.zeros(self.n)
                    dfidxtec2 = np.zeros(self.n)

                    mod_d = math.sqrt(pow(d[row][0], 2) + pow(d[row][1], 2) + pow(d[row][2], 2))
                    mod_rn = math.sqrt(pow(rn[row][0], 2) + pow(rn[row][1], 2) + pow(rn[row][2], 2))
                    mod_dt = math.sqrt(pow(dt[row][0], 2) + pow(dt[row][1], 2) + pow(dt[row][2], 2))

                    for i in range(3):
                        dxtecdx[i] = (self.modelPlus.result[row][i+1] - self.modelMinus.result[row][i+1]) /\
                                     (2 * self.deltaXYZ)
                        dxtecdx[i+3] = (self.modelPlus.result[row][i+4] - self.modelMinus.result[row][i+4]) /\
                                       (2 * self.deltaV)

                        # dfidxtec[i] = self.ISZ.d[row][i]
                        temp = (d[row][0]*rn[row][0]+d[row][1]*rn[row][1]+d[row][2]*rn[row][2])
                        dfidxtec1[i] = -(rs[row][i]/(mod_d*mod_rn)-0.5*((temp * (2*rs[row][1]-2*rn[row][1]))/(pow(mod_d, 3)*mod_rn)))/\
                                       (math.sqrt(-pow(temp, 2)/(pow(mod_d, 2)*mod_rn)+1))
                        # dfidxtec2[i] =
                        # dfidxtec1[i] = 1  # self.ISZ.ElevationAzimut[row*2]
                        if i == 0:
                            dfidxtec2[i] = -(1/mod_dt-0.5*((dt[row][0]*2*(dt[row][0]))/(pow(mod_dt, 3))))/(math.sqrt(-pow(dt[row][0],2)/pow(mod_dt, 2)+1))
                        else:
                            dfidxtec2[i] = 1/2 * (dt[row][0]*2*dt[row][i])/(pow(mod_dt, 3)*math.sqrt((-pow(dt[row][0], 2))/pow(mod_dt, 2)+1))
                        # dfidxtec2[i] = 1  # self.ISZ.ElevationAzimut[row*2+1]

                    self.Hm[row*2][column] = dxtecdx[0] * dfidxtec1[0] + dxtecdx[1] * dfidxtec1[1] + dxtecdx[2] * dfidxtec1[2]
                    self.Hm[row*2+1][column] = dxtecdx[0] * dfidxtec2[0] + dxtecdx[1] * dfidxtec2[1] + dxtecdx[2] * dfidxtec2[2]
                column += 1
            self.countK(0)

    # поиск корреляционной матрицы ошибок оценивания
    def countK(self, k):
        D_1 = linalg.inv(self.D)  # обратная матрица D
        Ht = self.Hm.transpose()  # транспонированная матрица H
        HD_1 = np.dot(Ht, D_1)  # произведение H трансп на обратную матрицу D
        K = np.dot(HD_1, self.Hm)
        K = linalg.inv(K)  # находим матрицу K
        KHt = np.dot(K, Ht)
        KHtD_1 = np.dot(KHt, D_1)
        dif = np.zeros((self.ISZ.iscElAz.shape[0], 1))
        for i in range(self.ISZ.iscElAz.shape[0]):
            dif[i] = self.ISZ.iscElAz[i] - self.ISZ.ElevationAzimut[i]
        deltaX = np.dot(KHtD_1, dif)
        X1 = np.zeros(self.n)
        for i in range(self.n):
            X1[i] = self.ISZ.result[k][i+1] + deltaX[i]
        self.X1 = X1
        a = 3
