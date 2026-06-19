# graphcal-py Design (PoC)

> Status: 最小 PoC。目標は「graphcal を Python から呼べる」だけ。

## なぜ subprocess

graphcal の Rust ライブラリ API はまだ安定していないため、PyO3 バインディングはすぐ壊れる可能性が高い。CLI (`graphcal eval --format json`) のほうが先に安定する見込みで、subprocess で薄く包むだけならメンテコストも低い。API 安定後に PyO3 へ差し替えるかは別途検討。

## PoC スコープ

関数 1 つだけ:

```python
graphcal.eval(file, overrides=None, binary="graphcal") -> dict
```

挙動:

1. `graphcal eval --format json <file> [--set k=v]...` を実行
2. stdout を `json.loads`
3. dict をそのまま返す

エラーはまず `subprocess.CalledProcessError` を素通しさせる (`check=True`)。stderr もそのまま例外に含まれる。

## 後回し (今はやらない)

- 例外ヒエラルキ / 友好的なエラーメッセージ
- 多次元 indexed 値の dataclass 化
- `--plot json` のヘルパ
- `Runner` クラス / バージョンチェック
- `pint`, `pandas`, asyncio 連携
- 将来の PyO3 移行

## 使い方

```python
import graphcal
result = graphcal.eval("rocket.gcl", overrides={"isp": "450.0 s"})
print(result["node"]["delta_v"]["si_value"])
```
