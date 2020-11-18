# pyopg

This project supplies the OPG Python3 common library package `pyopg`.

## Installion

Minimum *Python version 3.6* is required, as long as latest [PyPA packaging tools](https://packaging.python.org/tutorials/installing-packages/). For instance, we can install them in the [user site packages directory](https://docs.python.org/zh-cn/3/installing/index.html#install-packages-just-for-the-current-user), under latest *Centos 7.x*:

```bash
sudo yum-config-manager --enable updates
sudo yum makecache
sudo yum -y install python3-pip
pip3 install --user -U pip setuptools wheel
```

After that, install this package in [editable mode](https://pip.pypa.io/en/stable/reference/pip_install/#local-project-installs):
```bash
mkdir -p $(python3 -m site --user-base) \
&& cd $(python3 -m site --user-base) \
&& pip3 install --user -U -e "git+https://github.com/opgcn/pyopg.git#egg=pyopg"
```

