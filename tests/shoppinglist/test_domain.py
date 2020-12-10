import pytest
from valid8 import ValidationError

from shopping_list.domain import Name, Manufacturer, Quantity, Description, Price, Smartphone, Computer, ShoppingList, \
    Username, Email, Password


def test_name_format():
    wrong_values = ['', 'APP%LE', '<script>alert()</script>', 'Ciao /90 30', 'A' * 26]
    for value in wrong_values:
        with pytest.raises(ValidationError):
            Name(value)

    correct_values = ['S9 PLUS', 'REDMI NOTE 8 Pro', 'A' * 25]
    for value in correct_values:
        assert Name(value).value == value


def test_manufacturer_format():
    wrong_values = ['', 'A', 'APP%LE', '<script>alert()</script>', '8APPLE', 'Ciao /90 30', 'A' * 21]
    for value in wrong_values:
        with pytest.raises(ValidationError):
            Manufacturer(value)

    correct_values = ['Honor', 'Xiaomi', 'Dolce&Gabbana', 'Gigabyte-Haorus', 'A' * 20]
    for value in correct_values:
        assert Manufacturer(value).value == value


def test_quantity_range():
    wrong_quantities = [0, -5, 6]
    for value in wrong_quantities:
        with pytest.raises(ValidationError):
            Quantity(value)

    correct_quantities = [1, 3, 5]
    for value in correct_quantities:
        assert Quantity(value).value == value


def test_description_format():
    wrong_values = ['<script>alert()</script>', 'root/tree', '[:+%]{a}', 'A' * 101]
    for value in wrong_values:
        with pytest.raises(ValidationError):
            Description(value)

    correct_values = ['Caratteristiche: CPU,GPU,Chipset', 'CPU=Snapdragon750PROplus',
                      'Il prodotto presenta dei "piccoli" segnali di deterioramento', '(Gigabyte)-HaorusPRO', 'A' * 100]
    for value in correct_values:
        assert Description(value).value == value


def test_price_no_init():
    with pytest.raises(ValidationError):
        Price(1)


def test_price_cannot_be_negative():
    with pytest.raises(ValidationError):
        Price.create(-1, 0)


def test_price_no_cents():
    assert Price.create(1, 0) == Price.create(1)


def test_price_parse():
    assert Price.parse('10.20') == Price.create(10, 20)


def test_price_str():
    assert str(Price.create(9, 99)) == '9.99'


def test_price_euro():
    assert Price.create(11, 22).euro == 11


def test_price_cents():
    assert Price.create(11, 22).cents == 22


def test_price_add():
    assert Price.create(9, 99).add(Price.create(0, 1)) == Price.create(10)


def test_username_format():
    wrong_values = ['', '_ciao_', '<script>alert()</script>', 'uno spazio', 'è accentata', '%', 'A' * 26]
    for value in wrong_values:
        with pytest.raises(ValidationError):
            Username(value)

    correct_values = ['MARIO7777', 'MarioRossi', 'ciccio1997', 'A' * 25]
    for value in correct_values:
        assert Username(value).value == value


def test_email_format():
    wrong_values = ['', '_ciao@gmail.com', 'erica@libero290.com', '...@gmail.com', 'x<>@asdkjasld.89it',
                    'erica.coppolillo@', 'mario@gmail', 'x@gmx.', 'A' * 26]
    for value in wrong_values:
        with pytest.raises(ValidationError):
            Email(value)

    correct_values = ['marioRossi99@gmail.com', 'mario.rossi@libero.it', 'mario1999@gmail.com', 'A' * 20 + '@' + 'a.it']
    for value in correct_values:
        assert Email(value).value == value


def test_password_format():
    wrong_values = ['', 'password@', '<script>alert()</script>', '...asjdjadljas', 'ciaoCiao!=?',
                    '19999akdoa', 'A' * 26]
    for value in wrong_values:
        with pytest.raises(ValidationError):
            Password(value)

    correct_values = ['marioRossi17?', 'MARIOROSSi2!', 'francescoRICCIO22#', 'A' * 10 + 'a' * 2 + '1' * 5 + '!' * 3]
    for value in correct_values:
        assert Password(value).value == value


@pytest.fixture
def computers():
    return [
        Computer(Name('Air 13'), Manufacturer('Xiaomi'), Price.create(101), Quantity(1), Description("")),
        Computer(Name('Magibook 13'), Manufacturer('Huawei'), Price.create(8000), Quantity(1), Description("")),
        Computer(Name('XS-500'), Manufacturer('Asus'), Price.create(16000), Quantity(1),
                 Description("Questo prodotto è bellissimo")),
        Computer(Name('Swift 15'), Manufacturer('Acer'), Price.create(100), Quantity(1), Description("")),
        Computer(Name('h250p'), Manufacturer('HP'), Price.create(8000), Quantity(1), Description("")),

    ]


