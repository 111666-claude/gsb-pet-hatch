# pet-hatch

宠物孵化：时长、加速道具与领取幂等，只用 Python 标准库。

```
python3 -m pethatch.cli --sample early
python3 -m pethatch.cli --sample repeat
python3 -m unittest discover -s tests -v
```

## 口径（README 为准）

- **时长没到不能领**：`now - start < duration` 时 `claim` 必须返回 `HatchError`。
  `--sample early`（时长 3600 秒、只过了 100 秒）按口径是 `claimed=rejected`，现在给 `claimed=True`。
- **领取必须幂等**：同一个蛋只能领一次，第二次返回 `HatchError`。
  `--sample repeat`（连领两次）按口径是 `pets=1`，现在给 `pets=2`。
- **加速道具只能用一次**：第二次 `boost` 要报错，且加速要真实缩短所需时长。
- 不变量：`progress` 落在 [0, 1]；`claimed` 从 False 变 True 后不再变；同一批操作重复执行结果相同。
- 规模：10 万个蛋、每秒 10 万次进度查询 1 秒内完成，内存 O(蛋数)。

## 现在的行为

- `claim` 不看 `progress`，也不看 `claimed`：随时可领、可重复领。
- `boost` 每次调用都把 `start` 往前挪，能反复用。
- `progress` 没用上加速道具的减免。

## 输出

```
claimed=rejected
pets=1
```

## 目录

```
pethatch/hatch.py   孵化与领取
pethatch/cli.py     命令行入口
tests/              unittest 用例
```
