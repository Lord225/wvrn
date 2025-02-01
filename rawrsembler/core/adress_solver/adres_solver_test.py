# unit tests
import unittest
import core.quick as quick
import core
from core.adress_solver.adress_solver import calculate_label_segments, calculate_segment_lengths, mark_code_segments

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

TEST_CASE_7 = [
    ".ENTRY",
    "nop",
    "LABEL:",
    "nop",
    "nop",
    "nop",
    "jmp LABEL",
    "nop",
]

TEST_CASE_8 = [
    ".ENTRY",
    "nop",
    "LABEL:",
    "nop",
    "jmp LABEL",
    "jmp LABEL",
]

class TestMarkCodeSegments(unittest.TestCase):
    def get_state(self, CASE):
        if not hasattr(self, "profile"):
            self.profile = core.profile.profile.load_profile_from_file("wvrn.jsonc", False)

        return quick.parse(CASE, self.profile)

    def test_mark_code_segments_case_0(self):
        program, context = self.get_state(TEST_CASE_0)
        program, context = mark_code_segments(program, context)
        segments = [line["segment"] for line in program]
        self.assertEqual(segments, [3, 2, 1])

    def test_mark_code_segments_case_1(self):
        program, context = self.get_state(TEST_CASE_1)
        program, context = mark_code_segments(program, context)
        segments = [line["segment"] for line in program]
        self.assertEqual(segments, [3, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 0, 0, 0, 0, 0, 0, 0])

    def test_mark_code_segments_case_2(self):
        program, context = self.get_state(TEST_CASE_2)
        program, context = mark_code_segments(program, context)
        segments = [line["segment"] for line in program]
        self.assertEqual(segments, [2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0])

    def test_mark_code_segments_case_3(self):
        program, context = self.get_state(TEST_CASE_3)
        program, context = mark_code_segments(program, context)
        segments = [line["segment"] for line in program]
        self.assertEqual(segments, [3, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 1, 1, 0, 0, 0, 0, 0])

    def test_mark_code_segments_case_4(self):
        program, context = self.get_state(TEST_CASE_4)
        program, context = mark_code_segments(program, context)
        segments = [line["segment"] for line in program]
        self.assertEqual(segments, [0, 0, 0, 0])

    def test_mark_code_segments_case_5(self):
        program, context = self.get_state(TEST_CASE_5)
        program, context = mark_code_segments(program, context)
        segments = [line["segment"] for line in program]
        self.assertEqual(segments, [])

    def test_mark_code_segments_case_6(self):
        program, context = self.get_state(TEST_CASE_6)
        program, context = mark_code_segments(program, context)
        segments = [line["segment"] for line in program]
        self.assertEqual(segments, [1, 1, 0, 0])

    def test_mark_code_segments_case_7(self):
        program, context = self.get_state(TEST_CASE_7)
        program, context = mark_code_segments(program, context)
        segments = [line["segment"] for line in program]
        self.assertEqual(segments, [2, 1, 1, 1, 1, 0])

    def test_mark_code_segments_case_8(self):
        program, context = self.get_state(TEST_CASE_8)
        program, context = mark_code_segments(program, context)
        segments = [line["segment"] for line in program]
        self.assertEqual(segments, [3, 2, 2, 1])

