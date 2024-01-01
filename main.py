import enum
import random
from typing import Dict, List, Optional
import pandas as pd

BASH_COLOR_BLUE = '\033[34m'
BASH_COLOR_GREEN = '\033[32m'
BASH_COLOR_RED = '\033[31m'
BASH_COLOR_EMD = '\033[0m'


def blue_text(text):
    return BASH_COLOR_BLUE + text + BASH_COLOR_EMD


def green_text(text):
    return BASH_COLOR_GREEN + text + BASH_COLOR_EMD


def red_text(text):
    return BASH_COLOR_RED + text + BASH_COLOR_EMD


class FilterType(enum.Enum):
    AbsentLetter = 1
    HasAtLeastLetterAmount = 2
    HasExactLetterAmount = 3
    HasLetterExactPos = 4


class FilterRule:
    __filter_type: FilterType
    __pos: Optional[int]
    __amount: Optional[int]
    __letter: str

    def __init__(self, filter_type: FilterType,
                 letter: str,
                 pos: Optional[int] = None,
                 amount: Optional[int] = None) -> None:
        assert (filter_type == FilterType.HasLetterExactPos) == (
            pos is not None)
        assert (filter_type in (FilterType.HasAtLeastLetterAmount, FilterType.HasExactLetterAmount)) == (
            amount is not None)
        self.__filter_type = filter_type
        self.__pos = pos
        self.__amount = amount
        self.__letter = letter

    def matches_condition(self, word: str) -> bool:
        match self.__filter_type:
            case FilterType.HasLetterExactPos:
                return len(word) > self.__pos and word[self.__pos] == self.__letter
            case FilterType.HasAtLeastLetterAmount:
                return word.count(self.__letter) >= self.__amount
            case FilterType.HasExactLetterAmount:
                return word.count(self.__letter) == self.__amount
            case FilterType.AbsentLetter:
                return self.__letter not in word
            case _:
                assert False

    def print_myself(self) -> None:
        match self.__filter_type:
            case FilterType.HasLetterExactPos:
                print(green_text("Есть буква"), blue_text(self.__letter),
                      green_text("На позиции"), blue_text(str(self.__pos + 1)))
            case FilterType.HasAtLeastLetterAmount:
                print(green_text("Буква"), blue_text(self.__letter),
                      green_text("встречается хотя бы"), blue_text(str(self.__amount)), green_text("раз"))
            case FilterType.HasExactLetterAmount:
                print(green_text("Буква"), blue_text(self.__letter),
                      green_text("встречается ровно"), blue_text(str(self.__amount)), green_text("раз"))
            case FilterType.AbsentLetter:
                print(green_text("Нету буквы"), blue_text(self.__letter))
            case _:
                assert False


def apply_filter_rules(words: List[str], filter_rules: List[FilterRule]) -> List[str]:
    result = []
    for word in words:
        add_to_res = True
        for filter in filter_rules:
            if not filter.matches_condition(word):
                add_to_res = False
                break
        if add_to_res:
            result.append(word)
    return result


LOOP_TEXT = green_text("""
====================================
""") + blue_text("[1]") + green_text(""" Добавить слово
""") + blue_text("[2]") + green_text(""" Вывести список возможных слов
""") + blue_text("[3]") + green_text(""" Вывести список внесенных правил
""") + blue_text("[4]") + green_text(""" Очистить список внесенных правил
====================================""")


MASK_TUTORIAL = green_text("""\
Введите маску слова из пяти символов. 
""") + blue_text("N") + green_text(""" - буквы нет
""") + blue_text("E") + green_text(""" - буква есть ровно на этой позиции
""") + blue_text("M") + green_text(""" - буква есть где-то в слове""")


def add_word(filter_rules: List[FilterRule]):
    word = input(green_text("Введите слово из пяти букв:")).split()[0].upper()
    print(green_text("Слово"), blue_text(word))

    if len(word) != 5:
        print(red_text("Слово не из пяти букв"))
        return

    print(MASK_TUTORIAL)
    mask = input().split()[0].upper()
    print(green_text("Маска"), blue_text(mask))

    if len(mask) != 5:
        print(red_text("Маска не из пяти букв"))
        return
    for c in mask:
        if c not in 'NEM':
            print(red_text("Маска содержит некорректный символ"))
            return

    added_rules: List[FilterRule] = []
    # Add exact filter rules
    for i, c in enumerate(mask):
        if c == 'E':
            added_rules.append(FilterRule(
                FilterType.HasLetterExactPos, word[i], i))

    # Add amount and absent filter rules
    letter_to_masks: Dict[str, List[str]] = {
        letter: [] for letter in set(word)}
    for i, c in enumerate(mask):
        letter_to_masks[word[i]].append(c)

    for letter, letter_masks in letter_to_masks.items():
        letter_count = letter_masks.count('M') + letter_masks.count('E')
        if letter_count > 0:
            if 'N' in letter_masks:
                added_rules.append(FilterRule(
                    FilterType.HasExactLetterAmount, letter, pos=None, amount=letter_count))
            else:
                added_rules.append(FilterRule(
                    FilterType.HasAtLeastLetterAmount, letter, pos=None, amount=letter_count))
        else:
            assert 'N' in letter_masks
            added_rules.append(FilterRule(FilterType.AbsentLetter, letter))

    filter_rules += added_rules
    print(green_text("Список добавленных правил:"))
    for i in added_rules:
        i.print_myself()


def main():
    # Fetch all words

    data = pd.read_csv("nouns.csv", sep='\t')
    raw_words = list(data.bare)
    words = [word.upper() for word in raw_words if len(word) == 5]
    filter_rules: List[FilterRule] = []

    while True:
        print(LOOP_TEXT)
        match int(input()):
            case 1:
                add_word(filter_rules)
            case 2:
                print(green_text("Возможные слова (в случайном порядке):"))
                limit = 20
                res = apply_filter_rules(words, filter_rules)
                random.shuffle(res)
                res = res
                for i in res[:limit]:
                    print(blue_text(i))
                if len(res) > limit:
                    print(red_text("Всего"), blue_text(str(len(res))), red_text("слов. Вывод ограничен на"),
                          blue_text("20"),  red_text("слов"))
            case 3:
                if len(filter_rules) == 0:
                    print(red_text("Список правил пустой"))
                for i in filter_rules:
                    i.print_myself()
            case 4:
                filter_rules = []
                print(green_text("Список внесенных правил очищен"))
            case _:
                assert False


if __name__ == '__main__':
    main()
