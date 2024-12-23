<div align="center">

<img alt="Kamu: Planet-scale data pipeline" src="https://raw.githubusercontent.com/kamu-data/kamu-client-python/refs/heads/master/docs/readme-files/kamu_logo.png" width=300/>

[Website] | [Docs] | [Demo] | [Tutorials] | [Examples] | [FAQ] | [Chat]

[![Crates.io](https://img.shields.io/pypi/v/kamu?logo=python&logoColor=white&style=for-the-badge
)](https://pypi.org/project/kamu/)
[![Docs](https://img.shields.io/static/v1?logo=gitbook&logoColor=white&label=&message=Docs&color=gray&style=for-the-badge)](https://docs.kamu.dev/)
[![Chat](https://shields.io/discord/898726370199359498?style=for-the-badge&logo=discord&label=Discord)](https://discord.gg/nU6TXRQNXC)


</p>
</div>

## About
Python client library for Kamu.

Start with [`kamu-cli`](https://github.com/kamu-data/kamu-cli) repo if you are not familiar with the project.

## Installing
Install the library:
```bash
pip install kamu
```

Consider installing with extra features:
```bash
pip install kamu[jupyter-autoviz,jupyter-sql,spark]
```

### Extras
- `jupyter-autoviz`- Jupyter auto-viz for Pandas data frames
- `jupyter-sql` - Jupyter `%%sql` cell magic
- `spark` - extra libraries temporarily required to communicate with Spark engine


## Using in plain Python scripts
```python
import kamu

con = kamu.connect("grpc+tls://node.demo.kamu.dev:50050")

# Executes query on the node and returns result as Pandas DataFrame
df = con.query(
    """
    select
        event_time, open, close, volume
    from 'kamu/co.alphavantage.tickers.daily.spy'
    where from_symbol = 'spy' and to_symbol = 'usd'
    order by event_time
    """
)

print(df)
```

By default the connection will use `DataFusion` engine with Postgres-like SQL dialect.

The client library is based on modern [ADBC](https://arrow.apache.org/docs/format/ADBC.html) standard and the underlying connection can be used directly with other libraries supporting ADBC data sources:

```python
import kamu
import pandas

con = kamu.connect("grpc+tls://node.demo.kamu.dev:50050")

df = pandas.read_sql_query(
    "select 1 as x",
    con.as_adbc(),
)
```


## Using in Jupyter
Load the extension in your notebook:

```python
%load_ext kamu
```

Create connection:

```python
con = kamu.connect("grpc+tls://node.demo.kamu.dev:50050")
```

Extension provides a convenience `%%sql` magic:

```sql
%%sql
select
    event_time, open, close, volume
from 'kamu/co.alphavantage.tickers.daily.spy'
where from_symbol = 'spy' and to_symbol = 'usd'
order by event_time
```

The above is equivalent to:

```python
con.query("...")
```

To save the query result into a variable use:
```sql
%%sql -o df
select * from x
```

The above is equivalent to:

```python
df = con.query("...")
df
```

To silence the output add `-q`:
```sql
%%sql -o df -q
select * from x
```

The `kamu` extension automatically registers [`autovizwidget`](https://github.com/jupyter-incubator/sparkmagic) to offer some options to visualize your data frames.

![Jupyter extension](https://raw.githubusercontent.com/kamu-data/kamu-client-python/refs/heads/master/docs/readme-files/jupyter.png)


## Using with Spark
You can specify a different engine when connecting:

```python
con = kamu.connect("http://livy:8888", engine="spark")
```

Note that currently Spark connectivity relies on Livy HTTP gateway but in future will be unified under ADBC.

You can also provide extra configuration to the connection:

```python
con = kamu.connect(
    "http://livy:8888",
    engine="spark",
    connection_params=dict(
        driver_memory="1000m",
        executor_memory="2000m",
    ),
)
```


[Tutorials]: https://docs.kamu.dev/cli/learn/learning-materials/
[Examples]: https://docs.kamu.dev/cli/learn/examples/
[Docs]: https://docs.kamu.dev/welcome/
[Demo]: https://demo.kamu.dev/
[FAQ]: https://docs.kamu.dev/cli/get-started/faq/
[Chat]: https://discord.gg/nU6TXRQNXC
[Contributing]: https://docs.kamu.dev/contrib/
[Developer Guide]: ./DEVELOPER.md
[License]: https://docs.kamu.dev/contrib/license/
[Website]: https://kamu.dev
