import re
from dataclasses import dataclass, InitVar, field
from typing import Any, Union, List

from typeguard import typechecked
from valid8 import validate
from valid8 import ValidationError
from validation.dataclasses import validate_dataclass
from validation.regex import pattern


@typechecked
@dataclass(frozen=True, order=True)
class Name:
    value: str

    def __post_init__(self):
        validate_dataclass(self)
        validate('value', self.value, min_len=1, max_len=25, custom=pattern(r'[A-Za-z0-9 \-\_]+'))

    def __str__(self):
        return self.value




@typechecked
@dataclass(frozen=True, order=True)
class Manufacturer:
    value: str

    def __post_init__(self):
        validate_dataclass(self)
        validate('value', self.value, min_len=2, max_len=20, custom=pattern(r'[A-Za-z \_\-\&]+'))

    def __str__(self):
        return self.value


@typechecked
@dataclass(frozen=True, order=True)
class Quantity:
    value: int

    def __post_init__(self):
        validate_dataclass(self)
        validate('value', self.value, min_value=1, max_value=5)

    def __str__(self):
        return str(self.value)

    @staticmethod
    def cast(value: str) -> 'Quantity':
        return Quantity(int(value))


@typechecked
@dataclass(frozen=True, order=True)
class Price:
    value_in_cents: int
    create_key: InitVar[Any] = field(default=None)

    __create_key = object()
    __max_value = 100000000000 - 1
    __parse_pattern = re.compile(r'(?P<euro>\d{0,11})(?:\.(?P<cents>\d{2}))?')

    def __post_init__(self, create_key):
        validate('create_key', create_key, equals=self.__create_key)
        validate_dataclass(self)
        validate('value_in_cents', self.value_in_cents, min_value=0, max_value=self.__max_value)

    def __str__(self):
        return f'{self.value_in_cents // 100}.{self.value_in_cents % 100:02}'

    @staticmethod
    def create(euro: int, cents: int = 0) -> 'Price':
        validate('euro', euro, min_value=0, max_value=Price.__max_value // 100)
        validate('cents', cents, min_value=0, max_value=99)
        return Price(euro * 100 + cents, Price.__create_key)

    @staticmethod
    def parse(value: str) -> 'Price':
        m = Price.__parse_pattern.fullmatch(value)
        validate('value', m)
        euro = m.group('euro')
        cents = m.group('cents') if m.group('cents') else 0
        return Price.create(int(euro), int(cents))

    @property
    def cents(self) -> int:
        return self.value_in_cents % 100

    @property
    def euro(self) -> int:
        return self.value_in_cents // 100

    def add(self, other: 'Price') -> 'Price':
        return Price(self.value_in_cents + other.value_in_cents, self.__create_key)


@typechecked
@dataclass(frozen=True, order=True)
class Description:
    value: str

    def __post_init__(self):
        validate_dataclass(self)
        validate('value', self.value, max_len=100,
                 custom=pattern(r'[A-Za-z0-9\_\-\(\)\.\,\;\&\:\=\è\'\"\! ]*'))

    def __str__(self):
        return str(self.value)


@typechecked
@dataclass(frozen=True, order=True)
class Username:
    value: str

    def __post_init__(self):
        validate_dataclass(self)
        validate('value', self.value, min_len=8, max_len=25, custom=pattern(r'[A-Za-z0-9]+'))

    def __str__(self):
        return str(self.value)


@typechecked
@dataclass(frozen=True, order=True)
class Email:
    value: str

    def __post_init__(self):
        validate_dataclass(self)
        validate('value', self.value, min_len=8, max_len=25,
                 custom=pattern(r'[A-Za-z0-9]+[\.]*[A-Za-z]*@[A-Za-z]+\.[a-z]+'))

    def __str__(self):
        return str(self.value)


@typechecked
@dataclass(frozen=True, order=True)
class Password:
    value: str

    def __post_init__(self):
        validate_dataclass(self)
        validate('value', self.value, min_len=6, max_len=25,
                 custom=pattern(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!\#*?&])[A-Za-z\d@$!\#*?&]{6,}$'))

    def __str__(self):
        return str(self.value)


@typechecked
@dataclass(frozen=True, order=True)
class Smartphone:
    name: Name
    manufacturer: Manufacturer
    price: Price
    quantity: Quantity
    description: Description

    def is_equal(self, other):
        return isinstance(other,
                          Smartphone) and self.name.value == other.name.value and self.manufacturer.value == other.manufacturer.value

    @property
    def category(self) -> str:
        return 'Smartphone'


@typechecked
@dataclass(frozen=True, order=True)
class Computer:
    name: Name
    manufacturer: Manufacturer
    price: Price
    quantity: Quantity
    description: Description

    def is_equal(self, other):
        return isinstance(other,
                          Computer) and self.name.value == other.name.value and self.manufacturer.value == other.manufacturer.value

    @property
    def category(self) -> str:
        return 'Computer'


@typechecked
@dataclass(frozen=True)
class ShoppingList:
    __items: List[Union[Smartphone, Computer]] = field(default_factory=list, init=False)

    def items(self) -> int:
        return len(self.__items)

    def item(self, index: int) -> Union[Smartphone, Computer]:
        validate('index', index, min_value=0, max_value=self.items() - 1)
        return self.__items[index]

    def clear(self) -> None:
        self.__items.clear()

    def add_smartphone(self, smartphone: Smartphone) -> None:
        validate('items', self.items(), max_value=9)
        if self.there_are_duplicates(smartphone):
            raise ValueError
        self.__items.append(smartphone)

    def add_computer(self, computer: Computer) -> None:
        validate('items', self.items(), max_value=9)
        if self.there_are_duplicates(computer):
            raise ValueError
        self.__items.append(computer)

    def there_are_duplicates(self, item) -> bool:
        for i in self.__items:
            if item.is_equal(i):
                return True
        return False

    def remove_item(self, index: int) -> None:
        validate('index', index, min_value=0, max_value=self.items() - 1)
        del self.__items[index]

    def change_quantity(self, index: int, quantity: Quantity):
        validate('index', index, min_value=0, max_value=self.items() - 1)
        get_item = self.__items[index]
        self.remove_item(index)
        if get_item.category == "Smartphone":
            self.__items.insert(index,
                                Smartphone(get_item.name, get_item.manufacturer, get_item.price, quantity,
                                           get_item.description))
        else:
            self.__items.insert(index,
                                Computer(get_item.name, get_item.manufacturer, get_item.price, quantity,
                                         get_item.description))

    def sort_by_manufacturer(self) -> None:
        self.__items.sort(key=lambda x: x.manufacturer)

    def sort_by_price(self) -> None:
        self.__items.sort(key=lambda x: x.price)
