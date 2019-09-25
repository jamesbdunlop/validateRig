import unittest
import logging
from core import parser as c_parser
logger = logging.getLogger(__name__)


class Test_Parser(unittest.TestCase):

    def setUp(self):
        self.filepath = "C:/Temp/testRead.json"
        self.outfilepath = "C:/Temp/testOut.json"
        self.testData = {"test": "testVar"}
        self.testOutData = {"testOut": "testVarOut"}

    def tearDown(self):
        pass

    def test_readFile(self):
        data = c_parser.read(self.filepath)
        self.assertEqual(data, self.testData, "read data is not the same!!!")

    def test_writeFile(self):
        c_parser.write(self.outfilepath, self.testOutData)
        self.assertEqual(c_parser.read(self.outfilepath), self.testOutData, "out data is not the same!")


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(unittest.TestSuite())
