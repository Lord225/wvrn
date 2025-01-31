from calendar import c
import unittest
from core.profile.profile import AdressingMode
import core.quick as quick
import core.adress_solver
import core
from . import config
from core.context import Context


def compilation_pipeline(CODE):
    load_preproces_pipeline = core.pipeline.make_preproces_string_load_pipeline() # Load & Preprocess
    parse_pipeline = core.pipeline.make_parser_pipeline()             # Parse & Extract arguments
    format_pipeline = core.pipeline.make_format_pipeline()            # Format

    profile = core.profile.profile.load_profile_from_file('wvrn.jsonc', True)

    output, context = core.pipeline.exec_pipeline(load_preproces_pipeline, CODE, Context(profile), progress_bar_name='Loading')
    # set profile_name
    context.profile_name = 'wvrn.jsonc'

    config.override_from_dict(
        {
            'profile': 'wvrn.jsonc',
            'save': 'bin',
        }
    )

    output, context = core.pipeline.exec_pipeline(parse_pipeline, output, context, progress_bar_name='Parsing')

    solve_wvrn = \
    [
        ('solve adresses', core.adress_solver.adress_solver.solve_adresses),
    ]


    output, context = core.pipeline.exec_pipeline(solve_wvrn, output, context, progress_bar_name='Solving adresses')

    output, context = core.pipeline.exec_pipeline(parse_pipeline, output, context, progress_bar_name='Parsing')
 
    output, context = core.pipeline.exec_pipeline(format_pipeline, output, context, progress_bar_name='Formatting')

    return output, context


class TestIntegrationTestWvrn(unittest.TestCase):
    def collect_bytes(self, output):
        bytes = []
        for line in output:
            bytes.extend(line['formatted'])
        return bytes
    def collect_mached_command(self, output):
        commands = []
        for line in output:
            commands.append(line['mached_command'])
        return commands 
    def test_integration_wvrn_CASE_0(self):
        TEST_CASE_0 = """
            .ENTRY
            nop
        """
        output, context = compilation_pipeline(TEST_CASE_0)
        
        bytes = self.collect_bytes(output)

        self.assertEqual(bytes, ['00000000'])

        commands = self.collect_mached_command(output)

        self.assertEqual(commands, [
            ('sta', {'arg': 0})
        ])

    def test_integration_wvrn_CASE_1(self):
        TEST_CASE_1 = """
            .ENTRY
            lim 0
        """
        output, context = compilation_pipeline(TEST_CASE_1)
        
        bytes = self.collect_bytes(output)

        self.assertEqual(bytes, ['00000001', '00000011'])

        commands = self.collect_mached_command(output)

        self.assertEqual(commands, [
            ('lda', {'arg': 0}),
            ('addi', {'arg': 0})
        ])


















