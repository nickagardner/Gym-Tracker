from scrape_and_store import get_counts, store_counts


def main(event_data, context):
    """
    Main function wrapper (required by Google Cloud Run)
    :param event_data: Required parameter for Google Cloud Run
    :param context: Required parameter for Google Cloud Run
    :return: None
    """
    counts = get_counts()
    store_counts(counts)
