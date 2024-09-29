import aiofiles
import asyncio

def addLineToFile(filePath: str, line: str) -> None:
    with open(filePath, 'a', encoding='utf-8') as file:
        file.write(line + '\n')


def isLineInFile(filePath: str, line: str) -> bool:
    with open(filePath, 'r', encoding='utf-8') as file:
        return line in file.read().splitlines()


async def addLineToFileAsync(filePath: str, line: str) -> None:
    async with aiofiles.open(filePath, 'a', encoding='utf-8') as file:
        await file.write(line + '\n')


async def addLinesToFileAsync(filePath: str, lines: list[str]) -> None:
    tasks = [addLineToFileAsync(filePath, line) for line in lines if not isLineInFile(filePath, line)]

    await asyncio.gather(*tasks)
