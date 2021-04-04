import unittest
import copy
import resonance
import resonance.run
import numpy as np


class TestProcessor(unittest.TestCase):
    def __assertBlockEquals(self, expected_block, result_block, msg, name):
        self.assertIsInstance(
            expected_block, resonance.db.Base,
            '{}: Type of expected {} should be inherited from resonance.db.Base'
                .format(msg, name))
        self.assertEqual(type(expected_block), type(result_block),
                         '{}: Different block type for {}'.format(msg, name))
        self.assertTrue(expected_block.SI.is_similar(result_block.SI),
                        '{}: Different types of {}'.format(msg, name))

        self.assertTrue(
            np.array_equal(expected_block.TS, result_block.TS),
            '{}: Different timestamps of {} : {} != {}'.format(
                msg, name, expected_block.TS, result_block.TS))
        self.assertTrue(
            expected_block.is_similar(result_block),
            '{}: Different data in {} : {} != {}'.format(
                msg, name, expected_block, result_block))

    def __assertResults(self, expected: dict, result: dict, msg,
                        channel_comparison):
        self.assertEqual(expected.keys(), result.keys(),
                         '{}: Different number of output channels'.format(msg))
        for name in result.keys():
            expected_channel = expected[name]
            result_channel = result[name]
            channel_comparison(expected_channel, result_channel, name)

    def __assertResultsOnline(self, expected: dict, results: dict, msg):
        def channel_comparison(expected_channel, result_channel, name):
            self.assertEqual(
                len(expected_channel), len(result_channel),
                '{}: Different number of blocks in channel {}'.format(
                    msg, name))
            for i in range(0, len(expected_channel)):
                expected_block = expected_channel[i]
                result_block = result_channel[i]
                block_name = 'block #{} channel {}'.format(i, name)
                self.__assertBlockEquals(expected_block, result_block, msg,
                                         block_name)

        self.__assertResults(expected, results, msg, channel_comparison)

    def __assertResultsOffline(self, expected: dict, results: dict, msg):
        def channel_comparison(expected_channel, result_channel, name):
            channel_name = 'channel {}'.format(name)
            self.__assertBlockEquals(expected_channel, result_channel, msg,
                                     channel_name)

        self.__assertResults(expected, results, msg, channel_comparison)

    def check_processor(self,
                        si,
                        blocks,
                        expected,
                        processor,
                        *arguments,
                        only_offline=False):
        def code():
            inputs = [resonance.input(idx) for idx in range(0, len(si))]
            args = inputs + list(arguments)
            outputs = processor(*args)
            if isinstance(outputs, tuple):
                for idx, out in enumerate(outputs):
                    resonance.createOutput(out, 'out_{}'.format(idx))
            else:
                resonance.createOutput(outputs, 'out_0')

        if isinstance(expected, Exception):
            try:
                resonance.run.offline(si, blocks, code)
            except expected as error:
                offline_error = error
            except Exception as error:
                self.fail(
                    "Was expecting exception {} in run.offline, but got {}".
                        format(expected, error))
            else:
                self.fail(
                    "Was expecting exception {} in run.offline, but got no exception"
                        .format(expected))

            if not only_offline:
                try:
                    resonance.run.online(si, blocks, code)
                except expected as error:
                    self.assertEqual(
                        error, offline_error,
                        "Exception from run.online ({}) is not the same as from run.offline ({})"
                            .format(offline_error, error))
                except Exception as error:
                    self.fail(
                        "Was expecting exception {} in run.online, but got {}".
                            format(expected, error))
                else:
                    self.fail(
                        "Was expecting exception {} in run.online, but got no exception"
                            .format(expected))
        else:
            blocks_copy = copy.deepcopy(blocks)

            offline = resonance.run.offline(si, blocks_copy, code)
            self.assertListEqual(
                blocks, blocks_copy,
                "Processor should return new blocks, not modify the input ones"
            )

            expected_merged = {
                name: resonance.db.combine(*values)
                for name, values in expected.items()
            }

            self.__assertResultsOffline(expected_merged, offline,
                                        "Offline did not match expectations")

            if not only_offline:
                online = resonance.run.online(si,
                                              blocks_copy,
                                              code,
                                              return_blocks=True)
                self.assertListEqual(
                    blocks, blocks_copy,
                    "Processor should return new blocks, not modify the input ones"
                )

                self.__assertResultsOnline(
                    expected, online, "Online did not match the expectations")

                online_merged = resonance.run.online(si, blocks_copy, code)

                self.__assertResultsOffline(
                    online_merged, offline, "Offline not equals online merged")
