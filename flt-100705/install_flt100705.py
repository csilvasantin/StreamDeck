#!/usr/bin/env python3
"""FLT-100705 Install Stream Deck Scumm map on MacMini ProfilesV3."""
from __future__ import annotations
import base64, json, os, shutil, subprocess, sys, tempfile, time, uuid
from pathlib import Path
from datetime import datetime

HOME = Path("/Users/csilvasantin")
PROFILES = HOME / "Library/Application Support/com.elgato.StreamDeck/ProfilesV3"
PROFILE_ID = "6041EB74-86AB-42B5-8FEE-D1F8E4079C93.sdProfile"
PAGE_ID = "4F80C30E-4507-4783-89B6-D0C08C6D1AB8"
HELPERS_CANDIDATES = [
    HOME / "Applications/StreamDeck Helpers/Admira Live",
    HOME / "Applications/Stream Deck Helpers/Admira Live",
    HOME / "Applications/StreamDeckHelpers/Admira Live",
]
def resolve_helpers():
    for c in HELPERS_CANDIDATES:
        if c.exists():
            return c
    # default create at first
    return HELPERS_CANDIDATES[0]
HELPERS = resolve_helpers()
CLI = HOME / ".codex/streamdeck-admira-live/admira_live_cli.py"
if not CLI.exists():
    alt = HOME / ".codex/streamdeck-admira-live/admira_live_cli.py"
    if alt.exists():
        CLI = alt
STAGING = HOME / "Admira/streamdeck-scumm-flt100705"
BACKUP_ROOT = HOME / "Admira/backups"
OPEN_PLUGIN = "com.elgato.streamdeck.system.open"
OPEN_PLUGIN_ALTS = ("com.elgato.streamdeck.system.open", "com.elgato.streamdeck.system.open")
TS = datetime.now().strftime("%Y%m%d-%H%M%S")

KEYS = {
    "1,0": ("PREGUNTAR", "AL Preguntar.app", "preguntar", "SCUMM_01.png"),
    "2,0": ("EXAMINAR",  "AL Examinar.app",  "examinar",  "SCUMM_02.png"),
    "3,0": ("DEBATIR",   "AL Debatir.app",   "debatir",   "SCUMM_03.png"),
    "1,1": ("ENTRENAR",  "AL Entrenar.app",  "entrenar",  "SCUMM_04.png"),
    "2,1": ("CREAR",     "AL Crear.app",     "crear",     "SCUMM_05.png"),
    "3,1": ("YARIG.AI",  "AL Yarig.app",     "yarig",     "SCUMM_06.png"),
    "1,2": ("PENSAR",    "AL Pensar.app",    "pensar",    "SCUMM_07.png"),
    "2,2": ("VOTAR",     "AL Votar.app",     "votar",     "SCUMM_08.png"),
    "3,2": ("ANALIZAR",  "AL Analizar.app",  "analizar",  "SCUMM_09.png"),
}
KEEP_COL0 = {"0,0", "0,1", "0,2"}
KEEP_TITLE_SUBSTR = ("CAPTURA", "AREA", "ÁREA", "PANTALLA")

def log(msg):
    print(msg, flush=True)

def run(cmd, check=True):
    log("$ " + cmd)
    r = subprocess.run(cmd, shell=True, text=True, capture_output=True)
    if r.stdout:
        print(r.stdout, end="")
    if r.stderr:
        print(r.stderr, end="", file=sys.stderr)
    if check and r.returncode != 0:
        raise SystemExit(f"cmd failed ({r.returncode}): {cmd}")
    return r

def load_icons_b64():
    # 1) sidecar next to script
    here = Path(__file__).resolve().parent
    for cand in [here / "icons_b64_embed.json", STAGING / "icons_b64_embed.json",
                 Path("/tmp/flt100705-icons_b64_embed.json")]:
        if cand.exists():
            return json.loads(cand.read_text())
    # 2) embedded fallback marker replaced at pack time
    raw = EMBEDDED_ICONS_JSON
    if raw and raw != "__EMBED__":
        return json.loads(raw)
    raise FileNotFoundError("icons_b64_embed.json missing")

