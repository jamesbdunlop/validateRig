#  Copyright (c) 2019.  James Dunlop

import unittest
import logging
from core import parser as c_parser

logger = logging.getLogger(__name__)


class Test_Parser(unittest.TestCase):
    def setUp(self):
        self.filepath = "C:/Temp/testOut.json"
        self.testOutData = {"testOut": "testVarOut"}

    def tearDown(self):
        pass

    def test_readwriteFile(self):
        self.assertTrue(c_parser.write(self.filepath, self.testOutData))
        self.assertEqual(
            c_parser.read(self.filepath), self.testOutData, "out data is not the same!"
        )


if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    runner.run(unittest.TestSuite())
