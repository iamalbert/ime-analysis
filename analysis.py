import argparse
import collections
import statistics
import json
import numpy as np
import random 
from smart_open import smart_open

def get_cf():
    return json.load(smart_open("cht.small.freq.json"))

def analysis(input, proficiency):


    co2ch = collections.defaultdict(list)
    ch2co = collections.defaultdict(list)

    eff_ch2co = {}
    eff_co2ch = {}
    
    for line in input:
        try:
            code, char = line.strip().split(' ', maxsplit=1)

            if code not in co2ch:
                eff_code = code
            else:
                n = 1
                while True:
                    eff_code = f"{code}{n}"
                    if eff_code not in eff_co2ch:
                        break
                    n += 1

            co2ch[code].append(char)
            ch2co[char].append(eff_code)

        except Exception:
            pass

    for char, codes in ch2co.items():
        if len(codes) == 1:
            select_code = codes[0]
        else:
            shortest_code = min(codes, key=len)
            if random.random() <= proficiency:
                select_code = shortest_code
            else:
                s = random.choices(codes, k=2)
                select_code = s[0] if s[0] != shortest_code else s[1]

        eff_ch2co[char] = select_code
        eff_co2ch[select_code] = char

    print("* 只考慮編碼表內的字，無加權")
    evaluate(ch2co, co2ch, eff_ch2co, eff_co2ch)

    cf = get_cf()

    co2ch_f = collections.defaultdict(list)
    ch2co_f = collections.defaultdict(list)

    eff_ch2co_f = {}
    eff_co2ch_f = {}

    for char in cf:
        if char in ch2co:
            codes = ch2co[char]
            ch2co_f[char] = codes

            code = eff_ch2co[char]
            eff_ch2co_f[char] = code
            eff_co2ch_f[code] = char
    
    for code, chars in co2ch.items():
        for char in chars:
            if char in cf:
                co2ch_f[code].append(char)


    print(f"\n* 考慮最常使用的 {len(cf)} 字 (語料庫共 {sum(cf.values())} 字)")
    evaluate(ch2co_f, co2ch_f, eff_ch2co_f, eff_co2ch_f, cf=cf)


def evaluate(ch2co, co2ch, eff_ch2co, eff_co2ch, cf=None):

    print( "總字數  ", len(ch2co) )
    print( "總編碼數", len(co2ch) )
    
    code_mchar = [ (code, chars) for code, chars in co2ch.items() if len(chars) > 1]
    char_mcode = [ (char, codes) for char, codes in ch2co.items() if len(codes) > 1]

    print( "一碼多字(重碼字)   {:6d} {:6.2%}".format(len(code_mchar), len(code_mchar) / len(co2ch)))
    print( "一字多碼(多種拆法) {:6d} {:6.2%}".format(len(char_mcode), len(char_mcode) / len(ch2co)))

    codelen = [ len(code) for char, code in eff_ch2co.items() ]
    codelen_avg = statistics.mean(codelen)
    codelen_std = statistics.stdev(codelen)

    print( f"碼長: 平均 {codelen_avg:5.3f} 標準差 {codelen_std:5.3f}")

    if cf:
        print("依字頻加權後")
        char_freq = [ cf[char] for char in ch2co ]
        codelen_wavg = np.average(codelen, weights=char_freq)
        print( f"碼長: 平均 {float(codelen_wavg):5.3f}" )

    
def main():
    ap = argparse.ArgumentParser()

    ap.add_argument("input", metavar="FILE",
        help="要分析的 cin 檔",
        type=argparse.FileType('r', errors="ignore") )
    ap.add_argument("--proficiency", "-p",
        help="熟練度（使用最短碼的機率), 預設 1.0",
        type=float,
        default=1.0)

    args = ap.parse_args()

    analysis(args.input, args.proficiency)


if __name__ == '__main__':
    main()
