import unittest
from PySide2 import QtWidgets, QtGui
from app import ValidationUI


class Test_QApplication(unittest.TestCase):
    def setUp(self):
        super(Test_QApplication, self).setUp()
        if isinstance(QtGui.QGuiApplication, type(None)):
            self.app = QtWidgets.QApplication([])
        else:
            self.app = QtWidgets.QApplication().instance()

        self.mainWindow = ValidationUI()

    def tearDown(self):
        del self.app
        return super(Test_QApplication, self).tearDown()

    def test_QApplicationInstance(self):
        self.assertIsInstance(self.app, QtWidgets.QApplication)



if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    runner.run(unittest.TestSuite())
