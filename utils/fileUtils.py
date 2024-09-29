from typing import List

import aiofiles
import asyncio
import logging


def addLineToFile(filePath: str, line: str) -> None:
    with open(filePath, 'a', encoding='utf-8') as file:
        file.write(line + '\n')


def isLineInFile(filePath: str, line: str) -> bool:
    with open(filePath, 'r', encoding='utf-8') as file:
        return line in file.read().splitlines()


def readFile(filePath: str) -> list[str]:
    with open(filePath, 'r', encoding='utf-8') as file:
        return file.read().splitlines()


def removeLineFromFile(filePath: str, lineToRemove: str) -> None:
    with open(filePath, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    with open(filePath, 'w', encoding='utf-8') as file:
        for line in lines:
            if line.strip() != lineToRemove:
                file.write(line)


async def addLineToFileAsync(filePath: str, line: str) -> None:
    async with aiofiles.open(filePath, 'a', encoding='utf-8') as file:
        await file.write(line + '\n')


async def addLinesToFileAsync(filePath: str, lines: list[str]) -> None:
    tasks = [addLineToFileAsync(filePath, line) for line in lines if not isLineInFile(filePath, line)]

    await asyncio.gather(*tasks)


async def removeLineFromFileAsync(filePath: str, lineToRemove: str) -> None:
    async with aiofiles.open(filePath, 'r', encoding='utf-8') as file:
        lines = await file.readlines()

    async with aiofiles.open(filePath, 'w', encoding='utf-8') as file:
        for line in lines:
            if line.strip() != lineToRemove:
                await file.write(line)
