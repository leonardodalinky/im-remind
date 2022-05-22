# im-remind

## Install

```
pip install im-remind
```

## Usage

See the help page.

TL;DR:

```
im-remind -h
```

Or:
```
python -m im-remind
```

## Config file

Config file can simplify the usage of im-remind.

A template config file is provided in the `example_config.yaml`.

```yaml
qq:
  token: <qq-token>
  api-path: <qq-api-path>
  # session is used for simplify the command-line
  session:
    qq: <your-qq>
    group: <your-qq-group>
tg:
  token: <tg-token>
  api-path: <tg-api-path>
```

Replace the appropriate fields with your own values.

**Then, move the config file to `~/.im_remind.yaml` or `~/.config/im_remind.yaml`**

## Examples

```
im-remind qq "JOJO，我不想再做人了！！"
```
