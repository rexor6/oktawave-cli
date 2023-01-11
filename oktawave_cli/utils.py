import click
import logging
import time
import progressbar

logger = logging.getLogger(__name__)

def pretty_print_output(columns_names, data):
    """TODO: Docstring for .

    :param columns: TODO
    :returns: TODO

    """
    all_data = [columns_names]
    for row in data:
        words = [str(word) for word in row]
        all_data.append(words)
    col_width = max(len(word) for row in all_data for word in row) + 4
    i = 0
    for row in all_data:
        output = "".join(word.ljust(col_width) for word in row)
        click.echo(output)
        i+=1

def pretty_print_rows(rows_dict, obj):
    """TODO: Docstring for pretty_print_rowsj.

    :param row_dicts: Dict with mapping displayed name to obj attribute
    :param obj: object instance
    :returns: None

    """
    if obj:
        for row_name, attr in rows_dict.items():
            attr_value = getattr(obj, attr)
            row = f"{row_name}: {attr_value}"
            click.echo(row)
    else:
        raise Exception

#TODO - sprawdzic wersje progressbar, i ponizsze metody w dokumentacji.
# Czy w najnowszych wersjach nie maja dodakotwych parametrow.
def show_progress_from_ticket(ticket, ticket_helper):
    """ Print progressbar for given ticket. """
    ticket_id = ticket.id
    ticket = ticket_helper.get_ticket(ticket_id)
    with progressbar.ProgressBar(max_value=100) as progress_bar:
        while ticket.status.id == 135 and ticket.progress != 100:
            time.sleep(2)
            ticket = ticket_helper.get_ticket(ticket_id)
            if ticket:
                progress_bar.update(ticket.progress)
            else:
                progress_bar.finish(dirty=True)
                break

def ocs_size_helper(size, human_readable=True, is_byte=True, unit=None):
    """TODO: Docstring for size_to_human_readable.
    :returns: TODO

    """
    result_size = size
    if human_readable:
        if size < 1024:
            result_size = f"{size}B"
        elif 1024 <= size < 1024*1024:
            value = size/1024
            result_size = f"{value:.2f}KB"
        elif 1024*1024 <= size < 1024*1024*1024:
            value = size/(1024*1024)
            result_size = f"{value:.2f}MB"
        elif 1024*1024*1024 < size:
            value = size/(1024*1024*1024)
            result_size = f"{value:.2f}GB"
    return result_size
