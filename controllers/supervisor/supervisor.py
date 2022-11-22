"""Supervisor of the Maze Runner benchmark."""

from controller import Supervisor
import os


def isPositionChanged(v1, v2):
    return abs(v1[1] - v2[1]) > 0.001 or abs(v1[0] - v2[0]) > 0.001


def isMazeEndReached(position):
    return position[0] < 0.15 and position[0] > -0.15 and position[1] > -0.60 and position[1] < -0.45


robot = Supervisor()
timestep = int(4 * robot.getBasicTimeStep())
robot.step(10 * timestep)

thymio2 = robot.getFromDef("THYMIO2")

robot.step(10 * timestep)

mazeBlocksList = []
mazeBlocksListCount = 0
topChildrenField = robot.getFromDef("MAZE_WALLS").getField("children")
topNodesCount = topChildrenField.getCount()
for i in range(topNodesCount):
    node = topChildrenField.getMFNode(i)
    if node.getTypeName() == "MazeBlock":
        object = {
            "node": node,
            "initialPosition": node.getPosition()
        }
        mazeBlocksList.append(object)
        mazeBlocksListCount += 1


running = True
stopMessageSent = False
while running and robot.step(timestep) != -1:
    time = robot.getTime()
    # If some of the maze blocks have been moved immediately terminate the benchmark
    for i in range(0, mazeBlocksListCount):
        item = mazeBlocksList[i]
        if isPositionChanged(item['initialPosition'], item['node'].getPosition()):
            time = 60
            robot.wwiSendText("time:%-24.3f" % time)
            break

    if time < 60 and not isMazeEndReached(thymio2.getPosition()):
        robot.wwiSendText("time:%-24.3f" % time)
    else:
        running = False
        timestep = int(timestep / 4)

robot.wwiSendText("stop_%-24.3f" % time)

# Performance output used by automated CI script
CI = os.environ.get("CI")
if CI:
    print(f"performance:{time}")

robot.simulationSetMode(Supervisor.SIMULATION_MODE_PAUSE)
