"""Product-specific text prompts."""

from .text_input import show_text_popup


def show_feed_filter(stdscr, current_filter=""):
    """Open the story-filter popup."""
    return show_filter_popup(
        stdscr,
        "Filter stories",
        (
            'Example: python title:"open source" -site:example.com',
            "Fields: title: site: by: points:>=100 replies:>20",
            "State: is:visited is:unvisited is:fav is:unfav",
            "       is:read is:unread is:later is:unlater",
            "Prefix any term with - to exclude",
        ),
        current_filter,
    )


def show_record_filter(stdscr, title, descriptions, current_filter=""):
    """Open a filter popup for a management table."""
    return show_filter_popup(
        stdscr,
        title,
        descriptions,
        current_filter,
    )


def show_filter_popup(stdscr, title, descriptions, current_filter=""):
    """Edit a filter without replacing the current page."""
    return show_text_popup(
        stdscr,
        title,
        descriptions,
        current_filter,
        prompt_label="Filter",
        confirm_label="apply",
    )


def show_filter_name(stdscr, current_name=""):
    """Ask for a reusable filter name."""
    return show_text_popup(
        stdscr,
        "Save filter",
        (
            "Choose a short unique name.",
            "Using an existing custom name updates that saved filter.",
        ),
        current_name,
        prompt_label="Name",
        confirm_label="save",
    )
