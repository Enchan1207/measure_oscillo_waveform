# オシロスコープの波形をUSBTMCで取得する

## 環境

 - オシロスコープ: Tektronix TDS2012B
 - MacBook Pro 2020

## 概要

基本的には `dat:sou ch1` して `dat:enc ribinary` して `curve?` すれば、ch1のバイナリが降ってくる。データ構造は `#42500` で始まり、その後はデータ長分(2500個?)バイナリが続く。

このバイナリ構造が厄介。

## `curve?` の戻り値

`curve?` は基本的に**画面座標系の値を返す**(positionダイヤルに依存する)ため、プローブが測定した絶対値を求めるにはちょっとした計算が必要になる。

[Digital Oscilloscope Series Programmer Manual](https://www.tek.com/ja/oscilloscope/tds1000-manual) によれば、時間軸 $X_n$ および電圧 $Y_n$ は $n$ 番目のデータ $y_n$ を用いて以下の式により算出できる:

$$
\begin{aligned}
    X_n & = X_0 + X_{inc} \cdot n \\
    Y_n & = Y_0 + Y_{mul} (y_n - Y_{off})
\end{aligned}
$$

定数 $X_0$ , $X_{inc}$ , $Y_0$ , $Y_{mul}$ , $Y_{off}$ は、波形情報を取得する `wfmpre?` から取得できる。
`wfmp:xze?;xin?;yze?;ymu?;yof?` でまとめてもってくることも可能。

これを代入して計算すればいい感じの時間軸と縦軸を算出できる。なお、時間軸は水平トリガをゼロとして左右に正負の値を取る点に注意。

## License

This repository is published under [MIT License](LICENSE).
