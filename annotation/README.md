# 环境设置

请确保您的环境中已安装以下软件包：

```bash
pip install streamlit
```

**推荐使用 Firefox 浏览器以避免兼容性问题**，可以通过以下链接下载并安装 Firefox 浏览器：[Mozilla Firefox 官方网站](https://www.firefox.com.cn/)。Edge 和 Chrome 浏览器在渲染较大的 PDF 文件时会遇到问题。

# 准备待标注文件

在开始之前，请在当前工作目录中创建一个名为 `data` 的文件夹，并按以下结构组织您的文件：(具体data文件在项目的google drive中)

```
data
├── Math
│   ├── BMT
│   ├── COMC
│   └── ...
├── Physics
└── ...
```

这将确保程序能正确地定位并组织您的文件。

# 启动应用

设置完成后，在终端中运行以下命令以启动应用：

```bash
streamlit run main.py
```

所有标注的输出以 ./学科名/竞赛简称/文件名称/日期标志.json  存储在 ./output/ 文件夹。
