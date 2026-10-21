"""Data layer: values only, behind small repository classes.

Services read data through repositories, never from the dicts directly, so the
in-memory store can later be swapped for a database or an external API.
"""