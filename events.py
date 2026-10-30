from plugins.hydra import utils


def distribute_articles(**kwargs):
    """
    Copies the article into every journal linked to its own and returns the
    result for each journal.
    """
    article = kwargs.get('article')
    journals = utils.get_linked_journals(article)
    if not journals:
        return []
    return utils.distribute_articles(article, journals)