EMBEDDED_ICONS_JSON = "{\"SCUMM_01.png\": \"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\", \"SCUMM_02.png\": \"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\", \"SCUMM_03.png\": \"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\", \"SCUMM_04.png\": \"iVBORw0KGgoAAAANSUhEUgAAAJAAAACQCAYAAADnRuK4AAAFOUlEQVR4nO3df0zUdRzH8c8pEGKhIszMBg2ymE1T+8E6MwOvhQJZkbO5Nkcz19oql8uNfxobSxaN5pZLa87K5bQ8pjnc/MM/ssXqtNmaCkumCeTAtYCgCO2E/nCXgHdwx+v43n2/93z8x5fzzef73Yv3577emzvXenf2kAEmaEqsFwB7I0CQECBIkkYfaO0ZiMU6YBM5M1NHfE0HguSWDhTgzb3PynUgzr1w8XzQ43QgSEJ2oIBQyUNiGG8nogNBQoAgIUCQjPscKOCaf3Ay14E4k5IUXm8JO0DhFkRiIRWQECBICBAkBAgSAgQJAYIk7Nv41JSwHwoHGLjmD+txYaci3IJILGxhkBAgSAgQJAQIEgIECQGChHkgBMU8ECxBKiAhQJAQIEgIECQECBICBAnzQAiKeSBYgi0MEgIEie2f2NjlndSc+j5LdCBICBAkBAgS5oEsYrfrxzxQnHHq9bP9XVgokd71hLqbi1ado8ePBD1e4nkmovrxxpm/FrAMAYKEAEFCgCAhQJA4dh4oWuud7PMOdXdWvvr5Sf2540n4eaBorTdW522X680WBgkBgoQAQUKAICFAkBAgSBw7DxSt9cbqvGN9vRN+Hiha643VedvlettjlYhbBAgSe73A5UBMJCKhESBICBAkzANZVCdW9SeKeSCbzAPZ7bqOFp/xdyC7322FwnMgSAgQJAQIEgIECQGCxLHzQNF678Ro1bHb9Uv4eaB449Tr58yzgmUIECQECBICBIntXwtz6jvA2wUdCBLHzgNBk/DzQLAGWxgkBAgSAgQJAYKEAEFCgCBx7DwQNMwDwRKkAhICBAkBgoQAQUKAICFAkDAPhKCYB4Il2MIgIUCQECBICBAkBAgSAgQJ80AIinkgWIJUQEKAICFAkBAgSAgQJAQIknFv439p6/FZsRDEqVxTMNa36UCQECBICBAkBAgSAgSJ7f/UYsXSJTO8tTX5ga9/Pt/yd/XuPe3e2pr8hu8auyqqqlvefHHdXVs3vDRv3qqyU60Nhx9JS00d8YtTueOjSy1t7QOBOn/1/3P9aGNj9xu1dReWL1kcUX1jjLktJWVKs/fA0jvS0qY+8cqrZ5p/vdQ/fJ3D6w8ODVlzoSaJYzpQ6eYtTVmeYp/ntdfPBo6VLHNnLLw3b/rwx+WUPntq7tMlJ40xpubTz3/L8hT7dh8+cmV4nXd2fdK27ilP5qL586dHWt8YY1a5H5t1+7RpU7t6e/1rPSszR68zWH27ckyAGrbXLfj9+LGCnZVb8wLHjn3/Q3dlxYa7I63lcrnM4NCQ6e7r+/9vmSKpv9ZTlPljU3Pf1ye+/aO8qHD2FJdr3Pp2ZfstLKB085Ym39lzfcbc2NaMMebDLw92HNhWff+/fn/Y+0TD9roFxhjzcf2hztaOjqv3zL0zNZL6GenpSYUPPzTj3T2ftZ+7cLG/oqx0jvvBRemh6utnHluO6UDB9PT2+XfVH+pYvcw9K9x/s+att5vf3/vF5ZfXlM15IC83LdL6zxWumJ2clOSq2rQx++B72/KNudGRJlLfDhwToMAWc3rf3sXDj+/01nd29faGvVVcHxwc+mDf/sttnVeuVm3amB1p/fKVRZknTv/0Z5an2JflKfbt+MrbUbr88Yzk5CTXWPXtyrXenT2ivbf2DBhjbn5W6MJvTvJaWAI78+SjBcbc/FSknJmpI77vmA6E2CBAkBAgSAgQJAQIEgIECQGCZNyXMgL/DwAEQweCJGQH4vPYEQ46ECS3dKDRr3UAY6EDQUKAICFAkPwHDbXLW2DfnqsAAAAASUVORK5CYII=\", \"SCUMM_05.png\": \"iVBORw0KGgoAAAANSUhEUgAAAJAAAACQCAYAAADnRuK4AAAFSUlEQVR4nO3dfWhVdRzH8d/drtexO9z1AQSzrWiNteiBEZtubQ61KWnbtH9qGmQQgaQSVBMiYqOsPzRqatEDzYJQigID/aOydJR6wRJ0lTONdD4EIt657pi23fXHOm3Te7d797lP55736z/PORzP+fHh+7u/ne8919VUWTBkgEnKSvUFwN4IECQECBL3jRvOBPpTcR2wiUJfzph/U4EguakCWdpfyk3mdSDNrXmtL+x2KhAkESuQJVLy4AwTzURUIEgIECQECJIJPwNZrg+EEnkdSDMed3S1JeoARXtCOAupgIQAQUKAICFAkBAgSAgQJFEv43M8UR+KDNB/fSCq46JORbQnhLMwhUFCgCAhQJAQIEgIECQECBL6gRAW/UBIClIBCQGChABBQoAgIUCQECBI6AdCWPQDISmYwiAhQJDwwSbOYn2zm93fv0QFgoQAQUKAIKEfKMXSdVzpB7IJu48rq7BJirTasvuqKlb2jj9SjgBBQoAgIUCQECBI6AeawLsveGI6PtZx+mLvl2G3P/rwypjOE2/0A8VNbAGK1zjZZbyZwiAhQJAQIEgIECTOXFqFEa9Owj3ffhWPy7ENKhAk9ANNUqLHI9XjTT9QgiV6POwy3va4SqQtAgSJ41Zhif7e1rLF9TEdb/dVGxUIEgIECQGChH6gCaTqvlM93vQDRZSa/p5Y2WW8M7as2OUtGbGu2tINn4EgIUCQECBICBAkBAgS2/cDffpKXkzHr2r5O0FXklnoB4ogU+4jXTCakBAgSAgQJAQIkox9FhYJ7zaMLyoQJPQD/SfT7y9WDuoHiq2/J5L0vb/0xhQGCQGCxPYTP6un1KICQUKAICFAkNi+HwiJQT8QkoJUQEKAICFAkBAgSAgQJAQIEvqBEJaD+oGQSkxhkBAgSAgQJAQIEgIECQGChH4ghEU/EJKCVEBCgCAhQJAQIEgIECQECJIJl/FdZwP+ZFwI0lVuxXh7qUCQECBICBAkBAgSAgSJY75qsaSuZsa6dWtuua1wbs6lS5f/ebF502mPx5P18Y43S4wxJhjsG/z6m44rzRvfOD1/Xlm+td0YYzo7u4KNK5/uNMaYqVM9Wf5Du8vy8rzZy5Y/ebzr5B99VZUP5Ic7TyiU+R0MjqhA995T4t3a1npnR4e/Z35V488trW/96fXmZlv7H3v82V83vb797IrGpbPuLi32jt5eVFzjt8JjjDGLFz043evNzQ4Erg40NNTNGv3/RDpPJnNEgBYurJpujDFvt310rrc3OLj/wOHA/gOHA6OPcblcJhQKmUDP1f+/v7Rr57bSUyc7KrZsfvkOa1tDQ92so0d/6d2z97vL9Y88NDMra+wQhjtPJnPEFOZyucbdv2vntlJjjGnf8flf3d0XrhXcOifHmOGKcuSnY73WcT7fNHdNdXn+5i3vd584capvVVPj7PLy+6ZFOk9CbibNOKIC7dv3wxVjjNmw/qm5eXne7Orq8vzaBfN81v6m1et/a9vafv6J1Stm31VSFPEH55cvWzTT7Xa7NjavLdjRPvyZp6F+ZBqL9jyZxBEBOnb8RHDDcy2/1y6Y7/Mf2l32auvztweDfYPW/tBgaGj7O5+c7z538Vpz89oCa7s1hR34/rP7jRkOy48Hj/QUFdf4i4pr/B98uPPi0iW1M6ZMcbvGO08mczVVFgyN3nAm0G+MGflVm8pnLvAszMEOvjenwpiR93EX+nLG7HdEBULiECBICBAkBAgSAgQJAYKEAEEy4aMM6+8AQDhUIEgiViB+CRDRoAJBclMFuvFZBzAeKhAkBAgSAgTJv8hHfkO6PbMmAAAAAElFTkSuQmCC\", \"SCUMM_06.png\": \"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\", \"SCUMM_07.png\": \"iVBORw0KGgoAAAANSUhEUgAAAJAAAACQCAYAAADnRuK4AAAF7ElEQVR4nO3df0zUdRzH8ffh8aPDBJRmIydbKhS1zA05I0WbemIuwMqtQE22zB+pyz+aJfOPVtYm+ldYSzBYa2pW5pqms6hk08lmEUhK7PpDSWEj89A0xOuuP+DsxDu5430e3Peej//43PG97/e7170/97nv++5Mxbnj3QIMUsxQ7wAiGwGCCgGCirn/wFlH91DsByJEenLCLX9TgaByWwXyqC6zhHM/MMyVbr7mc5wKBBW/FcjDX/IQHQaaiahAUCFAUCFAUBnwNZBHj9N1N/cDw0ycObDaEnCAAt0gogupgAoBggoBggoBggoBggoBgkrAy/iEuIDvCgPo7nEGdL+AUxHoBhFdmMKgQoCgQoCgQoCgQoCgQoCgQj8QfKIfCGFBKqBCgKBCgKBCgKDCJfY+wX4XAJ/Y7UUFggr9QINk9PNBP1DQ4oK6t/HPR2CYwqBCgKBi7Ik8CMGuqvyt2qJtdUYFggoBggoBggr9QCFmlPNEP9AQibbzFF1Hi5AjQFAhQFAhQFAhQFAhQFChH6jPh68H186xqrzH57hRzhP9QEGjH2gwmMKgQoCgQoCgQoCgYowlQxDoJAwtKhBU6AfqY/TjCxb9QEEy+vHdLZw1qBAgqBAgqBAgqBAgqBAgqNAP1Mfoxxcs+oH88t33Y5zjC6+oe9r5u+bFNbLB4TUQVAgQVAgQVAgQVAgQVOgH6lPy1t9DvQvDCv1ACAtSARUCBBUCBBUCBJWouxbmz8HvvvY5vmBOQZj3JLJQgaBCP9AAovW46QcKkWg97kAxhUGFAEEl4if4TYuvhmQ7J2pm+9l+SDYvb3+aGJoNDTNUIKgQIKgQIKjQDxQmkXb+6AcaZox6/iJ+FeZvdeNvdRaq1dDd3n6kMObTAmFDgKBCgKBCgKBCgKBi2H6g8r1JPscTgvtVpyHb/lCjHwhhwRQGFQIEFQIEFQIEFQIEFQIEFfqB4BP9QAgLUgEVAgQVAgQVAgQVAgQVAgSVAZfxv51z1IdjRzBcWax3upUKBBUCBBUCBBUCBBUCBBXDBujJ3Owke2ud1d5aZz3VeGRqVeWWzJEjE0d4j9tb66z791U+6hnbXvHOJBGRlStK0k43104VEbFY7hlRVbkls7np26mNDYezt23dNMHzGPHxcTG//Hwo295aZ83MeNDS/3EbGw5nl2/ZOCEmxrCn2bgB8njhxTWnly5bf2bWzGnJi55/+j7v8YkZefVFzy5v9ozZ5s4YnZU16ZZvR7DZ8lLyZuQkz1/wUlPRwuXNnZ0Xb3humzN7ekpiomWEw3HZWVhoS+3/uO++t/3cwqL81EeyMgz7jQuGD5CISGxsbIyIiNvtvjm2Z3dFlr21zupdUWprj11a/9rL47z/93f72X9cLpe7dNmi+zMfmmB5v6LmvOe2wkJbakPDr1cOfvP9xYJn5o7pX2lMJpO4XC5xdF027GeiIuvTgoOwZ3dFVnf3ddePR084vvjyUOfkxx4eKdJbIU7+1HRFpHfaERHZUbWrfWdleabT6byZtFPNLVfnzV/S9NSsJ5JXvlKSVvbmmnRb/uLG+Pi4mLwZOUlbt+1oa2mxXyspLhqbkzN5lPfjiohU13ze0dZ24Xp4jzp8DB8g76AMpMtx2Vlds7d93drScT09N1wiIvnzZo4eMyYldv/+I3+aTCYp27g2PSnpXvOc2dNTzGaz6Y0Nq8d7/r+wwJZ64EDtRRGR4sXrzkyzThm1etWStH37DnWeabEb8gfoo2IK88UzhR39Ye/j3uM7P/6sw+H4f8r561KXc+mS58YeP/bVlDWvLntgR+Wu9o6Ozp7CAlvqseMnuyZm5NVPzMirr6za3Z4/b9bo2FizSUTE9a/Lvf2DT863/dF+fYNXyIzGVJw73u09cNbRLSIi1WUWERHJXXGBa2FR7PhHaVYRkdLNvQU0PTnhltujtgIhNAgQVAgQVAgQVAgQVAgQVAgQVAZ8J9rzPgDgCxUIKn4rkOedR+BOqEBQua0C9b/WAdwJFQgqBAgqBAgq/wEECqg3fl+aPAAAAABJRU5ErkJggg==\", \"SCUMM_08.png\": \"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\", \"SCUMM_09.png\": \"iVBORw0KGgoAAAANSUhEUgAAAJAAAACQCAYAAADnRuK4AAAFVElEQVR4nO3cf0yUdRzA8e/BeTKQH+FlyAyXIW20iSVwjZLaDKSlXP2hI7Qtlhul5mqzSVnrhxou/+gfaKssylkYLP/CbDFq3KYbm4vaQuu6lYAKyzkOSgdER3+4W6fcj+f4nPc8z937tfmHzz338Pjd2+/B8dlZ6isKZhUwTyl63wDMjYAgQkAQsd58YNA7qcd9wCSW56Td8Hd2IIjM2YH82vamx/M+YHANB64FPc4OBJGQO5BfqPKQHCK9ErEDQYSAIEJAEIn4PZDf9IzvVt4HDMZm1ba3aA5I6wWRXKgCIgQEEQKCCAFBhIAgQkAQ0fxjfJpN86lIAJPTM5rO01yF1gsiufASBhECgggBQYSAIEJAECEgiDAPhKCYB0JcUAVECAgiBAQRAoIIAUGEgCDCPBCCYh4IccFLGEQICCIEBBECgggBQYSAIMI8EIJiHghxwdvLMRbt52ub/VNw2VYgQkAQISCIEBBECAgizAPpzKjryjyQbmxRnW32deUlDCIEBBECgggBQcSYPwLoINl+hxUr7EAQYR5onmK1HkZdV+aBbrFYrYfZ19Xcdw/dERBECAgiBAQRAoIIAUGEeaB5itV6GHVdmQeKWqzmeJgHAjQjIIgQEEQICCIEBBECgojp54E+f2NRVOdveevvmHxd5oGuS7p5IKPN8Zh9Xc1999AdAUGEgCBCQBAhIIgQEESSbh7IaHM8Rl3XJJoHMtocD/NAgGYEBBECgggBQYSAIEJAEDH9PFC0jDbHY9R1ZR4oBKPN8Zh9XY35NmgQr2+9GvT474PBj4e+TvDjRrvOvqMZUV1HL+bOH7ojIIgQEEQICCIEBBHTzAMd6sjW9evHW1p0UyExl0TzQNATL2EQISCIEBBECAgiBAQRAoJI0s0DQRvmgRAXVAERAoIIAUGEgCBCQBAhIIhE/DH+1yFvXzxuBEaV7gj3KDsQRAgIIgQEEQKCCAFBJGECWrjQlvLjDydLPW6X456iFelKKfVgRWm2x+1ytLbsX6mUUs81bsk/+3NPmZbnlK5Zlek/L/DYK007CjxulyPwj7O2yh7peh63y/FT/zelh9599e6UlIRZ9sQJ6NF1D92WkZGe6vVOzDid1fbAx6qr1uYWF6+c82kF4Z4TSvPB1qHCosq+1fc/duaP88OTFy6OTvX29nkjXa/uqZ1n32luHXryiRr7vcVF5vjkBA0SJiCns9re3z/w14mvv7tSu7FqceD/8p6eU2MvvbhtWTTPieRgc9OK/KV32HbsfO037/jEjJbrWSwW5fP5lP/8RJAQAeXkZFkr15Znf9vtGuvudo3l5d1uKy8vyfI//uHhL0ZK16zKLCkpXqT1OeFse7Zuac36h3PffPu98wMD7qtarnesvaV4/77dd3125KvR4eFLU7H89+vJNJ8PFM6Gx9cttlqtlqY92wv8x5y11faurp4rSik17p2Yafu0Y2TXCw3Lpqf/8Wl5TihlZSWZL+9uvLOjs+vPzs4Tl7XeQ/3WXececNyXtf35p/OPHz95+dwvnmuxWwH9JMQO5Kyttp86fWa8sKiyr7Cosu+jw+0jNesfyV2wwGrxn/PxJ1+Oer3/v3REes6x9pZij9vl6P2+Y3Xg16rbvHFJamqqZfOmDUv83xw3PLMpL9L1fP/6ZlvfP3Jx+MLI1J6AyMzOUl9RMBt4YNA7qZRSqm1vulJKqYrGS/wuLImd/iDfoZRSDQeub5jLc9JueDwhdiDoh4AgQkAQISCIEBBECAgiBASRiO9E+98HAIJhB4JIyB3I/84jEA47EETm7EA3/64DCIcdCCIEBBECgsh/VKDIxCz47dEAAAAASUVORK5CYII=\", \"SCUMM_P2_PRESENTAR.png\": \"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\", \"SCUMM_P2_REUNION.png\": \"iVBORw0KGgoAAAANSUhEUgAAAJAAAACQCAYAAADnRuK4AAAFXklEQVR4nO3df0yUdRzA8c+huQNFxemwptA4ReSHpYXX8I/6A1tLg7Vsmrka1Vq19WMWOWcaztncCGeZQrXFhpKWMhZqscVa/xW6ubbUkhUOxgV2W5BXiMjd9Ye7AH1OHvw8PnfP8X7953PH9567vfd9PO7DzrW+KCMswC1KivUJwNkICCoEBJXJ1x/o6BuIxXnAITJnukf9mx0IKjfsQBFHs7LtPA/EuTXtbYbH2YGgEnUHiohWHiaGsa5E7EBQISCoEBBUxvw/UMTgUOh2ngfizJTJ5vYW0wGZXRATC1VAhYCgQkBQISCoEBBUCAgqpt/Gu6eYvisSwMDgkKn7ma7C7IKYWLiEQYWAoEJAUCEgqBAQVAgIKswDwRDzQLAFVUCFgKBCQFAhIKgQEFQICCrMA8EQ80CwBZcwqBAQVAgIKgQEFQKCCgFBhXkgGGIeCLagCqgQEFQICCoEBBUCggoBQcXx80AH52WN6/4butotedzq8injuv/LlYOWPK5dmAeKwrrnMb6AEuX1ux6XMKgQEFQICCoEBJX4fGt1G23d8K9FK6VYtI6zsQNBhXkgmzjt9WMeKM4k6uuXmM8KtiEgqEy4d2E7Dk61ZJ3aLZYs43jsQFAhIKgQEFQcPw80XrF6Hk57/ZgHioJ5IGtxCYMKAUGFgKBCQFAhIKgQEFQcMw/UlJ1jyTpHs7INj5e0/Wp4vP7daZY8bu0W4wnGp7f/Y8n6VmMeaJxi9fyc/ro6++wRcwQEFQKCCgFBxTEfEa9pb4vJ45bt7I/J4zoFOxBUJtw8EMxhHgi24BIGFQKCCgFBhYCgQkBQISCoOGYeCPZiHgi2oAqoEBBUCAgqBAQVAoIKAUGFeSAYYh4ItuASBhUCggoBQYWAoEJAUCEgqDAPBEPMA8EWVAEVAoIKAUGFgKBCQFAhIKiM+Tb+fGdfqx0ngjiVJd6b3cwOBBUCggoBQYWAoEJAFkhxu5O+3LUzZ1FmRnKsz8VuCRXQg8uWzvC3NHv9Lc3eC02N93+06S1Pkss16ri/pdnbsn9v/sj7e/PzUkVEGip3LT7xQVVu5HhtxdaFIiKvr1t7l++bY4VGP7Pu4ZWzv6vZV/BAQX7qvk3lnhX3LJk+8n5GaySShAooYvUbb57bVvNJ59qVxbOXLFw4deTxOcWPtBa/8uoZM+usWlE0q2CBZ2q02wvzclM/LN/oqTvx9Z95Tz51+nxH5+UDOyqy56Sl3WF2DadLyIBERFwul4TCYekNBP7/e6Tje6py/S3N3urNb3vMrNH8w4+9m8uenRft9pXLC2eEReTTxq96Av39wc+ajl1MTUmZFNmdzKzhdAn514LH91Tlioh83NDY09HdfeXuO+e6Ra7tQK1nzgYi9wuGQmGRa7GJiLhEJBgcHpzb+8WR7sPv7Vh0dWgofKvnYsUa8Swhd6DSjeW/VNYd9D1X+lh6nifL+KsCReSC74+BUDgs9y3OmTZr+vTJC+bPd//W1XU5cnvfpcBQTUNj96MritKMfv7bk6f+donI86Ul6dNSkieVlaxOD/T3B0dGOtYaTpeQAQVDofDu+kO+zp6LVypefCEjcjxyCTtdX3eviIjP7x98Z39Nx0tPPD73p0MHlv7e1TVQdeBz38i1qo829Px16ZLhn+WeOnsu8Nr7u9vLSlalnztyeFlOZmbyM9u2t/l7e6+aXcPpXOuLMkZtrR19AyIy/N2iBd+f5LOwCeznh5Z7RYa/LSlzpnvU7Qm5A8E+BAQVAoIKAUGFgKBCQFAhIKiM+VFG5PcAgBF2IKhE3YFi9T3tcBZ2IKjcsANd/1kHcDPsQFAhIKgQEFT+A4Z1h70w62SfAAAAAElFTkSuQmCC\", \"SCUMM_P2_MAC.png\": \"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\"}"

