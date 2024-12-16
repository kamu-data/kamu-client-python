# Developer Instructions

## Initial Setup
Normal `virtualenv` setup:
```sh
python -m venv .venv
source .venv/bin/activate
pip install --upgrade -r requirements.txt
pip install -e .
```

### NixOS
To initialize `virtualenv` instead run:
```sh
nix-shell -p python3 --command "python -m venv .venv --copies"
```

After installing all dependencies patch the binaries with:
```sh
nix shell github:GuillaumeDesforges/fix-python
fix-python --venv .venv
```

See [NixOS Wiki](https://wiki.nixos.org/wiki/Python#Running_compiled_libraries) for details.
