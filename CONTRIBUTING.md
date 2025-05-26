# Contributing to the EverQuest: Strange Aeons Companion App
Thank you for contributing to the Strange Aeons Companion App! Please take a moment to read this guide and do your best
to adhere to the [Driving Principles](#driving-principles) below.

## Driving Principles
As a contributor to the Strange Aeons Companion App, I promise to...

* ...respect the [Dependency Rule](https://medium.com/@aboutcoding/clean-architecture-the-essence-of-the-dependency-rule-969f1e8417f6)
  * User > Cog > Use Case < DAO < Database
  * Simple business logic (array filtering, attribute concatenation, etc.) can be performed by domain model classes; however most business logic should be exposed via use cases.
  * Business logic (in use cases and domain models) should only change if the needs of the application change. How these processes accomplish their goal should not depend on how information is getting in or out of the system; therefore, no business logic should exist in data access objects (DAOs) or cogs.
* ...follow the recipe book
  * Given a sufficiently-thick recipe book you can build anything.
  * Anything that a user can do should be in the recipe book. The recipes in the recipe book are use cases.
  * Recipes should be built from other recipes (complex use cases).
* ...speak in results, not exceptions
  * Because the system is driven by user input, exceptions are simply results we haven't yet anticipated.
  * Use cases should return result objects indicating success or failure (see `results.py`). Complex use cases should match on the type of these results to implement branching logic:
    * ```python 
        lookup_merchant_result = self.__lookup_merchant_use_case.lookup_merchant_by_city_name_and_merchant_name(city_name=city_name, merchant_name=merchant_name)
        match lookup_merchant_result:
            case LookupMerchantSuccess(merchant=found_merchant):
                # TODO
            case LookupMerchantFailure(city_name=city_name, merchant_name=merchant_name)
                # TODO
* ...test only the cogs
  * The only way for a user to interact with the system is to go through the cogs; therefore, we should only test the cogs. As cogs combine and reuse use cases their individual parts will each be tested.
  * Each test should test a pathway the user can take through the system. By testing all pathways, all code in the system will be tested organically.
* ...follow best practices
  * Instead of guessing, look up and use best practices for Python, Nextcord, Discord Bots, etc.
  * This includes keeping secrets out of version control. Keep .gitignore updated and only put secrets and passwords in `.env.local` (never `.env`).