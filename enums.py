import enum


class Bosses(enum.Enum):
    """
    Enum class for the boss
    """

    HyperCore = 1
    Krakken = 2
    Slime = 3


class HyperCoreHealth(enum.Enum):
    """
    Enum class for the HyperCore health
    """

    one = 1_500_000
    two = 2_230_000  # 730
    three = 2_914_000  # 684
    four = 3_569_000  # 655
    five = 4_200_500  # 631
    six = 4_814_000  # 613
    seven = 5_412_500  # 598
    eight = 5_998_000  # 585
    nine = 6_573_000  # 575
    ten = 7_138_000  # 565
    eleven = 7_694_500  # 556
    twelve = 8_243_500  # 549
    thirteen = 8_785_000  # 543
    fourteen = 9_320_000  # 538
    fifteen = 9_849_500  # 535
    sixteen = 10_373_500  # 524
    seventeen = 10_892_000  # 518
    eighteen = 11_406_000  # 514
    nineteen = 11_915_000  # 509
    twenty = 12_420_500  # 505
    twenty_one = 12_921_500  # 501
    twenty_two = 13_419_000  # 498
    twenty_three = 13_913_000  # 494
    twenty_four = 14_403_500  # 490
    twenty_five = 14_890_500  # 487
    twenty_six = 15_374_000  # 483

    # O padrão é simplesmente multiplicar o valor anterior por 1.5 e arredondar para o inteiro mais próximo
