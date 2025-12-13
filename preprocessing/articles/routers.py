class NewsAggregatorRouter:
    """
    A router to control database operations for the NewsArticle model.
    Routes NewsArticle queries to the news_aggregator database,
    and all other queries to the default database.
    """

    def db_for_read(self, model, **hints):
        """
        Attempts to read NewsArticle instances go to news_aggregator database.
        """
        if model._meta.app_label == 'articles' and model.__name__ == 'NewsArticle':
            return 'news_aggregator'
        return 'default'

    def db_for_write(self, model, **hints):
        """
        Attempts to write NewsArticle instances go to news_aggregator database.
        (But NewsArticle is managed=False, so no writes should happen)
        """
        if model._meta.app_label == 'articles' and model.__name__ == 'NewsArticle':
            return 'news_aggregator'
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations between objects in the same database.
        """
        db_set = {'default', 'news_aggregator'}
        if obj1._state.db in db_set and obj2._state.db in db_set:
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Don't migrate NewsArticle to any database (it's managed=False).
        Make sure the articles app's migrations only go to the default database.
        """
        if app_label == 'articles':
            if model_name == 'newsarticle':
                # Never migrate NewsArticle (managed=False)
                return False
            # Other models in articles app go to default database
            return db == 'default'
        # Other apps go to default database
        return db == 'default'