def write_icons():
    STAGING.mkdir(parents=True, exist_ok=True)
    icons = STAGING / "icons"
    icons.mkdir(exist_ok=True)
    b64map = load_icons_b64()
    for name, b64 in b64map.items():
        (icons / name).write_bytes(base64.b64decode(b64))
    aliases = [
        ("01-preguntar.png","SCUMM_01.png"),("02-examinar.png","SCUMM_02.png"),
        ("03-debatir.png","SCUMM_03.png"),("04-entrenar.png","SCUMM_04.png"),
        ("05-crear.png","SCUMM_05.png"),("06-yarig.png","SCUMM_06.png"),
        ("07-pensar.png","SCUMM_07.png"),("08-votar.png","SCUMM_08.png"),
        ("09-analizar.png","SCUMM_09.png"),
    ]
    for a, s in aliases:
        src = icons / s
        if src.exists():
            shutil.copy2(src, icons / a)
    log("icons -> " + str(icons))
    return icons

def backup(page_dir: Path):
    BACKUP_ROOT.mkdir(parents=True, exist_ok=True)
    bak = BACKUP_ROOT / ("flt100705-atajos-mac-" + TS + ".tar.gz")
    paths = [str(page_dir)]
    if CLI.exists():
        paths.append(str(CLI))
    run("tar czf '%s' %s" % (bak, " ".join("'%s'" % p for p in paths)))
    log("BACKUP=" + str(bak))
    return str(bak)

