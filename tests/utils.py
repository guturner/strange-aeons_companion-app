import uuid
from unittest.mock import Mock

from models.city import City, Directions, Merchant
from models.item import Item, SellsItemType, ItemType
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

def gm_not_registered():
    player = Player(
        name=Name(
            first="The",
            last="GM",
        ),
        is_gm=True
    )

    discord_account = DiscordAccount(
        user_id=None,
        username="fake_username_4"
    )

    return User(
        player=player,
        character=None,
        discord_account=discord_account
    )

def player_not_registered():
    player = Player(
        name=Name(
            first="Not",
            last="Registered",
        ),
        is_gm=False
    )

    character = Character(
        name=Name(
            first="The",
            last="Hero",
        ),
        level=4,
        race_name="Human",
        class_name="Warrior",
        alignment="NG"
    )

    discord_account = DiscordAccount(
        user_id=None,
        username="fake_username_5"
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
        stats=None,
        song_instrument=None,
        spell_level=None,
        spell_description=None
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
        stats=None,
        song_instrument=None,
        spell_level=None,
        spell_description=None
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
        stats="Spell Haste IV",
        song_instrument=None,
        spell_level=None,
        spell_description=None
    )

def item_song():
    return Item(
        item_type="song",
        name="Kumbaya",
        cost="1000 GP",
        size=None,
        armor_bonus=None,
        armor_check_penalty=None,
        damage=None,
        crit_range=None,
        delay=None,
        max_dexterity=None,
        stats=None,
        song_instrument="String",
        spell_level="Brd 30",
        spell_description="Peace & Love!"
    )

def item_spell():
    return Item(
        item_type="spell",
        name="Kamehameha",
        cost="1000 GP",
        size=None,
        armor_bonus=None,
        armor_check_penalty=None,
        damage=None,
        crit_range=None,
        delay=None,
        max_dexterity=None,
        stats=None,
        song_instrument=None,
        spell_level="Mag 30",
        spell_description="It's over 9000!"
    )

def item_melee_weapon():
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
        stats="magic resistance (5)",
        song_instrument=None,
        spell_level=None,
        spell_description=None
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
        stats="magic resistance (5)",
        song_instrument=None,
        spell_level=None,
        spell_description=None
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
        stats="magic resistance (5)",
        song_instrument=None,
        spell_level=None,
        spell_description=None
    )

def item_instrument():
    return Item(
        item_type="instrument",
        name="Lucille",
        cost="10000 GP",
        size=None,
        armor_bonus=None,
        armor_check_penalty=None,
        damage=None,
        crit_range=None,
        delay=None,
        max_dexterity=None,
        stats="+100 Play String Instruments",
        song_instrument=None,
        spell_level=None,
        spell_description=None
    )

def item_misc():
    return Item(
        item_type="unknown_item_type",
        name="Doohickey",
        cost="250 GP",
        size=None,
        armor_bonus=None,
        armor_check_penalty=None,
        damage=None,
        crit_range=None,
        delay=None,
        max_dexterity=None,
        song_instrument=None,
        stats="+1 Knowledge (engineering)",
        spell_level=None,
        spell_description=None
    )

def merchant(name="Merchant", description="General Goods", sells_item_types=None, custom_items=None, number_of_table_rows=8):
    if sells_item_types is None:
        sells_item_types = []
    return Merchant(
        merchant_id=uuid.uuid4(),
        name=name,
        description=description,
        sells_item_types=sells_item_types if sells_item_types is not None else [],
        custom_items=custom_items if custom_items is not None else [],
        number_of_table_rows=number_of_table_rows,
    )

def merchant_general_goods_and_weapons():
    return merchant(
        name="Mr. Chant",
        sells_item_types=[SellsItemType("general_good", None), SellsItemType("melee_weapon", None)]
    )

def merchant_jewelry():
    return merchant(
        name="Ensign Chant",
        description="Jeweler",
        sells_item_types=[SellsItemType("jewelry", None)]
    )

def merchant_general_goods_and_custom_armor():
    return merchant(
        name="Custom Or",
        description="Armorer",
        sells_item_types=[SellsItemType("general_good", None)],
        custom_items=[item_custom_armor()]
    )

def merchant_general_goods_and_custom_weapon():
    return merchant(
        name="Custom On",
        description="Weaponer",
        sells_item_types=[SellsItemType("general_good", None)],
        custom_items=[item_custom_weapon()]
    )

def merchant_songs():
    return merchant(
        name="Song Mann",
        description="Songs",
        sells_item_types=[SellsItemType("song", None)]
    )

def merchant_spells():
    return merchant(
        name="Spell Mann",
        description="Spells",
        sells_item_types=[SellsItemType("spell", None)]
    )

def recipe_book(build_inventory_table_use_case=Mock(), build_table_use_case=Mock(), lookup_city_use_case=Mock(), lookup_inventory_use_case=Mock(), lookup_merchant_use_case=Mock(), user_use_case=Mock()):
    return RecipeBook(
        build_inventory_table_use_case=build_inventory_table_use_case,
        build_table_use_case=build_table_use_case,
        lookup_city_use_case=lookup_city_use_case,
        lookup_inventory_use_case=lookup_inventory_use_case,
        lookup_merchant_use_case=lookup_merchant_use_case,
        user_use_cases=user_use_case
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
    elif username == "fake_username_2":
        return user_todd()
    elif username == "fake_username_3":
        return user_eli()
    elif username == "fake_username_4":
        return gm_not_registered()
    elif username == "fake_username_5":
        return player_not_registered()
    else:
        return None

def mock_update_user_by_username(username, user):
    if username == "fake_username_1":
        return user_guy()
    elif username == "fake_username_2":
        return user_todd()
    elif username == "fake_username_3":
        return user_eli()
    elif username == "fake_username_4":
        return gm_not_registered()
    elif username == "fake_username_5":
        return player_not_registered()
    else:
        return None

def mock_get_city_by_city_name(city_name):
    return city(city_name, merchants=[merchant_general_goods_and_weapons(), merchant_jewelry(), merchant_general_goods_and_custom_armor(), merchant_general_goods_and_custom_weapon(), merchant_songs(), merchant_spells()], occupants=[1])