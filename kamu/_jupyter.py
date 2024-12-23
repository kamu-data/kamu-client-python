from IPython.core import magic_arguments
from IPython.core.magic import Magics, cell_magic, magics_class, needs_local_scope

from ._connection import KamuConnection


@magics_class
class KamuMagics(Magics):
    """
    Kamu magics for Jupyter / IPython.
    """

    @cell_magic
    @needs_local_scope
    @magic_arguments.magic_arguments()
    @magic_arguments.argument(
        "-c",
        "--connection",
        type=str,
        default="con",
        help="Variable name that holds KamuConnection",
    )
    @magic_arguments.argument(
        "-o",
        "--output",
        type=str,
        default=None,
        help="If present, query will be stored in variable of this name.",
    )
    @magic_arguments.argument(
        "-q",
        "--quiet",
        type=bool,
        default=False,
        const=True,
        nargs="?",
        help="Execute query without returning the result dataframe.",
    )
    @magic_arguments.argument(
        "-n",
        "--max-rows",
        type=int,
        default=None,
        help="Maximum number of rows that will be pulled back from the server for SQL queries",
    )
    def sql(self, line, cell, local_ns=None):
        args = magic_arguments.parse_argstring(self.sql, line)
        print("Args:", args)

        connection = local_ns.get(args.connection)
        if not connection:
            raise ValueError(
                "KamuConnection not found, please provide -c <connection> argument"
            )
        if not isinstance(connection, KamuConnection):
            raise ValueError(
                f"Expected instance of KamuConnection, but found: {repr(connection)}"
            )

        sql = cell.strip()

        print("SQL:", sql)
        print("Conn:", connection)

        df = connection.query(sql)

        if args.output:
            local_ns[args.output] = df
        elif not args.quiet:
            return df
