# Kamu client library for Python

## Install

```bash
pip install kamu
```

## Use
Quick start:

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
