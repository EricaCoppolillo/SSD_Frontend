from pathlib import Path
from unittest.mock import patch, mock_open, Mock, call

import pytest

from shopping_list.app import App, main


@pytest.fixture
def mock_path():
    Path.exists = Mock()
    Path.exists.return_value = True
    return Path


@pytest.fixture
def data():
    data = [
        ['Smartphone', 'Redmi Note 8 Pro', 'Xiaomi', '3000.00', '1', 'This product is really beautiful bla bla'],
        ['Computer', 'MagicBook', 'Honor', '1000.00', '3', ''],
    ]
    print('\n'.join(['\t'.join(d) for d in data]))
    return '\n'.join(['\t'.join(d) for d in data])


@patch('builtins.input', side_effect=['0'])
@patch('builtins.print')
def test_app_sign_in(mocked_print, mocked_input):
    with patch('builtins.open', mock_open()) as mocked_open:
        App().run()
    mocked_print.assert_any_call('*** SIGN IN ***')
    mocked_print.assert_any_call('0:\tExit')
    mocked_print.assert_any_call('Bye!')
    mocked_input.assert_called()


@patch('builtins.input', side_effect=['1', '<script>', 'marioRossi', 'securePassword7!'])
@patch('builtins.print')
def test_app_sign_in_resists_wrong_username(mocked_print, mocked_input):
    with patch('builtins.open', mock_open()):
        App().run()
    mocked_print.assert_any_call('*** SIGN IN ***')
    mocked_print.assert_any_call('*** SHOPPING LIST ***')


@patch('builtins.input', side_effect=['1', 'marioRossi', 'notSecurePassword', 'securePassword7!'])
@patch('builtins.print')
def test_app_sign_in_resists_wrong_password(mocked_print, mocked_input):
    with patch('builtins.open', mock_open()):
        App().run()
    mocked_print.assert_any_call('*** SIGN IN ***')
    mocked_print.assert_any_call('*** SHOPPING LIST ***')


@patch('builtins.input', side_effect=['1', 'marioRossi', 'securePassword7!'])
@patch('builtins.print')
def test_app_shopping_list(mocked_print, mocked_input):
    with patch('builtins.open', mock_open()):
        App().run()
    mocked_print.assert_any_call('*** SIGN IN ***')
    mocked_print.assert_any_call('1:\tLogin')
    mocked_print.assert_any_call('*** SHOPPING LIST ***')
    mocked_input.assert_called()


@patch('builtins.input', side_effect=['1', 'marioRossi', 'securePassword9!'])
@patch('builtins.print')
def test_app_load_datafile(mocked_print, mocked_input, mock_path, data):
    with patch('builtins.open', mock_open(read_data=data)):
        App().run()
    mock_path.exists.assert_called_once()
    assert list(filter(lambda x: 'Smartphone' in str(x), mocked_print.mock_calls))
    mocked_input.assert_called()


@patch('builtins.input', side_effect=['1', 'marioRossi', 'securePassword9!'])
@patch('builtins.print')
def test_app_handles_corrupted_datafile(mocked_print, mocked_input, mock_path):
    with patch('builtins.open', mock_open(read_data='xyz')):
        App().run()
    mocked_print.assert_any_call('Continuing with an empty list of items...')
    mocked_input.assert_called()


@patch('builtins.input', side_effect=['1', 'marioRossi', 'securePassword9!'])
@patch('builtins.print')
def test_app_handles_unknown_type_in_datafile(mocked_print, mocked_input, mock_path):
    with patch('builtins.open', mock_open(read_data='Tablet\tGalaxy Tab\tSamsung\t2000\t1\tsuper bello fantastico')):
        App().run()
    mocked_print.assert_any_call('Continuing with an empty list of items...')
    mocked_input.assert_called()


@patch('builtins.input',
       side_effect=['1', 'marioRossi', 'securePassword7!', '1', 'Redmi Note 8', 'Xiaomi', '2', '900', ''])
@patch('builtins.print')
def test_app_add_smartphone(mocked_print, mocked_input, mock_path):
    with patch('builtins.open', mock_open()) as mocked_open:
        App().run()
    assert list(filter(lambda x: 'Smartphone' in str(x), mocked_print.mock_calls))

    handle = mocked_open()
    handle.write.assert_called_once_with('Smartphone\tRedmi Note 8\tXiaomi\t900.00\t2\t\n')
    mocked_input.assert_called()


@patch('builtins.input',
       side_effect=['1', 'marioRossi', 'securePassword7!', '1', '<script>', 'Redmi Note 8', 'Xiaomi', '2', '900', ''])
@patch('builtins.print')
def test_app_add_smartphone_resists_wrong_name(mocked_print, mocked_input, mock_path):
    with patch('builtins.open', mock_open()) as mocked_open:
        App().run()
    assert list(filter(lambda x: 'Smartphone' in str(x), mocked_print.mock_calls))

    handle = mocked_open()
    handle.write.assert_called_once_with('Smartphone\tRedmi Note 8\tXiaomi\t900.00\t2\t\n')
    mocked_input.assert_called()


