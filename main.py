#
# オシロスコープがキャプチャした波形を取得し、matplotlibでプロットする
#
import sys
from typing import List, Tuple

import usbtmc
from matplotlib import pyplot as plt
from functools import partial


def main() -> int:

    # 一番最初に見つかったTMCデバイスにつなぐ
    devices = usbtmc.list_devices()
    if len(devices) == 0:
        print("no USB-TMC device connected")
        return 1
    device = devices[0]
    instrument: usbtmc.Instrument = usbtmc.Instrument(device)
    instrument.open()
    print(f"Connected device: {instrument.ask('*IDN?')}")

    # 測定設定
    print("configure...")
    configure_device(instrument)

    # 波形取得
    print("fetch waveform #1...")
    waveform_1 = get_waveform(instrument, "ch1")
    print("fetch waveform #2...")
    waveform_2 = get_waveform(instrument, "ch2")

    # 描画
    fig = plt.figure()
    subplot = fig.add_subplot()
    subplot.plot(*waveform_1)
    subplot.plot(*waveform_2)
    plt.show()

    return 0


def configure_device(instrument: usbtmc.Instrument):
    """デバイスの測定構成を設定する

    Args:
        instrument (usbtmc.Instrument): 通信対象
    """
    commands = [
        "hdr 0",
        "sel:ch1 1",
        "sel:ch2 1",
        "ch1:sca 2",
        "ch1:pos -1.25",

        "hor:sca 2.5e-4",
        "hor:pos 5e-4",
        "trig:main:level 2.5",
    ]
    instrument.write(commands)


def get_waveform(instrument: usbtmc.Instrument, source: str) -> Tuple[List[float], List[float]]:
    """波形を取得・変換し、配列で返す

    Args:
        instrument (usbtmc.Instrument): 通信対象
        source (str): 波形取得ソース

    Returns:
        Tuple[List[float], List[float]]: 時間軸, y軸
    """

    # 波形ソースとフォーマットを設定
    instrument.write(f":dat:enc rib;:dat:sou {source}")

    # 呪文を詠唱し、計算に必要な値を取り出す
    magic_spell = "wfmp:yze?;ymu?;yof?;xze?;xin?"
    spell_result: str = instrument.ask(magic_spell)  # type: ignore
    elements: List[float] = list(map(float, spell_result.split(";")))
    assert len(elements) == 5
    y_zero, y_mul, y_off, x_zero, x_inc = tuple(elements)

    # 波形を取得して符号付き整数に整形
    instrument.write("curve?")
    waveform_bytes: bytes = instrument.read_raw()[6:]  # type: ignore
    bytes_to_signed_int = lambda byte_data: [byte if byte < 128 else byte - 256 for byte in byte_data]
    waveform_int: List[int] = bytes_to_signed_int(waveform_bytes)

    # 計算
    y_to_volts = lambda y, y_zero, y_mul, y_off: y_zero + y_mul * (y - y_off)
    x_to_seconds = lambda x, x_zero, x_inc: x_zero + x_inc * x

    y_to_volts_partial = partial(y_to_volts, y_zero=y_zero, y_mul=y_mul, y_off=y_off)
    x_to_seconds_partial = partial(x_to_seconds, x_zero=x_zero, x_inc=x_inc)

    waveform_seconds = list(map(x_to_seconds_partial, range(len(waveform_int))))
    waveform_volts = list(map(y_to_volts_partial, waveform_int))

    return (waveform_seconds, waveform_volts)


if __name__ == "__main__":
    sys.exit(main())
