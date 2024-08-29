def is_running_in_jupyter():
    try:
        from IPython import get_ipython

        if get_ipython() is not None:
            return True
        return False
    except ImportError:
        return False
