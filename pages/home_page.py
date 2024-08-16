import curses

def show_home_page(stdscr, articles, selected_index, current_page, total_pages, filter_query):
    stdscr.clear()
    height, width = stdscr.getmaxyx()

    # Filtreleme
    filtered_articles = [s for s in articles if filter_query.lower() in s.title.lower()]

    # Listeyi ekrana yazma
    for i, article in enumerate(filtered_articles):
        line = f"{i + 1}. {article.title} | ({article.link})"
        if len(line) > width - 1:
            line = line[:width-4] + '...'  # Kısaltma
        try:
            if i == selected_index:
                stdscr.attron(curses.A_REVERSE)
            stdscr.addstr(i, 0, line)
            if i == selected_index:
                stdscr.attroff(curses.A_REVERSE)
        except curses.error:
            continue

    # Filtre bilgisi gösterme
    if filter_query:
        filter_info = f"Filter: {filter_query} (Press Space to clear filter)"
        stdscr.addstr(height - 3, 0, filter_info[:width])

    # Seçili öğe hakkında bilgi
    if filtered_articles:
        info_line = f"Selected: {filtered_articles[selected_index].title}" if selected_index < len(filtered_articles) else "Selected: None"
        stdscr.addstr(height - 2, 0, info_line[:width])

    # Footer bilgileri
    footer_info = f"Page {current_page}/{total_pages} | Press 'h' for Help"
    stdscr.addstr(height - 1, 0, footer_info[:width])

    stdscr.refresh()
