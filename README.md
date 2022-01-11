# うどんAIアプリ開発用データ管理方法について 

## ディレクトリ


## データ管理手順
1. 定期的にKSBアプリ(Gmail)とUDON AIアプリ(AWS)から投稿されたデータをダウンロードする。
1. ダウンロードしたデータをudon_ai_dataset_main内の各フォルダに振り分ける
    - 正解が不明なもの，怪しいものは使用しない。
    - 既存のフォルダにない店のものは新たにフォルダを作成し，同時にExcelファイルを更新する
1. データの振り分けが終わったら学習用のデータセット(dataset_yyyymmdd.zip)と店舗名のリスト(shop.py)を生成する。 