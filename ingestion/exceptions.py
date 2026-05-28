class BulkLoaderError(Exception):
    """
    Raised the Bulk Loader function is called but error raised.
    """
    pass

class S3UtilsError(Exception):
    """
    Raised when the S3 utils function is called but error raised.
    """
    pass


class RedshiftUtilsError(Exception):
    """"
    Raised when the Redshift utils function is called but error raised.
    """