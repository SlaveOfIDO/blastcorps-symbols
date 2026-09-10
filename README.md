# BlastCorps symbols

Needed for the recomp project.

## Requirements


Put your baserom.us.v11.z64 into the root folder.

```
git submodule update --init --recursive
virtualenv .env
. .env/bin/activate
pip install -r lib/blastcorps/requirements.txt
pip install -r requirements.txt
```

## Build

```
make
```