def ensure_helper(app_name: str, verb: str):
    HELPERS.mkdir(parents=True, exist_ok=True)
    app = HELPERS / app_name
    if app.exists():
        log("helper exists: " + str(app))
        return app
    scpt_line = (
        'do shell script "/usr/bin/python3 '
        '/Users/csilvasantin/.codex/streamdeck-admira-live/admira_live_cli.py '
        + verb + ' >/tmp/al-' + verb + '.log 2>&1 &"'
    )
    tmp = Path(tempfile.mkdtemp()) / (verb + ".applescript")
    tmp.write_text(scpt_line + "\n")
    run('osacompile -o "%s" "%s"' % (app, tmp))
    log("created helper: " + str(app))
    return app

def extend_cli():
    if not CLI.exists():
        log("WARNING: CLI missing at " + str(CLI))
        return False
    text = CLI.read_text()
    additions = {
        "examinar": "clickVerb('examinar')",
        "votar": "clickVerb('votar')",
        "pensar": "clickVerb('leer')",
        "reunion": "clickVerb('reunion')",
        "mostrar": "(window.MacHoy&&MacHoy.toggle())||document.getElementById('btn-mostrar')&&document.getElementById('btn-mostrar').click()",
    }
    import re
    changed = False
    # Strategy: if JS_ACTIONS dict exists, insert missing keys after opening {
    m = re.search(r"JS_ACTIONS\s*=\s*\{", text)
    if not m:
        block = "\n# FLT-100705\nJS_ACTIONS_EXTRA = {\n"
        for k, v in additions.items():
            block += '    "%s": %s,\n' % (k, json.dumps(v))
        block += "}\n"
        block += "try:\n    JS_ACTIONS.update(JS_ACTIONS_EXTRA)\nexcept Exception:\n    pass\n"
        CLI.write_text(text + block)
        log("CLI appended JS_ACTIONS_EXTRA")
        return True
    for key, js in additions.items():
        if re.search(r"['\"]%s['\"]\s*:" % key, text):
            log("CLI already has " + key)
            continue
        # re-find each time as text grows
        m = re.search(r"JS_ACTIONS\s*=\s*\{", text)
        insert_at = m.end()
        entry = '\n    "%s": %s,' % (key, json.dumps(js))
        text = text[:insert_at] + entry + text[insert_at:]
        changed = True
        log("CLI +" + key)
    if changed:
        CLI.write_text(text)
        log("CLI updated")
    return True

