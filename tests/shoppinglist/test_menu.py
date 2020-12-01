from unittest.mock import patch, call, Mock

import pytest
from valid8 import ValidationError

from shopping_list.menu import MenuDescription, Key, Entry, Menu


def test_menu_description_must_be_string():
    MenuDescription('ok')
    with pytest.raises(TypeError):
        MenuDescription(0)
    with pytest.raises(TypeError):
        MenuDescription(None)


def test_menu_description_must_be_non_empty_string():
    MenuDescription('correct')
    with pytest.raises(ValidationError):
        MenuDescription('')


def test_menu_description_must_not_exceed_1000_chars():
    MenuDescription('a' * 1000)
    with pytest.raises(ValidationError):
        MenuDescription('a' * 1001)


def test_menu_description_must_not_contain_special_chars():
    for special_char in ['\n', '\r', '*', '^', '$']:
        with pytest.raises(ValidationError):
            MenuDescription(special_char)


def test_key_cannot_be_empty():
    with pytest.raises(ValidationError):
        Key('')


def test_key_cannot_exceed_10_chars():
    with pytest.raises(ValidationError):
        Key('a' * 11)


def test_key_cannot_contain_special_chars():
    for special_char in ['\n', '\r', '*', '^', '$']:
        with pytest.raises(ValidationError):
            Key(special_char)


def test_entry_on_selected():
    mocked_on_selected = Mock()
    entry = Entry(Key('1'), MenuDescription('Say hi'), on_selected=lambda: mocked_on_selected())
    entry.on_selected()
    mocked_on_selected.assert_called_once()


@patch('builtins.print')
def test_entry_on_selected_print_something(mocked_print):
    entry = Entry(Key('1'), MenuDescription('Say hi'), on_selected=lambda: print('hi'))
    entry.on_selected()
    assert mocked_print.mock_calls == [call('hi')]


def test_menu_builder_cannot_create_empty_menu():
    menu_builder = Menu.Builder(MenuDescription('a description'))
    with pytest.raises(ValidationError):
        menu_builder.build()


def test_menu_builder_cannot_create_menu_without_exit():
    menu_builder = Menu.Builder(MenuDescription('a description'))
    with pytest.raises(ValidationError):
        menu_builder.build()
    menu_builder.with_entry(Entry.create('1', 'exit', is_exit=True))
    menu_builder.build()


def test_menu_builder_cannot_call_two_times_build():
    menu_builder = Menu.Builder(MenuDescription('a description'))
    menu_builder.with_entry(Entry.create('1', 'first entry', is_exit=True))
    menu_builder.build()
    with pytest.raises(ValidationError):
        menu_builder.build()


def test_menu_does_not_contain_duplicates():
    menu_builder = Menu.Builder(MenuDescription('a description'))
    menu_builder.with_entry(Entry.create('1', 'first entry'))
    with pytest.raises(ValidationError):
        menu_builder.with_entry(Entry.create('1', 'first entry'))


@patch('builtins.input', side_effect=['1', '0'])
@patch('builtins.print')
def test_menu_selection_call_on_selected(mocked_print, mocked_input):
    menu = Menu.Builder(MenuDescription('a description')) \
        .with_entry(Entry.create('1', 'first entry', on_selected=lambda: print('first entry selected'))) \
        .with_entry(Entry.create('0', 'exit', is_exit=True)) \
        .build()
    menu.run()
    mocked_print.assert_any_call('first entry selected')
    mocked_input.assert_called()


@patch('builtins.input', side_effect=['-1', '0'])
@patch('builtins.print')
def test_menu_selection_on_wrong_key(mocked_print, mocked_input):
    menu = Menu.Builder(MenuDescription('a description')) \
        .with_entry(Entry.create('1', 'first entry', on_selected=lambda: print('first entry selected'))) \
        .with_entry(Entry.create('0', 'exit', is_exit=True)) \
        .build()
    menu.run()
    mocked_print.assert_any_call('Invalid selection. Please, try again...')
    mocked_input.assert_called()
