from lark import Lark, Transformer, v_args, LarkError
import sys

# Грамматика XML
xml_grammar = """
NAME: /[_a-z]+/
STRING: /[a-zA-Z0-9 ,;.!?#@$%^&*(){}\[\]\/ ]+/
NUMBER: /-?\d+(\.\d+)?/   
FUNC: /(?:print)|(?:sqrt)|\+/ 

constant: "<const>"(name value)"</const>"
constexpression: "<constexpr>"(func name number?)"</constexpr>"
name: "<name>"NAME"</name>"
func: "<func>"FUNC"</func>"
number: "<number>"NUMBER"</number>"
string: "<string>"STRING"</string>"
comment: "<!--"STRING"-->"
array: "<items>"arrayitem*"</items>"
arrayitem: "<item>"value"</item>"
dict: "<dictionary>"dictitem*"</dictionary>" 
dictitem: "<dictitem>" (name value) "</dictitem>"
?value: string
    | array
    | number
    | dict
    | constexpression

?start:(value | comment | constant)+
"""

# Создаем парсер
xml_parser = Lark(xml_grammar, start='start', parser='earley')

# Трансформер для преобразования XML в конфигурационный язык
@v_args(inline=True)
class XMLToConfig(Transformer):
    def __init__(self):
        self.output = []
        self.consts = {}

    def constant(self, name, value):
        if name in  self.consts:
            raise LarkError(f"Константа {name} уже объявлена")
        if self.output[-2].startswith("^(print "):
            self.output = self.output[:-3]
            self.output.append(value)
        else:
            self.output = self.output[:-2]
        self.output.append(f"(def {name} {value});")
        self.consts[name] = value
        return f"(def {name} {value});"

    def constexpression(self, func, name, number=None):
        if name not in self.consts:
            raise LarkError(f"Константа {name} ещё не объявлена")
        if number is None:
            self.output = self.output[:-1]
        else:
            self.output = self.output[:-2]

        match func:
            case "+":
                try:
                    self.consts[name] = str(float(self.consts[name]) + float(number))
                    self.output.append(f'^({func} {name} {number})')
                    return self.consts[name]
                except ValueError:
                    if number is None:
                        raise LarkError(f"Значение, на которое увеличивается значение {name}, не указано")
                    raise LarkError(f"Значение {name} не является числом")

            case "sqrt":
                try:
                    self.consts[name] = str(float(self.consts[name]) ** 0.5)
                    self.output.append(f'^({func} {name})')
                    return self.consts[name]
                except ValueError:
                    raise ValueError(f"Значение {name} не является числом")

            case "print":
                self.output.append(f'^({func} {name})')
                self.output.append(self.consts[name])
                return self.consts[name]

    def name(self, token):
        self.output.append(token.value)
        return token.value

    def func(self, token):
        return token.value

    def number(self, token):
        self.output.append(token.value)
        return token.value

    def string(self, token):
        self.output.append(f"@\"{token.value}\"")
        return f"@\"{token.value}\""

    def comment(self, token):
        self.output.append(f"REM {token.value}")
        return f"REM {token.value}"

    def array(self, *items):
        values = ", ".join(items)
        self.output.append(f"[{values}]")
        return f"[{values}]"

    def arrayitem(self, value):
        self.output.pop()
        return value

    def dictitem(self, name, value):
        self.output = self.output[:-2]
        return f"{name} = {value}"

    def dict(self, *dictitems):
        items = []
        dictitems = list(dictitems)
        for i in range (len(dictitems)):
            items.append(dictitems[i].split('=')[0])
            if "struct {" in dictitems[i]:
                dictitems[i] = dictitems[i].replace('\n','\n\t')
        if len(items) != len(set(items)):
            raise ValueError("В словаре использованы повторяющиеся имена для ключей")
        fields = ",\n\t".join(dictitems)
        self.output.append(f"struct {{\n\t{fields}\n}}")
        return f"struct {{\n\t{fields}\n}}"

    def value(self, value):
        return value

def pretty(string):
    return ''.join([line.strip() for line in string.split('\n')])

if __name__ == "__main__":
    xml_input = ''.join([line.strip() for line in open(sys.argv[1]).readlines()])
    # xml_input = "<const><name>ffff</name><string>hhh</string></const><constexpr><func>+</func><name>ffff</name></constexpr>"
    try:
        tree = xml_parser.parse(xml_input)
        transformer = XMLToConfig()
        transformer.transform(tree)
        print("\n".join(transformer.output))
    except Exception as e:
        print(f"Error: {str(e)}")