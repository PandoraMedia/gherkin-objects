import unittest
from gherkin_objects.objects import ExampleTable, ExampleTableRow, ExampleTableCell, InvalidGherkinError


class ExampleTableTests(unittest.TestCase):

    def test_example_table_sanity(self):
        table = ExampleTable(
            header_row=ExampleTableRow(cells=[
                ExampleTableCell('A'),
                ExampleTableCell('B'),
            ]),
            data_rows=[
                ExampleTableRow(cells=[
                    ExampleTableCell('C'),
                    ExampleTableCell('D'),
                ]),
            ],
        )
        self.assertEqual(len(table.data_rows), 1)
        self.assertEqual(len(table.values), 2)

    def test_example_table_from_2d_array(self):
        table = ExampleTable.from_2d_array([
            ['A', 'B'],
            ['C', 'D'],
        ])
        self.assertEqual(table.values[0][0], 'A')
        self.assertEqual(table.values[0][1], 'B')
        self.assertEqual(table.values[1][0], 'C')
        self.assertEqual(table.values[1][1], 'D')

    def test_example_table_from_2d_array_non_square(self):
        with self.assertRaises(InvalidGherkinError):
            table = ExampleTable.from_2d_array([
                ['A', 'B'],
                ['C'],
            ])

    def test_example_table_from_text(self):
        text = '''
        Examples:
        | A | B |
        | C | D |
        '''
        table = ExampleTable.from_text(text)
        self.assertEqual(table.values[0][0], 'A')
        self.assertEqual(table.values[0][1], 'B')
        self.assertEqual(table.values[1][0], 'C')
        self.assertEqual(table.values[1][1], 'D')


if __name__ == '__main__':
    unittest.main()
