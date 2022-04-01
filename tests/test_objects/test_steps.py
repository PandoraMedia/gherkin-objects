import unittest
from gherkin_objects.objects import Step, StepType, StepKeyword, InvalidGherkinError


class MyTestCase(unittest.TestCase):

    def test_step_sanity(self):
        step = Step(keyword=StepKeyword.AND,
                    text="a simple step",
                    step_type=StepType.GIVEN)

        self.assertEqual(step.raw_keyword, 'And')
        self.assertEqual(step.raw_text, 'And a simple step')

        self.assertEqual(step.real_keyword, 'Given')
        self.assertEqual(step.real_text, 'Given a simple step')

        self.assertEqual(step.text_without_keyword, 'a simple step')

    def test_step_type_inference(self):
        step = Step(keyword=StepKeyword.GIVEN, text='a simple step')

        self.assertEqual(step.step_type, StepType.GIVEN)

    def test_step_type_inference_failure(self):
        with self.assertRaises(ValueError):
            Step(keyword=StepKeyword.AND, text='a simple step')

    def test_step_from_text(self):
        step = Step.from_text('Given a simple step')
        self.assertEqual(step.raw_keyword, 'Given')
        self.assertEqual(step.real_keyword, 'Given')
        self.assertEqual(step.text_without_keyword, 'a simple step')

    def test_step_from_text_with_step_type(self):
        step = Step.from_text('And a simple step', step_type=StepType.GIVEN)
        self.assertEqual(step.raw_keyword, 'And')
        self.assertEqual(step.real_keyword, 'Given')
        self.assertEqual(step.text_without_keyword, 'a simple step')

    def test_step_from_text_without_step_type_failure(self):
        with self.assertRaises(ValueError):
            Step.from_text('And a simple step')

    def test_invalid_step_from_text(self):
        with self.assertRaises(InvalidGherkinError):
            Step.from_text('a simple step')

    def test_step_equality(self):
        step1 = Step(keyword=StepKeyword.GIVEN, text='a simple step')
        step2 = Step(keyword=StepKeyword.GIVEN, text='a simple step')
        self.assertEqual(step1, step2)

    def test_step_inequality(self):
        step1 = Step(keyword=StepKeyword.GIVEN, text='a simple step')
        step2 = Step(keyword=StepKeyword.WHEN, text='a complex step')
        self.assertNotEqual(step1, step2)

    def test_multiple_steps_from_text(self):
        text = """
        Given step 1
        When step 2
        Then step 3
        """

        expected_steps = [
            Step(keyword=StepKeyword.GIVEN, text='step 1'),
            Step(keyword=StepKeyword.WHEN, text='step 2'),
            Step(keyword=StepKeyword.THEN, text='step 3'),
        ]

        actual_steps = Step.multiple_from_text(text)

        self.assertSequenceEqual(actual_steps, expected_steps)

    def test_multiple_steps_from_text_with_step_type_inference(self):
        text = """
        Given step 1
        And step 2
        Then step 3
        * step 4
        * step 5
        """

        expected_steps = [
            Step(keyword=StepKeyword.GIVEN,
                 text='step 1',
                 step_type=StepType.GIVEN),
            Step(keyword=StepKeyword.AND,
                 text='step 2',
                 step_type=StepType.GIVEN),
            Step(keyword=StepKeyword.THEN,
                 text='step 3',
                 step_type=StepType.THEN),
            Step(keyword=StepKeyword.BULLET,
                 text='step 4',
                 step_type=StepType.THEN),
            Step(keyword=StepKeyword.BULLET,
                 text='step 5',
                 step_type=StepType.THEN),
        ]

        actual_steps = Step.multiple_from_text(text)

        self.assertSequenceEqual(actual_steps, expected_steps)

    def test_step_with_data_table___1_row(self):
        text = """
        Given step 1
        When step 2
        Then step 3
        | data 1 |
        | data 2 |
        """

        expected_steps = [
            Step(keyword=StepKeyword.GIVEN, text='step 1'),
            Step(keyword=StepKeyword.WHEN, text='step 2'),
            Step(keyword=StepKeyword.THEN, text='step 3'),
        ]
        actual_steps = Step.multiple_from_text(text)
        self.assertSequenceEqual(actual_steps, expected_steps)

        self.assertSequenceEqual(actual_steps[2].data_table.rows,
                                 [['data 1'], ['data 2']])

    def test_step_with_data_table___2_rows(self):
        text = """
        Given step 1
        When step 2
        Then step 3
        | data_1_1 | data_1_2 |
        | data_2_1 | data_2_2 |
        """

        expected_steps = [
            Step(keyword=StepKeyword.GIVEN, text='step 1'),
            Step(keyword=StepKeyword.WHEN, text='step 2'),
            Step(keyword=StepKeyword.THEN, text='step 3'),
        ]
        actual_steps = Step.multiple_from_text(text)
        self.assertSequenceEqual(actual_steps, expected_steps)

        expected_data_table_rows = [
            ['data_1_1', 'data_1_2'],
            ['data_2_1', 'data_2_2'],
        ]
        actual_data_table_rows = actual_steps[2].data_table.rows
        self.assertSequenceEqual(actual_data_table_rows,
                                 expected_data_table_rows)

    def test_step_with_data_table___complex(self):
        text = """
        Given step 1
        | 1 | 2 | 3 | 4 |
        
        When step 2
        | 11 | 12 | 13 |
        | 1 | 2 | 3 |
        | 4 | 5 | 6 |
        
        Then step 3
        | data_1_1 | data_1_2 |
        | data_2_1 | data_2_2 |
        """

        expected_steps = [
            Step(keyword=StepKeyword.GIVEN, text='step 1'),
            Step(keyword=StepKeyword.WHEN, text='step 2'),
            Step(keyword=StepKeyword.THEN, text='step 3'),
        ]
        actual_steps = Step.multiple_from_text(text)
        self.assertSequenceEqual(actual_steps, expected_steps)

        # Table 1
        expected_data_table_rows = [
            ['1', '2', '3', '4'],
        ]
        actual_data_table_rows = actual_steps[0].data_table.rows
        self.assertSequenceEqual(actual_data_table_rows,
                                 expected_data_table_rows)

        # Table 2
        expected_data_table_rows = [
            ['11', '12', '13'],
            ['1', '2', '3'],
            ['4', '5', '6'],
        ]
        actual_data_table_rows = actual_steps[1].data_table.rows
        self.assertSequenceEqual(actual_data_table_rows,
                                 expected_data_table_rows)

        # Table 3
        expected_data_table_rows = [
            ['data_1_1', 'data_1_2'],
            ['data_2_1', 'data_2_2'],
        ]
        actual_data_table_rows = actual_steps[2].data_table.rows
        self.assertSequenceEqual(actual_data_table_rows,
                                 expected_data_table_rows)


if __name__ == '__main__':
    unittest.main()
