![Banner of CJK-character-count](resource/banner.png)

# CJK-character-count

This is a program that counts the amount of CJK characters based on Unicode ranges and Chinese encoding standards.  
此软件以统一码（Unicode）区块与汉字编码标准统计字体内的汉字数量。

**[Download here. 在此下载。](https://github.com/NightFurySL2001/CJK-character-count/releases)**

---

## How this works 如何运作

This program accepts 1 font file at a time (OpenType/TrueType single font file currently) and extract the character list from `cmap` table, which records the Unicode (base-10)-glyph shape for a font. The list is then parsed to count the amount of characters based on Unicode ranges (comparing the hexadecimal range) and Chinese encoding standards (given a list of .txt files with the actual character in it).  
此软件可计算一套字体内的汉字数量，目前只限 OpenType/TrueType 单字体文件而已。导入字体时，软件将从`cmap`表（储存字体内（十进制）统一码与字符对应的表）提取汉字列表，然后以该列表依统一码区块（比对十六进制码位）与汉字编码标准（比对 .txt 文件）统计字体内的汉字数量。

## Currently supported font formats 支援的字体格式

Major font formats are supported in this software.  
主要字体格式本软件皆都支援。

` *.ttf, *.otf, *.woff, *.woff2, *.ttc, *.otc`

## Software interface 软件界面

`main.exe` is the English version, `main-zhs.exe` is the Chinese (Simplified) version, `main-zht.exe` is the Chinese (Traditional) version.

`main.exe` 为英文版，`main-zhs.exe` 为简体中文版，`main-zht.exe` 为繁体中文版。

<img src="https://raw.githubusercontent.com/NightFurySL2001/CJK-character-count/master/resource/jf-openhuninn-sample-en.png" width="500" >

<img src="https://raw.githubusercontent.com/NightFurySL2001/CJK-character-count/master/resource/jf-openhuninn-sample-zhs.png" width="500" >

<img src="https://raw.githubusercontent.com/NightFurySL2001/CJK-character-count/master/resource/jf-openhuninn-sample-zht.png" width="500" >

## Currently supported encoding standard/standardization list 支援的编码标准／汉字表

Details of the character lists can be found in https://github.com/NightFurySL2001/cjktables.  
字表详情可参见 https://github.com/NightFurySL2001/cjktables 。

### Encoding standard 编码标准

-   [GB/T 2312](https://en.wikipedia.org/wiki/GB_2312)

-   [GB/T 12345](https://zh.wikipedia.org/wiki/GB_12345)  
    \*_Note: Source file from [character_set](https://gitlab.com/mrhso/character_set/-/blob/master/GB12345.txt) by @mrhso.  
    注：字表来源为 @mrhso [character_set](https://gitlab.com/mrhso/character_set/-/blob/master/GB12345.txt)。_

-   [GBK](<https://en.wikipedia.org/wiki/GBK_(character_encoding)>)  
    \*_Note: Private Use Area (PUA) characters are removed and not counted, resulting in 20923 characters.  
    注：不计算私用区（PUA）字符，共计 20923 字。_

-   [GB 18030-2022 Implementation Level 1/实现等级 1](https://en.wikipedia.org/wiki/GB_18030)

-   [GB/Z 40637-2021 Standard Glyph List of Generally Used Chinese Chars for Ancient Books Publishing/古籍印刷通用字规范字形表](https://zh.wikipedia.org/zh-my/%E5%8F%A4%E7%B1%8D%E5%8D%B0%E5%88%B7%E9%80%9A%E7%94%A8%E5%AD%97%E8%A7%84%E8%8C%83%E5%AD%97%E5%BD%A2%E8%A1%A8)

-   [BIG5/五大码](https://en.wikipedia.org/wiki/Big5)

-   [BIG 5 Common Character Set/五大码常用汉字表](https://en.wikipedia.org/wiki/Big5)

-   [Hong Kong Supplementary Character Set (HKSCS)/香港增补字符集](https://en.wikipedia.org/wiki/Hong_Kong_Supplementary_Character_Set)

-   [IICore/国际表意文字核心](https://appsrv.cse.cuhk.edu.hk/~irg/irg/IICore/IICore.htm)（Deprecated/已废除）

-   [Hong Kong Supplementary Character Set/香港增補字符集](https://zh.wikipedia.org/wiki/%E9%A6%99%E6%B8%AF%E5%A2%9E%E8%A3%9C%E5%AD%97%E7%AC%A6%E9%9B%86)

-   [jf7000 Core Set/当务字集基本包](https://justfont.com/jf7000)

### Standardization list 汉字表

-   [List of Frequently Used Characters in Modern Chinese/现代汉语常用字表](https://zh.wiktionary.org/wiki/Appendix:%E7%8E%B0%E4%BB%A3%E6%B1%89%E8%AF%AD%E5%B8%B8%E7%94%A8%E5%AD%97%E8%A1%A8)  
    \*_Note: Old name in this software was 3500 Commonly Used Chinese Characters.  
    注：旧版软件内名称为《3500 字常用汉字表》。_

-   [List of Commonly Used Characters in Modern Chinese/现代汉语通用字表](https://zh.wiktionary.org/wiki/Appendix:%E7%8E%B0%E4%BB%A3%E6%B1%89%E8%AF%AD%E9%80%9A%E7%94%A8%E5%AD%97%E8%A1%A8)

-   [Table of General Standard Chinese Characters/通用规范汉字表](https://en.wikipedia.org/wiki/Table_of_General_Standard_Chinese_Characters)

-   [List of Frequently Used Characters of Compulsory Education/义务教育语文课程常用字表](https://old.pep.com.cn/xiaoyu/jiaoshi/tbjx/kbjd/kb2011/201202/t20120206_1099050.htm)

-   [Chart of Standard Forms of Common National Characters/常用國字標準字體表](https://zh.wikipedia.org/wiki/%E5%B8%B8%E7%94%A8%E5%9C%8B%E5%AD%97%E6%A8%99%E6%BA%96%E5%AD%97%E9%AB%94%E8%A1%A8)  
    \*_Note: Old name in this software was 《台湾教育部常用字表》.  
    注：旧版软件内名称为《台湾教育部常用字表》。_
-   [Chart of Standard Forms of Less-Than-Common National Characters/次常用國字標準字體表](https://zh.wikipedia.org/wiki/%E5%B8%B8%E7%94%A8%E5%9C%8B%E5%AD%97%E6%A8%99%E6%BA%96%E5%AD%97%E9%AB%94%E8%A1%A8)  
    \*_Note: Old name in this software was 《台湾教育部次常用字表》, and was temporarily removed in v0.10 and v0.11.  
    注：旧版软件内名称为《台湾教育部次常用字表》，并于 0.10 版和 0.11 版暂时移除。_

-   [List of Graphemes of Commonly-used Chinese Characters (Online version)/常用字字形表（线上版）](https://zh.wikipedia.org/wiki/%E5%B8%B8%E7%94%A8%E5%AD%97%E5%AD%97%E5%BD%A2%E8%A1%A8)

-   [Supplementary Character Set (suppchara, level 1-6)/常用香港外字表（1-6 级）](https://github.com/ichitenfont/suppchara)

### Foundry list 厂商字表

-   [Hanyi Fonts Simp./Trad. List/汉仪简繁字表](https://github.com/3type/glyphs-han/blob/master/Tables/Commonly%20Used%20on%20Internet.txt)

-   FounderType Simp./Trad. List 方正简繁字表

## License 授权

This software is licensed under [MIT License](https://opensource.org/licenses/MIT). Details of the license can be found in the [accompanying `LICENSE` file](LICENSE).  
本软件以 [MIT 授权条款](https://opensource.org/licenses/MIT)发布。授权详情可在[随附的 `LICENSE` 文件内](LICENSE)查阅。

## To build 如何构建

Please install [latest version of Python 3](https://www.python.org/downloads/) and set up a new virtual environment with `python3 -m venv venv`.  
请先安装[最新版本的 Python 3](https://www.python.org/downloads/) 并创建新的虚拟环境 `python3 -m venv venv`。

Install the required dependencies:  
安装需要的依赖模块：

```sh
pip3 install -r requirements.txt
```

And then build the program:  
最后构建软件：

```sh
.\build.bat
```

## To-do 待办事项

-   Redesign GUI with [Kivy](https://kivy.org/)/[PySide6]().

## Changelog 更新日志

Refer to [readme.txt](readme.txt). 参考[readme.txt](readme.txt)。

---

This program is requested by [MaoKen](http://www.maoken.com/). Visit their site to see this in action.

此软件由[猫啃网](http://www.maoken.com/)要求。浏览该网址以查看使用方式。
