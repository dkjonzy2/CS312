from which_pyqt import PYQT_VER

if PYQT_VER == 'PYQT5':
    from PyQt5.QtCore import QLineF, QPointF, QObject
elif PYQT_VER == 'PYQT6':
    from PyQt6.QtCore import QLineF, QPointF, QObject
else:
    raise Exception('Unsupported Version of PyQt: {}'.format(PYQT_VER))

import time

# Some global color constants that might be useful
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Global variable that controls the speed of the recursion automation, in seconds
#
PAUSE = 0.25


#
# This is the class you have to complete.
#
class ConvexHullSolver(QObject):

    # Class constructor
    def __init__(self):
        super().__init__()
        self.pause = False

    # Some helper methods that make calls to the GUI, allowing us to send updates
    # to be displayed.

    def showTangent(self, line, color):
        self.view.addLines(line, color)
        if self.pause:
            time.sleep(PAUSE)

    def eraseTangent(self, line):
        self.view.clearLines(line)

    def blinkTangent(self, line, color):
        self.showTangent(line, color)
        self.eraseTangent(line)

    def showHull(self, polygon, color):
        self.view.addLines(polygon, color)
        if self.pause:
            time.sleep(PAUSE)

    def eraseHull(self, polygon):
        self.view.clearLines(polygon)

    def showText(self, text):
        self.view.displayStatusText(text)

    # This is the method that gets called by the GUI and actually executes
    # the finding of the hull
    def compute_hull(self, points, pause, view):
        self.pause = pause
        self.view = view
        assert (type(points) == list and type(points[0]) == QPointF)

        t1 = time.time()
        # Sort points by x value
        points.sort(key=lambda x: x.x())
        t2 = time.time()

        t3 = time.time()
        polygon = self.convex_hullDC(points)
        t4 = time.time()

        # when passing lines to the display, pass a list of QLineF objects.  Each QLineF
        # object can be created with two QPointF objects corresponding to the endpoints
        self.showHull(polygon, RED)
        self.showText('Time Elapsed (Convex Hull): {:3.3f} sec. (Sorting): {:3.3f} sec'.format(t4 - t3, t2 - t1))

    def convex_hullDC(self, points):
        if len(points) <= 3:
            polygon = [QLineF(points[i], points[(i + 1) % len(points)]) for i in range(len(points))]
            polygon.sort(key=lambda x: self.getLineSlope(x))  # might not be working as order of points is not fixed?
            return polygon
        mid = len(points) // 2
        leftHull = self.convex_hullDC(points[:mid])
        rightHull = self.convex_hullDC(points[mid:])

        # Merge left and right
        # Get starting points and indices
        leftPoint, leftIndex = self.rightMostPoint(leftHull)
        rightPoint, rightIndex = self.leftMostPoint(rightHull)

        topLeftIndex = leftIndex
        bottomLeftIndex = leftIndex
        topRightIndex = rightIndex
        bottomRightIndex = rightIndex

        # Create and show connecting line
        topConnLine = QLineF(leftPoint, rightPoint)
        # self.showHull(leftHull.copy(), RED) # this was changing length of leftHull....
        # self.showHull(rightHull.copy(), RED)
        # self.showTangent([topConnLine], BLUE)

        moving = True
        while moving:
            moving = False
            # self.eraseTangent([topConnLine])
            nextRight = rightHull[(topRightIndex + 1) % len(rightHull)].pointAt(0)
            nextLine = QLineF(topConnLine.pointAt(0), nextRight)
            if self.getLineSlope(nextLine) > self.getLineSlope(topConnLine):
                moving = True
                topRightIndex += 1
                topConnLine = nextLine
            # self.showTangent([topConnLine], BLUE)

            # self.eraseTangent([topConnLine])
            nextLeft = leftHull[(topLeftIndex - 1) % len(leftHull)].pointAt(0)
            nextLine = QLineF(nextLeft, topConnLine.pointAt(1))
            if self.getLineSlope(nextLine) < self.getLineSlope(topConnLine):
                moving = True
                topLeftIndex -= 1
                topConnLine = nextLine
        # self.showTangent([topConnLine], BLUE)

        bottomConnLine = QLineF(leftPoint, rightPoint)
        moving = True
        while moving:
            moving = False
            # self.eraseTangent([bottomConnLine])
            nextRight = rightHull[(bottomRightIndex - 1) % len(rightHull)].pointAt(0)
            nextLine = QLineF(bottomConnLine.pointAt(0), nextRight)
            if self.getLineSlope(nextLine) < self.getLineSlope(bottomConnLine):
                moving = True
                bottomRightIndex -= 1
                bottomConnLine = nextLine
            # self.showTangent([bottomConnLine], BLUE)

            # self.eraseTangent([bottomConnLine])
            nextLeft = leftHull[(bottomLeftIndex + 1) % len(leftHull)].pointAt(0)
            nextLine = QLineF(nextLeft, bottomConnLine.pointAt(1))
            if self.getLineSlope(nextLine) > self.getLineSlope(bottomConnLine):
                moving = True
                bottomLeftIndex += 1
                bottomConnLine = nextLine
        # self.showTangent([bottomConnLine], BLUE)

        # Construct new hull
        newHullPoints = [topConnLine.pointAt(0)]
        nextPoint = topConnLine.pointAt(1)
        while nextPoint != bottomConnLine.pointAt(1):
            newHullPoints.append(nextPoint)
            nextPoint = rightHull[(topRightIndex + 1) % len(rightHull)].pointAt(0)
            topRightIndex += 1
        newHullPoints.append(bottomConnLine.pointAt(1))
        nextPoint = bottomConnLine.pointAt(0)
        while nextPoint != topConnLine.pointAt(0):
            newHullPoints.append(nextPoint)
            nextPoint = leftHull[(bottomLeftIndex + 1) % len(leftHull)].pointAt(0)
            bottomLeftIndex += 1
        newHull = [QLineF(newHullPoints[i], newHullPoints[(i + 1) % len(newHullPoints)]) for i in range(len(newHullPoints))]
        # self.showHull(newHull.copy(), RED)
        return newHull

    def getLineSlope(self, line):
        if line.dx() == 0:
            return 0
        return line.dy()/line.dx()

    def rightMostPoint(self, hull):
        rightPoint = hull[0].pointAt(0)
        hullIndex = 0
        for i in range(len(hull)):
            if hull[i].x1() > rightPoint.x():
                rightPoint = hull[i].pointAt(0)
                hullIndex = i
        return rightPoint, hullIndex

    def leftMostPoint(self, hull):
        leftPoint = hull[0].pointAt(0)
        hullIndex = 0
        for i in range(len(hull)):
            if hull[i].x1() < leftPoint.x():
                leftPoint = hull[i].pointAt(0)
                hullIndex = i
        return leftPoint, hullIndex