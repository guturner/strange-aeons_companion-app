# ---------------------------------------------------------------------------
# Filtering
# ---------------------------------------------------------------------------

def filter_choices(choices: list[str], typed: str, max_results: int = 25) -> list[str]:
    """
    Filter a flat list of strings by case-insensitive substring match.
    Used for city autocomplete.
    """
    typed = typed.strip().lower()
    if not typed:
        return choices[:max_results]
    return [c for c in choices if typed in c.lower()][:max_results]


def filter_labelled_choices(
        choices: list[tuple[str, str]], typed: str, max_results: int = 25
) -> dict[str, str]:
    """
    Filter a list of (display_label, submitted_value) tuples by substring match
    against the display label, then return as {label: value} dict ready for
    interaction.response.send_autocomplete().

    Matching is done against the label (which includes the description suffix)
    so typing "bow" matches "Eldin Trueshot — Bowyer".
    """
    typed = typed.strip().lower()
    matched = (
        (label, value)
        for label, value in choices
        if not typed or typed in label.lower()
    )
    return {label: value for label, value in list(matched)[:max_results]}


# ---------------------------------------------------------------------------
# Choice builders
# ---------------------------------------------------------------------------

def city_choices_for_user(recipe_book, discord_user_id: int) -> list[str]:
    """
    Returns city names the given Discord user is an occupant of.
    Used by the 'city' parameter autocomplete.
    """
    cities = recipe_book.build_inventory_table.lookup_cities_by_discord_user_id(discord_user_id)
    return [city.name for city in cities] if cities else []


def merchant_choices_for_city(
        recipe_book, city_name: str
) -> list[tuple[str, str]]:
    """
    Returns (display_label, submitted_value) tuples for each merchant in the city.

    Display label:    "Eldin Trueshot (Bowyer)"
    Submitted value:  "Eldin Trueshot"

    The description suffix lets players identify the right merchant at a glance
    without having to memorise names. Filtering works against the full label so
    typing a description word (e.g. "spell", "jewel") also narrows the list.

    Returns [] if city_name is empty or the city is not found.
    """
    if not city_name or not city_name.strip():
        return []
    city = recipe_book.lookup_city.lookup_city_by_city_name(city_name)
    if city is None or not city.merchants:
        return []
    return [
        (f"{merchant.name} ({merchant.description})", merchant.name)
        for merchant in city.merchants
    ]
