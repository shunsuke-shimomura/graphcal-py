# graphcal-py Design

> Status: CLI wrapper package。目標は「graphcal を Python から型付きで安全に呼べる」こと。

## なぜ subprocess

graphcal の Rust ライブラリ API はまだ安定していないため、PyO3 バインディングはすぐ壊れる可能性が高い。CLI (`graphcal eval --format json`) のほうが先に安定する見込みで、subprocess で薄く包むだけならメンテコストも低い。API 安定後に PyO3 へ差し替えるかは別途検討。

## モジュール構成

`import graphcal` の公開 API は変えず、実装を小さなモジュールに分割している:

| モジュール | 責務 |
|-----------|------|
| `cli.py` | `eval` / `eval_file` / `check`。subprocess 呼び出しのみ |
| `errors.py` | `GraphcalError` / `GraphcalCommandError` / `GraphcalEvaluationError` / `GraphcalCheckError` |
| `overrides.py` | `Override` と `normalize_overrides` |
| `project.py` | `GraphcalProject` と `graphcal.toml` の読み取り |
| `result.py` | `GraphcalResult` / `GraphcalValue` |
| `__init__.py` | 公開 API の再エクスポート |

大きな抽象化層は置かない。このパッケージはあくまで CLI wrapper。

## 挙動

1. `graphcal eval --format json <file> [--set name=value]...` を実行
2. stdout を `json.loads` して `GraphcalResult` に包む
3. 非ゼロ終了は `GraphcalEvaluationError` に変換(command / stdout / stderr / returncode / file / overrides を保持)

## 値アクセス

Graphcal の JSON は dimensioned dict と plain scalar が混在するため、
`GraphcalValue` が差を吸収する:

- dict 値: `value` は `si_value` を優先
- plain 数値: `si_value` / `display_value` はその数値を返す
- `as_float()` は非数値に `TypeError`
- `as_scaled(exponent)` は SI 値を `10 ** exponent` で割るだけ(m/s → km/s なら `as_scaled(3)`)

単位変換テーブルは持たない。中途半端なテーブルはカバー範囲の穴が事故のもとに
なるため、10 進接頭辞の除去 (`as_scaled`) だけを提供し、実際の単位変換
(rad → deg など) は呼び出し側で `math.degrees` 等を使って明示する。
次元検査は Graphcal 側の責務であり、Python 側で汎用単位系を実装しない。

## 使い方

```python
import graphcal

result = graphcal.eval(
    "examples/orbital_transfer.gcl",
    overrides=[
        graphcal.Override.length("parking_orbit_altitude", 410.0, "km"),
        graphcal.Override.angle("target_inclination", 51.6, "deg"),
        graphcal.Override.mass("propellant_mass", 2800.0, "kg"),
    ],
)

print(result.node("delta_v").as_scaled(3))          # m/s -> km/s
print(result.node("orbital_radius").display_value)  # km (表示単位のまま)
```

## 後回し (今はやらない)

- 多次元 indexed 値の dataclass 化
- `--plot json` のヘルパ
- `Runner` クラス / バージョンチェック
- `pint`, `pandas`, asyncio 連携
- 将来の PyO3 移行
