# ![PYOPG](pyopg.png)

This project supplies the OPG common Python3 base library package `pyopg`.

## Installion

Python *3.6+* is required, as long as latest [PyPA packaging tools](https://packaging.python.org/tutorials/installing-packages/). For instance, we can install them in the [user site packages directory](https://docs.python.org/zh-cn/3/installing/index.html#install-packages-just-for-the-current-user), under latest *Centos 7.x*:

```bash
sudo yum-config-manager --enable updates
sudo yum makecache
sudo yum -y install python3-pip
pip3 install --user -U pip setuptools wheel
```

After that, install or update this package in the [editable mode](https://pip.pypa.io/en/stable/reference/pip_install/#local-project-installs):
```bash
mkdir -p $(python3 -m site --user-base) \
&& cd $(python3 -m site --user-base) \
&& pip3 install --user -U -e "git+https://github.com/opgcn/pyopg.git#egg=pyopg"
```

Finally, you can test some package usage, for example:
```bash
python3 -m pyopg.color
```

## Documention

To generate HTML *pydoc* files locally:

```bash
mkdir $(python3 -m site --user-base)/docs
&& cd $(python3 -m site --user-base)/docs
&& pydoc3 -w $(pydoc3 -k pyopg | cut -d' ' -f1)
&& ls -al
```
