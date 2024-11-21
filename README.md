# Отчет по проекту: XML парсер и трансформер

## 1. Общее описание

Этот проект реализует парсер XML-документов с использованием библиотеки Lark и трансформирует их в конфигурационный язык. Парсер распознает константы, выражения и различные структуры данных (массивы и словари) и генерирует соответствующий код. Проект включает в себя функционал для выполнения константных вычислений, таких как сложение, вывод и вычисление квадратного корня.

## 2. Описание всех функций и настроек

### Грамматика XML

Грамматика, используемая в проекте, определяет структуру входящего XML-документа:

# Подробное описание грамматики XML

Давайте подробно рассмотрим представленную грамматику, которая описывает структуру XML-документа, используемого для парсинга. Эта грамматика предназначена для распознавания различных элементов XML, таких как константы, выражения, имена, функции и другие структуры данных.

## Описание грамматики

1. **Лексемы**:
   - **NAME**: 
     - Регулярное выражение: `/[_a-z]+/`
     - Описание: Имя может состоять из строчных букв латинского алфавита и символа подчеркивания. Это означает, что имена должны начинаться с буквы или символа подчеркивания и могут содержать только буквы и подчеркивания.
   
   - **STRING**: 
     - Регулярное выражение: `/[a-zA-Z0-9 ,;.!?#@$%^&*(){}\[\]\/ ]+/`
     - Описание: Строковые значения могут содержать буквы (как верхнего, так и нижнего регистра), цифры, пробелы и различные специальные символы. Это позволяет использовать текстовые значения, которые могут содержать как алфавитные, так и числовые символы, а также знаки препинания.

   - **NUMBER**:
     - Регулярное выражение: `/-?\d+(\.\d+)?/`
     - Описание: Числовые значения могут быть целыми или дробными. Они могут начинаться с опционального знака минус (для отрицательных чисел), за которым следуют одна или более цифр. Если присутствует десятичная точка, то за ней могут следовать дополнительные цифры.

   - **FUNC**:
     - Регулярное выражение: `/(?:print)|(?:sqrt)|\+/`
     - Описание: Функции, поддерживаемые в данной грамматике, это `print`, `sqrt` (квадратный корень) и оператор `+` (сложение).

2. **Правила**:
   - **constant**:
     - Описание: `<const>` определяет константу с именем и значением, заключенными в теги `<name>` и `<value>`. 
     - Пример: `<const><name>x</name><number>10</number></const>`

   - **constexpression**:
     - Описание: `<constexpr>` представляет выражение с функцией, именем и опциональным числовым значением. Это правило позволяет выполнять вычисления с константами.
     - Пример: `<constexpr><func>+</func><name>x</name><number>y</number></constexpr>`

   - **name**:
     - Описание: `<name>` используется для обрамления имен (например, имен констант или переменных) с использованием правила `NAME`.

   - **func**:
     - Описание: `<func>` обрамляет функции, используя правило `FUNC`.

   - **number**:
     - Описание: `<number>` обрамляет числовые значения с использованием правила `NUMBER`.

   - **string**:
     - Описание: `<string>` обрамляет строковые значения с использованием правила `STRING`.

   - **comment**:
     - Описание: `<comment>` позволяет добавлять комментарии в XML-документ. Комментарии заключены в `<!--` и `-->` и могут содержать текст, соответствующий `STRING`.

   - **array**:
     - Описание: `<items>` представляет массив, который может содержать несколько элементов, определенных правилами `arrayitem`.

   - **arrayitem**:
     - Описание: `<item>` обрамляет отдельные элементы массива, которые могут быть любыми значениями, определенными в правилах.

   - **dict**:
     - Описание: `<dictionary>` представляет словарь, который может содержать несколько пар "ключ-значение", определенных правилами `dictitem`.

   - **dictitem**:
     - Описание: `<dictitem>` обрамляет пары "ключ-значение", где ключ — это имя, а значение — это любое значение, соответствующее правилам.

   - **value**:
     - Описание: Определяет возможные типы значений, которые могут быть строками, массивами, числами, словарями или значениями выражений.

3. **Стартовое правило**:
   - **start**:
     - Описание: Основное правило, которое включает в себя одно или несколько значений, комментариев или констант. Это правило определяет, что документ может содержать произвольное количество элементов, соответствующих описанным выше правилам.

### Основные классы и методы

#### `XMLParser`

- **`Lark`**: Создает экземпляр парсера на основе определенной грамматики.

#### `XMLToConfig(Transformer)`

- **`constant(name, value)`**: Обрабатывает объявление константы.
- **`constexpression(func, name, number=None)`**: Обрабатывает константные выражения для выполнения функций `print`, `sqrt` и `+`.
- **`name(token)`**: Обрабатывает имена.
- **`func(token)`**: Обрабатывает функции.
- **`number(token)`**: Обрабатывает числовые значения.
- **`string(token)`**: Обрабатывает строковые значения.
- **`comment(token)`**: Обрабатывает комментарии.
- **`array(*items)`**: Обрабатывает массивы.
- **`dictitem(name, value)`**: Обрабатывает элементы словаря.
- **`dict(*dictitems)`**: Обрабатывает словари.
- **`pretty(string)`**: Упрощает форматирование строк.

## 3. Описание команд для сборки проекта

### Установка зависимостей

Для работы проекта требуется библиотека Lark. Установите её с помощью pip:

```bash
pip install lark-parser
```
Для запуска проекта используйте следующую команду:

```bash
python config_parser.py filename
```
Где ```filename``` - название файла, который вы хотите перевести на учебный язык

## 4. Примеры использования

### Пример 1
#### Входной файл:
```xml
<!-- User profile configuration -->
<const>
    <name>profile</name>
    <dictionary>
        <dictitem>
            <name>username</name>
            <string>john doe</string>
        </dictitem>
        <dictitem>
            <name>age</name>
            <number>25</number>
        </dictitem>
        <dictitem>
            <name>hobbies</name>
            <items>
                <item>
                    <string>Reading</string>
                </item>
                <item>
                    <string>Gaming</string>
                </item>
                <item>
                    <string>Traveling</string>
                </item>
            </items>
        </dictitem>
        <dictitem>
            <name>address</name>
            <dictionary>
                <dictitem>
                    <name>street</name>
                    <string>Main St.</string>
                </dictitem>
                <dictitem>
                    <name>house</name>
                    <number>123</number>
                </dictitem>
                <dictitem>
                    <name>country</name>
                    <string>USA</string>
                </dictitem>
            </dictionary>
        </dictitem>
    </dictionary>
</const>
```
### Результат работы парсера:
![Пример 1](/images/пример_1)

### Пример 2
#### Входной файл:
```xml
<const>
    <name>x</name>
    <number>10</number>
</const>
<const>
    <name>y</name>
    <number>5</number>
</const>
<const>
    <name>z</name>
    <constexpr>
        <func>+</func>
        <name>x</name>
        <number>2</number>
    </constexpr>
</const>
<constexpr>
        <func>sqrt</func>
        <name>x</name>
</constexpr>
<constexpr>
    <func>print</func>
    <name>x</name>
</constexpr>
<constexpr>
    <func>print</func>
    <name>y</name>
</constexpr>
<constexpr>
    <func>print</func>
    <name>z</name>
</constexpr>
<constexpr>
    <func>+</func>
    <name>z</name>
    <number>100</number>
</constexpr>
<constexpr>
    <func>print</func>
    <name>z</name>
</constexpr>
```

### Результат работы парсера:
![Пример 2](/images/пример_2)

## 5. Результаты прогона тестов
![Результаты тестов](/images/результаты_тестов)
