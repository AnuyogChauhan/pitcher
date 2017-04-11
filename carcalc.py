def calcSpeed(mouseInput):
    analogInput = int(mouseInput * 255 / 1000)

    # polynomial constants
    A = -0.0092
    B = 4.272
    C = -212.8

    # second order polynomial representing the speed (kph)
    return str(min(max(int(A * pow(analogInput, 2) + B * analogInput + B),0),325))

def calcDist(mouseInput):
    analogInput = int(mouseInput * 255 / 1000)

    # polynomial constants
    A = -0.00001
    B = .0056 
    C = -.4468
    
    CAR_SCALE = 32

    # second order polynomial representing the minimum distance (meters)
    return str(max(int(CAR_SCALE * float(A * pow(analogInput, 2) + B * analogInput + C)),2))

def calcActualSpeed(mouseInput):
    analogInput = int(mouseInput * 255 / 1000)
    A = -.00008
    B = .0419 
    C = -3.0315

    # second order polynomial representing the actual slot car speed (m/s)
    return max(round(float(A * pow(analogInput, 2) + B * analogInput + C),2),0)

# test 
# f = 0
# for i in range(0,100):
#     f += 10
    # print(calcDist(f), 'm')
    # print(calcSpeed(f),'kph')
    # print(calcActualSpeed(f), 'm/s')
