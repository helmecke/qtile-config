# qtile-config

## Getting Started

I manage _qtile-config_ using [(GNU Stow)](http://www.gnu.org/software/stow/).

Install _qtile-config_ by cloning the git repository. I recommand using [ghq](https://github.com/x-motemen/ghq).

```bash
ghq get https://github.com/helmecke/qtile-config.git

# or

git clone https://github.com/helmecke/qtile-config.git ~/.qtile-config
```

You can now symlink any configurations you wish to use:

```bash
# Enter repository folder
cd $(ghq list -p | grep helmecke/qtile-config)

#or

cd ~/.qtile-config

# Symlink qtile config
stow -t ~ qtile

# Remove qtile symlink
stow -t ~ -D qtile
```
