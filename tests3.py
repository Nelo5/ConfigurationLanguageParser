import unittest

from lark import LarkError

from config_parser import xml_parser, XMLToConfig, pretty


class TestXMLToConfig(unittest.TestCase):

    def setUp(self):
        self.parser = xml_parser
        self.transformer = XMLToConfig()

    def test_constant_number(self):
        input_xml = "<const><name>max_value</name><number>100</number></const>"
        expected_output = "(def max_value 100);"
        tree = self.parser.parse(input_xml)
        self.transformer.transform(tree)
        self.assertIn(expected_output, self.transformer.output)

    def test_constant_string(self):
        input_xml = "<const><name>greeting</name><string>Hello, World!</string></const>"
        expected_output = '(def greeting @"Hello, World!");'
        tree = self.parser.parse(input_xml)
        self.transformer.transform(tree)
        self.assertIn(expected_output, self.transformer.output)

    def test_constant_array(self):
        input_xml = "<const><name>my_array</name><items><item><number>1</number></item><item><string>two</string></item></items></const>"
        expected_output = '(def my_array [1, @"two"]);'
        tree = self.parser.parse(input_xml)
        result = self.transformer.transform(tree)
        self.assertEqual(expected_output, result)

    def test_constant_dict(self):
        input_xml = """<const><name>my_dict</name><dictionary>
        <dictitem><name>key_one</name><string>value1</string></dictitem>
        <dictitem><name>key_two</name><number>42</number></dictitem></dictionary></const>"""
        expected_output = '(def my_dict struct {\n\tkey_one = @"value1",\n\tkey_two = 42\n});'
        tree = self.parser.parse(pretty(input_xml))
        self.transformer.transform(tree)
        self.assertIn(expected_output, self.transformer.output)

    def test_constant_expression_add(self):
        input_xml = """
        <const><name>base</name><number>5</number></const>
        <const><name>result</name><constexpr><func>+</func><name>base</name><number>10</number></constexpr></const>
        """
        expected_output = "(def base 5);(def result 15.0);"
        tree = self.parser.parse(pretty(input_xml))
        self.transformer.transform(tree)
        self.assertEqual(expected_output, ''.join(self.transformer.output))

    def test_constant_expression_sqrt(self):
        input_xml = """
        <const><name>value</name><number>9</number></const>
        <const><name>sqrt_value</name><constexpr><func>sqrt</func><name>value</name></constexpr></const>
        """
        expected_output = "(def value 9);(def sqrt_value 3.0);"
        tree = self.parser.parse(pretty(input_xml))
        self.transformer.transform(tree)
        self.assertEqual(expected_output, ''.join(self.transformer.output))

    def test_constant_expression_print(self):
        input_xml = """
        <const><name>message</name><string>Hello!</string></const>
        <const><name>print_message</name><constexpr><func>print</func><name>message</name></constexpr></const>
        """
        expected_output = '(def message @"Hello!");@"Hello!"(def print_message @"Hello!");'
        tree = self.parser.parse(pretty(input_xml))
        self.transformer.transform(tree)
        self.assertEqual(expected_output, ''.join(self.transformer.output))

    def test_duplicate_constant_declaration(self):
        input_xml = """
        <const><name>pi</name><number>3.14</number></const>
        <const><name>pi</name><number>3.14</number></const>
        """
        with self.assertRaises(LarkError) as context:
            tree = self.parser.parse(pretty(input_xml))
            self.transformer.transform(tree)
        self.assertEqual(str(context.exception), 'Error trying to process rule "constant":\n\nКонстанта pi уже объявлена')

    def test_complex_array(self):
        input_xml = """
           <const><name>result</name><number>10</number></const>
           <items>
               <item><number>1</number></item>
               <item><string>Hello</string></item>
               <item><items><item><number>2</number></item><item><string>three</string></item></items></item>
               <item><dictionary>
                   <dictitem><name>key_one</name><string>value1</string></dictitem>
                   <dictitem><name>key_two</name><number>42</number></dictitem>
               </dictionary></item>
               <item><constexpr><func>+</func><name>result</name><number>5</number></constexpr></item>
           </items>
           """
        expected_output = """(def result 10);[1, @"Hello", [2, @"three"], struct {\n\tkey_one = @"value1",\n\tkey_two = 42\n}, 15.0]"""
        tree = self.parser.parse(pretty(input_xml))
        self.transformer.transform(tree)

        # Объединим результат для проверки
        result_output = ''.join(self.transformer.output)
        self.assertEqual(expected_output.strip(), result_output.strip())
    def test_complex_dict(self):
        input_xml = """
           <const><name>result</name><number>10</number></const>
           <dictionary>
               <dictitem><name>first</name><number>1</number></dictitem>
               <dictitem><name>second</name><string>Hello</string></dictitem>
               <dictitem><name>third</name><items><item><number>2</number></item><item><string>three</string></item></items></dictitem>
               <dictitem>
                   <name>fourth</name>
                   <dictionary>
                       <dictitem><name>key_one</name><string>value1</string></dictitem>
                       <dictitem><name>key_two</name><number>42</number></dictitem>
                   </dictionary></dictitem>
               <dictitem><name>fifth</name><constexpr><func>+</func><name>result</name><number>5</number></constexpr></dictitem>
           </dictionary>
           """
        expected_output = """(def result 10);struct {\n\tfirst = 1,\n\tsecond = @"Hello",\n\tthird = [2, @"three"],\n\tfourth = struct {\n\t\tkey_one = @"value1",\n\t\tkey_two = 42\n\t},\n\tfifth = 15.0\n}"""
        tree = self.parser.parse(pretty(input_xml))
        self.transformer.transform(tree)

        # Объединим результат для проверки
        result_output = ''.join(self.transformer.output)
        self.assertEqual(expected_output.strip(), result_output.strip())

    def test_const_expression_print(self):
        input_xml = """
        <const><name>my_value</name><number>42</number></const>
        <constexpr><func>print</func><name>my_value</name></constexpr>
        """
        expected_output = "(def my_value 42);^(print my_value)42"
        tree = self.parser.parse(pretty(input_xml))
        self.transformer.transform(tree)
        result_output = ''.join(self.transformer.output)
        self.assertEqual(expected_output, result_output.strip())

    def test_const_expression_sqrt(self):
        input_xml = """
        <const><name>my_number</name><number>16</number></const>
        <constexpr><func>sqrt</func><name>my_number</name></constexpr>
        """
        expected_output = "(def my_number 16);^(sqrt my_number)"
        tree = self.parser.parse(pretty(input_xml))
        self.transformer.transform(tree)
        result_output = ''.join(self.transformer.output)
        self.assertIn(expected_output, result_output.strip())

    def test_const_expression_addition_with_numeric_argument(self):
        input_xml = """
        <const><name>base_value</name><number>10</number></const>
        <constexpr><func>+</func><name>base_value</name><number>5</number></constexpr>
        """
        expected_output = "(def base_value 10);^(+ base_value 5)"
        tree = self.parser.parse(pretty(input_xml))
        self.transformer.transform(tree)
        result_output = ''.join(self.transformer.output)
        self.assertIn(expected_output, result_output.strip())

    def test_const_expression_addition_with_non_numeric_argument(self):
        input_xml = """
        <const><name>greeting</name><number>1</number></const>
        <constexpr><func>+</func><name>greeting</name></constexpr>
        """
        with self.assertRaises(LarkError) as context:
            tree = self.parser.parse(pretty(input_xml))
            self.transformer.transform(tree)
        self.assertEqual(str(context.exception), f'Error trying to process rule "constexpression":\n\nfloat() argument must be a string or a real number, not \'NoneType\'')

    def test_const_expression_addition_when_constant_value_not_number(self):
        input_xml = """
        <const><name>my_value</name><string>not a number</string></const>
        <constexpr><func>+</func><name>my_value</name><number>5</number></constexpr>
        """
        with self.assertRaises(LarkError) as context:
            tree = self.parser.parse(pretty(input_xml))
            self.transformer.transform(tree)
        self.assertEqual(str(context.exception), 'Error trying to process rule "constexpression":\n\nЗначение my_value не является числом')

    def test_const_expression_sqrt_when_constant_value_not_number(self):
        input_xml = """
        <const><name>my_value</name><string>not a number</string></const>
        <constexpr><func>sqrt</func><name>my_value</name></constexpr>
        """
        with self.assertRaises(LarkError) as context:
            tree = self.parser.parse(pretty(input_xml))
            self.transformer.transform(tree)
        self.assertEqual(str(context.exception), 'Error trying to process rule "constexpression":\n\nЗначение my_value не является числом')

    def test_const_expression_addition_when_constant_not_defined(self):
        input_xml = """
        <constexpr><func>+</func><name>undefined_value</name><number>5</number></constexpr>
        """
        with self.assertRaises(LarkError) as context:
            tree = self.parser.parse(pretty(input_xml))
            self.transformer.transform(tree)
        self.assertEqual(str(context.exception), 'Error trying to process rule "constexpression":\n\nКонстанта undefined_value ещё не объявлена')


if __name__ == '__main__':
    unittest.main()