def test_computer_category(computers):
    for computer in computers:
        assert computer.category == 'Computer'


@pytest.fixture
def smartphones():
    return [
        Smartphone(Name('S20 Plus'), Manufacturer('Samsung'), Price.create(100), Quantity(3), Description("")),
        Smartphone(Name('Iphone 10 pro'), Manufacturer('Apple'), Price.create(1007), Quantity(2), Description("")),
        Smartphone(Name('Velvet'), Manufacturer('LG'), Price.create(590), Quantity(1),
                   Description("Questo prodotto è bellissimo")),
        Smartphone(Name('Find X'), Manufacturer('Oppo'), Price.create(16000), Quantity(1),
                   Description("Questo prodotto è bellissimo")),
        Smartphone(Name('Legion Phone Duel'), Manufacturer('Lenovo'), Price.create(100), Quantity(1), Description("")),
    ]


def test_smartphone_category(smartphones):
    for smartphone in smartphones:
        assert smartphone.category == 'Smartphone'


def test_shopping_list_add_computers(computers):
    shopping_list = ShoppingList()
    size = 0
    for computer in computers:
        shopping_list.add_computer(computer)
        size += 1
        assert shopping_list.items() == size
        assert shopping_list.item(size - 1) == computer


def test_shopping_list_max_cardinality(computers, smartphones):
    shopping_list = ShoppingList()
    for computer in computers:
        shopping_list.add_computer(computer)
    for smartphone in smartphones:
        shopping_list.add_smartphone(smartphone)
    with pytest.raises(ValidationError):
        shopping_list.add_computer(
            Computer(Name('Omen'), Manufacturer('HP'), Price.create(100), Quantity(1), Description("")))


def test_shopping_list_no_computer_duplicates():
    shopping_list = ShoppingList()
    shopping_list.add_computer(
        Computer(Name('Haorus'), Manufacturer('Gigabyte'), Price.create(100), Quantity(1), Description("")))
    with pytest.raises(ValueError):
        shopping_list.add_computer(
            Computer(Name('Haorus'), Manufacturer('Gigabyte'), Price.create(100), Quantity(4), Description("")))


def test_shopping_list_add_smartphones(smartphones):
    shopping_list = ShoppingList()
    size = 0
    for smartphone in smartphones:
        shopping_list.add_smartphone(smartphone)
        size += 1
        assert shopping_list.items() == size
        assert shopping_list.item(size - 1) == smartphone


def test_shopping_list_no_smartphone_duplicates():
    shopping_list = ShoppingList()
    shopping_list.add_smartphone(
        Smartphone(Name('Velvet'), Manufacturer('LG'), Price.create(100), Quantity(1), Description("")))
    with pytest.raises(ValueError):
        shopping_list.add_smartphone(
            Smartphone(Name('Velvet'), Manufacturer('LG'), Price.create(100), Quantity(4), Description("")))


def test_shopping_list_remove_item(smartphones, computers):
    shopping = ShoppingList()
    for computer in computers:
        shopping.add_computer(computer)
    for smartphone in smartphones:
        shopping.add_smartphone(smartphone)

    shopping.remove_item(0)
    assert shopping.item(0) == computers[1]

    with pytest.raises(ValidationError):
        shopping.remove_item(-1)
    with pytest.raises(ValidationError):
        shopping.remove_item(shopping.items())

    while shopping.items():
        shopping.remove_item(0)
    assert shopping.items() == 0


def test_shopping_list_sort_by_manufacturer(smartphones, computers):
    shopping = ShoppingList()
    shopping.add_computer(computers[0])
    shopping.add_smartphone(smartphones[0])
    shopping.sort_by_manufacturer()
    assert shopping.item(0) == smartphones[0]


def test_shopping_list_sort_by_price(smartphones, computers):
    shopping = ShoppingList()
    shopping.add_computer(computers[0])
    shopping.add_smartphone(smartphones[0])
    shopping.sort_by_price()
    assert shopping.item(0) == smartphones[0]


def test_shopping_list_change_quantity(smartphones):
    shopping = ShoppingList()
    shopping.add_smartphone(smartphones[0])
    shopping.change_quantity(0, Quantity(1))

    with pytest.raises(ValidationError):
        shopping.change_quantity(-1, Quantity(1))
    with pytest.raises(ValidationError):
        shopping.change_quantity(shopping.items(), Quantity(1))

    assert shopping.item(0).quantity.value == 1