class TestCalculateLabelSegments(unittest.TestCase):
    def get_state(self, CASE):
        if not hasattr(self, "profile"):
            self.profile = core.profile.profile.load_profile_from_file("wvrn.jsonc", False)

        return quick.parse(CASE, self.profile)

    def test_calculate_label_segments_case_0(self):
        program, context = self.get_state(TEST_CASE_0)
        program, context = mark_code_segments(program, context)
        label_segments = calculate_label_segments(program, context)
        self.assertEqual(label_segments, {"LABEL": 2, "LABEL2": 1, "LABEL3": 1})

    def test_calculate_label_segments_case_1(self):
        program, context = self.get_state(TEST_CASE_1)
        program, context = mark_code_segments(program, context)
        label_segments = calculate_label_segments(program, context)
        self.assertEqual(label_segments, {"LABEL": 2, "LABEL2": 1})

    def test_calculate_label_segments_case_2(self):
        program, context = self.get_state(TEST_CASE_2)
        program, context = mark_code_segments(program, context)
        label_segments = calculate_label_segments(program, context)
        self.assertEqual(label_segments, {"LABEL": 3, "LABEL2": 2})

    def test_calculate_label_segments_case_3(self):
        program, context = self.get_state(TEST_CASE_3)
        program, context = mark_code_segments(program, context)
        label_segments = calculate_label_segments(program, context)
        self.assertEqual(label_segments, {"LABEL": 3, "LABEL2": 1})

    def test_calculate_label_segments_case_4(self):
        program, context = self.get_state(TEST_CASE_4)
        program, context = mark_code_segments(program, context)
        label_segments = calculate_label_segments(program, context)
        self.assertEqual(label_segments, {})

    def test_calculate_label_segments_case_5(self):
        program, context = self.get_state(TEST_CASE_5)
        program, context = mark_code_segments(program, context)
        label_segments = calculate_label_segments(program, context)
        self.assertEqual(label_segments, {})

    def test_calculate_label_segments_case_6(self):
        program, context = self.get_state(TEST_CASE_6)
        program, context = mark_code_segments(program, context)
        label_segments = calculate_label_segments(program, context)
        self.assertEqual(label_segments, {'LABEL': 2, 'LABEL1': 1})

    def test_calculate_segment_lengths_case_0(self):
        program, context = self.get_state(TEST_CASE_0)
        program, context = mark_code_segments(program, context)
        segment_lengths = calculate_segment_lengths(program)
        self.assertEqual(segment_lengths, {2: 1, 1: 1, 0: 1})

    def test_calculate_segment_lengths_case_1(self):
        program, context = self.get_state(TEST_CASE_1)
        program, context = mark_code_segments(program, context)
        segment_lengths = calculate_segment_lengths(program)
        self.assertEqual(segment_lengths, {3: 1, 2: 9, 1: 1, 0: 7})

    def test_calculate_segment_lengths_case_2(self):
        program, context = self.get_state(TEST_CASE_2)
        program, context = mark_code_segments(program, context)
        segment_lengths = calculate_segment_lengths(program)
        self.assertEqual(segment_lengths, {2: 1, 1: 9, 0: 8})

    def test_calculate_segment_lengths_case_3(self):
        program, context = self.get_state(TEST_CASE_3)
        program, context = mark_code_segments(program, context)
        segment_lengths = calculate_segment_lengths(program)
        self.assertEqual(segment_lengths, {3: 1, 2: 9, 1: 3, 0: 5})

    def test_calculate_segment_lengths_case_4(self):
        program, context = self.get_state(TEST_CASE_4)
        program, context = mark_code_segments(program, context)
        segment_lengths = calculate_segment_lengths(program)
        self.assertEqual(segment_lengths, {0: 4})

    def test_calculate_segment_lengths_case_5(self):
        program, context = self.get_state(TEST_CASE_5)
        program, context = mark_code_segments(program, context)
        segment_lengths = calculate_segment_lengths(program)
        self.assertEqual(segment_lengths, {0: 0})

    def test_calculate_segment_lengths_case_6(self):
        program, context = self.get_state(TEST_CASE_6)
        program, context = mark_code_segments(program, context)
        segment_lengths = calculate_segment_lengths(program)
        self.assertEqual(segment_lengths, {1: 2, 0: 2})

    def test_calculate_segment_lengths_case_7(self):
        program, context = self.get_state(TEST_CASE_7)
        program, context = mark_code_segments(program, context)
        segment_lengths = calculate_segment_lengths(program)
        self.assertEqual(segment_lengths, {2: 1, 1: 4, 0: 0})

if __name__ == '__main__':
    unittest.main()
