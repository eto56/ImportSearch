# importsearch

importsearch は CLI から Python ファイルの import 依存を探索するツールです。  
エントリーファイルを指定するだけで、辿ったファイル一覧や依存グラフをテーブル形式で確認できます。

## 主な機能

- **CLI レポート**: 1 コマンドで依存ファイルの一覧と訪問済みファイルを出力。
- **出力形式の選択**: `print` (装飾付き)、`text`、`json` の 3 種類に対応。
- **冪等な解析**: 解析対象は `Path` ベースで扱われ、循環や重複を避けて探索します。

## インストール

```bash
pip install importsearch
```

## 使い方 (CLI)

```bash
importsearch path/to/main.py --root . --output-format print
```

### 主なオプション

- `--root / -r`: 解析のルートディレクトリ (省略時はカレントディレクトリ)  
- `--output-format / -o`: `print` / `text` / `json`  
- `--output-file / -of`: `text` / `json` 出力時のファイル名 (拡張子は自動付与)  
- `--verbose / -v`: 解析の進捗ログを表示

### 例: テキストファイルに保存する

```bash
importsearch src/main.py --root . --output-format text --output-file report
```

標準出力に解析結果を表示しつつ、`report.txt` も生成されます。

## プログラムから使う場合 (オプション)

CLI がメインですが、クラスを直接利用することもできます。

```python
import argparse
from pathlib import Path
from importsearch import importsearch

args = argparse.Namespace(
    file_path=Path("src/main.py"),
    root_path=Path("."),
    output_format="json",
    output_path=Path("dependencies"),
    verbose=False,
)

searcher = importsearch(args)
searcher.search()
searcher.summary()
```

## 開発

テストは `pytest` で実行できます。

```bash
pytest
```

コントリビュート歓迎です。気になる改善点があれば Issue や Pull Request をお待ちしています。
