import uuid
from unittest.mock import Mock

from models.city import City, Directions, InventoryType, Merchant
from models.inventory import Item
from models.user import Character, DiscordAccount, Player, Name, User
from use_cases.recipe_book import RecipeBook


def user_guy():
    player = Player(
        name=Name(
            first="Guy",
            last="Turner",
        ),
        is_gm=True
    )

    character = None

    discord_account = DiscordAccount(
        user_id=1,
        username="fake_username_1"
    )

    return User(
        player=player,
        character=character,
        discord_account=discord_account
    )

def user_todd():
    player = Player(
        name=Name(
            first="Todd",
            last="Pettit",
        ),
        is_gm=False
    )

    character = Character(
        name=Name(
            first="Tanner",
            last=None,
        ),
        level=4,
        race_name="Half-Vah'Shir",
        class_name="Bard",
        alignment="N"
    )

    discord_account = DiscordAccount(
        user_id=2,
        username="fake_username_2"
    )

    return User(
        player=player,
        character=character,
        discord_account=discord_account
    )


def user_eli():
    player = Player(
        name=Name(
            first="Eli",
            last="Orrvar",
        ),
        is_gm=False
    )

    character = Character(
        name=Name(
            first="Keir",
            last="Renwick",
        ),
        level=4,
        race_name="Human",
        class_name="Shadow Knight",
        alignment="N"
    )

    discord_account = DiscordAccount(
        user_id=3,
        username="fake_username_3"
    )

    return User(
        player=player,
        character=character,
        discord_account=discord_account
    )

def city(city_name, merchants, occupants):
    return City(
        city_id=uuid.uuid4(),
        name=city_name,
        directions=Directions(
            question="Where are the merchants?",
            answer="Here are the merchants.",
            not_found="No merchant named {{merchant_name}}."
        ),
        merchants=merchants,
        occupants=occupants
    )

def item_general_good():
    return Item(
        item_type="general_good",
        name="Widget",
        cost="100 GP",
        size=None,
        armor_bonus=None,
        armor_check_penalty=None,
        damage=None,
        crit_range=None,
        delay=None,
        max_dexterity=None,
        stats=None
    )

def item_general_jewelry():
    return Item(
        item_type="jewelry",
        name="Star Sapphire",
        cost="1000 GP",
        size=None,
        armor_bonus=None,
        armor_check_penalty=None,
        damage=None,
        crit_range=None,
        delay=None,
        max_dexterity=None,
        stats=None
    )

def item_armor_jewelry():
    return Item(
        item_type="jewelry",
        name="Khaji Da",
        cost="100000 GP",
        size=None,
        armor_bonus=None,
        armor_check_penalty=None,
        damage=None,
        crit_range=None,
        delay=None,
        max_dexterity=None,
        stats="Spell Haste IV"
    )

def item_weapon():
    return Item(
        item_type="melee_weapon",
        name="Wabbajack",
        cost="10000 GP",
        size="Large, Martial",
        armor_bonus=None,
        armor_check_penalty=None,
        damage="1D10",
        crit_range="10-20, x10",
        delay="Quick",
        max_dexterity=None,
        stats="magic resistance (5)"
    )

def item_custom_armor():
    return Item(
        item_type="armor",
        name="Customizer I",
        cost="1000 GP",
        size="Heavy",
        armor_bonus="+10",
        armor_check_penalty="-2",
        damage=None,
        crit_range=None,
        delay=None,
        max_dexterity="+5",
        stats="magic resistance (5)"
    )

def item_custom_weapon():
    return Item(
        item_type="melee_weapon",
        name="Customizer II",
        cost="1000 GP",
        size="Large, Martial",
        armor_bonus=None,
        armor_check_penalty=None,
        damage="1D10",
        crit_range="10-20, x10",
        delay="Quick",
        max_dexterity=None,
        stats="magic resistance (5)"
    )

def merchant(merchant_name, inventory, merchant_type="General Goods", sells_general_goods=InventoryType(False, None), sells_weapons=InventoryType(False, None), sells_armor=InventoryType(False, None), sells_jewelry=InventoryType(False, None)):
    return Merchant(
        merchant_id=uuid.uuid4(),
        name=merchant_name,
        merchant_type=merchant_type,
        introductions=[],
        sells_general_goods=sells_general_goods,
        sells_weapons=sells_weapons,
        sells_armor=sells_armor,
        sells_jewelry=sells_jewelry,
        inventory=inventory
    )

def merchant_general_goods_and_weapons():
    return merchant(
        merchant_name="Mr. Chant",
        inventory=[],
        sells_general_goods=InventoryType(True, "{}"),
        sells_weapons=InventoryType(True, "{}")
    )

def merchant_jewelry():
    return merchant(
        merchant_name="Ensign Chant",
        inventory=[],
        sells_jewelry=InventoryType(True, "{}")
    )

def merchant_general_goods_and_custom_armor():
    return merchant(
        merchant_name="Custom Or",
        merchant_type="Armorer",
        inventory=[
            item_custom_armor()
        ],
        sells_general_goods=InventoryType(True, "{}")
    )

def merchant_general_goods_and_custom_weapon():
    return merchant(
        merchant_name="Custom On",
        merchant_type="Weaponer",
        inventory=[
            item_custom_weapon()
        ],
        sells_general_goods=InventoryType(True, "{}")
    )

def recipe_book(build_inventory_table_use_case=Mock(), build_table_use_case=Mock(), lookup_city_use_case=Mock(), lookup_inventory_use_case=Mock(), lookup_merchant_use_case=Mock(), lookup_user_use_case=Mock(), update_user_use_case=Mock()):
    return RecipeBook(
        build_inventory_table_use_case=build_inventory_table_use_case,
        build_table_use_case=build_table_use_case,
        lookup_city_use_case=lookup_city_use_case,
        lookup_inventory_use_case=lookup_inventory_use_case,
        lookup_merchant_use_case=lookup_merchant_use_case,
        lookup_user_use_case=lookup_user_use_case,
        update_user_use_case=update_user_use_case
    )

def mock_get_user_by_user_id(user_id):
    if user_id == 1:
        return user_guy()
    if user_id == 2:
        return user_todd()
    if user_id == 3:
        return user_eli()
    else:
        return None

def mock_get_user_by_username(username):
    if username == "fake_username_1":
        return user_guy()
    if username == "fake_username_2":
        return user_todd()
    if username == "fake_username_3":
        return user_eli()
    else:
        return None

def mock_update_user_by_username(username, user):
    if username == "fake_username_1":
        return user_guy()
    if username == "fake_username_2":
        return user_todd()
    if username == "fake_username_3":
        return user_eli()
    else:
        return None

def mock_get_city_by_city_name(city_name):
    return city(city_name, merchants=[merchant_general_goods_and_weapons(), merchant_jewelry(), merchant_general_goods_and_custom_armor(), merchant_general_goods_and_custom_weapon()], occupants=[1])

def mock_get_general_goods(additional_filter):
    return [item_general_good()]

def mock_get_weapons(additional_filter):
    return [item_weapon()]

def mock_get_jewelry(additional_filter):
    return [item_armor_jewelry(), item_general_jewelry()]