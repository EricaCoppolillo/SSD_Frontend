from getpass import getpass

import csv
import sys
from pathlib import Path
from typing import Tuple, Callable, Any
import requests

from valid8 import validate, ValidationError

from shopping_list.domain import ShoppingList, Smartphone, Computer, Name, Manufacturer, Quantity, Price, Description, \
    Username, \
    Password, Email
from shopping_list.menu import Menu, MenuDescription, Entry


class App:
    __filename = Path(__file__).parent.parent / 'shoppingList.csv'
    __delimiter = ';'
    __logged = False
    __key = None

    def __init__(self):
        self.__first_menu = self.init_first_menu()
        self.__menu = self.__init_shopping_list_menu()
        self.__shoppinglist = ShoppingList()

    def init_first_menu(self) -> Menu:
        return Menu.Builder(MenuDescription('SIGN IN'), auto_select=lambda: print('Welcome!')) \
            .with_entry(Entry.create('1', 'Login', is_logged=lambda: self.__try_login())) \
            .with_entry(Entry.create('2', 'Register', on_selected=lambda: self.__try_register(), is_logged=lambda: True)) \
            .with_entry(Entry.create('0', 'Exit', on_selected=lambda: print('Bye!'), is_exit=True)) \
            .build()

    def __init_shopping_list_menu(self) -> Menu:
        return Menu.Builder(MenuDescription('SHOPPING LIST'), auto_select=lambda: self.__print_items()) \
            .with_entry(Entry.create('1', 'Add Smartphone', on_selected=lambda: self.__add_smartphone())) \
            .with_entry(Entry.create('2', 'Add Computer', on_selected=lambda: self.__add_computer())) \
            .with_entry(Entry.create('3', 'Remove Item', on_selected=lambda: self.__remove_item())) \
            .with_entry(Entry.create('4', 'Change quantity', on_selected=lambda: self.__change_quantity())) \
            .with_entry(Entry.create('5', 'Sort by Manufacturer', on_selected=lambda: self.__sort_by_manufacturer())) \
            .with_entry(Entry.create('6', 'Sort by Price', on_selected=lambda: self.__sort_by_price())) \
            .with_entry(Entry.create('0', 'Exit', on_selected=lambda: print('Bye!'), is_exit=True)) \
            .build()

    @staticmethod
    def __retrieve_key(res):
        json = res.json()
        return json['key']

    def __try_login(self) -> bool:
        username = self.__read("Username", Username)
        password = self.__read("Password", Password)

        # res = requests.post(url=f'{api_server}/auth/login/', data={'username': username, 'password': password})
        # if res.status_code != 200:
        #     return False

        # App.retrieve_key(res)

        return True


    def __try_register(self) -> None:
        username = self.__read("Username", Username)
        email = self.__read("Email", Email)
        password = self.__read("Password", Password)

        # res = .../ the user get authenticated
        #App.retrieve_key(res)

        return True


    def __print_items(self) -> None:
        print_sep = lambda: print('-' * 200)
        print_sep()
        fmt = '%3s %-30s %-30s %-30s %10s %50s'
        print(fmt % ('#', 'NAME', 'MANUFACTURER', 'PRICE', 'QUANTITY', 'DESCRIPTION'))
        print_sep()
        for index in range(self.__shoppinglist.items()):
            item = self.__shoppinglist.item(index)
            print(fmt % (index + 1, item.name, item.manufacturer, item.price, item.quantity, item.description))
        print_sep()

    def __add_smartphone(self) -> None:
        smartphone = Smartphone(*self.__read_item())
        self.__shoppinglist.add_smartphone(smartphone)
        self.__save()
        print('Smartphone added!')

    def __add_computer(self) -> None:
        computer = Computer(*self.__read_item())
        self.__shoppinglist.add_computer(computer)
        self.__save()
        print('Computer added!')

    def __remove_item(self) -> None:
        def builder(value: str) -> int:
            validate('value', int(value), min_value=0, max_value=self.__shoppinglist.items())
            return int(value)

        index = self.__read('Index (0 to cancel operation)', builder)
        if index == 0:
            print('Operation cancelled!')
            return
        self.__shoppinglist.remove_item(index - 1)
        self.__save()
        print('Item removed!')

    def __change_quantity(self) -> None:
        def builder(value: str) -> int:
            validate('value', int(value), min_value=0, max_value=self.__shoppinglist.items())
            return int(value)

        index = self.__read('Index (0 to cancel operation)', builder)
        if index == 0:
            print('Operation cancelled!')
            return

        quantity = self.__read('New Quantity', Quantity.cast)
        self.__shoppinglist.change_quantity(index - 1, quantity)
        self.__save()
        print('Quantity changed!')

    def __sort_by_manufacturer(self) -> None:
        self.__shoppinglist.sort_by_manufacturer()
        self.__save()

    def __sort_by_price(self) -> None:
        self.__shoppinglist.sort_by_price()
        self.__save()

    def __run(self) -> None:
        try:
            self.__load()
        except ValueError as e:
            print(e)
            print('Continuing with an empty list of item...')

        while not self.__first_menu.run() == (True, False):
            self.__menu.run()

    def run(self) -> None:
        try:
            self.__run()
        except Exception as e:
            print(e, file=sys.stderr)

    def __load(self) -> None:
        if not Path(self.__filename).exists():
            return

        with open(self.__filename) as file:
            reader = csv.reader(file, delimiter=self.__delimiter)
            for row in reader:
                validate('row length', row, length=6)

                typ = row[0]

                itemName = Name(row[1])

                manufacturer = Manufacturer(row[2])

                price = Price.create(Price.parse(row[3]).euro, Price.parse(row[3]).cents)

                quantity = Quantity(int(row[4]))

                description = Description(row[5])
                if typ == 'Smartphone':
                    self.__shoppinglist.add_smartphone(Smartphone(itemName, manufacturer, price, quantity, description))
                elif typ == 'Computer':
                    self.__shoppinglist.add_computer(Computer(itemName, manufacturer, price, quantity, description))
                else:
                    raise ValueError('Unknown item type in shoppingList.csv')

    def __save(self) -> None:
        with open(self.__filename, 'w') as file:
            writer = csv.writer(file, delimiter=self.__delimiter, lineterminator='\n')
            for index in range(self.__shoppinglist.items()):
                item = self.__shoppinglist.item(index)
                writer.writerow(
                    [item.category, item.name, item.manufacturer, item.price, item.quantity, item.description])

    @staticmethod
    def __read(prompt: str, builder: Callable) -> Any:
        while True:
            try:
                if prompt != 'Password':
                    line = input(f'{prompt}: ')
                else:
                    line = input(f'{prompt}: ')
                    # line = getpass(f'{prompt}: ')
                res = builder(line.strip())
                return res
            except (TypeError, ValueError, ValidationError) as e:
                print(e)

    def __read_item(self) -> Tuple[Name, Manufacturer, Price, Quantity, Description]:
        item = self.__read('Name', Name)
        manufacturer = self.__read('Manufacturer', Manufacturer)
        quantity = self.__read('Quantity', Quantity.cast)
        price = self.__read('Price', Price.parse)
        description = self.__read('Description', Description)
        return item, manufacturer, price, quantity, description


#######PARTE PER LA GESTIONE DEL LOGIN/REGISTRAZIONE#######

api_server = 'http://localhost:8000/api/v1'


# 3. Exit


def main(name: str):
    if name == '__main__':
        App().run()


main(__name__)