def find_page_dir(profile: Path) -> Path:
    direct = profile / "Profiles" / PAGE_ID
    if direct.exists():
        return direct
    if (profile / PAGE_ID).exists():
        return profile / PAGE_ID
    # folder named with uuid
    for d in profile.rglob("*"):
        if d.is_dir() and PAGE_ID in d.name:
            return d
    for man in profile.rglob("manifest.json"):
        try:
            data = json.loads(man.read_text())
        except Exception:
            continue
        name = str(data.get("Name") or data.get("name") or "")
        if "Atajos Mac" in name:
            return man.parent
        # uuid in path
        if PAGE_ID in str(man):
            return man.parent
    raise FileNotFoundError("Page " + PAGE_ID + " not found")

def rewrite_manifest(page_dir: Path, icons_dir: Path):
    man_path = page_dir / "manifest.json"
    if not man_path.exists():
        found = list(page_dir.rglob("manifest.json"))
        if not found:
            raise FileNotFoundError(str(man_path))
        man_path = found[0]
        page_dir = man_path.parent

    data = json.loads(man_path.read_text())
    images_dir = page_dir / "Images"
    images_dir.mkdir(exist_ok=True)
    for _pos, (_t, _a, _v, icon_name) in KEYS.items():
        shutil.copy2(icons_dir / icon_name, images_dir / icon_name)

    controllers = data.get("Controllers")
    if controllers and isinstance(controllers, list) and controllers:
        actions = controllers[0].get("Actions")
        if actions is None:
            actions = {}
            controllers[0]["Actions"] = actions
    else:
        actions = data.get("Actions")
        if actions is None:
            raise RuntimeError("No Actions in manifest; keys=" + str(list(data.keys())[:30]))

    # Save hotkeys aside (CAPTURA/AREA/PANTALLA) before rewrite
    hotkey_aside = {}
    for k, v in list(actions.items()):
        title = ""
        try:
            title = ((v.get("States") or [{}])[0].get("Title") or "").upper()
        except Exception:
            pass
        if any(s in title for s in KEEP_TITLE_SUBSTR):
            hotkey_aside[k] = json.loads(json.dumps(v))
            log("aside hotkey %s title=%r" % (k, title))

    # Remap 9 Open keys.
    #
    # OJO CON LA FORMA (MorfeoMacMini, 2026-09-20). En ProfilesV3 —Stream Deck
    # 7.4.2— cada tecla es una accion PLANA:
    #     {"ActionID":…, "Name":"Open", "Plugin":{…}, "Settings":{…},
    #      "States":[…], "UUID":"com.elgato.streamdeck.system.open"}
    # NO un envoltorio con una lista "Actions" dentro, que es la forma vieja.
    # Buscando la muestra por ov["Actions"][0] no se encontraba nunca, se caia al
    # camino de respaldo y ese escribia el envoltorio antiguo: sin UUID ni Plugin
    # de primer nivel. La app lo lee como TECLA VACIA, asi que el script no
    # instalaba nada: BORRABA las nueve y decia "INSTALL DONE". Pasó de verdad en
    # el MacMini y hubo que reescribir el manifest a mano.
    sample = None
    for ov in actions.values():
        if not isinstance(ov, dict):
            continue
        if ov.get("UUID") == OPEN_PLUGIN or ov.get("Name") == "Open":
            sample = ov
            break

    for pos, (title, app_name, verb, icon_name) in KEYS.items():
        app = ensure_helper(app_name, verb)
        path_setting = '"%s"' % app
        if sample:
            new = json.loads(json.dumps(sample))
        else:
            # Sin muestra en esta pagina, se construye la accion plana entera.
            new = {
                "LinkedTitle": True,
                "Name": "Open",
                "Plugin": {"Name": "Open", "UUID": OPEN_PLUGIN, "Version": "1.0"},
                "Resources": None,
                "State": 0,
                "States": [{
                    "FontFamily": "", "FontSize": 10, "FontStyle": "",
                    "FontUnderline": False, "OutlineThickness": 2,
                    "TitleAlignment": "bottom", "TitleColor": "#ffffff",
                }],
            }
        # ActionID propio: clonar el de la muestra deja nueve teclas con el mismo
        # identificador y la app se lia al guardar.
        new["ActionID"] = str(uuid.uuid4())
        new["UUID"] = OPEN_PLUGIN
        new["Name"] = "Open"
        new["Plugin"] = {"Name": "Open", "UUID": OPEN_PLUGIN, "Version": "1.0"}
        new.setdefault("Settings", {})["path"] = path_setting
        new.pop("Actions", None)          # restos de la forma vieja, si los hubiera
        if not new.get("States"):
            new["States"] = [{}]
        # El manifest guarda la imagen RELATIVA a la pagina: "Images/SCUMM_01.png".
        # Con el nombre pelado la tecla sale en negro.
        new["States"][0]["Image"] = "Images/" + icon_name
        new["States"][0]["Title"] = title
        new["States"][0]["ShowTitle"] = False     # el icono ya trae la palabra dibujada
        actions[pos] = new
        log("SET %s -> %s -> %s" % (pos, title, app))

    # Restore hotkeys at their original coords (do not overwrite our new 9 if conflict —
    # left column 0,* should hold them; if they were at 0,0/1,0/2,0 top-row style, keep there
    # ONLY when that key is NOT one of our KEYS)
    for k, v in hotkey_aside.items():
        if k in KEYS:
            # conflict: place into left column by title
            title = ((v.get("States") or [{}])[0].get("Title") or "").upper()
            target = None
            if "CAPTURA" in title:
                target = "0,0"
            elif "AREA" in title or "ÁREA" in title:
                target = "0,1"
            elif "PANTALLA" in title:
                target = "0,2"
            if target and target not in KEYS:
                actions[target] = v
                log("MOVED hotkey %s -> %s" % (k, target))
            else:
                log("WARNING: could not place hotkey %s title=%r" % (k, title))
        else:
            actions[k] = v
            log("RESTORE hotkey at %s" % k)

    if controllers and isinstance(controllers, list):
        controllers[0]["Actions"] = actions
        data["Controllers"] = controllers
    else:
        data["Actions"] = actions

    man_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    log("wrote " + str(man_path))
    return actions, str(man_path)

