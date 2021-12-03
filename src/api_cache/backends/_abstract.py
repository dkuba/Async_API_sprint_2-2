import abc


class Backend:
    @abc.abstractmethod
    async def get(self, key: str) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    async def set(self, key: str, value: str, expire: int = None):
        raise NotImplementedError
