# unit tests
import unittest
import core.quick as quick
import core
from core.adress_solver.adress_solver import calculate_label_segments, calculate_segment_lengths, mark_code_segments


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

    def get_state(self, CASE):
        if not hasattr(self, "profile"):
            self.profile = core.profile.profile.load_profile_from_file("wvrn.jsonc", False)

        return quick.parse(CASE, self.profile)

        
    def test_mark_code_segments(self):
        program, context = self.get_state(TestAdressSolver.TEST_CASE_0)

        program, context = mark_code_segments(program, context)
        segments  = [line["segment"] for line in program]        

        self.assertEqual(segments, [2, 1, 0])

        program, context = self.get_state(TestAdressSolver.TEST_CASE_1)
        program, context = mark_code_segments(program, context)
        
        segments  = [line["segment"] for line in program]

        self.assertEqual(segments, [3, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 0, 0, 0, 0, 0, 0, 0])

        program, context = self.get_state(TestAdressSolver.TEST_CASE_2)
        program, context = mark_code_segments(program, context)

        segments  = [line["segment"] for line in program]

        self.assertEqual(segments, [2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0])

        program, context = self.get_state(TestAdressSolver.TEST_CASE_3)
        program, context = mark_code_segments(program, context)

        segments  = [line["segment"] for line in program]

        self.assertEqual(segments, [3, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 1, 1, 0, 0, 0, 0, 0])

        program, context = self.get_state(TestAdressSolver.TEST_CASE_4)
        program, context = mark_code_segments(program, context)

        segments  = [line["segment"] for line in program]

        self.assertEqual(segments, [0, 0, 0, 0])

        program, context = self.get_state(TestAdressSolver.TEST_CASE_5)
        program, context = mark_code_segments(program, context)

        segments  = [line["segment"] for line in program]

        self.assertEqual(segments, [])

        program, context = self.get_state(TestAdressSolver.TEST_CASE_6)
        program, context = mark_code_segments(program, context)

        segments  = [line["segment"] for line in program]

        self.assertEqual(segments, [1, 1, 0, 0])

    def test_calculate_label_segments(self):
        program, context = self.get_state(TestAdressSolver.TEST_CASE_0)
        program, context = mark_code_segments(program, context)

        label_segments = calculate_label_segments(program, context)

        self.assertEqual(label_segments, {"LABEL": 1, "LABEL2": 0, "LABEL3": 0})

        program, context = self.get_state(TestAdressSolver.TEST_CASE_1)
        program, context = mark_code_segments(program, context)

        label_segments = calculate_label_segments(program, context)
        
        self.assertEqual(label_segments, {"LABEL": 2, "LABEL2": 0})

        program, context = self.get_state(TestAdressSolver.TEST_CASE_2)
        program, context = mark_code_segments(program, context)

        label_segments = calculate_label_segments(program, context)

        self.assertEqual(label_segments, {"LABEL": 1, "LABEL2": 0})

        program, context = self.get_state(TestAdressSolver.TEST_CASE_3)
        program, context = mark_code_segments(program, context)

        label_segments = calculate_label_segments(program, context)

        self.assertEqual(label_segments, {"LABEL": 2, "LABEL2": 0})

        program, context = self.get_state(TestAdressSolver.TEST_CASE_4)
        program, context = mark_code_segments(program, context)

        label_segments = calculate_label_segments(program, context)

        self.assertEqual(label_segments, {})

        program, context = self.get_state(TestAdressSolver.TEST_CASE_5)
        program, context = mark_code_segments(program, context)

        label_segments = calculate_label_segments(program, context)

        self.assertEqual(label_segments, {})

        program, context = self.get_state(TestAdressSolver.TEST_CASE_6)
        program, context = mark_code_segments(program, context)

        label_segments = calculate_label_segments(program, context)

        print(label_segments)

        self.assertEqual(label_segments, {"LABEL1": 0, "LABEL": 1})

    def test_calculate_segment_lengths(self):
        program, context = self.get_state(TestAdressSolver.TEST_CASE_0)
        program, context = mark_code_segments(program, context)

        segment_lengths = calculate_segment_lengths(program)

        self.assertEqual(segment_lengths, {2: 1, 1: 1, 0: 1})

        program, context = self.get_state(TestAdressSolver.TEST_CASE_1)
        program, context = mark_code_segments(program, context)

        segment_lengths = calculate_segment_lengths(program)
        
        self.assertEqual(segment_lengths, {3: 1, 2: 9, 1: 1, 0: 7})

        program, context = self.get_state(TestAdressSolver.TEST_CASE_2)
        program, context = mark_code_segments(program, context)

        segment_lengths = calculate_segment_lengths(program)

        self.assertEqual(segment_lengths, {2: 1, 1: 9, 0: 8})

        program, context = self.get_state(TestAdressSolver.TEST_CASE_3)
        program, context = mark_code_segments(program, context)

        segment_lengths = calculate_segment_lengths(program)

        self.assertEqual(segment_lengths, {3: 1, 2: 9, 1: 3, 0: 5})

        program, context = self.get_state(TestAdressSolver.TEST_CASE_4)
        program, context = mark_code_segments(program, context)

        segment_lengths = calculate_segment_lengths(program)

        self.assertEqual(segment_lengths, {0: 4})

        program, context = self.get_state(TestAdressSolver.TEST_CASE_5)
        program, context = mark_code_segments(program, context)

        segment_lengths = calculate_segment_lengths(program)

        self.assertEqual(segment_lengths, {0: 0})

        program, context = self.get_state(TestAdressSolver.TEST_CASE_6)
        program, context = mark_code_segments(program, context)

        segment_lengths = calculate_segment_lengths(program)

        self.assertEqual(segment_lengths, {1: 2, 0: 2})

if __name__ == '__main__':
    unittest.main()





