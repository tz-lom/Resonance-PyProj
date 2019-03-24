import unittest
import copy
import resonance
import resonance.run
import numpy as np


class TestProcessor(unittest.TestCase):
    def assertResults(self, result: dict, expected: dict, msg):
        self.assertEqual(result.keys(), expected.keys(), msg)
        for name in result.keys():
            if isinstance(expected[name], resonance.db.Channels):
                self.assertEqual(expected[name].SI, result[name].SI, msg)
                self.assertTrue(np.array_equal(expected[name].TS, result[name].TS), msg)
                self.assertTrue(np.allclose(expected[name], result[name], equal_nan=True), msg)
            else:
                self.assertEqual(expected[name], result[name], msg)

    def check_processor(self, si, blocks, expected, processor, *arguments):
        def code():
            inputs = [resonance.input(idx) for idx in range(0, len(si))]
            args = inputs + list(arguments)
            outputs = processor(*args)
            if isinstance(outputs, list):
                [resonance.createOutput(out, 'out_{}'.format(idx)) for idx, out in enumerate(outputs)]
            else:
                resonance.createOutput(outputs, 'out_0')

        if isinstance(expected, Exception):
            try:
                resonance.run.online(si, blocks, code)
            except expected as error:
                online_error = error
            except Exception as error:
                self.fail("Was expecting exception {} in run.online, but got {}".format(expected, error))
            else:
                self.fail("Was expecting exception {}, but got no exception".format(expected))

            try:
                resonance.run.online(si, blocks, code)
            except expected as error:
                self.assertEqual(error, online_error, "Exception from online ({}) is not the same as from offline ({})"
                                 .format(online_error, error))
            except Exception as error:
                self.fail("Was expecting exception {} in run.online, but got {}".format(expected, error))
            else:
                self.fail("Was expecting exception {}, but got no exception".format(expected))
        else:
            blocks_copy = copy.deepcopy(blocks)

            offline = resonance.run.offline(si, blocks_copy, code)
            self.assertListEqual(blocks, blocks_copy,
                                 "Processor should return new blocks, not modify the input ones")

            online = resonance.run.online(si, blocks_copy, code)
            self.assertListEqual(blocks, blocks_copy,
                                 "Processor should return new blocks, not modify the input ones")

            self.assertResults(expected, online, "Online did not match the expectations")
            self.assertResults(online, offline, "Offline not equals online")
