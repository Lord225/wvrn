# unit tests
import unittest

from rawrsembler.core.adress_solver.adress_solver import mark_code_segments


class TestAdressSolver(unittest.TestCase):
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
        "LABEL:",
        "LABEL2:",
        "nop",
        "brc true LABEL",
        "nop",
        "nop",
    ]

    def test_mark_code_segments(self):
        import core.quick as quick
        import core

        profile = core.profile.profile.load_profile_from_file("wvrn.jsonc", False)
        program, context = quick.parse(TestAdressSolver.TEST_CASE_1, profile)

        program, context = mark_code_segments(program, context)

        print(program)