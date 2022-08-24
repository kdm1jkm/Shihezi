############################################################
# 연도는 1982년부터 2022년 사이로 월은 3월 부터 8월 사이
# 1. 홈팀이 MBC일 때  승 column에서 H의 개수
# 2. 홈팀이 MBC일 때  승 column에서 A의 개수
# 3. 방문팀이 MBC일 때  승 column에서 A의 개수
# 4. 방문팀이 MBC일 때  승 column에서 H의 개수
#   [1] ‘1’과 ‘3’의 합 & ‘2’과 ‘4’의 합 (따로)
# 5. 홈 팀이 MBC일 때 scorelist 짝수 항의 합
# 6. 홈 팀이 MBC일 때 scorelist 홀수 항의 합
# 7. 방문팀이 MBC일 때 scorelist 홀수 항의 합
# 8. 방문팀이 MBC일 때 scorelist 짝수 항의 합
#   [2] ‘5’와 ’7’의 합 & ‘6’과 ‘8’의 합 (따로)
############################################################


from collections import defaultdict
from datetime import datetime
import pickle
import pandas as pd
import openpyxl

import os


# constants
FILE_NAME = "data"
MONTH_RANGE = range(3, 8 + 1)
TEAM = "MBC"
OUTPUT_NAME = (
    lambda num: f"output/{datetime.now().strftime('%Y%m%d-%H%M%S')}-{num}.xlsx"
)

# TEAM = input("Enter team: ")


def 득실점(data: pd.DataFrame, month_range=MONTH_RANGE):
    data = data.loc[data["month"].isin(month_range)]

    count: dict[str, dict[int, list[int]]] = defaultdict(
        lambda: defaultdict(lambda: [0, 0])
    )

    for _, row in data.iterrows():
        scores = (
            row["scorelist"]
            if isinstance(row["scorelist"], list)
            else [row["scorelist"]]
        )
        for i, score in enumerate(map(int, scores)):
            if i % 2 == 0:
                count[row["홈팀"]][row["year"]][0] += score
                count[row["방문팀"]][row["year"]][1] += score
            else:
                count[row["홈팀"]][row["year"]][1] += score
                count[row["방문팀"]][row["year"]][0] += score

    result: dict[str, list[tuple[int, int, int]]] = dict()
    for k, v in count.items():
        result[k] = [(nk, nv[0], nv[1]) for nk, nv in v.items()]

    return result


def 승패횟수(data: pd.DataFrame, month_range=MONTH_RANGE):
    data = data.loc[data["month"].isin(month_range)]

    홈 = data.loc[data["승"] == "H"]
    원정 = data.loc[data["승"] == "A"]

    홈_승리 = 홈.rename(columns={"홈팀": "팀"})
    원정_승리 = 원정.rename(columns={"방문팀": "팀"})

    홈_패배 = 원정.rename(columns={"홈팀": "팀"})
    원정_패배 = 홈.rename(columns={"방문팀": "팀"})

    count: dict[str, dict[int, list[int]]] = defaultdict(
        lambda: defaultdict(lambda: [0, 0])
    )

    for 승리 in [홈_승리, 원정_승리]:
        for _, row in 승리.iterrows():
            count[row["팀"]][row["year"]][0] += 1

    for 패배 in [홈_패배, 원정_패배]:
        for _, row in 패배.iterrows():
            count[row["팀"]][row["year"]][1] += 1

    result: dict[str, list[tuple[int, int, int]]] = dict()
    for k, v in count.items():
        result[k] = [(nk, nv[0], nv[1]) for nk, nv in v.items()]

    return result


def main():
    # 파일 읽어옴
    with open(FILE_NAME, "rb") as f:
        data = pd.DataFrame(pickle.load(f))

    result1 = 승패횟수(data)
    result2 = 득실점(data)

    # 파일로 저장
    if not os.path.isdir("./output"):
        os.mkdir("./output")

    def write_excel(ws, data):
        for d in data:
            ws.append(d)

    wb = openpyxl.Workbook()

    for k, v in result1.items():
        ws = wb.create_sheet(str(k))
        ws.append(["팀", "승리", "패배"])
        write_excel(ws, v)

    del wb["Sheet"]
    wb.save(OUTPUT_NAME(1))

    wb = openpyxl.Workbook()

    for k, v in result2.items():
        ws = wb.create_sheet(str(k))
        ws.append(["팀", "득점", "실점"])
        write_excel(ws, v)

    del wb["Sheet"]
    wb.save(OUTPUT_NAME(2))

    # pandas로 나타내기
    frame1 = [
        f'{k}\n{pd.DataFrame(v, columns=["연도", "승리", "패배"])}'
        for k, v in result1.items()
    ]
    frame2 = [
        f'{k}\n{pd.DataFrame(v, columns=["연도", "득점", "실점"])}'
        for k, v in result2.items()
    ]
    print(*frame1, sep="\n=========\n")
    print("*****************************************************")
    print(*frame2, sep="\n=========\n")


if __name__ == "__main__":
    main()
