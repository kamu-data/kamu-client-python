# Kamu client library for Python

## Installation

```bash
pip install kamu
```

## Use
Reading data into Pandas data frame:

```python
import kamu
import pandas

con = kamu.connect("grpc+tls://node.demo.kamu.dev:50050")

df = pandas.read_sql_query(
    r"""
    select
        *
    from 'kamu/net.rocketpool.reth.tokens-minted'
    limit 10
    """,
    con.as_adbc()
)

print(df)
```
