import pytest
from valid8 import ValidationError

from shopping_list.domain import Name, Manufacturer, Quantity, Description, Price, Smartphone, Computer, ShoppingList


def test_name_format():
    wrong_values = ['','APP%LE', '<script>alert()</script>', 'Ciao /90 30', 'A' * 26]
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
    wrong_values = ['', 'a', '<script>alert()</script>', 'root/tree', '[:+%]{a}', 'A' * 101, 'A' * 19]
    for value in wrong_values:
        with pytest.raises(ValidationError):
            Description(value)

    correct_values = ['Caratteristiche: CPU,GPU,Chipset', 'CPU=Snapdragon750PROplus',
                      'Il prodotto presenta dei "piccoli" segnali di deterioramento', '(Gigabyte)-HaorusPRO', 'A' * 100]
    for value in correct_values:
        dvalue=Description(value).value
        print(dvalue)
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


@pytest.fixture
def computers():
    return [
        Computer(Name('Air 13'), Manufacturer('Xiaomi'), Price.create(101), Quantity(1)),
        Computer(Name('Magibook 13'), Manufacturer('Huawei'), Price.create(8000), Quantity(1)),
        Computer(Name('XS-500'), Manufacturer('Asus'), Price.create(16000), Quantity(1),
                 Description("Questo prodotto è bellissimo")),
        Computer(Name('Swift 15'), Manufacturer('Acer'), Price.create(100), Quantity(1)),
        Computer(Name('h250p'), Manufacturer('HP'), Price.create(8000), Quantity(1)),

    ]


def test_computer_category(computers):
    for computer in computers:
        computer.category == 'Computer'


@pytest.fixture
def smartphones():
    return [
        Smartphone(Name('S20 Plus'), Manufacturer('Samsung'), Price.create(100), Quantity(3)),
        Smartphone(Name('Iphone 10 pro'), Manufacturer('Apple'), Price.create(1007), Quantity(2)),
        Smartphone(Name('Velvet'), Manufacturer('LG'), Price.create(590), Quantity(1),
                   Description("Questo prodotto è bellissimo")),
        Smartphone(Name('Find X'), Manufacturer('Oppo'), Price.create(16000), Quantity(1),
                   Description("Questo prodotto è bellissimo")),
        Smartphone(Name('Legion Phone Duel'), Manufacturer('Lenovo'), Price.create(100), Quantity(1)),
    ]


def test_smartphone_category(smartphones):
    for smartphone in smartphones:
        smartphone.category == 'Smartphone'


def test_shoppinglist_add_computers(computers):
    shoppingList = ShoppingList()
    size = 0
    for computer in computers:
        shoppingList.add_computer(computer)
        size += 1
        assert shoppingList.items() == size
        assert shoppingList.item(size - 1) == computer


def test_shoppinglist_max_cardinality(computers, smartphones):
    shoppingList = ShoppingList()
    for computer in computers:
        shoppingList.add_computer(computer)
    for smartphone in smartphones:
        shoppingList.add_smartphone(smartphone)
    with pytest.raises(ValidationError):
        shoppingList.add_computer(Computer(Name('Omen'), Manufacturer('HP'), Price.create(100), Quantity(1)))


def test_shoppinglist_no_computer_duplicates():
    shoppingList = ShoppingList()
    shoppingList.add_computer(Computer(Name('Haorus'), Manufacturer('Gigabyte'), Price.create(100), Quantity(1)))
    with pytest.raises(ValidationError):
        shoppingList.add_computer(Computer(Name('Haorus'), Manufacturer('Gigabyte'), Price.create(100), Quantity(4)))


def test_shoppinglist_add_smartphones(smartphones):
    shoppingList = ShoppingList()
    size = 0
    for smartphone in smartphones:
        shoppingList.add_smartphone(smartphone)
        size += 1
        assert shoppingList.items() == size
        assert shoppingList.item(size - 1) == smartphone


def test_shoppinglist_no_smartphone_duplicates():
    shoppingList = ShoppingList()
    shoppingList.add_smartphone(Smartphone(Name('Velvet'), Manufacturer('LG'), Price.create(100), Quantity(1)))
    with pytest.raises(ValidationError):
        shoppingList.add_smartphone(Smartphone(Name('Velvet'), Manufacturer('LG'), Price.create(100), Quantity(4)))


def test_shoppinglist_remove_item(smartphones, computers):
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


def test_shoppinglist_sort_by_manufacturer(smartphones, computers):
    shopping = ShoppingList()
    shopping.add_computer(computers[0])
    shopping.add_smartphone(smartphones[0])
    shopping.sort_by_manufacturer()
    assert shopping.item(0) == smartphones[0]


def test_shoppinglist_sort_by_price(smartphones, computers):
    shopping = ShoppingList()
    shopping.add_computer(computers[0])
    shopping.add_smartphone(smartphones[0])
    shopping.sort_by_price()
    assert shopping.item(0) == smartphones[0]


def test_shoppinglist_change_quantity(smartphones):
    shopping = ShoppingList()
    shopping.add_smartphone(smartphones[0])
    shopping.change_quantity(0, Quantity(1))

    with pytest.raises(ValidationError):
        shopping.change_quantity(-1, Quantity(1))
    with pytest.raises(ValidationError):
        shopping.change_quantity(shopping.items(), Quantity(1))

    assert shopping.item(0).quantity.value == 1
