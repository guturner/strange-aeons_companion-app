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
* ...test only the cogs
  * The only way for a user to interact with the system is to go through the cogs; therefore, we should only test the cogs. As cogs combine and reuse use cases their individual parts will each be tested.
  * Each test should test a pathway the user can take through the system. By testing all pathways, all code in the system will be tested organically.
* ...follow best practices
  * Instead of guessing, look up and use best practices for Python, Nextcord, Discord Bots, etc.
  * This includes keeping secrets out of version control. Keep .gitignore updated and only put secrets and passwords in `.env.local` (never `.env`).