# unit tests
import unittest
import core.quick as quick
import core
from core.adress_solver.adress_solver import calculate_label_segments, mark_code_segments


class TestAdressSolver(unittest.TestCase):

    TEST_CASE_0 = [
        ".ENTRY",
        "nop",
        "LABEL:",
        "nop",
        "LABEL2:",
        "LABEL3:",
        "nop",
    ]
    TEST_CASE_1 = [
        ".ENTRY",
        "nop",
        "LABEL:",
        "nop",
        "nop",
        "nop",
        "nop",
        "nop",
        "nop",
        "nop",
        "nop",
        "nop",
        "brc true LABEL",
        "LABEL2:",
        "nop",
        "nop",
        "nop",
        "nop",
        "nop",
        "nop",
        "nop",
    ]
    TEST_CASE_2 = [
        ".ENTRY",
        "nop",
        "LABEL:",
        "nop",
        "nop",
        "nop",
        "nop",
        "nop",
        "nop",
        "nop",
        "nop",
        "nop",
        "LABEL2:",
        "brc true LABEL",
        "nop",
        "nop",
        "nop",
        "nop",
        "nop",
        "nop",
        "nop",
    ]
    TEST_CASE_3 = [
        ".ENTRY",
        "nop",
        "LABEL:",
        "nop",
        "nop",
        "nop",
        "nop",
        "nop",
        "nop",
        "nop",
        "nop",
        "nop",
        "brc true LABEL",
        "nop",
        "nop",
        "LABEL2:",
        "nop",
        "nop",
        "nop",
        "nop",
        "nop",
    ]
    TEST_CASE_4 = [
        ".ENTRY",
        "nop",
        "nop",
        "nop",
        "nop",
    ]

    TEST_CASE_5 = [
        ".ENTRY",
    ]

    TEST_CASE_6 = [
        ".ENTRY",
        "nop",
        "nop",
        "LABEL1:",
        "nop",
        "nop",
        "LABEL:",
    ]

    def test_mark_code_segments(self):
        profile = core.profile.profile.load_profile_from_file("wvrn.jsonc", False)
        program, context = quick.parse(TestAdressSolver.TEST_CASE_0, profile)

        program, context = mark_code_segments(program, context)
        segments  = [line["segment"] for line in program]        

        self.assertEqual(segments, [2, 1, 0])

        program, context = quick.parse(TestAdressSolver.TEST_CASE_1, profile)
        program, context = mark_code_segments(program, context)
        segments  = [line["segment"] for line in program]

        self.assertEqual(segments, [3, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 0, 0, 0, 0, 0, 0, 0])

        program, context = quick.parse(TestAdressSolver.TEST_CASE_2, profile)
        program, context = mark_code_segments(program, context)

        segments  = [line["segment"] for line in program]

        self.assertEqual(segments, [2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0])

        program, context = quick.parse(TestAdressSolver.TEST_CASE_3, profile)
        program, context = mark_code_segments(program, context)

        segments  = [line["segment"] for line in program]

        self.assertEqual(segments, [3, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 1, 1, 0, 0, 0, 0, 0])

        program, context = quick.parse(TestAdressSolver.TEST_CASE_4, profile)
        program, context = mark_code_segments(program, context)

        segments  = [line["segment"] for line in program]

        self.assertEqual(segments, [0, 0, 0, 0])


        program, context = quick.parse(TestAdressSolver.TEST_CASE_5, profile)
        program, context = mark_code_segments(program, context)

        segments  = [line["segment"] for line in program]

        self.assertEqual(segments, [])

        program, context = quick.parse(TestAdressSolver.TEST_CASE_6, profile)
        program, context = mark_code_segments(program, context)

        segments  = [line["segment"] for line in program]

        self.assertEqual(segments, [1, 1, 0, 0])

    def test_calculate_label_segments(self):
        profile = core.profile.profile.load_profile_from_file("wvrn.jsonc", False)

        program, context = quick.parse(TestAdressSolver.TEST_CASE_0, profile)
        program, context = mark_code_segments(program, context)

        label_segments = calculate_label_segments(program, context)

        self.assertEqual(label_segments, {"LABEL": 1, "LABEL2": 0, "LABEL3": 0})



