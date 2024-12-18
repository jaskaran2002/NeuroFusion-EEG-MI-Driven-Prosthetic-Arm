import pybullet as p
import pybullet_data
from time import sleep
import time

physicsClient = p.connect(p.GUI)
p.setAdditionalSearchPath(pybullet_data.getDataPath())
p.setGravity(0,0,0)

startPos = [0,0,0]
startOrientation = p.getQuaternionFromEuler([0,0,0])
print('*****************************************')
simulationId = p.loadURDF("level-1/2f1t.urdf", startPos, startOrientation)
print('*****************************************')
# for i in range (10000):
#     # maxForce = 0
#     # mode = p.VELOCITY_CONTROL
#     # p.setJointMotorControl2(simulationId, 1, controlMode=mode, force=maxForce)
#     p.stepSimulation()
#     time.sleep(1./240.)
# cubePos, cubeOrn = p.getBasePositionAndOrientation(simulationId)
# print(cubePos,cubeOrn)

# number_of_joints = p.getNumJoints(simulationId)
# for joint_number in range(number_of_joints):
#     info = p.getJointInfo(simulationId, joint_number)
#     print(info[0], ": ", info[1])

Grab = p.addUserDebugParameter('Grab', 0, 30.0, 0)
Elbow = p.addUserDebugParameter('Elbow', 0, 3, 0)
Wrist = p.addUserDebugParameter('Wrist', 0, 9, 0)
grab_indices = [2,3,4]
elbow_indices = [0]
wrist_indices = [1]
while True:
    user_grab = p.readUserDebugParameter(Grab)
    user_elbow = p.readUserDebugParameter(Elbow)
    user_wrist = p.readUserDebugParameter(Wrist)
    for joint_index in grab_indices:
        p.setJointMotorControl2(simulationId, joint_index,
                                p.POSITION_CONTROL,
                                targetVelocity=user_grab)
    for joint_index in elbow_indices:
        p.setJointMotorControl2(simulationId, joint_index,
                                p.POSITION_CONTROL, 
                                targetPosition=user_elbow)
    for joint_index in wrist_indices:
        p.setJointMotorControl2(simulationId, joint_index,
                                p.POSITION_CONTROL, 
                                targetPosition=user_wrist,
                                force = 0.001)
    p.stepSimulation()

# # p.disconnect()
