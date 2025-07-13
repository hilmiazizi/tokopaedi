import logging

def setup_custom_logging():
    SEARCH_LEVEL = 25
    DETAIL_LEVEL = 26
    REVIEWS_LEVEL = 27

    logging.addLevelName(SEARCH_LEVEL, "SEARCH")
    logging.addLevelName(DETAIL_LEVEL, "DETAIL")
    logging.addLevelName(REVIEWS_LEVEL, "REVIEW")

    class CustomLogger(logging.Logger):
        def search(self, message, *args, **kwargs):
            if self.isEnabledFor(SEARCH_LEVEL):
                self._log(SEARCH_LEVEL, message, args, **kwargs)
        
        def detail(self, message, *args, **kwargs):
            if self.isEnabledFor(DETAIL_LEVEL):
                self._log(DETAIL_LEVEL, message, args, **kwargs)
        
        def reviews(self, message, *args, **kwargs):
            if self.isEnabledFor(REVIEWS_LEVEL):
                self._log(REVIEWS_LEVEL, message, args, **kwargs)

    logging.setLoggerClass(CustomLogger)

    logging.basicConfig(
        level=SEARCH_LEVEL,
        format="{asctime} - {levelname} - {message}",
        style="{",
        datefmt="%Y-%m-%d %H:%M",
    )

    return logging.getLogger(__name__)