def print_grid(actions):
    print("=== FINAL GRID ===")
    for r in range(3):
        row = []
        for c in range(4):
            k = "%d,%d" % (c, r)
            v = actions.get(k) or {}
            try:
                t = ((v.get("States") or [{}])[0].get("Title") or "(empty)")
            except Exception:
                t = "(empty)"
            row.append("%s:%s" % (k, t))
        print(" | ".join(row))

def main():
    log("=== FLT-100705 INSTALL START ===")
    icons = write_icons()
    if not PROFILES.exists():
        log("FATAL: ProfilesV3 missing")
        sys.exit(2)
    profile = PROFILES / PROFILE_ID
    if not profile.exists():
        hits = list(PROFILES.glob("*6041EB74*"))
        if not hits:
            log("FATAL: profile missing; listing:")
            for p in sorted(PROFILES.iterdir())[:40]:
                log("  " + p.name)
            sys.exit(2)
        profile = hits[0]
    log("profile=" + str(profile))
    page_dir = find_page_dir(profile)
    log("page_dir=" + str(page_dir))
    bak = backup(page_dir)

    run('killall "Stream Deck" || true', check=False)
    time.sleep(2)

    extend_cli()
    for _pos, (_t, app_name, verb, _i) in KEYS.items():
        ensure_helper(app_name, verb)

    actions, man = rewrite_manifest(page_dir, icons)

    # La app se llama "Elgato Stream Deck" en /Applications; con "Stream Deck" a
    # secas macOS responde "Unable to find application named" y el teclado se
    # quedaba MUERTO, porque el killall de arriba si acierta (ese es el nombre del
    # proceso, no el del bundle). Se prueban los dos nombres y se comprueba.
    relanzada = False
    for nombre in ("Elgato Stream Deck", "Stream Deck"):
        r = run('open -a "%s"' % nombre, check=False)
        if r.returncode == 0:
            relanzada = True
            log("relanzada como %r" % nombre)
            break
    if not relanzada:
        log("AVISO: no se pudo relanzar Stream Deck; abrela a mano")
    time.sleep(2)

    # re-read
    data = json.loads(Path(man).read_text())
    controllers = data.get("Controllers") or []
    actions = (controllers[0].get("Actions") if controllers else None) or data.get("Actions") or {}
    print_grid(actions)
    print("BACKUP=" + bak)
    print("MANIFEST=" + man)
    # helpers check
    problemas = []
    for _pos, (_t, app_name, _v, _i) in KEYS.items():
        ok = (HELPERS / app_name).exists()
        print("helper %s: %s" % (app_name, "OK" if ok else "MISSING"))
        if not ok:
            problemas.append("helper ausente: " + app_name)

    # COMPROBAR DE VERDAD ANTES DE CANTAR VICTORIA. La version anterior imprimia
    # "INSTALL DONE" y salia con 0 aunque la rejilla hubiera quedado con las nueve
    # teclas vacias: el que lo lanzaba se creia que estaba puesto. Si algo no
    # cuadra, se dice y se sale con error, que para eso esta el backup.
    for pos, (title, app_name, _v, icon_name) in KEYS.items():
        a = actions.get(pos) or {}
        st = (a.get("States") or [{}])[0]
        if a.get("UUID") != OPEN_PLUGIN:
            problemas.append("%s (%s): sin accion Open (UUID=%r)" % (pos, title, a.get("UUID")))
        ruta = (a.get("Settings") or {}).get("path", "").strip('"')
        if not ruta or not os.path.exists(ruta):
            problemas.append("%s (%s): ruta inexistente %r" % (pos, title, ruta))
        if st.get("Image") != "Images/" + icon_name:
            problemas.append("%s (%s): icono %r" % (pos, title, st.get("Image")))
    if not relanzada:
        problemas.append("Stream Deck no relanzado")

    if problemas:
        print("=== FLT-100705 INSTALL FALLIDO ===")
        for p in problemas:
            print("  ! " + p)
        print("Restaura con: tar xzf '%s' -C /" % bak)
        sys.exit(1)
    print("=== FLT-100705 INSTALL DONE ===")

if __name__ == "__main__":
    main()
