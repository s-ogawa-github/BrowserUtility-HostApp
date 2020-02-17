# BrowserUtility-HostApp
 
## 概要
* Firefox or ChromeのBrowser Utility for Development workアドオンと連携するHostApp
* ブラウザの右クリックメニューでOpen in IE (Browser Utility)の項目をクリックした場合、引数で与えられるURLをIEで開く
* (Firefoxのみ)ブラウザの右クリックメニューでファイルパスの項目を実行した場合、引数で与えられるURLを新規タブでオープンする

## インストール
* BrowserUtility-HostAppから'Source code (zip)'をダウンロードしてください。

　　https://github.com/s-ogawa-github/BrowserUtility-HostApp/releases/latest

　　ダウンロードしたzipファイルを解凍し、フォルダ内の host_app_install.bat を実行してください（実行後にフォルダを移動させた場合は再実行が必要です）

* 本ツールはPython環境が必要です。

　　Python環境が入っていない場合は、python.orgからVersion3.6以降をインストールしてpyスクリプトが実行できる状態にするか、

　　もしくは以下から python.exe をダウンロードし、host_app/srcフォルダの直下に格納してください

　　https://github.com/masamitsu-murase/single_binary_stackless_python/releases/tag/v3.6.8-slp-L22

## アンインストール 
* フォルダ内の host_app_uninstall.bat を実行してください