@patch('builtins.input',
       side_effect=['1', 'marioRossi', 'securePassword7!', '1', 'Redmi Note 8', 'Xiaomi', 'asd', '-1', '2', '900', ''])
@patch('builtins.print')
def test_app_add_smartphone_resists_wrong_quantity(mocked_print, mocked_input, mock_path):
    with patch('builtins.open', mock_open()) as mocked_open:
        App().run()
    assert list(filter(lambda x: 'Smartphone' in str(x), mocked_print.mock_calls))

    handle = mocked_open()
    handle.write.assert_called_once_with('Smartphone\tRedmi Note 8\tXiaomi\t900.00\t2\t\n')
    mocked_input.assert_called()


@patch('builtins.input',
       side_effect=['1', 'marioRossi', 'securePassword7!', '1', 'Redmi Note 8', 'Xiaomi', '2', 'asd', '-1', '900', ''])
@patch('builtins.print')
def test_app_add_smartphone_resists_wrong_price(mocked_print, mocked_input, mock_path):
    with patch('builtins.open', mock_open()) as mocked_open:
        App().run()
    assert list(filter(lambda x: 'Smartphone' in str(x), mocked_print.mock_calls))

    handle = mocked_open()
    handle.write.assert_called_once_with('Smartphone\tRedmi Note 8\tXiaomi\t900.00\t2\t\n')
    mocked_input.assert_called()


@patch('builtins.input', side_effect=['1', 'marioRossi', 'securePassword7!', '2', 'Mi Air', 'Xiaomi', '1', '400',
                                      'really excellent product!!!'])
@patch('builtins.print')
def test_app_add_computer(mocked_print, mocked_input, mock_path):
    with patch('builtins.open', mock_open()) as mocked_open:
        App().run()
    assert list(filter(lambda x: 'Computer' in str(x), mocked_print.mock_calls))

    handle = mocked_open()
    handle.write.assert_called_once_with('Computer\tMi Air\tXiaomi\t400.00\t1\treally excellent product!!!\n')
    mocked_input.assert_called()


@patch('builtins.input', side_effect=['1', 'marioRossi', 'securePassword7!', '3', '1'])
@patch('builtins.print')
def test_app_remove_item(mocked_print, mocked_input, mock_path, data):
    with patch('builtins.open', mock_open(read_data=data)) as mocked_open:
        App().run()
    mocked_input.assert_called()
    mocked_print.assert_called()

    handle = mocked_open()
    handle.write.assert_called_once_with('Computer\tMagicBook\tHonor\t1000.00\t3\t\n')


@patch('builtins.input', side_effect=['1', 'marioRossi', 'securePassword7!', '3', '4', '1'])
@patch('builtins.print')
def test_app_remove_item_resists_wrong_index(mocked_print, mocked_input, mock_path, data):
    with patch('builtins.open', mock_open(read_data=data)) as mocked_open:
        App().run()
    mocked_input.assert_called()
    mocked_print.assert_called()

    handle = mocked_open()
    handle.write.assert_called_once_with('Computer\tMagicBook\tHonor\t1000.00\t3\t\n')


@patch('builtins.input', side_effect=['1', 'marioRossi', 'securePassword7!', '5'])
@patch('builtins.print')
def test_app_sort_by_price(mocked_print, mocked_input, mock_path, data):
    with patch('builtins.open', mock_open(read_data=data)) as mocked_open:
        App().run()
    mocked_input.assert_called()
    mocked_print.assert_called()

    handle = mocked_open()
    assert handle.write.mock_calls == [
        call('Computer\tMagicBook\tHonor\t1000.00\t3\t\n'),
        call('Smartphone\tRedmi Note 8 Pro\tXiaomi\t3000.00\t1\tThis product is really beautiful bla bla\n'),
    ]


@patch('builtins.input', side_effect=['1', 'marioRossi', 'securePassword7!', '5', '4', '0'])
@patch('builtins.print')
def test_app_sort_by_manufacturer(mocked_print, mocked_input, mock_path, data):
    with patch('builtins.open', mock_open(read_data=data)) as mocked_open:
        App().run()
    mocked_input.assert_called()
    mocked_print.assert_called()

    handle = mocked_open()
    assert handle.write.mock_calls == [
        call('Computer\tMagicBook\tHonor\t1000.00\t3\t\n'),
        call('Smartphone\tRedmi Note 8 Pro\tXiaomi\t3000.00\t1\tThis product is really beautiful bla bla\n'),
    ]


# @patch('builtins.input', side_effect=['0'])
# @patch('builtins.print')
# def test_app_global_exception_handler(mocked_print, mocked_input):
#     with patch.object(Path, 'exists') as mocked_path_exits:
#         mocked_path_exits.side_effect = Mock(side_effect=Exception('Test'))
#         App().run()
#     assert mocked_input.mock_calls == []
#     assert list(filter(lambda x: 'Panic Error!' in str(x), mocked_print.mock_calls))
