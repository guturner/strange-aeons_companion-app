# EverQuest: Strange Aeons
This is the companion app for the EverQuest: Strange Aeons campaign.

## Usage
This bot only responds to direct messages.

First, hail the bot by either typing `Hail` or running the `!hail` command. This will initialize your profile.

Then, ask your GM what commands to run during gameplay; for example, you might use `!shop` to browse a merchant's inventory.

### Commands
* `!help`: Get help.
* `!hail`: Initialize your character profile.
* `!shop [city_name]`: Look for merchants in a city.
* `!shop [city_name] [merchant_name]`: Browse a merchant's inventory.
* `!whoami`: Retrieve your character profile.

### How Does the Bot Work?
There is not yet an administrative user interface.
First, the admin manually populates a Mongo database according to 
the [schemas below](#schema) (or use the [provided sample data](#sample-data)).
Then, the admin manually makes any changes to the data (for example, changing `user.character`, `user.discord`,
and `user.player`).

Next, each player (including the GM) should `!hail` the bot. This upserts the player in the database by associating their
Discord user ID with their Discord username. If the player's Discord username is not found in the database they will be
presented with an error.

Then the bot is ready to be used. See [usage](#usage) or [commands](#commands) above.

## Development
Please read CONTRIBUTING.md before continuing.

### Setup
Manage your virtual environment using Poetry.

In PyCharm:
* Go to 'Settings'.
* Go to 'Project: strange-aeons'
* Go to 'Python Interpreter'
* Click Add 'Interpreter' > 'Add Local Interpreter...'
* On the 'Generate New' tab, select 'Type: Poetry'
  * Poetry will read the pyproject.toml file to install dependencies.

Run `poetry install`.

### Database
The EverQuest: Strange Aeons companion app requires a MongoDB database.
As there is not yet an administrative UI, the admin must manually populate the database with data according to
the schema below:

#### Schema

* `users` collection:
  * ```json
    {
      "userId" : [null, NumberLong],
        "player" : {
            "name" : {
                "first" : [String],
                "last" : [String]
            },
            "gm" : [Boolean]
        },
        "discord" : {
            "username" : [String]
        },
        "character" : { // if "gm" is true, then "character" is null
            "name" : {
                "first" : [String],
                "last" : [String]
            },
            "race" : [String],
            "class" : [String],
            "level" : [NumberInt],
            "alignment" : [String]
        }
    }
    ```
    
* `cities` collection:
  * ```json
    {
      "cityId" : [UUID],
      "name" : [String],
      "merchants" : [
          {
              "merchantId" : [UUID],
              "name" : [String],
              "type" : [String],
              "introductions" : [
                  [String]
              ],
              "sellsArmor" : {
                  "enabled" : [Boolean],
                  "filter" : [null, String]
              },
              "sellsGeneralGoods" : {
                  "enabled" : [Boolean],
                  "filter" : [null, String]
              },
              "sellsJewelry" : {
                  "enabled" : [Boolean],
                  "filter" : [null, String]
              },
              "sellsWeapons" : {
                  "enabled" : [Boolean],
                  "filter" : [null, String]
              },
              "inventory" : [
                  // see "inventories" below
              ]
          }
      ],
      "occupants" : [
          [NumberLong]
      ],
      "directions" : {
          "question" : [String],
          "answer" : [String],
          "notFound" : [String]
      }
    }
    ```
    
* `inventories` collection:
  * ```json
    {
      "type" : [String],
      "masterwork" : [Boolean],
      "name" : [String],
      "armor_bonus" : [null, String],
      "armor_check_penalty" : [null, String],
      "damage" : [null, String],
      "crit_range" : [null, String],
      "delay" : [null, String],
      "max_dexterity" : [null, String],
      "size" : [null, String],
      "stats" : [null, String],
      "cost" : [String]
    }
    ```
    
#### Sample Data
See the `sample_data/mongodb` folder for sample data that you can load into MongoDB.
    
### Testing
```
pip install pytest
pytest
```

#### End-to-End Tests
The EverQuest: Strange Aeons Companion App uses [Testcontainers](https://testcontainers.com/) for end-to-end (E2E) integration
testing. Ensure you have Docker Desktop running locally.

E2E tests can be found under `tests/*e2e.py`