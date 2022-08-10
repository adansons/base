import click


def CatchAllExceptions(cls, handler):
    """
    Function to override the default exception handler of click.
    With thanks to this Stack Overflow answer:
    https://stackoverflow.com/questions/52213375/python-click-exception-handling-under-setuptools

    Parameters
    ----------
    cls : The class that the handler is being applied e.g. click.Command
    handler : The handler function to print the error message

    Returns
    -------
    Cls : The new class itself with the handler applied
    """

    class Cls(cls):
        _original_args = None

        def make_context(self, info_name, args, parent=None, **extra):

            # grab the original command line arguments
            self._original_args = " ".join(args)

            try:
                return super(Cls, self).make_context(
                    info_name, args, parent=parent, **extra
                )
            except Exception as exc:
                # call the handler
                handler(self, info_name, exc)
                # let the user see the original error
                raise

        def invoke(self, ctx):
            try:
                return super(Cls, self).invoke(ctx)
            except Exception as exc:
                # call the handler
                handler(self, ctx.info_name, exc)

                # let the user see the original error
                raise

    return Cls


def search_export_exception(cmd, info_name, exc):
    """
    Function to handle the exception for "base search --export" command.

    Parameters
    ----------
    cmd: The command that user is trying to run
    info_name: The name of the exception
    exc: The exception message

    Returns
    -------
    None
    """
    # send error info to rollbar, etc, here
    if ("'--export' requires an argument" or "'--e' requires an argument") in str(exc):
        click.echo("You can specify ‘json’ or ‘csv’ as export-file-type")
    elif ("'--output' requires an argument" or "'--o' requires an argument") in str(
        exc
    ):
        click.echo("You can specify the output file name")
    else:
        click.echo("Raised error: {}".format(exc))
